"""End-to-end tests of the scan pipeline against local HTTP servers.
Run:  python3 -m unittest discover -s tests -v
"""

import threading
import time
import unittest

from tests.helpers import (
    Site, html, links, redirect, status_route, run_scan, by_url, categories,
)
from models import MAX_PER_HOST


def pages_site(n=8, **kw):
    """/ -> /p1../pN, each page links to all others + an image and a css."""
    routes = {}
    everything = ["/"] + [f"/p{i}" for i in range(1, n + 1)]
    for path in everything:
        routes[path] = html(
            links(*everything), '<img src="/logo.png">',
            head='<link rel="stylesheet" href="/site.css">')
    routes["/logo.png"] = status_route(200, b"PNG")
    routes["/site.css"] = lambda h, m: h.reply(
        200, b"body{background:url(/bg.png)} @import 'extra.css';",
        ctype="text/css")
    routes["/extra.css"] = lambda h, m: h.reply(
        200, b".x{background:url(/bg2.png)}", ctype="text/css")
    routes["/bg.png"] = status_route(200, b"PNG")
    routes["/bg2.png"] = status_route(404, b"nope")
    return Site(routes)


class TestScenarios(unittest.TestCase):

    def test_A_small_site(self):
        site = pages_site(8)
        self.addCleanup(site.close)
        engine = run_scan(site.url("/"))
        cats = categories(engine)
        self.assertEqual(engine.pages_scanned, 9)
        # every discovered URL got exactly one result
        self.assertEqual(engine.links_discovered, engine.links_checked)
        self.assertEqual(len(engine.results), engine.links_discovered)
        # css url()/@import discovered; only bg2.png is dead
        self.assertEqual(cats[site.url("/bg.png")], "ok")
        self.assertEqual(cats[site.url("/bg2.png")], "broken")
        self.assertEqual(sum(1 for c in cats.values() if c == "broken"), 1)
        # nothing requested twice (pages/css are not re-checked)
        for (method, path), n in site.hits.items():
            if path in ("/robots.txt", "/sitemap.xml", "/sitemap_index.xml"):
                continue
            self.assertEqual(n, 1, f"{path} requested {n}x")
        self.assertEqual(engine.threads_alive(), [])

    def test_B_redirects(self):
        site = Site({
            "/": html(links("/old")),
            "/old": redirect(301, "/mid"),
            "/mid": redirect(302, "/final"),
            "/final": html("done"),
        })
        self.addCleanup(site.close)
        engine = run_scan(site.url("/"))
        link, result = by_url(engine)[site.url("/old")]
        self.assertEqual(result.category, "redirect")
        self.assertEqual(result.status, 200)
        self.assertEqual(result.final_url, site.url("/final"))
        self.assertEqual([c for c, _ in result.redirect_history], [301, 302])
        self.assertIn("301", result.redirect_chain_text)
        self.assertIn("/mid", result.redirect_chain_text)
        self.assertEqual(engine.broken_links + engine.unverified_links, 0)
        self.assertEqual(engine.redirects, 1)

    def test_C_status_classification(self):
        routes = {"/": html(links("/404", "/410", "/401", "/403", "/500", "/400"))}
        for code in (404, 410, 401, 403, 500, 400):
            routes[f"/{code}"] = status_route(code)
        site = Site(routes)
        self.addCleanup(site.close)
        engine = run_scan(site.url("/"))
        cats = categories(engine)
        for code, expected in ((404, "broken"), (410, "broken"),
                               (401, "unverified"), (403, "unverified"),
                               (500, "unverified"), (400, "unverified")):
            self.assertEqual(cats[site.url(f"/{code}")], expected, code)
        # a persistent 500 was retried once before being reported
        self.assertEqual(site.count("/500"), 2)
        self.assertEqual(site.count("/404"), 1)

    def test_D_head_404_get_200(self):
        def handler(h, method):
            h.reply(404 if method == "HEAD" else 200, b"ok")
        site = Site({"/": html('<a href="/headtrap">x</a><img src="/headtrap2">'),
                     "/headtrap": handler, "/headtrap2": handler})
        self.addCleanup(site.close)
        engine = run_scan(site.url("/"))
        cats = categories(engine)
        self.assertEqual(cats[site.url("/headtrap")], "ok")
        self.assertEqual(cats[site.url("/headtrap2")], "ok")
        self.assertEqual(sum(n for (m, _), n in site.hits.items() if m == "HEAD"), 0)

    def test_E_timeout_is_unverified_and_bounded(self):
        def slow(h, method):
            time.sleep(30)
        site = Site({"/": html(links("/x"), '<img src="/slow.png">'),
                     "/x": html("ok"), "/slow.png": slow})
        self.addCleanup(site.close)
        started = time.monotonic()
        engine = run_scan(site.url("/"))
        took = time.monotonic() - started
        link, result = by_url(engine)[site.url("/slow.png")]
        self.assertEqual(result.error_type, "TIMEOUT")
        self.assertEqual(result.category, "unverified")     # never Broken
        self.assertFalse(result.is_broken)
        self.assertEqual(result.attempts, 2)
        self.assertLess(took, 20, f"timeout handling took {took:.1f}s")
        self.assertEqual(engine.broken_links, 0)
        self.assertEqual(engine.unverified_links, 1)
        # the rest of the scan was not held up by the slow URL
        self.assertEqual(categories(engine)[site.url("/x")], "ok")

    def test_F_503_retry_200(self):
        state = {"n": 0}
        def flaky(h, method):
            state["n"] += 1
            h.reply(503 if state["n"] == 1 else 200, b"ok")
        site = Site({"/": html('<img src="/flaky.png">'), "/flaky.png": flaky})
        self.addCleanup(site.close)
        engine = run_scan(site.url("/"))
        link, result = by_url(engine)[site.url("/flaky.png")]
        self.assertEqual(result.category, "ok")
        self.assertEqual(result.attempts, 2)
        self.assertEqual(state["n"], 2)

    def test_G_429(self):
        state = {"n": 0}
        def once(h, method):
            state["n"] += 1
            if state["n"] == 1:
                h.reply(429, b"slow down", headers={"Retry-After": "1"})
            else:
                h.reply(200, b"ok")
        site = Site({
            "/": html('<img src="/once.png"><img src="/always.png">'),
            "/once.png": once,
            "/always.png": status_route(429, headers={"Retry-After": "120"}),
        })
        self.addCleanup(site.close)
        started = time.monotonic()
        engine = run_scan(site.url("/"))
        took = time.monotonic() - started
        cats = categories(engine)
        self.assertEqual(cats[site.url("/once.png")], "ok")
        self.assertEqual(cats[site.url("/always.png")], "unverified")
        self.assertEqual(engine.broken_links, 0)
        # Retry-After: 120 must not stall the scan
        self.assertLess(took, 8, f"429 handling took {took:.1f}s")

    def test_H_duplicates_checked_once_sources_kept(self):
        site = Site({
            "/": html(links(*["/dup"] * 20), '<img src="/i.png">' * 10,
                      links("/p1")),
            "/p1": html(links("/dup"), '<img src="/i.png">'),
            "/dup": html("dup"),
            "/i.png": status_route(200),
        })
        self.addCleanup(site.close)
        engine = run_scan(site.url("/"))
        self.assertEqual(site.count("/dup"), 1)
        self.assertEqual(site.count("/i.png"), 1)
        link, result = by_url(engine)[site.url("/dup")]
        self.assertGreaterEqual(link.occurrence_count, 21)
        sources = {src for src, _t, _x in link.occurrences}
        self.assertEqual(sources, {site.url("/"), site.url("/p1")})
        self.assertEqual(sum(1 for l, _ in engine.results if l.url == site.url("/dup")), 1)

    def test_I_per_host_concurrency_limit(self):
        n = 40
        routes = {"/": html(links(*[f"/p{i}" for i in range(n)]),
                            "".join(f'<img src="/a{i}.png">' for i in range(n)))}
        for i in range(n):
            routes[f"/p{i}"] = html(links("/"))
            routes[f"/a{i}.png"] = status_route(200)
        site = Site(routes, delay=0.1)
        self.addCleanup(site.close)
        engine = run_scan(site.url("/"))
        self.assertEqual(engine.pages_scanned, n + 1)
        self.assertLessEqual(site.max_active, MAX_PER_HOST,
                             f"max concurrent {site.max_active}")
        self.assertGreater(site.max_active, 1, "expected some parallelism")

    def test_K_crawl_depth(self):
        def chain(n=7):
            routes = {}
            for i in range(n):
                path = "/" if i == 0 else f"/d{i}"
                nxt = f"/d{i + 1}"
                routes[path] = html(links(nxt) if i < n - 1 else "", f'<img src="/i{i}.png">')
                routes[f"/i{i}.png"] = status_route(200)
            return routes
        for depth in (0, 1, 3, 5):
            with self.subTest(depth=depth):
                site = Site(chain())
                self.addCleanup(site.close)
                engine = run_scan(site.url("/"), depth=depth)
                self.assertEqual(engine.pages_scanned, depth + 1)
                # every crawled page stored its depth
                self.assertEqual(
                    {u.replace(site.base, ""): d for u, d in engine.page_depths.items()},
                    {("/" if i == 0 else f"/d{i}"): i for i in range(depth + 1)})
                # links on the last crawled page are still CHECKED ...
                nxt = site.url(f"/d{depth + 1}")
                self.assertIn(nxt, by_url(engine))
                self.assertEqual(site.count(f"/d{depth + 1}"), 1)
                # ... but not crawled: nothing beyond it was ever discovered
                self.assertNotIn(site.url(f"/i{depth + 1}.png"), by_url(engine))
                self.assertEqual(site.count(f"/d{depth + 2}"), 0)
        site = Site(chain())
        self.addCleanup(site.close)
        engine = run_scan(site.url("/"), depth=None)   # Unlimited
        self.assertEqual(engine.pages_scanned, 7)

    def test_external_links_are_checked_not_crawled(self):
        other = Site({"/x": html(links("/y")), "/y": html("y")})
        self.addCleanup(other.close)
        site = Site({"/": html(f'<a href="{other.url("/x")}">ext</a>')})
        self.addCleanup(site.close)
        engine = run_scan(site.url("/"))
        self.assertEqual(categories(engine)[other.url("/x")], "ok")
        self.assertEqual(engine.pages_scanned, 1)
        self.assertEqual(other.count("/x"), 1)
        self.assertEqual(other.count("/y"), 0)

    def test_transport_errors_are_unverified(self):
        dead = Site({})
        dead_url = dead.url("/")
        dead.close()                                   # closed port
        plain = Site({"/": html("plain")})
        self.addCleanup(plain.close)
        site = Site({"/": html(
            f'<a href="{dead_url}">refused</a>'
            f'<a href="https://127.0.0.1:{plain.port}/">ssl</a>'
            '<a href="http://no-such-host.invalid/">dns</a>')})
        self.addCleanup(site.close)
        engine = run_scan(site.url("/"))
        cats = categories(engine)
        self.assertEqual(cats[dead_url], "unverified")
        self.assertEqual(cats[f"https://127.0.0.1:{plain.port}/"], "unverified")
        self.assertEqual(cats["http://no-such-host.invalid/"], "unverified")
        self.assertEqual(engine.broken_links, 0)

    def test_robots_and_sitemap(self):
        site = Site({
            "/": html(links("/private/a", "/open")),
            "/open": html("open"),
            "/private/a": html(links("/private/b")),
            "/private/b": html("b"),
            "/hidden": html("only in sitemap"),
            "/robots.txt": "User-agent: *\nDisallow: /private/\n"
                           "Sitemap: {base}/custom-sitemap.xml\n",
            "/custom-sitemap.xml": lambda h, m: h.reply(
                200, (f'<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                      f'<sitemap><loc>{h.server.base}/child.xml</loc></sitemap></sitemapindex>').encode(),
                ctype="application/xml"),
            "/child.xml": lambda h, m: h.reply(
                200, (f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                      f'<url><loc>{h.server.base}/hidden</loc></url></urlset>').encode(),
                ctype="application/xml"),
        })
        site.httpd.base = site.base
        site.routes["/robots.txt"] = site.routes["/robots.txt"].replace("{base}", site.base)
        self.addCleanup(site.close)
        engine = run_scan(site.url("/"))
        found = by_url(engine)
        self.assertIn(site.url("/hidden"), found)             # via sitemap index
        self.assertEqual(found[site.url("/hidden")][0].source_type, "sitemap")
        # disallowed page: status-checked, never parsed
        self.assertEqual(found[site.url("/private/a")][1].category, "ok")
        self.assertNotIn(site.url("/private/b"), found)
        self.assertEqual(site.count("/private/b"), 0)
        # with depth 0 the sitemap is not used
        site2 = Site({"/": html("x"), "/sitemap.xml": lambda h, m: h.reply(
            200, f'<urlset><url><loc>{h.server.base}/s</loc></url></urlset>'.encode())})
        site2.httpd.base = site2.base
        self.addCleanup(site2.close)
        engine = run_scan(site2.url("/"), depth=0)
        self.assertEqual(site2.count("/s"), 0)
        self.assertEqual(site2.count("/sitemap.xml"), 0)

    def test_slow_robots_and_sitemap_do_not_block(self):
        def hang(h, m):
            time.sleep(30)
        site = Site({"/": html(links("/a", "/b")), "/a": html("a"), "/b": html("b"),
                     "/robots.txt": hang, "/sitemap.xml": hang,
                     "/sitemap_index.xml": hang})
        self.addCleanup(site.close)
        started = time.monotonic()
        engine = run_scan(site.url("/"))
        took = time.monotonic() - started
        self.assertEqual(engine.pages_scanned, 3)
        self.assertLess(took, 15, f"took {took:.1f}s")

    def test_crawl_delay(self):
        site = Site({"/": html(links("/a", "/b", "/c")), "/a": html("a"),
                     "/b": html("b"), "/c": html("c"),
                     "/robots.txt": "User-agent: *\nCrawl-delay: 1\n"})
        self.addCleanup(site.close)
        started = time.monotonic()
        engine = run_scan(site.url("/"), discover_sitemap=False)
        took = time.monotonic() - started
        self.assertEqual(engine.pages_scanned, 4)
        self.assertGreaterEqual(took, 2.5)     # 4 pages, >=1s apart


class TestStop(unittest.TestCase):

    def _big_slow_site(self, delay):
        n = 300
        routes = {"/": html(links(*[f"/p{i}" for i in range(n)]))}
        for i in range(n):
            routes[f"/p{i}"] = html(links(*[f"/p{(i + k) % n}" for k in range(1, 6)]),
                                    "".join(f'<img src="/i{i}_{k}.png">' for k in range(5)))
            for k in range(5):
                routes[f"/i{i}_{k}.png"] = status_route(200)
        return Site(routes, delay=delay)

    def test_J_stop_during_scan(self):
        site = self._big_slow_site(0.2)
        self.addCleanup(site.close)
        from scan_engine import ScanConfig, ScanEngine
        engine = ScanEngine(ScanConfig(start_url=site.url("/"), max_depth=None))
        engine.start()
        time.sleep(1.5)
        self.assertFalse(engine.finished.is_set())
        snap = engine.snapshot()
        self.assertGreater(snap["links_discovered"], 10)      # scan was in progress
        t0 = time.monotonic()
        engine.stop()
        self.assertTrue(engine.finished.wait(10))
        took = time.monotonic() - t0
        self.assertLess(took, 3, f"STOP took {took:.1f}s")
        self.assertEqual(engine.threads_alive(), [])
        # no new work reaches the server after the scan finished
        hits = sum(site.hits.values())
        time.sleep(1.0)
        self.assertEqual(sum(site.hits.values()), hits)
        events = []
        while not engine.events.empty():
            events.append(engine.events.get())
        self.assertEqual(events[-1], ("finished", True))

    def test_J_stop_while_waiting_for_slow_request(self):
        def slow(h, m):
            time.sleep(60)
        site = Site({"/": html('<img src="/slow.png">' * 1 + links("/p")),
                     "/p": html("p"), "/slow.png": slow})
        self.addCleanup(site.close)
        from scan_engine import ScanConfig, ScanEngine
        engine = ScanEngine(ScanConfig(start_url=site.url("/"), max_depth=5))
        engine.start()
        time.sleep(1.0)                      # request to /slow.png is in flight
        t0 = time.monotonic()
        engine.stop()
        self.assertTrue(engine.finished.wait(12))
        took = time.monotonic() - t0
        self.assertLess(took, 8, f"STOP with a hanging request took {took:.1f}s")
        self.assertEqual(engine.threads_alive(), [])


class TestPipelineLive(unittest.TestCase):
    def test_links_checked_while_crawl_still_running(self):
        """The old two-phase behaviour (crawl everything, then check) must be
        gone: link results must arrive while pages are still queued."""
        n = 60
        routes = {"/": html(links(*[f"/p{i}" for i in range(n)]))}
        for i in range(n):
            routes[f"/p{i}"] = html('<img src="/a%d.png">' % i, links("/"))
            routes[f"/a{i}.png"] = status_route(200)
        site = Site(routes, delay=0.1)
        self.addCleanup(site.close)
        from scan_engine import ScanConfig, ScanEngine
        engine = ScanEngine(ScanConfig(start_url=site.url("/"), max_depth=5))
        engine.start()
        overlap = False
        growing = []
        deadline = time.monotonic() + 60
        while not engine.finished.is_set() and time.monotonic() < deadline:
            s = engine.snapshot()
            growing.append(s["pages_scanned"])
            if s["pages_queued"] > 0 and s["links_checked"] > s["pages_scanned"] + 3 \
                    and s["links_checked"] > 0:
                overlap = True
            time.sleep(0.05)
        self.assertTrue(engine.finished.is_set())
        self.assertTrue(overlap, "checking did not overlap with crawling")
        self.assertEqual(growing[-1], n + 1)
        self.assertTrue(len(set(growing)) > 5, "pages_scanned did not grow live")


if __name__ == "__main__":
    unittest.main()
