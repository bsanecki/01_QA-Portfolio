"""Page-level building blocks of the crawler.

Nothing in this module starts threads or touches the GUI:

* LinkExtractor  - finds every URL in HTML / CSS / sitemaps (pure parsing)
* RobotsPolicy   - robots.txt rules, Crawl-delay and Sitemap: lines
* PageFetcher    - "how do I download a page" abstraction. HttpPageFetcher is
                   the fast requests-based implementation; a browser-based one
                   lives in browser_crawler.py and plugs in the same way.

The parallel pipeline that ties these together is in scan_engine.py.
"""

import re
import time
import xml.etree.ElementTree as ET
import zlib
from html import unescape
from urllib import robotparser
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup

from link_checker import USER_AGENT, perform_request
from models import (
    AUX_TIMEOUT,
    MAX_BODY_SECONDS,
    MAX_CSS_BYTES,
    MAX_PAGE_BYTES,
    MAX_SITEMAP_BYTES,
    PAGE_RETRY_TIMEOUT,
    PAGE_TIMEOUT,
    DiscoveredLink,
)
from settings import scale_timeout
from utils import normalize_url

# Source types whose *internal* targets are crawled as HTML pages.
PAGE_SOURCE_TYPES = frozenset({
    "start", "link", "area", "iframe", "frame", "meta-refresh", "base",
    "sitemap",
})
# Source types whose *internal* targets are stylesheets to parse for url()s.
STYLESHEET_SOURCE_TYPES = frozenset({"stylesheet", "css/import"})

_SKIP_PREFIXES = (
    "#", "mailto:", "tel:", "javascript:", "data:", "blob:", "about:",
    "file:", "chrome:", "chrome-extension:", "sms:", "whatsapp:", "skype:",
    "magnet:", "ftp:",
)
# Unrendered template placeholders would only produce false "broken" links.
_TEMPLATE_MARKERS = ("{{", "}}", "${", "{%", "<%", "%7b%7b", "%7B%7B")
# <link rel=...> values that are connection hints, not navigable resources.
_SKIP_LINK_RELS = frozenset({"dns-prefetch", "preconnect", "pingback"})

_CSS_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
_CSS_URL_RE = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.IGNORECASE)
_CSS_IMPORT_RE = re.compile(
    r"@import\s+(?:url\(\s*)?(['\"]?)([^'\")\s;]+)\1", re.IGNORECASE)
_META_REFRESH_RE = re.compile(r"url\s*=\s*['\"]?([^'\";]+)", re.IGNORECASE)
_CHARSET_RE = re.compile(r"charset\s*=\s*['\"]?([\w\-]+)", re.IGNORECASE)


def charset_from_content_type(content_type):
    match = _CHARSET_RE.search(content_type or "")
    return match.group(1) if match else None


# ---------------------------------------------------------------------------
# Link extraction
# ---------------------------------------------------------------------------


class LinkExtractor:
    """Find URLs in HTML, CSS and sitemap documents. Pure functions of their
    input: no network, no shared state, safe to call from many threads."""

    # (tag, attribute, source_type). <link href> is handled separately because
    # its source type depends on rel=.
    RESOURCE_ATTRIBUTES = (
        ("a", "href", "link"),
        ("area", "href", "area"),
        ("script", "src", "script"),
        ("img", "src", "image"),
        ("iframe", "src", "iframe"),
        ("frame", "src", "frame"),
        ("embed", "src", "embed"),
        ("object", "data", "object/data"),
        ("object", "classid", "object/classid"),
        ("object", "codebase", "object/codebase"),
        ("video", "src", "video"),
        ("video", "poster", "video/poster"),
        ("audio", "src", "audio"),
        ("source", "src", "source"),
        ("track", "src", "track"),
        ("form", "action", "form"),
        ("button", "formaction", "button"),
        ("input", "src", "input"),
        ("input", "formaction", "input/formaction"),
        ("body", "background", "body/background"),
        ("html", "manifest", "html/manifest"),
        ("blockquote", "cite", "blockquote/cite"),
        ("q", "cite", "q/cite"),
        ("del", "cite", "del/cite"),
        ("ins", "cite", "ins/cite"),
        ("applet", "codebase", "applet/codebase"),
    )

    _SRCSET_TAGS = frozenset({"img", "source"})
    _NO_TEXT_TAGS = frozenset({"html", "body", "form", "object", "applet"})

    def __init__(self):
        specs = {}
        for tag, attribute, source_type in self.RESOURCE_ATTRIBUTES:
            specs.setdefault(tag, []).append((attribute, source_type))
        self._specs = {tag: tuple(items) for tag, items in specs.items()}

    # -- helpers -------------------------------------------------------------

    @classmethod
    def _text_for_tag(cls, tag):
        text = ""
        if tag.name not in cls._NO_TEXT_TAGS:
            text = tag.get_text(" ", strip=True)
        if not text:
            for attr in ("alt", "title", "aria-label", "name", "id"):
                value = tag.get(attr)
                if value and isinstance(value, str):
                    text = value.strip()
                    break
        return text[:120]

    @staticmethod
    def _srcset_urls(value):
        if not value:
            return []
        urls = []
        for part in str(value).split(","):
            pieces = part.strip().split()
            if pieces:
                urls.append(pieces[0])
        return urls

    @staticmethod
    def _make_link(raw_url, base_url, source_url, source_text, source_type):
        if not raw_url or not isinstance(raw_url, str):
            return None
        raw_url = unescape(raw_url.strip())
        if not raw_url:
            return None
        lowered = raw_url.lower()
        if lowered.startswith(_SKIP_PREFIXES):
            return None
        if any(marker in raw_url for marker in _TEMPLATE_MARKERS):
            return None

        try:
            absolute = normalize_url(urljoin(base_url, raw_url))
            parts = urlsplit(absolute)
        except ValueError:
            return None  # malformed URL (e.g. broken IPv6 literal)

        if parts.scheme not in ("http", "https") or not parts.netloc:
            return None

        return DiscoveredLink(
            url=absolute,
            source_url=source_url,
            source_text=source_text,
            source_type=source_type,
        )

    def _css_links(self, css_text, base_url, source_url, source_text,
                   url_type, import_type):
        if not css_text:
            return []
        css_text = _CSS_COMMENT_RE.sub("", css_text)
        links = []
        # @import first so a URL that appears in both forms is typed as an
        # import (a stylesheet we will parse), not a plain css resource.
        import_spans = []
        for match in _CSS_IMPORT_RE.finditer(css_text):
            import_spans.append(match.span())
            link = self._make_link(
                match.group(2), base_url, source_url, source_text, import_type)
            if link:
                links.append(link)
        for match in _CSS_URL_RE.finditer(css_text):
            start = match.start()
            if any(a <= start < b for a, b in import_spans):
                continue  # already handled as @import
            value = match.group(2).strip()
            link = self._make_link(
                value, base_url, source_url, source_text, url_type)
            if link:
                links.append(link)
        return links

    # -- public API ----------------------------------------------------------

    def extract_html(self, content, page_url, charset=None):
        """All URLs referenced by an HTML document, resolved against the
        page URL (or its <base href>)."""
        if isinstance(content, bytes):
            soup = BeautifulSoup(content, "html.parser", from_encoding=charset)
        else:
            soup = BeautifulSoup(content, "html.parser")

        links = []
        resolution_base = page_url

        base_tag = soup.find("base", href=True)
        if base_tag:
            candidate = self._make_link(
                base_tag.get("href"), page_url, page_url, "<base>", "base")
            if candidate:
                resolution_base = candidate.url
                links.append(candidate)

        def add(raw, text, source_type):
            link = self._make_link(
                raw, resolution_base, page_url, text, source_type)
            if link:
                links.append(link)

        for tag in soup.find_all(True):
            name = tag.name
            text = None

            specs = self._specs.get(name)
            if specs:
                for attribute, source_type in specs:
                    raw = tag.get(attribute)
                    if raw:
                        if text is None:
                            text = self._text_for_tag(tag)
                        add(raw, text, source_type)

            if name == "link":
                raw = tag.get("href")
                if raw:
                    rels = [str(v).lower() for v in (tag.get("rel") or [])]
                    if not _SKIP_LINK_RELS.intersection(rels):
                        source_type = (
                            "stylesheet" if "stylesheet" in rels else "link-tag")
                        add(raw, "<stylesheet>" if source_type == "stylesheet"
                            else f"<link rel={' '.join(rels)}>", source_type)

            elif name in self._SRCSET_TAGS:
                srcset = tag.get("srcset")
                if srcset:
                    if text is None:
                        text = self._text_for_tag(tag)
                    for candidate in self._srcset_urls(srcset):
                        add(candidate, text, f"{name}/srcset")

            elif name == "style":
                links.extend(self._css_links(
                    tag.get_text(), resolution_base, page_url, "<style>",
                    "css", "css/import"))

            elif name == "meta":
                equiv = str(tag.get("http-equiv") or "").lower()
                if equiv == "refresh":
                    match = _META_REFRESH_RE.search(str(tag.get("content") or ""))
                    if match:
                        add(match.group(1).strip(), "meta refresh",
                            "meta-refresh")

            inline_style = tag.get("style")
            if inline_style and isinstance(inline_style, str) \
                    and "url(" in inline_style.lower():
                if text is None:
                    text = self._text_for_tag(tag)
                links.extend(self._css_links(
                    inline_style, resolution_base, page_url, text,
                    "css", "css/import"))

        return links

    def extract_css(self, css_text, css_url):
        """URLs referenced by a stylesheet (url(...) and @import)."""
        return self._css_links(
            css_text, css_url, css_url, "<stylesheet>",
            "css/resource", "css/import")

    @staticmethod
    def parse_sitemap(content):
        """Returns (is_index, [urls]) for a sitemap or sitemap index."""
        if content[:2] == b"\x1f\x8b":  # .xml.gz served without Content-Encoding
            content = zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(
                content, MAX_SITEMAP_BYTES)
        root = ET.fromstring(content)
        is_index = root.tag.rsplit("}", 1)[-1].lower() == "sitemapindex"
        urls = []
        for element in root.iter():
            if element.tag.rsplit("}", 1)[-1].lower() != "loc":
                continue
            value = (element.text or "").strip()
            if value:
                urls.append(value)
        return is_index, urls


# ---------------------------------------------------------------------------
# Fetching
# ---------------------------------------------------------------------------


def _read_limited(response, limit, stop_event):
    """Read at most `limit` bytes, with a wall-clock cap, aborting on STOP."""
    chunks = []
    total = 0
    deadline = time.monotonic() + MAX_BODY_SECONDS
    for chunk in response.iter_content(chunk_size=65536):
        if stop_event is not None and stop_event.is_set():
            return None
        if not chunk:
            continue
        chunks.append(chunk)
        total += len(chunk)
        if total >= limit or time.monotonic() > deadline:
            break
    return b"".join(chunks)


def _is_success(response):
    return 200 <= response.status_code < 300


def _html_reader(response, stop_event):
    if not _is_success(response):
        return None
    content_type = response.headers.get("Content-Type", "").lower()
    if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
        return None
    return _read_limited(response, MAX_PAGE_BYTES, stop_event)


def _css_reader(response, stop_event):
    if not _is_success(response):
        return None
    content_type = response.headers.get("Content-Type", "").lower()
    path = urlsplit(response.url).path.lower()
    if "text/css" not in content_type and not path.endswith(".css"):
        return None
    return _read_limited(response, MAX_CSS_BYTES, stop_event)


def _any_reader(limit):
    def reader(response, stop_event):
        if not _is_success(response):
            return None
        return _read_limited(response, limit, stop_event)
    return reader


# kind -> (timeout, retry_timeout, max_attempts, body_reader)
_FETCH_PROFILES = {
    "page": (PAGE_TIMEOUT, PAGE_RETRY_TIMEOUT, 2, _html_reader),
    "css": (PAGE_TIMEOUT, PAGE_RETRY_TIMEOUT, 2, _css_reader),
    # robots.txt and sitemaps are optional: one short attempt, never a stall.
    "sitemap": (AUX_TIMEOUT, AUX_TIMEOUT, 1, _any_reader(MAX_SITEMAP_BYTES)),
    "robots": (AUX_TIMEOUT, AUX_TIMEOUT, 1, _any_reader(512 * 1024)),
}


class PageFetcher:
    """Downloads a document and returns a link_checker.RequestOutcome (or
    None if the scan was stopped).

    Implementations: HttpPageFetcher (below) and
    browser_crawler.BrowserPageFetcher (JavaScript rendering).
    """

    name = "base"

    def fetch(self, url, stop_event, kind="page"):
        raise NotImplementedError

    def close_thread(self):
        """Called by every worker thread just before it exits."""


class HttpPageFetcher(PageFetcher):
    name = "http"

    def __init__(self, sessions, limiter, timeout_scale=1.0,
                 follow_redirects=True):
        self.sessions = sessions
        self.limiter = limiter
        self.timeout_scale = timeout_scale
        self.follow_redirects = follow_redirects

    def fetch(self, url, stop_event, kind="page"):
        timeout, retry_timeout, attempts, reader = _FETCH_PROFILES[kind]
        return perform_request(
            self.sessions.get(),
            url,
            timeout=scale_timeout(timeout, self.timeout_scale),
            retry_timeout=scale_timeout(retry_timeout, self.timeout_scale),
            limiter=self.limiter,
            stop_event=stop_event,
            body_reader=reader,
            max_attempts=attempts,
            priority=True,   # crawl requests go before plain link checks
            follow_redirects=self.follow_redirects,
        )


# ---------------------------------------------------------------------------
# robots.txt
# ---------------------------------------------------------------------------


class RobotsPolicy:
    """robots.txt rules. Until (and unless) robots.txt has loaded, everything
    is allowed, so a slow or missing robots.txt can never stall a scan."""

    def __init__(self, enabled=True):
        self.enabled = enabled
        self._parser = None
        self.sitemaps = []
        self.crawl_delay = None

    def load(self, fetcher, start_url, stop_event):
        if not self.enabled:
            return
        robots_url = urljoin(start_url, "/robots.txt")
        try:
            outcome = fetcher.fetch(robots_url, stop_event, kind="robots")
            if (
                outcome is not None
                and outcome.result.status == 200
                and outcome.body
            ):
                parser = robotparser.RobotFileParser()
                parser.parse(outcome.body.decode("utf-8", "replace").splitlines())
                self.sitemaps = parser.site_maps() or []
                delay = parser.crawl_delay(USER_AGENT)
                self.crawl_delay = float(delay) if delay is not None else None
                self._parser = parser  # publish last: rules are complete
        except Exception:
            pass  # robots.txt is best-effort

    def can_fetch(self, url):
        parser = self._parser
        if not self.enabled or parser is None:
            return True
        try:
            return parser.can_fetch(USER_AGENT, url)
        except Exception:
            return True
