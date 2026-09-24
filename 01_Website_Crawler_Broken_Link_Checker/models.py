"""Data models, tunable constants and the single source of truth for how a
link result is classified and described (used by both GUI and Excel)."""

from dataclasses import dataclass, field
from http import HTTPStatus

# ---------------------------------------------------------------------------
# Tunable settings
# ---------------------------------------------------------------------------

CRAWL_WORKERS = 4            # threads that download + parse pages
CHECK_WORKERS = 10           # threads that check discovered links
MAX_PER_HOST = 4             # concurrent requests to one host (crawl + check)
HOST_MIN_INTERVAL = 0.08     # seconds between request starts to one host
MAX_CRAWL_DELAY = 5.0        # robots.txt Crawl-delay is honoured up to this

LINK_TIMEOUT = (3.0, 5.0)         # (connect, read) for link checks
LINK_RETRY_TIMEOUT = (4.0, 6.0)
PAGE_TIMEOUT = (4.0, 8.0)         # (connect, read) for pages / CSS
PAGE_RETRY_TIMEOUT = (5.0, 10.0)
AUX_TIMEOUT = (3.0, 4.0)          # robots.txt / sitemap: single attempt
MAX_RETRY_AFTER = 2.0             # never sleep longer than this for 429

MAX_PAGE_BYTES = 5 * 1024 * 1024
MAX_CSS_BYTES = 1024 * 1024
MAX_SITEMAP_BYTES = 20 * 1024 * 1024
MAX_BODY_SECONDS = 20.0           # wall-clock cap for reading one body
ROBOTS_MAX_WAIT = 8.0             # scan starts without robots.txt after this
STOP_JOIN_SECONDS = 15.0          # max time to wait for workers after STOP

# Distinct source pages remembered per URL (the URL itself is still checked
# only once). Protects memory for site-wide links repeated on every page.
MAX_OCCURRENCES_PER_URL = 1000

# 4xx statuses we are confident mean "dead resource". Every other 4xx
# (401, 403, 429, 400, 405, ...) is often bot protection / rate limiting and
# is reported as Unverified.
BROKEN_STATUSES = frozenset({404, 410})

CAT_OK = "ok"
CAT_REDIRECT = "redirect"
CAT_BROKEN = "broken"
CAT_UNVERIFIED = "unverified"

# Values of the single "Crawl mode" selector. HTTP needs no Playwright;
# every browser entry renders pages with that browser; Auto picks for you.
CRAWL_MODES = (
    "Auto", "HTTP", "Chromium", "Chrome", "Firefox", "Edge", "Brave", "Opera",
)
DEFAULT_CRAWL_MODE = "HTTP"

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


@dataclass
class DiscoveredLink:
    url: str
    source_url: str
    source_text: str
    source_type: str = "link"
    depth: int = 0
    # Every (source_page, source_type, link_text) the URL was seen on.
    occurrences: list = field(default_factory=list)
    occurrence_count: int = 0
    done: bool = False   # set once a result has been recorded for this URL
    route: str = ""      # "page" | "css" | "check" (how the engine handles it)


@dataclass
class LinkResult:
    url: str
    status: int | None
    final_url: str
    elapsed: float
    error_type: str = ""
    error_message: str = ""
    method: str = "GET"
    redirect_history: list = field(default_factory=list)  # [(status, url)]
    attempts: int = 1

    # -- classification ----------------------------------------------------

    @property
    def category(self):
        if self.status is None:
            # A redirect loop is a genuinely broken link; every other
            # transport failure (timeout, DNS, SSL, reset) is unverified.
            if self.error_type == "TOO MANY REDIRECTS":
                return CAT_BROKEN
            return CAT_UNVERIFIED
        status = self.status
        if status in BROKEN_STATUSES:
            return CAT_BROKEN
        if status >= 400 or status < 200:
            return CAT_UNVERIFIED
        if self.redirect_history or 300 <= status < 400:
            return CAT_REDIRECT
        return CAT_OK

    @property
    def is_broken(self):
        return self.category == CAT_BROKEN

    @property
    def is_unverified(self):
        return self.category == CAT_UNVERIFIED

    @property
    def is_redirect(self):
        return self.category == CAT_REDIRECT

    @property
    def is_ok(self):
        return self.category == CAT_OK

    @property
    def is_server_error(self):
        return self.status is not None and 500 <= self.status <= 599

    @property
    def status_text(self):
        if self.status is not None:
            try:
                reason = HTTPStatus(self.status).phrase
            except ValueError:
                reason = ""
            return f"{self.status} {reason}".strip()
        return self.error_type or "ERROR"

    @property
    def problem_kind(self):
        """Finer label for the Problems tab / summary breakdown."""
        if self.category not in (CAT_BROKEN, CAT_UNVERIFIED):
            return ""
        if self.category == CAT_BROKEN:
            return "Broken"
        if self.status is None:
            if self.error_type == "TIMEOUT":
                return "Timeout"
            return "SSL/Connection"
        if self.is_server_error:
            return "Server Error"
        return "Blocked/Unverified"

    @property
    def redirect_chain_text(self):
        """A → 301 → B → 302 → C (final 200)"""
        if not self.redirect_history:
            return ""
        nodes = [url for _code, url in self.redirect_history] + [self.final_url]
        text = nodes[0]
        for (code, _url), nxt in zip(self.redirect_history, nodes[1:]):
            text += f" → {code} → {nxt}"
        if self.status is not None:
            text += f" (final {self.status})"
        return text


def describe_result(link, result):
    """One display/Excel row for a result. GUI and Excel both use this so the
    two can never disagree."""
    category = result.category
    if result.status is None:
        details = result.error_message or result.error_type
    elif category == CAT_REDIRECT:
        chain = result.redirect_chain_text
        details = (
            f"Redirect: {chain}" if chain
            else f"Redirect → {result.final_url}"
        )
    elif result.is_server_error:
        details = f"Server error: {result.status_text}"
    elif category == CAT_UNVERIFIED:
        details = f"{result.status_text} - could not verify (access restricted or unsupported)"
    else:
        details = result.status_text

    if result.attempts > 1:
        details = f"{details} (after {result.attempts} attempts)"

    occurrences = max(link.occurrence_count, 1)
    if occurrences > 1:
        details = f"{details} | found {occurrences}x"

    tag = {
        CAT_OK: "ok",
        CAT_REDIRECT: "redirect",
    }.get(category, "error")

    return {
        "status": result.status_text,
        "category": category,
        "url": link.url,
        "source_page": link.source_url,
        "source_type": link.source_type,
        "link_text": link.source_text,
        "final_url": result.final_url,
        "response_time": f"{result.elapsed:.2f}s",
        "response_seconds": round(result.elapsed, 3),
        "details": details,
        "problem_kind": result.problem_kind,
        "method": result.method,
        "depth": link.depth,
        "occurrences": occurrences,
        "tag": tag,
    }
