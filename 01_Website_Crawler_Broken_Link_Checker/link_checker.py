"""HTTP request core shared by the link checker and the page crawler.

GET (stream=True) is used on purpose instead of HEAD: some servers answer
HEAD differently from GET (e.g. HEAD 404 while GET 200). With stream=True only
the response headers are read, so large files are not downloaded just to learn
their status.
"""

import re
import threading
import time
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from time import perf_counter
from urllib.parse import urljoin

import requests

from models import (
    LINK_RETRY_TIMEOUT,
    LINK_TIMEOUT,
    MAX_RETRY_AFTER,
    LinkResult,
)
from rate_limiter import HostRateLimiter
from utils import normalize_url

__all__ = [
    "USER_AGENT", "DEFAULT_TIMEOUT", "RETRY_TIMEOUT", "LinkResult",
    "HostRateLimiter", "normalize_url", "RequestOutcome", "ThreadSessions",
    "perform_request", "check_link",
]

# A normal browser-like UA avoids servers treating a custom crawler UA as a
# special bot; the tool still identifies itself via X-Website-Crawler.
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/140.0.0.0 Safari/537.36"
)

DEFAULT_TIMEOUT = LINK_TIMEOUT          # (connect, read)
RETRY_TIMEOUT = LINK_RETRY_TIMEOUT

TRANSIENT_STATUSES = frozenset({408, 429}) | frozenset(range(500, 600))
_SMALL_BODY = 64 * 1024


@dataclass
class RequestOutcome:
    result: LinkResult
    body: object = None            # bytes (HTTP) / str (browser) / None
    content_type: str = ""


class ThreadSessions:
    """One requests.Session per worker thread (Session is not thread-safe),
    all closed together when the scan ends."""

    def __init__(self):
        self._local = threading.local()
        self._sessions = []
        self._lock = threading.Lock()

    def get(self):
        session = getattr(self._local, "session", None)
        if session is None:
            session = requests.Session()
            session.max_redirects = 10
            session.headers.update({
                "User-Agent": USER_AGENT,
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;q=0.9,"
                    "image/avif,image/webp,*/*;q=0.8"
                ),
                "Accept-Language": "en-US,en;q=0.9",
                "X-Website-Crawler": "WebsiteCrawlerBrokenLinkChecker/3.0",
            })
            self._local.session = session
            with self._lock:
                self._sessions.append(session)
        return session

    def close_all(self):
        with self._lock:
            sessions, self._sessions = self._sessions, []
        for session in sessions:
            try:
                session.close()
            except Exception:
                pass


_SSL_REASON_RE = re.compile(r"\[SSL: ([A-Z0-9_]+)\]([^()]*)")


def _short_error(error):
    text = str(error)
    lowered = text.lower()
    if isinstance(error, requests.exceptions.SSLError) or "ssl" in lowered[:200]:
        match = _SSL_REASON_RE.search(text)
        if match:
            return f"SSL error: {match.group(1)} {match.group(2).strip()}".strip()
        if "certificate" in lowered:
            return "SSL error: certificate could not be verified"
        return "SSL error: TLS handshake failed"
    if ("nameresolution" in lowered or "name or service not known" in lowered
            or "getaddrinfo" in lowered or "nodename nor servname" in lowered):
        return "DNS lookup failed (host not found)"
    if "connection refused" in lowered:
        return "Connection refused"
    if "connection reset" in lowered or "connectionreseterror" in lowered:
        return "Connection reset by server"
    if "remotedisconnected" in lowered or "connection aborted" in lowered:
        return "Server closed the connection"
    if "timed out" in lowered:
        return "Request timed out"
    return text if len(text) <= 180 else text[:177] + "..."


def _retry_after_seconds(response):
    value = response.headers.get("Retry-After", "")
    seconds = None
    try:
        seconds = float(value)
    except (TypeError, ValueError):
        try:
            seconds = parsedate_to_datetime(value).timestamp() - time.time()
        except (TypeError, ValueError, OverflowError):
            seconds = None
    if seconds is None:
        return 0.5
    # Never let a server-provided Retry-After stall a scan.
    return min(max(seconds, 0.0), MAX_RETRY_AFTER)


def _release_response(response):
    """Close a streamed response. Small bodies are drained first so the
    keep-alive connection can be reused instead of re-doing TCP/TLS."""
    try:
        length = response.headers.get("Content-Length")
        if length is not None and int(length) <= _SMALL_BODY:
            _ = response.content
    except Exception:
        pass
    finally:
        try:
            response.close()
        except Exception:
            pass


def _error_result(url, elapsed, error_type, error, attempts):
    return LinkResult(
        url=url,
        status=None,
        final_url=url,
        elapsed=elapsed,
        error_type=error_type,
        error_message=_short_error(error),
        method="GET",
        attempts=attempts,
    )


def perform_request(
    session,
    url,
    *,
    timeout=DEFAULT_TIMEOUT,
    retry_timeout=RETRY_TIMEOUT,
    limiter=None,
    stop_event=None,
    body_reader=None,
    max_attempts=2,
    priority=False,
    follow_redirects=True,
):
    """GET `url` with bounded retries. Returns a RequestOutcome, or None if
    the scan was stopped.

    Retried (once): timeout, connection error, 408, 429, 5xx.
    429 honours Retry-After but never for more than MAX_RETRY_AFTER seconds.

    body_reader(response, stop_event) -> bytes|None is called while the
    response is still open (and the host slot still held) for the final
    response; it decides whether the body is read at all.

    follow_redirects=False reports the first response as it is (e.g. 301);
    its final_url is then the Location target, if the server sent one.
    """
    attempts = 0
    retry_delay = 0.0
    last_error = None

    for attempt_index in range(max_attempts):
        attempts = attempt_index + 1

        if attempt_index > 0:
            if stop_event is not None:
                if stop_event.wait(retry_delay):
                    return None
            elif retry_delay:
                time.sleep(retry_delay)

        if stop_event is not None and stop_event.is_set():
            return None

        acquired = False
        response = None
        request_started = perf_counter()
        is_last = attempt_index == max_attempts - 1

        try:
            if limiter is not None:
                acquired = limiter.acquire(
                    url, stop_event=stop_event, priority=priority)
                if not acquired:
                    return None

            request_started = perf_counter()
            response = session.get(
                url,
                allow_redirects=follow_redirects,
                timeout=timeout if attempt_index == 0 else retry_timeout,
                stream=True,
            )
            elapsed = perf_counter() - request_started
            status = response.status_code

            if status in TRANSIENT_STATUSES and not is_last:
                if status == 429:
                    retry_delay = _retry_after_seconds(response)
                    if limiter is not None:
                        limiter.penalize(url, retry_delay)
                else:
                    retry_delay = 0.35
                continue  # response released in `finally`

            body = None
            content_type = response.headers.get("Content-Type", "")
            if body_reader is not None:
                body = body_reader(response, stop_event)

            final_url = response.url
            if not follow_redirects and 300 <= status < 400:
                location = response.headers.get("Location")
                if location:
                    final_url = urljoin(response.url, location)

            result = LinkResult(
                url=url,
                status=status,
                final_url=final_url,
                elapsed=elapsed,
                method="GET",
                redirect_history=[
                    (item.status_code, item.url) for item in response.history
                ],
                attempts=attempts,
            )
            return RequestOutcome(result, body, content_type)

        except requests.exceptions.SSLError as error:
            return RequestOutcome(_error_result(
                url, perf_counter() - request_started,
                "SSL ERROR", error, attempts))

        except requests.exceptions.TooManyRedirects:
            return RequestOutcome(_error_result(
                url, perf_counter() - request_started,
                "TOO MANY REDIRECTS",
                "Redirect loop or more than 10 redirects", attempts))

        except requests.exceptions.Timeout as error:
            last_error = ("TIMEOUT", error, perf_counter() - request_started)
            retry_delay = 0.35

        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.ChunkedEncodingError,
        ) as error:
            last_error = (
                "CONNECTION ERROR", error, perf_counter() - request_started)
            retry_delay = 0.35

        except (
            requests.exceptions.InvalidURL,
            requests.exceptions.InvalidSchema,
            requests.exceptions.MissingSchema,
        ) as error:
            return RequestOutcome(_error_result(
                url, 0.0, "INVALID URL", error, attempts))

        except Exception as error:  # includes other RequestException types
            return RequestOutcome(_error_result(
                url, perf_counter() - request_started,
                "REQUEST ERROR", error, attempts))

        finally:
            if response is not None:
                _release_response(response)
            if acquired and limiter is not None:
                limiter.release(url)

    error_type, error, elapsed = last_error or (
        "REQUEST ERROR", "No response after retry", 0.0)
    return RequestOutcome(
        _error_result(url, elapsed, error_type, error, attempts))


def check_link(
    session,
    url,
    timeout=DEFAULT_TIMEOUT,
    limiter=None,
    stop_event=None,
    retry_timeout=None,
    follow_redirects=True,
):
    """Check one URL (GET, headers only). Returns a LinkResult, or None when
    the scan was stopped before/while the request ran.

    Used by both the full scan and the Single Link Check screen."""
    outcome = perform_request(
        session,
        url,
        timeout=timeout,
        retry_timeout=RETRY_TIMEOUT if retry_timeout is None else retry_timeout,
        limiter=limiter,
        stop_event=stop_event,
        follow_redirects=follow_redirects,
    )
    return None if outcome is None else outcome.result
