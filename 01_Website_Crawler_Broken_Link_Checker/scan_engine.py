"""Parallel scan pipeline (no Tkinter in here).

                START
                  |
            URL DISCOVERY  <------------------------------+
                  |                                        |
         +--------+--------+                               |
         v        v        v                               |
       PAGE     PAGE     PAGE      (crawl workers)  --------+  new URLs go
         |        |        |                                  straight back
         +--------+--------+                                  into the queue
                  |
              LINK QUEUE
                  |
         +--------+--------+
         v        v        v
      CHECK    CHECK    CHECK      (check workers)
         |        |        |
         +--------+--------+
                  |
               RESULTS  -> event queue -> GUI

* One registry (`_entries`) guarantees every URL is fetched exactly once.
  Every discovered URL ends up in exactly one of three places:
    - page queue  : internal HTML page within Crawl Depth  (fetch + parse)
    - page queue  : internal stylesheet                    (fetch + parse url())
    - check queue : everything else (external, assets, beyond Crawl Depth,
                    disallowed by robots.txt)              (status only)
  Pages and stylesheets are therefore not requested a second time by the
  checker: the crawl request *is* their link check.
* Pages are dequeued breadth-first (lowest depth first).
* All requests, crawl and check alike, pass through one shared per-host
  limiter, so the load on a single server is bounded.
* STOP is a threading.Event that every wait and every queue poll observes.
"""

import itertools
import queue
import threading
import time
from dataclasses import dataclass
from urllib.parse import urljoin

from browser_crawler import (
    BrowserPageFetcher,
    BrowserUnavailable,
    check_browser,
    resolve_auto,
)
from crawler import (
    PAGE_SOURCE_TYPES,
    STYLESHEET_SOURCE_TYPES,
    HttpPageFetcher,
    LinkExtractor,
    RobotsPolicy,
    charset_from_content_type,
)
from link_checker import ThreadSessions, check_link
from models import (
    CAT_BROKEN,
    CAT_OK,
    CAT_REDIRECT,
    CAT_UNVERIFIED,
    CHECK_WORKERS,
    CRAWL_WORKERS,
    HOST_MIN_INTERVAL,
    LINK_RETRY_TIMEOUT,
    LINK_TIMEOUT,
    MAX_CRAWL_DELAY,
    MAX_OCCURRENCES_PER_URL,
    MAX_PER_HOST,
    ROBOTS_MAX_WAIT,
    STOP_JOIN_SECONDS,
    DiscoveredLink,
    LinkResult,
)
from rate_limiter import HostRateLimiter
from settings import DEFAULT_REQUEST_TIMEOUT, scale_timeout
from utils import host_key, normalize_url

CRAWL_MODE_HTTP = "http"
CRAWL_MODE_BROWSER = "browser"
CRAWL_MODE_AUTO = "auto"


@dataclass
class ScanConfig:
    start_url: str
    max_depth: int | None = 5           # None = Unlimited
    crawl_mode: str = CRAWL_MODE_HTTP
    browser: str = "chromium"           # used when crawl_mode == "browser"
    crawl_workers: int = CRAWL_WORKERS
    check_workers: int = CHECK_WORKERS
    max_per_host: int = MAX_PER_HOST
    host_min_interval: float = HOST_MIN_INTERVAL
    respect_robots: bool = True
    discover_sitemap: bool = True
    # From Settings. The defaults keep the built-in behaviour.
    request_timeout: float = DEFAULT_REQUEST_TIMEOUT
    follow_redirects: bool = True


class ScanEngine:
    """Runs one scan. Thread model:

    * one coordinator thread   - robots.txt, seeding, completion detection
    * N crawl worker threads   - fetch + parse pages/CSS/sitemaps
    * M check worker threads   - status-check every other URL

    The caller (GUI) only ever touches: start(), stop(), snapshot(), the
    `events` queue, and - after the "finished" event - `results`.
    """

    def __init__(self, config, events=None):
        self.config = config
        self.events = events if events is not None else queue.Queue()

        self.start_url = normalize_url(config.start_url)
        if not host_key(self.start_url):
            raise ValueError("URL has no host")
        self.max_depth = (
            None if config.max_depth is None else max(0, int(config.max_depth))
        )

        self._stop = threading.Event()    # user pressed STOP
        self._halt = threading.Event()    # work is over -> workers exit
        self._lock = threading.Lock()

        # URL registry: url -> DiscoveredLink (first occurrence + all sources)
        self._entries = {}
        self.page_depths = {}             # every crawled page keeps its depth
        self.results = []                 # [(DiscoveredLink, LinkResult)]

        self.pages_scanned = 0
        self.links_discovered = 0
        self.links_checked = 0
        self.ok_links = 0
        self.redirects = 0
        self.broken_links = 0
        self.unverified_links = 0
        self._pages_queued = 0
        self._current = {}                # thread id -> url being processed

        # (depth, seq, kind, url): lowest depth first = breadth-first crawl
        self._pages = queue.PriorityQueue()
        self._checks = queue.Queue()
        self._seq = itertools.count()
        self._sitemaps_seen = set()
        self.browser_label = ""          # browser used for rendering, if any
        self._sitemap_pending = []       # sitemap URLs held back (limited depth)

        self._allowed_hosts = frozenset({host_key(self.start_url)})

        self._limiter = HostRateLimiter(
            max_concurrent=config.max_per_host,
            min_interval=config.host_min_interval,
        )
        self._sessions = ThreadSessions()
        self._timeout_scale = config.request_timeout / DEFAULT_REQUEST_TIMEOUT
        self._http = HttpPageFetcher(
            self._sessions, self._limiter,
            timeout_scale=self._timeout_scale,
            follow_redirects=config.follow_redirects,
        )
        self._browser = None
        self._robots = RobotsPolicy(enabled=config.respect_robots)
        self._extractor = LinkExtractor()

        self._threads = []
        self._coordinator = None
        self._robots_thread = None
        self._start_time = None
        self._end_time = None
        self.finished = threading.Event()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self):
        self._coordinator = threading.Thread(
            target=self._run, name="scan-coordinator", daemon=True)
        self._coordinator.start()

    def stop(self):
        """Ask everything to wind down. Returns immediately; a
        ("finished", True) event follows once all threads have exited."""
        self._stop.set()

    @property
    def stopping(self):
        return self._stop.is_set()

    def is_internal(self, url):
        return host_key(url) in self._allowed_hosts

    def snapshot(self):
        """Real, current state of queues and counters (thread-safe)."""
        now = time.monotonic()
        with self._lock:
            state = {
                "pages_scanned": self.pages_scanned,
                "pages_queued": self._pages_queued,
                "links_discovered": self.links_discovered,
                "links_checked": self.links_checked,
                "ok": self.ok_links,
                "redirects": self.redirects,
                "broken": self.broken_links,
                "unverified": self.unverified_links,
                "current_pages": list(self._current.values()),
            }
        state["checks_queued"] = self._checks.qsize()
        started = self._start_time
        end = self._end_time if self._end_time is not None else now
        state["elapsed"] = 0.0 if started is None else max(0.0, end - started)

        # Orientation only: remaining = discovered - checked; it grows while
        # the crawl is still finding new URLs.
        remaining = state["links_discovered"] - state["links_checked"]
        estimate = None
        if (
            self._end_time is None
            and state["links_checked"] >= 5
            and state["elapsed"] >= 2.0
            and remaining > 0
        ):
            rate = state["links_checked"] / state["elapsed"]
            if rate > 0:
                estimate = remaining / rate
        state["estimated"] = estimate
        return state

    def threads_alive(self):
        return [t for t in self._all_threads() if t.is_alive()]

    # ------------------------------------------------------------------
    # Coordinator
    # ------------------------------------------------------------------

    def _all_threads(self):
        threads = list(self._threads)
        if self._robots_thread is not None:
            threads.append(self._robots_thread)
        if self._coordinator is not None:
            threads.append(self._coordinator)
        return threads

    def _run(self):
        self._start_time = time.monotonic()
        try:
            self._prepare()
            if not self._stop.is_set():
                self._seed()
                self._start_workers()
                self._wait_until_idle()
        except Exception as error:  # pragma: no cover - safety net
            self.events.put(("fatal_error", f"{type(error).__name__}: {error}"))
            self._stop.set()
        finally:
            self._halt.set()
            self._join_workers()
            self._sessions.close_all()
            self._end_time = time.monotonic()
            self.finished.set()
            self.events.put(("finished", self._stop.is_set()))

    def _prepare_browser(self):
        """HTTP mode never touches Playwright. Browser mode uses exactly the
        chosen browser; Auto picks the first available one. A missing
        browser is reported and the scan continues in plain HTTP mode."""
        mode = self.config.crawl_mode
        if mode == CRAWL_MODE_HTTP:
            return
        if mode == CRAWL_MODE_BROWSER:
            check = check_browser(self.config.browser)
            if not check.ok:
                self.events.put((
                    "notice",
                    check.message.splitlines()[0] + " - continuing in HTTP mode."))
                return
        else:
            check = resolve_auto()
            if check is None:
                self.events.put((
                    "notice",
                    "Auto: no browser available - using the HTTP crawler."))
                return
        self.browser_label = check.label
        self._browser = BrowserPageFetcher(
            self._limiter, check.browser_id, check.path)
        self._browser.navigation_timeout_ms = int(
            self.config.request_timeout * 1000)
        self.events.put(("notice", f"JavaScript rendering with {check.label}."))

    def _prepare(self):
        self._prepare_browser()

        if not self.config.respect_robots:
            return

        # robots.txt is fetched off the coordinator thread and waited for at
        # most ROBOTS_MAX_WAIT seconds: a slow robots.txt cannot hold up the
        # scan, and STOP stays responsive.
        self._robots_thread = threading.Thread(
            target=self._robots.load,
            args=(self._http, self.start_url, self._stop),
            name="robots-loader",
            daemon=True,
        )
        self._robots_thread.start()
        deadline = time.monotonic() + ROBOTS_MAX_WAIT
        while (
            self._robots_thread.is_alive()
            and time.monotonic() < deadline
            and not self._stop.is_set()
        ):
            self._robots_thread.join(0.05)

        delay = self._robots.crawl_delay
        if delay:
            self._limiter.set_host_interval(
                self.start_url, min(float(delay), MAX_CRAWL_DELAY))

    def _seed(self):
        start = DiscoveredLink(
            url=self.start_url,
            source_url="(start URL)",
            source_text="Start page",
            source_type="start",
        )
        if not self._robots.can_fetch(self.start_url):
            self.events.put((
                "notice", "The start page is disallowed by robots.txt - "
                          "it is only checked, not crawled."))
        self._register(start, depth=0)

        if self.config.discover_sitemap and (
            self.max_depth is None or self.max_depth >= 1
        ):
            candidates = list(self._robots.sitemaps)
            candidates.append(urljoin(self.start_url, "/sitemap.xml"))
            candidates.append(urljoin(self.start_url, "/sitemap_index.xml"))
            for candidate in candidates:
                try:
                    candidate = normalize_url(candidate)
                except ValueError:
                    continue
                if self.is_internal(candidate):
                    self._enqueue_sitemap(candidate)

    def _start_workers(self):
        for index in range(max(1, self.config.crawl_workers)):
            thread = threading.Thread(
                target=self._crawl_worker, name=f"crawl-{index + 1}",
                daemon=True)
            self._threads.append(thread)
        for index in range(max(1, self.config.check_workers)):
            thread = threading.Thread(
                target=self._check_worker, name=f"check-{index + 1}",
                daemon=True)
            self._threads.append(thread)
        for thread in self._threads:
            thread.start()

    def _wait_until_idle(self):
        # Order matters: only crawl workers create new work. Once the page
        # queue is fully done, nothing can be added to the check queue any
        # more, so reading the check queue second is race-free.
        while not self._stop.is_set():
            if self._pages.unfinished_tasks == 0:
                if self._flush_sitemap_pending():
                    continue
                if self._checks.unfinished_tasks == 0:
                    return
            self._stop.wait(0.05)

    def _flush_sitemap_pending(self):
        """Once crawling is finished, register the sitemap-only URLs held
        back by a limited Crawl Depth. They are beyond the depth limit, so
        the engine only status-checks them. Returns True if any were added.
        """
        with self._lock:
            pending, self._sitemap_pending = self._sitemap_pending, []
        for link in pending:
            self._register(link, depth=self.max_depth + 1)
        return bool(pending)

    def _join_workers(self):
        deadline = time.monotonic() + STOP_JOIN_SECONDS
        for thread in self._threads + (
            [self._robots_thread] if self._robots_thread else []
        ):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            thread.join(remaining)

    # ------------------------------------------------------------------
    # Registry / routing
    # ------------------------------------------------------------------

    def _depth_allowed(self, depth):
        return self.max_depth is None or depth <= self.max_depth

    def _route(self, link, depth):
        """Decide what happens to a newly discovered URL. Called with the
        lock held; must not do any I/O."""
        if self.is_internal(link.url):
            source_type = link.source_type
            if source_type in PAGE_SOURCE_TYPES and self._depth_allowed(depth):
                if self._robots.can_fetch(link.url):
                    return "page"
            elif source_type in STYLESHEET_SOURCE_TYPES:
                if self._robots.can_fetch(link.url):
                    return "css"
        # External links, assets, pages beyond Crawl Depth and pages
        # disallowed by robots.txt: status check only, never crawled.
        return "check"

    @staticmethod
    def _add_occurrence(entry, source):
        entry.occurrence_count += 1
        key = (source.source_url, source.source_type)
        occurrences = entry.occurrences
        if occurrences and occurrences[-1][:2] == key:
            return
        if len(occurrences) < MAX_OCCURRENCES_PER_URL:
            occurrences.append(
                (source.source_url, source.source_type, source.source_text))

    def _register(self, link, depth):
        """Add a discovered URL. New URLs are queued immediately; URLs seen
        before only gain an extra source occurrence."""
        if self._stop.is_set():
            return
        url = link.url
        with self._lock:
            entry = self._entries.get(url)
            if entry is not None:
                self._add_occurrence(entry, link)
                self._reconsider(entry, link, depth)
                return

            link.depth = depth
            self._add_occurrence(link, link)
            self._entries[url] = link
            self.links_discovered += 1

            route = self._route(link, depth)
            link.route = route
            if route == "page":
                self.page_depths[url] = depth
                self._pages_queued += 1
                self._pages.put((depth, next(self._seq), "page", url))
            elif route == "css":
                self._pages.put((depth, next(self._seq), "css", url))
            else:
                self._checks.put(link)

    def _reconsider(self, entry, link, depth):
        """Called (lock held) when a known URL is found again.

        Crawl workers run concurrently, so a URL is not always first found
        by its shallowest parent. Depth must be the SHORTEST path from the
        start page, otherwise Crawl Depth would depend on thread timing:

        * a lower depth replaces the stored one (a queued page picks it up
          when a worker takes it);
        * a URL that was only status-checked because it looked too deep is
          promoted to a crawled page if this shorter path allows crawling.
        """
        if depth < entry.depth:
            entry.depth = depth
            if entry.route == "page":
                self.page_depths[entry.url] = depth
        if entry.route == "check" and self._route(link, entry.depth) == "page":
            entry.route = "page"
            self.page_depths[entry.url] = entry.depth
            self._pages_queued += 1
            self._pages.put((entry.depth, next(self._seq), "page", entry.url))

    def _enqueue_sitemap(self, url):
        with self._lock:
            if url in self._sitemaps_seen or self._stop.is_set():
                return
            self._sitemaps_seen.add(url)
            self._pages.put((0, next(self._seq), "sitemap", url))

    def _register_all(self, links, source_depth):
        # Links found on a page at depth d are at depth d + 1.
        for link in links:
            if self._stop.is_set():
                return
            self._register(link, source_depth + 1)

    # ------------------------------------------------------------------
    # Results
    # ------------------------------------------------------------------

    def _record_result(self, link, result):
        with self._lock:
            if link.done:
                return
            link.done = True
            self.results.append((link, result))
            self.links_checked += 1
            category = result.category
            if category == CAT_OK:
                self.ok_links += 1
            elif category == CAT_REDIRECT:
                self.redirects += 1
            elif category == CAT_BROKEN:
                self.broken_links += 1
            else:
                self.unverified_links += 1
        self.events.put(("result", link, result))

    def _record_internal_error(self, link, error):
        self._record_result(link, LinkResult(
            url=link.url, status=None, final_url=link.url, elapsed=0.0,
            error_type="REQUEST ERROR",
            error_message=f"Internal error: {type(error).__name__}: {error}",
        ))

    def _set_current(self, url):
        with self._lock:
            if url is None:
                self._current.pop(threading.get_ident(), None)
            else:
                self._current[threading.get_ident()] = url

    # ------------------------------------------------------------------
    # Crawl workers
    # ------------------------------------------------------------------

    def _crawl_worker(self):
        try:
            while not self._halt.is_set():
                try:
                    depth, _seq, kind, url = self._pages.get(timeout=0.2)
                except queue.Empty:
                    continue

                if kind == "page":
                    with self._lock:
                        self._pages_queued -= 1

                try:
                    if self._stop.is_set():
                        continue  # drain quickly, do no new work
                    self._set_current(url)
                    if kind == "page":
                        self._process_page(url, depth)
                    elif kind == "css":
                        self._process_css(url, depth)
                    else:
                        self._process_sitemap(url)
                except Exception as error:
                    link = self._entries.get(url)
                    if link is not None and kind != "sitemap":
                        self._record_internal_error(link, error)
                finally:
                    self._set_current(None)
                    self._pages.task_done()
        finally:
            try:
                self._http.close_thread()
                if self._browser is not None:
                    self._browser.close_thread()
            except Exception:
                pass

    def _process_page(self, url, depth):
        link = self._entries[url]
        depth = min(depth, link.depth)     # shortest path wins (see _reconsider)
        outcome = self._http.fetch(url, self._stop, kind="page")
        if outcome is None:
            return  # stopped mid-request

        result = outcome.result
        self._record_result(link, result)

        if (
            depth == 0
            and result.status is not None
            and self.config.follow_redirects   # nothing was followed otherwise
        ):
            self._adopt_start_host(result.final_url)

        html = outcome.body
        if html is None or self._stop.is_set():
            return
        final_url = result.final_url
        if not self.is_internal(final_url):
            return  # redirected off-site: never crawl someone else's pages

        with self._lock:
            self.pages_scanned += 1

        charset = charset_from_content_type(outcome.content_type)
        links = self._extractor.extract_html(html, final_url, charset)
        links.extend(self._render_links(final_url, links))
        self._register_all(links, depth)

    def _render_links(self, url, static_links):
        """Extra links found by rendering the page in a browser, if enabled."""
        mode = self.config.crawl_mode
        browser = self._browser
        if browser is None or mode == CRAWL_MODE_HTTP:
            return []
        if mode == CRAWL_MODE_AUTO and any(
            link.source_type in PAGE_SOURCE_TYPES for link in static_links
        ):
            return []  # the static HTML already has navigation links
        try:
            rendered = browser.fetch(url, self._stop)
        except BrowserUnavailable as error:
            self._browser = None
            self.events.put((
                "notice", f"Browser mode unavailable ({error}) - "
                          "continuing in HTTP mode."))
            return []
        except Exception:
            return []  # a rendering problem must never lose the static links
        if rendered is None or rendered.body is None:
            return []
        return self._extractor.extract_html(rendered.body, url)

    def _adopt_start_host(self, final_url):
        """If the start URL redirects to another host (brand.com -> brand.io)
        the destination becomes the site being scanned."""
        if not final_url or self.is_internal(final_url):
            return
        self._allowed_hosts = self._allowed_hosts | {host_key(final_url)}
        self.events.put((
            "notice", f"Start URL redirected to {final_url} - "
                      "scanning that host."))

    def _process_css(self, url, depth):
        link = self._entries[url]
        depth = min(depth, link.depth)
        outcome = self._http.fetch(url, self._stop, kind="css")
        if outcome is None:
            return
        self._record_result(link, outcome.result)
        if outcome.body is None or self._stop.is_set():
            return
        charset = charset_from_content_type(outcome.content_type) or "utf-8"
        try:
            text = outcome.body.decode(charset, "replace")
        except LookupError:
            text = outcome.body.decode("utf-8", "replace")
        links = self._extractor.extract_css(text, outcome.result.final_url)
        self._register_all(links, depth)

    def _process_sitemap(self, url):
        outcome = self._http.fetch(url, self._stop, kind="sitemap")
        if (
            outcome is None
            or outcome.result.status != 200
            or not outcome.body
        ):
            return  # optional: a missing/slow sitemap never blocks the scan
        try:
            is_index, urls = self._extractor.parse_sitemap(outcome.body)
        except Exception:
            return

        for raw in urls:
            if self._stop.is_set():
                return
            try:
                value = normalize_url(raw)
            except ValueError:
                continue
            if not self.is_internal(value):
                continue
            if is_index:
                self._enqueue_sitemap(value)
            elif self.max_depth is None:
                self._register(DiscoveredLink(
                    url=value, source_url=url, source_text="sitemap",
                    source_type="sitemap"), depth=1)
            else:
                # A sitemap has no link-hops, so it must not pull pages past
                # Crawl Depth into the crawl. Collect them; they are
                # status-checked (never parsed) once the crawl is done.
                with self._lock:
                    self._sitemap_pending.append(DiscoveredLink(
                        url=value, source_url=url, source_text="sitemap",
                        source_type="sitemap"))

    # ------------------------------------------------------------------
    # Check workers
    # ------------------------------------------------------------------

    def _check_worker(self):
        while not self._halt.is_set():
            try:
                link = self._checks.get(timeout=0.2)
            except queue.Empty:
                continue
            try:
                if self._stop.is_set():
                    continue
                self._set_current(None)
                result = check_link(
                    self._sessions.get(),
                    link.url,
                    timeout=scale_timeout(LINK_TIMEOUT, self._timeout_scale),
                    retry_timeout=scale_timeout(
                        LINK_RETRY_TIMEOUT, self._timeout_scale),
                    limiter=self._limiter,
                    stop_event=self._stop,
                    follow_redirects=self.config.follow_redirects,
                )
                if result is not None:
                    self._record_result(link, result)
            except Exception as error:
                self._record_internal_error(link, error)
            finally:
                self._checks.task_done()
