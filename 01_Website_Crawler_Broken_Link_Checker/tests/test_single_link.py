"""Single Link Check: shares link_checker + LinkResult classification with
the Full Website Scan (no second HTTP checker)."""

import socket
import time
import unittest
from unittest import mock

import link_checker
import single_link
from tests.helpers import Site, html, redirect, status_route, run_scan, by_url
from settings import AppSettings
from single_link import (
    FIELDS, check_single_link, prepare_url, summarize_result,
)


def rows(result):
    return dict(summarize_result(result)["rows"])


class TestPrepareUrl(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(prepare_url("  HTTPS://Example.com  "), "https://example.com/")
        self.assertEqual(prepare_url("http://a.b/x?y=1#frag"), "http://a.b/x?y=1")

    def test_invalid(self):
        for bad in ("", "   ", "example.com", "ftp://x.org", "javascript:alert(1)",
                    "http://", "https:///path"):
            with self.assertRaises(ValueError, msg=repr(bad)):
                prepare_url(bad)


class TestCheckSingleLink(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.site = Site({
            "/ok": html("fine"),
            "/old": redirect(301, "/mid"),
            "/mid": redirect(302, "/ok"),
            "/gone": status_route(404),
            "/removed": status_route(410),
            "/forbidden": status_route(403),
            "/boom": status_route(500),
            "/loop": redirect(302, "/loop"),
        })

    @classmethod
    def tearDownClass(cls):
        cls.site.close()

    def check(self, path, **settings):
        return check_single_link(self.site.url(path), AppSettings(**settings))

    def test_uses_the_shared_checker(self):
        with mock.patch.object(single_link, "check_link",
                               wraps=link_checker.check_link) as spy:
            self.check("/ok")
        self.assertEqual(spy.call_count, 1)

    def test_ok(self):
        r = self.check("/ok")
        self.assertEqual((r.status, r.category), (200, "ok"))
        d = rows(r)
        self.assertEqual(list(d), list(FIELDS))
        self.assertEqual(d["URL"], self.site.url("/ok"))
        self.assertEqual(d["HTTP Status"], "200 OK")
        self.assertEqual(d["Status Category"], "OK")
        self.assertRegex(d["Response Time"], r"^\d+\.\d\ds$")
        self.assertEqual(d["Final URL"], self.site.url("/ok"))
        self.assertEqual(d["Redirects"], "None")

    def test_redirect_chain(self):
        r = self.check("/old")
        d = rows(r)
        self.assertEqual(d["Status Category"], "Redirect")
        self.assertEqual(d["HTTP Status"], "200 OK")
        self.assertEqual(d["Final URL"], self.site.url("/ok"))
        self.assertTrue(d["Redirects"].startswith("2 redirects:"))
        self.assertIn("301", d["Redirects"])
        self.assertIn("/mid", d["Redirects"])
        self.assertIn("Redirect:", d["Details"])

    def test_redirects_not_followed(self):
        site = Site({"/old": redirect(301, "/mid"), "/mid": html("m")})
        self.addCleanup(site.close)
        r = check_single_link(site.url("/old"), AppSettings(follow_redirects=False))
        d = rows(r)
        self.assertEqual(d["HTTP Status"], "301 Moved Permanently")
        self.assertEqual(d["Status Category"], "Redirect")
        self.assertEqual(d["Final URL"], site.url("/mid"))
        self.assertEqual(site.count("/mid"), 0)
        self.assertIn("not followed", d["Redirects"])

    def test_same_classification_as_the_full_scan(self):
        paths = ["/ok", "/old", "/gone", "/removed", "/forbidden", "/boom", "/loop"]
        page = html("".join(f'<img src="{p}">' for p in paths))
        site = Site({"/": page, **{p: self.site.routes[p] for p in paths}})
        self.addCleanup(site.close)
        scan = by_url(run_scan(site.url("/")))
        for p in paths:
            single = check_single_link(site.url(p))
            scanned = scan[site.url(p)][1]
            self.assertEqual(single.category, scanned.category, p)
            self.assertEqual(single.status, scanned.status, p)
            self.assertEqual(single.error_type, scanned.error_type, p)

    def test_categories(self):
        expected = {"/gone": "Broken", "/removed": "Broken", "/forbidden": "Unverified",
                    "/boom": "Unverified", "/loop": "Broken"}
        for path, label in expected.items():
            self.assertEqual(rows(self.check(path))["Status Category"], label, path)
        self.assertEqual(rows(self.check("/gone"))["HTTP Status"], "404 Not Found")

    def test_connection_error_is_reported_not_raised(self):
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]           # nothing listens here any more
        d = rows(check_single_link(f"http://127.0.0.1:{port}/"))
        self.assertTrue(d["HTTP Status"].startswith("No response"))
        self.assertEqual(d["Status Category"], "Unverified")
        self.assertTrue(d["Details"])

    def test_timeout_setting_is_applied(self):
        def slow(h, m):
            time.sleep(2.5)
            h.reply(200, b"ok")
        site = Site({"/slow": slow})
        self.addCleanup(site.close)
        self.assertEqual(check_single_link(site.url("/slow")).status, 200)
        r = check_single_link(site.url("/slow"), AppSettings(request_timeout=1))
        self.assertEqual(r.error_type, "TIMEOUT")
        self.assertEqual(rows(r)["Status Category"], "Unverified")

    def test_stop_event(self):
        import threading
        stop = threading.Event()
        stop.set()
        self.assertIsNone(check_single_link(self.site.url("/ok"), stop_event=stop))


if __name__ == "__main__":
    unittest.main()
