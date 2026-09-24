"""Settings: validation, persistence and - most important - that the three
values really change what the scanner does. Run with the other tests:
    python3 -m unittest discover -s tests -t .
"""

import json
import os
import tempfile
import time
import unittest

from tests.helpers import Site, html, links, redirect, run_scan, by_url
from settings import (
    DEFAULT_REQUEST_TIMEOUT,
    AppSettings,
    SettingsError,
    SettingsStore,
    parse_timeout,
    scale_timeout,
)
from models import LINK_TIMEOUT, PAGE_TIMEOUT
from scan_engine import ScanConfig


class TestSettingsValues(unittest.TestCase):
    def test_defaults_preserve_current_behaviour(self):
        s = AppSettings()
        self.assertEqual(s.request_timeout, 15)
        self.assertTrue(s.follow_redirects)
        self.assertTrue(s.respect_robots)
        self.assertEqual(s.timeout_scale, 1)
        # default scale leaves the built-in timeouts exactly as they were
        self.assertEqual(scale_timeout(LINK_TIMEOUT, s.timeout_scale), LINK_TIMEOUT)
        self.assertEqual(scale_timeout(PAGE_TIMEOUT, s.timeout_scale), PAGE_TIMEOUT)
        # ScanConfig defaults agree with the Settings defaults
        c = ScanConfig(start_url="http://x/")
        self.assertEqual(
            (c.request_timeout, c.follow_redirects, c.respect_robots),
            (DEFAULT_REQUEST_TIMEOUT, True, True))

    def test_scaling(self):
        self.assertEqual(scale_timeout((3.0, 5.0), 2), (6.0, 10.0))
        self.assertEqual(scale_timeout((3.0, 5.0), 1 / 15), (1.0, 1.0))  # floor 1 s

    def test_timeout_validation(self):
        self.assertEqual(parse_timeout(" 30 "), 30)
        for bad in ("", "abc", "0", "-5", "121", "1.5", None):
            with self.assertRaises(SettingsError, msg=repr(bad)):
                parse_timeout(bad)

    def test_from_dict_is_lenient(self):
        s = AppSettings.from_dict(
            {"request_timeout": "x", "follow_redirects": "yes", "respect_robots": False})
        self.assertEqual(s, AppSettings(15, True, False))
        self.assertEqual(AppSettings.from_dict(None), AppSettings())


class TestSettingsStore(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.path = os.path.join(self.dir.name, "s.json")

    def test_save_and_reload(self):
        store = SettingsStore(self.path)
        self.assertEqual(store.current, AppSettings())      # nothing saved yet
        self.assertTrue(store.save(AppSettings(40, False, False)))
        self.assertEqual(SettingsStore(self.path).current, AppSettings(40, False, False))

    def test_corrupt_or_missing_file_gives_defaults(self):
        with open(self.path, "w") as f:
            f.write("{not json")
        self.assertEqual(SettingsStore(self.path).current, AppSettings())
        bad = os.path.join(self.dir.name, "nope", "s.json")
        store = SettingsStore(bad)
        self.assertFalse(store.save(AppSettings(20)))       # cannot write ...
        self.assertEqual(store.current.request_timeout, 20)  # ... still applied

    def test_file_content(self):
        SettingsStore(self.path).save(AppSettings(25, True, False))
        with open(self.path) as f:
            self.assertEqual(json.load(f), {
                "request_timeout": 25, "follow_redirects": True,
                "respect_robots": False})


class TestSettingsAffectScanner(unittest.TestCase):
    def test_follow_redirects_on_vs_off(self):
        def make():
            site = Site({
                "/": html(links("/old")),
                "/old": redirect(301, "/mid"),
                "/mid": redirect(302, "/final"),
                "/final": html(links("/beyond")),
                "/beyond": html("x"),
            })
            self.addCleanup(site.close)
            return site

        on = make()
        engine = run_scan(on.url("/"))
        link, result = by_url(engine)[on.url("/old")]
        self.assertEqual((result.status, result.category), (200, "redirect"))
        self.assertEqual(result.final_url, on.url("/final"))
        self.assertIn(on.url("/beyond"), by_url(engine))      # crawled through it

        off = make()
        engine = run_scan(off.url("/"), follow_redirects=False)
        link, result = by_url(engine)[off.url("/old")]
        self.assertEqual(result.status, 301)                  # reported as is
        self.assertEqual(result.category, "redirect")
        self.assertEqual(result.final_url, off.url("/mid"))   # Location target
        self.assertEqual(off.count("/mid"), 0)                # never followed
        self.assertEqual(off.count("/final"), 0)
        self.assertNotIn(off.url("/beyond"), by_url(engine))

    def test_follow_redirects_off_checks_external_links_too(self):
        target = Site({"/moved": redirect(301, "/new"), "/new": html("n")})
        self.addCleanup(target.close)
        site = Site({"/": html(links(target.url("/moved")))})
        self.addCleanup(site.close)
        engine = run_scan(site.url("/"), follow_redirects=False)
        result = by_url(engine)[target.url("/moved")][1]
        self.assertEqual(result.status, 301)
        self.assertEqual(target.count("/new"), 0)

    def _robots_site(self):
        site = Site({
            "/": html(links("/private/a")),
            "/private/a": html(links("/private/b")),
            "/private/b": html("b"),
            "/robots.txt": "User-agent: *\nDisallow: /private/\n",
        })
        self.addCleanup(site.close)
        return site

    def test_respect_robots_on_vs_off(self):
        site = self._robots_site()
        engine = run_scan(site.url("/"))                       # default: respect
        self.assertNotIn(site.url("/private/b"), by_url(engine))
        self.assertEqual(site.count("/robots.txt"), 1)

        site = self._robots_site()
        engine = run_scan(site.url("/"), respect_robots=False)
        self.assertIn(site.url("/private/b"), by_url(engine))  # crawled
        self.assertEqual(site.count("/robots.txt"), 0)         # not even fetched

    def test_request_timeout_changes_when_a_request_gives_up(self):
        def slow(h, m):
            time.sleep(2.5)
            h.reply(200, b"ok", ctype="image/png")

        def make():
            site = Site({"/": html('<img src="/slow.png">'), "/slow.png": slow})
            self.addCleanup(site.close)
            return site

        site = make()                                          # default 15 -> read 5 s
        result = by_url(run_scan(site.url("/")))[site.url("/slow.png")][1]
        self.assertEqual(result.category, "ok")

        site = make()                                          # 1 s -> gives up
        result = by_url(run_scan(site.url("/"), request_timeout=1))[site.url("/slow.png")][1]
        self.assertEqual(result.error_type, "TIMEOUT")
        self.assertEqual(result.category, "unverified")        # still never Broken


if __name__ == "__main__":
    unittest.main()
