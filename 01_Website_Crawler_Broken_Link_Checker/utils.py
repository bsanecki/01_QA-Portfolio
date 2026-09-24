"""Small shared helpers (no network, no GUI)."""

import re
from urllib.parse import urlsplit, urlunsplit

_STRIP_CHARS_RE = re.compile(r"[\t\r\n]")
_DEFAULT_PORTS = {"http": ":80", "https": ":443"}


def normalize_url(url: str) -> str:
    """Normalize a URL for deduplication *without* changing its meaning.

    * scheme and host are lower-cased
    * default ports (:80 for http, :443 for https) are dropped
    * the #fragment is removed
    * an empty path becomes "/"
    * the query string is kept exactly as written
    * a trailing slash is kept exactly as written: "/docs" and "/docs/" may be
      different resources on some servers, so they are not merged.

    May raise ValueError for malformed URLs; callers that parse untrusted
    HTML must catch it.
    """
    url = _STRIP_CHARS_RE.sub("", url.strip())
    parts = urlsplit(url)
    scheme = parts.scheme.lower()

    userinfo, at, hostport = parts.netloc.rpartition("@")
    hostport = hostport.lower()
    default_port = _DEFAULT_PORTS.get(scheme)
    if default_port and hostport.endswith(default_port):
        hostport = hostport[: -len(default_port)]
    netloc = f"{userinfo}{at}{hostport}"

    return urlunsplit((scheme, netloc, parts.path or "/", parts.query, ""))


def host_key(url_or_netloc: str) -> str:
    """Host identity used for the internal/external decision.

    "www.example.com" and "example.com" are treated as the same site; other
    sub-domains and other ports are different hosts.
    """
    netloc = url_or_netloc
    if "://" in netloc:
        netloc = urlsplit(netloc).netloc
    netloc = netloc.rpartition("@")[2].lower()
    return netloc[4:] if netloc.startswith("www.") else netloc


def format_time(seconds) -> str:
    seconds = max(0, int(seconds))
    hours, rest = divmod(seconds, 3600)
    minutes, secs = divmod(rest, 60)
    if hours:
        return f"{hours}h {minutes}m {secs}s"
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"
