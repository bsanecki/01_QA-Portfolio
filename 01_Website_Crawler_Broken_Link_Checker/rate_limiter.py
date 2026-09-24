import threading
from collections import defaultdict
from time import monotonic
from urllib.parse import urlsplit


class HostRateLimiter:
    """Limit concurrent requests *and* request frequency per host.

    One instance is shared by crawl workers and link-check workers, so the
    total pressure on a single server is bounded no matter how many workers
    exist globally.

    Crawl requests (priority=True) are served before plain link checks for
    the same host, because discovering pages is what feeds the whole
    pipeline. A waiting link check is never held back for longer than
    MAX_YIELD_SECONDS, so checks cannot starve.
    """

    MAX_YIELD_SECONDS = 1.0

    def __init__(self, max_concurrent=4, min_interval=0.08):
        self.max_concurrent = max(1, int(max_concurrent))
        self.min_interval = max(0.0, float(min_interval))
        self._lock = threading.Lock()
        self._conditions = {}
        self._active = defaultdict(int)
        self._last_start = defaultdict(float)
        self._interval = {}            # per-host override (Crawl-delay / 429)
        self._blocked_until = defaultdict(float)
        self._priority_waiting = defaultdict(int)

    @staticmethod
    def _host(url):
        return urlsplit(url).netloc.lower()

    def _condition_for(self, host):
        with self._lock:
            condition = self._conditions.get(host)
            if condition is None:
                condition = threading.Condition(self._lock)
                self._conditions[host] = condition
            return condition

    def set_host_interval(self, url, interval):
        """Raise the minimum delay between requests to url's host
        (used for robots.txt Crawl-delay). Never lowers an existing value."""
        host = self._host(url)
        with self._lock:
            current = self._interval.get(host, self.min_interval)
            self._interval[host] = max(current, float(interval))

    def penalize(self, url, delay):
        """Called after a 429: pause new requests to the host for `delay`
        seconds and slow the host down a little for the rest of the scan."""
        host = self._host(url)
        condition = self._condition_for(host)
        with condition:
            now = monotonic()
            self._blocked_until[host] = max(
                self._blocked_until[host], now + max(0.0, delay)
            )
            current = self._interval.get(host, self.min_interval)
            self._interval[host] = min(max(current * 2, 0.25), 1.5)

    def acquire(self, url, stop_event=None, priority=False):
        host = self._host(url)
        condition = self._condition_for(host)

        with condition:
            waiting_since = monotonic()
            if priority:
                self._priority_waiting[host] += 1
            try:
                while True:
                    if stop_event is not None and stop_event.is_set():
                        return False

                    now = monotonic()
                    interval = self._interval.get(host, self.min_interval)
                    ready_at = max(
                        self._last_start[host] + interval,
                        self._blocked_until[host],
                    )
                    wait_for = ready_at - now

                    yielding = (
                        not priority
                        and self._priority_waiting[host] > 0
                        and now - waiting_since < self.MAX_YIELD_SECONDS
                    )

                    if (
                        not yielding
                        and self._active[host] < self.max_concurrent
                        and wait_for <= 0
                    ):
                        self._active[host] += 1
                        self._last_start[host] = now
                        return True

                    condition.wait(timeout=min(max(wait_for, 0.02), 0.15))
            finally:
                if priority:
                    self._priority_waiting[host] -= 1

    def release(self, url):
        host = self._host(url)
        condition = self._condition_for(host)
        with condition:
            self._active[host] = max(0, self._active[host] - 1)
            condition.notify_all()
