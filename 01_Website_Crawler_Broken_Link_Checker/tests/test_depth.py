"""Crawl Depth semantics (branching tree, back-links, sitemap, races).

Depth N = pages at most N link-hops from the start page are DOWNLOADED and
PARSED. Links found on them are always status-checked, but pages beyond
depth N are never parsed / expanded.
"""

import time
import unittest

from tests.helpers import Site, html, links, run_scan, by_url

# depth: 0 "/" | 1 /a /b | 2 /a1 /a2 /b1 | 3 /a11 | 4 /a111
TREE = {
    "/": ["/a", "/b"],
    "/a": ["/a1", "/a2", "/"],          # "/" = back-link (cycle)
    "/b": ["/b1"],
    "/a1": ["/a11"],
    "/a2": ["/b1", "/a"],               # b1 also reachable via /a2 (3 hops)
    "/b1": ["/a11"],                    # a11 reachable via a1 and via b1
    "/a11": ["/a111"],
    "/a111": [],
}
# depth -> (pages_scanned, links_discovered)
EXPECTED = {
    0: (1, 3),      # / ; discovered: /, /a, /b
    1: (3, 6),      # + /a /b ; discovered + /a1 /a2 /b1
    2: (6, 7),      # + /a1 /a2 /b1 ; discovered + /a11
    3: (7, 8),      # + /a11 ; discovered + /a111
    4: (8, 8),
    None: (8, 8),
}


def tree_site(**kw):
    return Site({p: html(links(*c) if c else "leaf") for p, c in TREE.items()}, **kw)


class TestCrawlDepth(unittest.TestCase):
    def test_depth_levels_give_different_exact_results(self):
        for depth, (pages, discovered) in EXPECTED.items():
            with self.subTest(depth=depth):
                site = tree_site()
                self.addCleanup(site.close)
                engine = run_scan(site.url("/"), depth=depth)
                self.assertEqual(engine.pages_scanned, pages)
                self.assertEqual(engine.links_discovered, discovered)
                self.assertEqual(len(engine.results), discovered)
                self.assertEqual(engine.links_checked, discovered)
                # Pages scanned == pages really downloaded AND parsed: every
                # crawled page is in page_depths; nothing else is.
                self.assertEqual(len(engine.page_depths), pages)
                # every URL was requested exactly once (crawl or check)
                for path in TREE:
                    self.assertLessEqual(site.count(path), 1, path)
                for path, _ in ((p, 0) for p in TREE):
                    if site.url(path) in by_url(engine):
                        self.assertEqual(site.count(path), 1, path)

    def test_depth_counts_grow_monotonically(self):
        seen = []
        for depth in (0, 1, 2, 3, 4):
            site = tree_site()
            self.addCleanup(site.close)
            seen.append(run_scan(site.url("/"), depth=depth).pages_scanned)
        self.assertEqual(seen, sorted(set(seen)))          # strictly increasing
        self.assertEqual(seen, [1, 3, 6, 7, 8])

    def test_pages_beyond_depth_are_checked_but_never_queued_or_parsed(self):
        site = tree_site()
        self.addCleanup(site.close)
        engine = run_scan(site.url("/"), depth=1)
        found = by_url(engine)
        # boundary pages (depth 2) are checked...
        for path in ("/a1", "/a2", "/b1"):
            self.assertIn(site.url(path), found)
            self.assertEqual(site.count(path), 1)
            self.assertNotIn(site.url(path), engine.page_depths)
        # ...but their children are not even discovered
        self.assertNotIn(site.url("/a11"), found)
        self.assertEqual(site.count("/a11"), 0)

    def test_page_depths_are_shortest_paths(self):
        site = tree_site()
        self.addCleanup(site.close)
        engine = run_scan(site.url("/"), depth=None)
        d = {p: engine.page_depths[site.url(p)] for p in TREE}
        self.assertEqual(d, {"/": 0, "/a": 1, "/b": 1, "/a1": 2, "/a2": 2,
                             "/b1": 2, "/a11": 3, "/a111": 4})

    def test_depth_is_shortest_path_even_when_shallow_parent_is_slow(self):
        """X is 2 hops away via slow /p1, 3 hops via fast /p2 -> /q. With
        Crawl Depth 2 X must still be crawled (regression: whichever parent
        finished first used to decide X's depth)."""
        def slow(body, secs):
            def handler(h, m):
                time.sleep(secs)
                h.reply(200, body.encode())
            return handler
        site = Site({
            "/": html(links("/p1", "/p2")),
            "/p1": slow("<html>" + links("/x") + "</html>", 0.8),
            "/p2": html(links("/q")),
            "/q": html(links("/x")),
            "/x": html(links("/deep")),
            "/deep": html("deep"),
        })
        self.addCleanup(site.close)
        engine = run_scan(site.url("/"), depth=2)
        self.assertIn(site.url("/x"), engine.page_depths)
        self.assertEqual(engine.page_depths[site.url("/x")], 2)
        self.assertIn(site.url("/deep"), by_url(engine))     # found on x
        self.assertNotIn(site.url("/deep"), engine.page_depths)
        # Rare race: /x may be status-checked once before the shorter path
        # promotes it to a crawl (2 GETs) - but it is reported exactly once.
        self.assertLessEqual(site.count("/x"), 2)
        self.assertEqual(
            sum(1 for link, _r in engine.results if link.url == site.url("/x")), 1)

    def test_sitemap_only_pages_do_not_bypass_depth(self):
        def build():
            s = Site({
                "/": html(links("/a")),
                "/a": html("a"),
                "/orphan1": html(links("/orphan-child")),
                "/orphan2": html("o2"),
                "/orphan-child": html("c"),
                "/sitemap.xml": lambda h, m: h.reply(
                    200, ("<urlset><url><loc>%s/orphan1</loc></url>"
                          "<url><loc>%s/orphan2</loc></url></urlset>"
                          % (h.server.base, h.server.base)).encode(),
                    ctype="application/xml"),
            })
            s.httpd.base = s.base
            self.addCleanup(s.close)
            return s
        site = build()
        engine = run_scan(site.url("/"), depth=1)
        found = by_url(engine)
        self.assertEqual(engine.pages_scanned, 2)             # "/" and "/a"
        self.assertIn(site.url("/orphan1"), found)            # still checked
        self.assertEqual(found[site.url("/orphan1")][1].category, "ok")
        self.assertNotIn(site.url("/orphan-child"), found)    # not crawled
        self.assertEqual(site.count("/orphan-child"), 0)

        site = build()                                         # Unlimited crawls them
        engine = run_scan(site.url("/"), depth=None)
        self.assertIn(site.url("/orphan-child"), by_url(engine))
        self.assertEqual(engine.pages_scanned, 5)

    def test_stylesheet_assets_do_not_count_as_pages(self):
        site = Site({
            "/": html("", head='<link rel="stylesheet" href="/s.css">'),
            "/s.css": lambda h, m: h.reply(200, b"a{background:url(/i.png)}",
                                           ctype="text/css"),
            "/i.png": lambda h, m: h.reply(200, b"x", ctype="image/png"),
        })
        self.addCleanup(site.close)
        engine = run_scan(site.url("/"), depth=0)
        self.assertEqual(engine.pages_scanned, 1)
        self.assertIn(site.url("/i.png"), by_url(engine))


if __name__ == "__main__":
    unittest.main()
