"""More-screen content: How to Use, HTTP Status Codes, About (no GUI)."""

import unittest

import app_info
from models import BROKEN_STATUSES, LinkResult


class TestHowTo(unittest.TestCase):
    def test_covers_every_required_topic(self):
        text = " ".join(h + " " + b for h, b in app_info.HOW_TO_USE)
        for topic in (
            "Full Website Scan", "Single Link Check", "Crawl Depth", "HTTP",
            "Auto", "Chromium", "Chrome", "Firefox", "Edge", "Brave", "Opera",
            "OK", "Redirect", "Broken", "Unverified", "STOP", "Report", "Excel",
        ):
            self.assertIn(topic, text, topic)


class TestStatusReference(unittest.TestCase):
    def setUp(self):
        self.rows = {r.code: r for r in app_info.status_code_reference()}

    def test_required_codes_present(self):
        for code in ("200", "301", "302", "400", "401", "403", "404", "408",
                     "429", "500", "502", "503"):
            self.assertIn(code, self.rows)
            self.assertTrue(self.rows[code].text)

    def test_names_are_the_official_phrases(self):
        self.assertEqual(self.rows["404"].name, "Not Found")
        self.assertEqual(self.rows["503"].name, "Service Unavailable")

    def test_categories_match_the_real_classifier(self):
        for row in self.rows.values():
            if row.code.isdigit():
                real = LinkResult("u", int(row.code), "u", 0.0).category
                self.assertEqual(row.category, real, row.code)

        expected_broken = {str(c) for c in BROKEN_STATUSES}
        shown_broken = {
            c for c, r in self.rows.items()
            if r.category == "broken" and c.isdigit()
        }

        self.assertEqual(shown_broken, expected_broken)
        self.assertEqual(self.rows["200"].category_label, "OK")
        self.assertEqual(self.rows["301"].category_label, "Redirect")
        self.assertEqual(self.rows["403"].category_label, "Unverified")
        self.assertEqual(self.rows["No response"].category, "unverified")
        self.assertEqual(self.rows["Redirect loop"].category, "broken")


class TestAbout(unittest.TestCase):
    def test_author_and_paypal_url(self):
        from urllib.parse import urlsplit

        self.assertEqual(app_info.AUTHOR_NAME, "Bartosz Sanecki")

        parts = urlsplit(app_info.PAYPAL_URL)

        self.assertEqual(parts.scheme, "https")
        self.assertEqual(parts.netloc, "paypal.me")
        self.assertEqual(parts.path, "/bsanecki")


    def test_texts(self):
        self.assertEqual(
            app_info.TECHNOLOGIES,
            (
                "Python",
                "Playwright",
                "Requests",
                "BeautifulSoup",
                "Tkinter",
                "pytest",
            )
        )


if __name__ == "__main__":
    unittest.main()
