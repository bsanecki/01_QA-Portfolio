"""GUI tests for the menu, Single Link Check, Settings, More, About, PayPal
and Exit. Needs a display (Linux: xvfb-run -a python3 -m unittest
tests.test_gui_screens); skipped automatically when none is available."""

import os
import tempfile
import time
import tkinter as tk
import unittest
from tkinter import messagebox
from unittest import mock

from tests.helpers import Site, html, redirect, status_route


def _display_ok():
    try:
        root = tk.Tk()
        root.destroy()
        return True
    except tk.TclError:
        return False


HAVE_DISPLAY = _display_ok()

# Several Tk roots are created and destroyed in one process here. A Tk
# variable that is garbage-collected on a worker thread after its interpreter
# is gone would abort the process ("Tcl_AsyncDelete"), so variables are not
# finalised by __del__ while the tests run.
tk.Variable.__del__ = lambda self: None


def pump(app, seconds=0.2):
    end = time.time() + seconds
    while time.time() < end:
        app.update()
        time.sleep(0.01)


def wait_for(app, condition, timeout=30):
    end = time.time() + timeout
    while time.time() < end:
        app.update()
        if condition():
            return True
        time.sleep(0.01)
    return False


_APPS = []   # keep every root alive: a Tk root finalised on a worker thread aborts


def new_app(settings_path=None):
    import main

    path = settings_path or os.path.join(tempfile.mkdtemp(), "settings.json")
    app = main.WebsiteCrawlerApp(settings_path=path)
    _APPS.append(app)
    return app


def cancel_timers(app):
    """Timers are per thread in Tcl: leftovers of a destroyed root would fire
    (and print errors) while the next root runs."""
    for after_id in app.tk.splitlist(app.tk.call("after", "info")):
        app.tk.call("after", "cancel", after_id)


def close_app(app):
    cancel_timers(app)
    app.on_close()


def top_frame(app):
    """Name of the top-most screen (last child in Tk's stacking order)."""
    container = app.menu_frame.master
    names = {
        str(f): n
        for n, f in vars(app).items()
        if isinstance(f, tk.Frame) and n.endswith("_frame")
    }
    stack = container.tk.splitlist(
        container.tk.call("winfo", "children", container)
    )
    return names[stack[-1]]


def all_widgets(widget):
    """Return widget and all widgets nested inside it."""
    result = [widget]

    for child in widget.winfo_children():
        result.extend(all_widgets(child))

    return result


@unittest.skipUnless(HAVE_DISPLAY, "no display available")
class TestMenuAndNavigation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = new_app()
        pump(cls.app)

    @classmethod
    def tearDownClass(cls):
        close_app(cls.app)

    def test_application_opens_directly_on_the_main_menu(self):
        import main

        app = new_app()
        self.addCleanup(close_app, app)
        pump(app, 0.1)

        self.assertEqual(top_frame(app), "menu_frame")
        self.assertFalse(hasattr(app, "welcome_frame"))
        self.assertFalse(hasattr(main, "WelcomeFrame"))

    def test_main_menu_entries(self):
        self.assertEqual(
            list(self.app.menu_frame.buttons),
            [
                "Full Website Scan",
                "Single Link Check",
                "Settings",
                "More",
                "Exit",
            ],
        )

    def test_menu_buttons_open_the_right_screens(self):
        b = self.app.menu_frame.buttons

        for label, screen in (
            ("Full Website Scan", "scanner_frame"),
            ("Single Link Check", "single_frame"),
            ("Settings", "settings_frame"),
            ("More", "more_frame"),
        ):
            self.app.show_menu()
            b[label].invoke()
            pump(self.app, 0.05)
            self.assertEqual(top_frame(self.app), screen, label)

    def test_more_menu(self):
        app = self.app
        app.show_more()

        self.assertEqual(
            list(app.more_frame.buttons),
            ["How to Use", "HTTP Status Codes", "About"],
        )

        for label, screen in (
            ("How to Use", "how_to_frame"),
            ("HTTP Status Codes", "status_frame"),
            ("About", "about_frame"),
        ):
            app.show_more()
            app.more_frame.buttons[label].invoke()
            pump(app, 0.05)
            self.assertEqual(top_frame(app), screen, label)

        app.show_how_to()

        for w in app.how_to_frame.winfo_children():
            if isinstance(w, tk.Button):
                w.invoke()

        self.assertEqual(top_frame(app), "more_frame")

    def test_how_to_use_screen_shows_the_guide(self):
        text = self.app.how_to_frame.read_text()

        for topic in (
            "Full Website Scan",
            "Single Link Check",
            "Crawl Depth",
            "Chromium",
            "Brave",
            "Unverified",
            "STOP",
            "Excel",
        ):
            self.assertIn(topic, text)

    def test_status_codes_screen_lists_codes_with_classification(self):
        text = self.app.status_frame.read_text()

        for code in (
            "200",
            "301",
            "302",
            "400",
            "401",
            "403",
            "404",
            "408",
            "429",
            "500",
            "502",
            "503",
        ):
            self.assertIn(code, text)

        self.assertIn("404  Not Found   [Broken]", text)
        self.assertIn("403  Forbidden   [Unverified]", text)
        self.assertIn("301  Moved Permanently   [Redirect]", text)

    def test_about_screen_and_paypal_button(self):
        about = self.app.about_frame

        # Search recursively because some About-screen elements can be
        # placed inside nested Frames.
        widgets = all_widgets(about)

        labels = [
            w.cget("text")
            for w in widgets
            if isinstance(w, (tk.Label, tk.Button))
        ]

        for expected in (
            "Website Crawler & Broken Link Checker",
            "Developed by:",
            "Bartosz Sanecki",
            "Support the Developer",
            "Support via PayPal",
        ):
            self.assertIn(expected, labels)

        # The PayPal e-mail and Copy button were removed.
        self.assertFalse(
            any("PayPal:" in text for text in labels)
        )
        self.assertFalse(
            any(text == "Copy" for text in labels)
        )

        self.assertFalse(
            any("Credits" in text for text in labels)
        )

        self.assertTrue(
            any("Playwright" in text and "pytest" in text for text in labels)
        )

        # The PayPal button should open the author's PayPal.Me page.
        with mock.patch(
            "more_screens.webbrowser.open",
            return_value=True,
        ) as opened:
            about.paypal_button.invoke()

        opened.assert_called_once()

        url = opened.call_args[0][0]

        self.assertEqual(
            url,
            "https://paypal.me/bsanecki",
        )


@unittest.skipUnless(HAVE_DISPLAY, "no display available")
class TestExit(unittest.TestCase):
    def test_exit_closes_the_application(self):
        app = new_app()
        pump(app, 0.1)
        app.show_menu()
        cancel_timers(app)

        app.menu_frame.buttons["Exit"].invoke()

        with self.assertRaises(tk.TclError):
            app.winfo_exists()
            app.update()


@unittest.skipUnless(HAVE_DISPLAY, "no display available")
class TestSettingsScreen(unittest.TestCase):
    def setUp(self):
        self.path = os.path.join(tempfile.mkdtemp(), "s.json")
        self.app = new_app(self.path)
        self.addCleanup(close_app, self.app)
        pump(self.app, 0.1)
        self.sf = self.app.settings_frame

    def test_defaults_and_only_three_settings(self):
        self.app.show_settings()

        self.assertEqual(self.sf.timeout_var.get(), "15")
        self.assertTrue(self.sf.redirects_var.get())
        self.assertTrue(self.sf.robots_var.get())

        self.assertEqual(
            sorted(vars(self.sf.store.current)),
            sorted(
                [
                    "request_timeout",
                    "follow_redirects",
                    "respect_robots",
                ]
            ),
        )

    def test_save_updates_shared_config_and_persists(self):
        self.app.show_settings()

        self.sf.timeout_var.set("30")
        self.sf.redirects_var.set(False)
        self.sf.robots_var.set(False)
        self.sf.save_button.invoke()

        cur = self.app.settings_store.current

        self.assertEqual(
            (
                cur.request_timeout,
                cur.follow_redirects,
                cur.respect_robots,
            ),
            (30, False, False),
        )

        self.assertEqual(top_frame(self.app), "menu_frame")

        from settings import SettingsStore

        self.assertEqual(SettingsStore(self.path).current, cur)

        # Both feature screens read the very same object.
        self.assertEqual(
            self.app.scanner_frame.get_settings(),
            cur,
        )
        self.assertEqual(
            self.app.single_frame.get_settings(),
            cur,
        )

    def test_cancel_discards_changes(self):
        self.app.show_settings()

        self.sf.timeout_var.set("99")
        self.sf.redirects_var.set(False)
        self.sf.robots_var.set(False)
        self.sf.cancel_button.invoke()

        self.assertEqual(
            self.app.settings_store.current.request_timeout,
            15,
        )
        self.assertEqual(top_frame(self.app), "menu_frame")

        self.app.show_settings()

        self.assertEqual(
            self.sf.timeout_var.get(),
            "15",
        )
        self.assertTrue(
            self.sf.redirects_var.get()
        )

    def test_invalid_timeout_is_rejected_inline(self):
        self.app.show_settings()

        for bad in ("abc", "0", "500", ""):
            self.sf.timeout_var.set(bad)
            self.sf.save_button.invoke()

            self.assertEqual(
                top_frame(self.app),
                "settings_frame",
                bad,
            )
            self.assertTrue(
                self.sf.message_label.cget("text"),
                bad,
            )
            self.assertEqual(
                self.app.settings_store.current.request_timeout,
                15,
            )

    def test_saved_settings_reach_a_full_scan(self):
        site = Site({
            "/": html('<a href="/old">o</a>'),
            "/old": redirect(301, "/new"),
            "/new": html("n"),
        })

        self.addCleanup(site.close)

        self.app.settings_store.save(
            __import__("settings").AppSettings(15, False, True)
        )

        sc = self.app.scanner_frame
        sc.url_entry.insert(0, site.url("/"))

        with mock.patch.object(messagebox, "showinfo"):
            sc.start_scan()

            self.assertEqual(
                sc.engine.config.follow_redirects,
                False,
            )

            self.assertTrue(
                wait_for(self.app, lambda: sc.finished)
            )

        self.assertEqual(
            site.count("/new"),
            0,
        )

        self.assertEqual(
            top_frame(self.app),
            "report_frame",
        )


@unittest.skipUnless(HAVE_DISPLAY, "no display available")
class TestSingleLinkScreen(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = new_app()

        cls.site = Site({
            "/ok": html("fine"),
            "/old": redirect(301, "/ok"),
            "/gone": status_route(404),
            "/slow": lambda h, m: (
                time.sleep(1.5),
                h.reply(200, b"ok"),
            )[1],
        })

        cls.frame = cls.app.single_frame
        cls.app.show_single_check()
        pump(cls.app, 0.1)

    @classmethod
    def tearDownClass(cls):
        cls.site.close()
        close_app(cls.app)

    def run_check(self, url):
        f = self.frame

        f.url_entry.delete(0, "end")
        f.url_entry.insert(0, url)
        f.check_button.invoke()

        self.assertTrue(
            wait_for(self.app, lambda: not f.checking, 30)
        )

        return {
            k: v.get("1.0", "end").strip()
            for k, v in f.values.items()
        }

    def test_ok_result_fields(self):
        v = self.run_check(self.site.url("/ok"))

        self.assertEqual(
            v["URL"],
            self.site.url("/ok"),
        )
        self.assertEqual(
            v["HTTP Status"],
            "200 OK",
        )
        self.assertEqual(
            v["Status Category"],
            "OK",
        )
        self.assertRegex(
            v["Response Time"],
            r"^\d+\.\d\ds$",
        )
        self.assertEqual(
            v["Final URL"],
            self.site.url("/ok"),
        )
        self.assertEqual(
            v["Redirects"],
            "None",
        )
        self.assertEqual(
            v["Details"],
            "200 OK",
        )

    def test_redirect_and_broken(self):
        v = self.run_check(self.site.url("/old"))

        self.assertEqual(
            v["Status Category"],
            "Redirect",
        )
        self.assertIn(
            "301",
            v["Redirects"],
        )

        v = self.run_check(self.site.url("/gone"))

        self.assertEqual(
            (
                v["HTTP Status"],
                v["Status Category"],
            ),
            (
                "404 Not Found",
                "Broken",
            ),
        )

    def test_invalid_urls_are_handled_gracefully(self):
        for bad in (
            "",
            "example.com",
            "http://",
            "ftp://x",
        ):
            self.frame.url_entry.delete(0, "end")
            self.frame.url_entry.insert(0, bad)
            self.frame.check_button.invoke()

            self.assertFalse(
                self.frame.checking,
                bad,
            )
            self.assertTrue(
                self.frame.status_label.cget("text"),
                bad,
            )
            self.assertEqual(
                self.frame.values["HTTP Status"]
                .get("1.0", "end")
                .strip(),
                "",
            )

    def test_request_error_is_shown_not_raised(self):
        v = self.run_check(
            "http://127.0.0.1:9/"
        )

        self.assertTrue(
            v["HTTP Status"].startswith("No response")
        )
        self.assertEqual(
            v["Status Category"],
            "Unverified",
        )
        self.assertTrue(
            v["Details"]
        )

    def test_gui_stays_responsive_during_a_slow_request(self):
        f = self.frame

        f.url_entry.delete(0, "end")
        f.url_entry.insert(0, self.site.url("/slow"))
        f.check_button.invoke()

        self.assertTrue(f.checking)
        self.assertEqual(
            str(f.check_button.cget("state")),
            "disabled",
        )

        ticks, worst, last = 0, 0.0, time.time()

        while f.checking and ticks < 5000:
            self.app.update()

            now = time.time()
            worst = max(
                worst,
                now - last,
            )
            last = now

            ticks += 1
            time.sleep(0.005)

        self.assertGreater(
            ticks,
            50,
        )
        self.assertLess(
            worst,
            0.3,
        )
        self.assertEqual(
            f.values["HTTP Status"]
            .get("1.0", "end")
            .strip(),
            "200 OK",
        )
        self.assertEqual(
            str(f.check_button.cget("state")),
            "normal",
        )


if __name__ == "__main__":
    unittest.main()
