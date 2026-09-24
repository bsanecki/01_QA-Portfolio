"""Browser selection: detection, clear errors, HTTP independence, Auto."""

import os
import tempfile
import unittest
from unittest import mock

import browser_crawler as bc
import scan_engine
from full_scanner import mode_for_label
from models import CRAWL_MODES
from tests.helpers import Site, html, links, run_scan, by_url


class TestDetection(unittest.TestCase):
    def test_usual_locations_per_platform(self):
        env = {"PROGRAMFILES": r"C:\Program Files",
               "PROGRAMFILES(X86)": r"C:\Program Files (x86)",
               "LOCALAPPDATA": r"C:\Users\me\AppData\Local"}
        for browser_id in ("chrome", "edge", "brave", "opera"):
            spec = bc.BROWSERS[browser_id]
            for platform in ("win32", "darwin", "linux"):
                with self.subTest(browser=browser_id, platform=platform):
                    paths = bc.candidate_paths(spec, platform, env, "/home/me")
                    self.assertTrue(paths)
                    if platform == "win32":
                        self.assertTrue(all(p.startswith("C:") for p in paths))
                        self.assertTrue(all(p.lower().endswith(".exe") for p in paths))
                    if platform == "darwin":
                        self.assertTrue(all(".app/Contents/MacOS" in p for p in paths))

    def test_found_wherever_it_is_installed(self):
        # Chrome installed only in the per-user folder on Windows
        env = {"LOCALAPPDATA": r"C:\Users\me\AppData\Local"}
        target = os.path.join(env["LOCALAPPDATA"], r"Google\Chrome\Application\chrome.exe")
        found = bc.find_system_browser(
            "chrome", platform="win32", env=env, exists=lambda p: p == target,
            which=lambda n: None, registry=lambda e: None)
        self.assertEqual(found, target)
        # found via PATH on Linux
        found = bc.find_system_browser(
            "brave", platform="linux", env={}, exists=lambda p: False,
            which=lambda n: "/x/brave" if n == "brave-browser" else None)
        self.assertEqual(found, "/x/brave")
        # found via the Windows registry (non-standard install dir)
        found = bc.find_system_browser(
            "opera", platform="win32", env={}, exists=lambda p: p == r"D:\Opera\opera.exe",
            which=lambda n: None, registry=lambda exe: r"D:\Opera\opera.exe")
        self.assertEqual(found, r"D:\Opera\opera.exe")
        # not installed
        self.assertIsNone(bc.find_system_browser(
            "edge", platform="linux", env={}, exists=lambda p: False,
            which=lambda n: None))

    def test_playwright_download_detection(self):
        with tempfile.TemporaryDirectory() as root:
            self.assertFalse(bc.playwright_browser_downloaded("firefox", [root]))
            os.mkdir(os.path.join(root, "firefox-1488"))
            self.assertTrue(bc.playwright_browser_downloaded("firefox", [root]))
            self.assertFalse(bc.playwright_browser_downloaded("chromium", [root]))
            os.mkdir(os.path.join(root, "chromium_headless_shell-1194"))
            self.assertTrue(bc.playwright_browser_downloaded("chromium", [root]))

    def test_clear_messages_instead_of_crashes(self):
        with mock.patch.object(bc, "playwright_installed", return_value=False):
            check = bc.check_browser("chrome")
            self.assertFalse(check.ok)
            self.assertIn("pip install playwright", check.message)
        with mock.patch.object(bc, "playwright_installed", return_value=True), \
                mock.patch.object(bc, "find_system_browser", return_value=None):
            for browser_id, label in (("chrome", "Google Chrome"), ("edge", "Microsoft Edge"),
                                      ("brave", "Brave"), ("opera", "Opera")):
                check = bc.check_browser(browser_id)
                self.assertFalse(check.ok)
                self.assertIn(label, check.message)
                self.assertIn("not found", check.message)
        with mock.patch.object(bc, "playwright_installed", return_value=True), \
                mock.patch.object(bc, "playwright_browser_downloaded", return_value=False):
            self.assertIn("playwright install firefox", bc.check_browser("firefox").message)
            self.assertIn("playwright install chromium", bc.check_browser("chromium").message)
        self.assertFalse(bc.check_browser("netscape").ok)

    def test_auto_order_and_none(self):
        def fake(available):
            return lambda i, **k: bc.BrowserCheck(i in available, i, i)
        with mock.patch.object(bc, "check_browser", fake({"edge", "firefox"})):
            self.assertEqual(bc.resolve_auto().browser_id, "edge")
        with mock.patch.object(bc, "check_browser", fake({"chromium", "edge"})):
            self.assertEqual(bc.resolve_auto().browser_id, "chromium")
        with mock.patch.object(bc, "check_browser", fake(set())):
            self.assertIsNone(bc.resolve_auto())

    def test_selector_labels(self):
        self.assertEqual(CRAWL_MODES, ("Auto", "HTTP", "Chromium", "Chrome",
                                       "Firefox", "Edge", "Brave", "Opera"))
        self.assertEqual(mode_for_label("HTTP")[0], "http")
        self.assertEqual(mode_for_label("Auto")[0], "auto")
        for label in CRAWL_MODES[2:]:
            self.assertEqual(mode_for_label(label), ("browser", label.lower()))
            self.assertIn(label.lower(), bc.BROWSERS)


class FakeFetcher:
    """Stands in for a real browser: 'renders' a page by adding a JS link."""
    instances = []

    def __init__(self, limiter, browser_id="chromium", path=None):
        self.browser_id = browser_id
        self.rendered = []
        FakeFetcher.instances.append(self)

    def fetch(self, url, stop_event, kind="page"):
        from link_checker import RequestOutcome
        from models import LinkResult
        self.rendered.append(url)
        body = "<html><a href='/js-page'>js</a></html>"
        return RequestOutcome(LinkResult(url=url, status=200, final_url=url, elapsed=0.0), body, "text/html")

    def close_thread(self):
        pass


class BrokenFetcher(FakeFetcher):
    def fetch(self, url, stop_event, kind="page"):
        raise RuntimeError("browser crashed")


class TestEngineBrowserModes(unittest.TestCase):
    def setUp(self):
        FakeFetcher.instances.clear()

    def _site(self):
        site = Site({
            "/": html(""),                               # SPA shell: no links
            "/js-page": html(links("/static-only")),
            "/static-only": html("x"),
        })
        self.addCleanup(site.close)
        return site

    def test_http_mode_never_touches_playwright(self):
        site = self._site()
        boom = mock.Mock(side_effect=AssertionError("playwright used in HTTP mode"))
        with mock.patch.object(scan_engine, "check_browser", boom), \
                mock.patch.object(scan_engine, "resolve_auto", boom), \
                mock.patch.object(scan_engine, "BrowserPageFetcher", boom):
            engine = run_scan(site.url("/"), crawl_mode="http")
        self.assertEqual(engine.pages_scanned, 1)
        self.assertNotIn(site.url("/js-page"), by_url(engine))

    def test_missing_browser_is_a_notice_not_a_crash(self):
        site = self._site()
        missing = bc.BrowserCheck(False, "opera", "Opera",
                                  message="Opera was not found on this computer.")
        with mock.patch.object(scan_engine, "check_browser", return_value=missing):
            engine = run_scan(site.url("/"), crawl_mode="browser", browser="opera")
        notices = []
        while not engine.events.empty():
            ev = engine.events.get()
            if ev[0] == "notice":
                notices.append(ev[1])
        self.assertTrue(any("Opera was not found" in n and "HTTP mode" in n for n in notices))
        self.assertEqual(engine.pages_scanned, 1)            # plain HTTP scan still ran

    def test_chosen_browser_is_the_only_one_started(self):
        site = self._site()
        ok = bc.BrowserCheck(True, "brave", "Brave", "/usr/bin/brave")
        with mock.patch.object(scan_engine, "check_browser", return_value=ok), \
                mock.patch.object(scan_engine, "BrowserPageFetcher", FakeFetcher):
            engine = run_scan(site.url("/"), crawl_mode="browser", browser="brave")
        self.assertEqual({f.browser_id for f in FakeFetcher.instances}, {"brave"})
        self.assertEqual(len(FakeFetcher.instances), 1)      # one fetcher, shared
        self.assertIn(site.url("/js-page"), by_url(engine))  # JS link found
        self.assertEqual(engine.browser_label, "Brave")

    def test_auto_renders_only_pages_without_static_links(self):
        site = Site({
            "/": html(links("/plain")),                  # has navigation
            "/plain": html(""),                          # SPA-like page
            "/js-page": html("j"),
        })
        self.addCleanup(site.close)
        ok = bc.BrowserCheck(True, "chromium", "Chromium")
        with mock.patch.object(scan_engine, "resolve_auto", return_value=ok), \
                mock.patch.object(scan_engine, "BrowserPageFetcher", FakeFetcher):
            engine = run_scan(site.url("/"), crawl_mode="auto")
        rendered = [u for f in FakeFetcher.instances for u in f.rendered]
        self.assertIn(site.url("/plain"), rendered)          # no static links
        self.assertNotIn(site.url("/"), rendered)             # has navigation
        self.assertIn(site.url("/js-page"), by_url(engine))

    def test_browser_crash_does_not_lose_static_links(self):
        site = Site({"/": html(links("/a")), "/a": html("a")})
        self.addCleanup(site.close)
        ok = bc.BrowserCheck(True, "chromium", "Chromium")
        with mock.patch.object(scan_engine, "check_browser", return_value=ok), \
                mock.patch.object(scan_engine, "BrowserPageFetcher", BrokenFetcher):
            engine = run_scan(site.url("/"), crawl_mode="browser")
        self.assertEqual(engine.pages_scanned, 2)
        self.assertEqual(site.count("/a"), 1)

    def test_auto_without_any_browser_is_plain_http(self):
        site = self._site()
        with mock.patch.object(scan_engine, "resolve_auto", return_value=None):
            engine = run_scan(site.url("/"), crawl_mode="auto")
        self.assertEqual(engine.pages_scanned, 1)
        self.assertEqual(engine.browser_label, "")


JS_PAGE = (b"<html><body><div id=app></div><script>"
           b"document.getElementById('app').innerHTML="
           b"'<a href=\"/from-js\">js link</a>';</script></body></html>")


@unittest.skipUnless(bc.check_browser("chromium").ok, "Playwright Chromium not installed")
class TestRealBrowser(unittest.TestCase):
    def _site(self):
        site = Site({"/": lambda h, m: h.reply(200, JS_PAGE),
                     "/from-js": html("found")})
        self.addCleanup(site.close)
        return site

    def test_http_does_not_see_js_links_but_chromium_does(self):
        site = self._site()
        engine = run_scan(site.url("/"), crawl_mode="http")
        self.assertNotIn(site.url("/from-js"), by_url(engine))
        site = self._site()
        engine = run_scan(site.url("/"), crawl_mode="browser", browser="chromium", timeout=120)
        self.assertIn(site.url("/from-js"), by_url(engine))
        self.assertEqual(engine.pages_scanned, 2)

    def test_auto_finds_js_links(self):
        site = self._site()
        engine = run_scan(site.url("/"), crawl_mode="auto", timeout=120)
        self.assertIn(site.url("/from-js"), by_url(engine))

    @unittest.skipUnless(bc.check_browser("chrome").ok, "Chrome not installed")
    def test_installed_chrome_executable(self):
        site = self._site()
        engine = run_scan(site.url("/"), crawl_mode="browser", browser="chrome", timeout=120)
        self.assertIn(site.url("/from-js"), by_url(engine))


if __name__ == "__main__":
    unittest.main()
