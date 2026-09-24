"""Report tables: scrollbars (vertical + horizontal) and easy Copy URL.
Needs a display (Linux: xvfb-run -a python3 -m unittest tests.test_report_table);
skipped automatically without one."""

import tkinter as tk
import unittest
from tkinter import ttk
from unittest import mock

from models import DiscoveredLink, LinkResult
from tests.test_gui_screens import HAVE_DISPLAY, _APPS, pump

N = 120


def sample_results():
    results = []
    for i in range(N):
        url = f"https://target.example/item/{i}"
        link = DiscoveredLink(
            url=url, source_url=f"https://source.example/page/{i}",
            source_text=f"link text {i}", source_type="link")
        status = 404 if i % 3 == 0 else 200
        results.append((link, LinkResult(url, status, url, 0.12)))
    return results


@unittest.skipUnless(HAVE_DISPLAY, "no display available")
class TestReportTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from report import ScanReportFrame
        cls.root = tk.Tk()
        _APPS.append(cls.root)          # keep alive (see test_gui_screens)
        cls.root.geometry("1100x750+0+0")
        cls.report = ScanReportFrame(cls.root, back_to_scanner=lambda: None)
        cls.report.pack(fill="both", expand=True)
        cls.report.load_report("https://target.example/", 5, 3, sample_results())
        pump(cls.root, 0.3)
        cls.tree = max(cls.report.copy_bars, key=lambda t: len(t.get_children()))
        while len(cls.tree.get_children()) < N:
            pump(cls.root, 0.1)
        # the "All Links" tab is not the selected one: select it so it is mapped
        notebook = [w for w in cls.report.winfo_children()
                    if isinstance(w, ttk.Notebook)][0]
        notebook.select(len(notebook.tabs()) - 1)
        pump(cls.root, 0.3)

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def scrollbars(self):
        frame = self.tree.master
        return {str(w.cget("orient")): w for w in frame.winfo_children()
                if isinstance(w, ttk.Scrollbar)}

    def click_row(self, index, button=1):
        item = self.tree.get_children()[index]
        self.tree.see(item)
        pump(self.root, 0.1)
        x, y, w, h = self.tree.bbox(item, "status")
        self.tree.event_generate(f"<Button-{button}>", x=x + 5, y=y + h // 2)
        pump(self.root, 0.1)
        return item

    # -- scrolling -----------------------------------------------------------

    def test_both_scrollbars_exist_and_are_visible(self):
        bars = self.scrollbars()
        self.assertEqual(set(bars), {"vertical", "horizontal"})
        h, v = bars["horizontal"], bars["vertical"]
        self.assertTrue(h.winfo_ismapped() and v.winfo_ismapped())
        self.assertGreater(h.winfo_height(), 5)                 # really shown
        # horizontal bar sits at the bottom of the table, under the tree
        self.assertGreaterEqual(h.winfo_rooty(),
                                self.tree.winfo_rooty() + self.tree.winfo_height())
        # the table keeps its window size instead of stretching to the columns
        total = sum(int(self.tree.column(c, "width")) for c in self.tree["columns"])
        self.assertGreater(total, self.tree.winfo_width())
        self.assertLess(self.tree.winfo_width(), self.root.winfo_width())

    def test_all_columns_reachable_by_horizontal_scrolling(self):
        self.assertEqual(
            [self.tree.heading(c, "text") for c in self.tree["columns"]],
            ["Status", "URL", "Source Page", "Source Type", "Link Text",
             "Final URL", "Response Time", "Details"])
        self.tree.xview_moveto(0)
        pump(self.root, 0.1)
        first, last = self.tree.xview()
        self.assertEqual(first, 0.0)
        self.assertLess(last, 1.0)                              # cut off on the right
        bar = self.scrollbars()["horizontal"]
        self.tree.xview_moveto(1.0)                             # what dragging does
        pump(self.root, 0.1)
        self.assertEqual(self.tree.xview()[1], 1.0)             # "Details" reached
        self.assertGreater(self.tree.xview()[0], 0.0)
        self.assertEqual(bar.get()[1], 1.0)                     # bar follows
        self.tree.xview_moveto(0)

    def test_scrollbar_commands_drive_the_table(self):
        bar = self.scrollbars()["horizontal"]
        self.tree.xview_moveto(0)
        self.root.tk.call(str(bar.cget("command")), "scroll", 1, "pages")
        pump(self.root, 0.1)
        self.assertGreater(self.tree.xview()[0], 0.0)
        self.tree.xview_moveto(0)

    def test_shift_wheel_scrolls_sideways_and_wheel_stays_vertical(self):
        self.tree.xview_moveto(0)
        self.tree.yview_moveto(0)
        pump(self.root, 0.1)
        self.tree.event_generate("<Shift-Button-5>", x=50, y=50)
        pump(self.root, 0.1)
        self.assertGreater(self.tree.xview()[0], 0.0)           # moved right
        self.assertEqual(self.tree.yview()[0], 0.0)             # not down
        self.tree.event_generate("<Shift-Button-4>", x=50, y=50)
        pump(self.root, 0.1)
        self.assertEqual(self.tree.xview()[0], 0.0)             # and back
        self.tree.event_generate("<Button-5>", x=50, y=50)      # plain wheel
        pump(self.root, 0.1)
        self.assertGreater(self.tree.yview()[0], 0.0)           # vertical still works

    def test_vertical_scrolling_and_bar(self):
        self.tree.yview_moveto(0)
        pump(self.root, 0.1)
        self.assertLess(self.tree.yview()[1], 1.0)
        self.tree.yview_moveto(1.0)
        pump(self.root, 0.1)
        self.assertEqual(self.tree.yview()[1], 1.0)
        self.assertEqual(self.scrollbars()["vertical"].get()[1], 1.0)
        self.tree.yview_moveto(0)

    # -- copy URL ------------------------------------------------------------

    def test_left_click_selects_row_and_enables_copy_url(self):
        button, info = self.report.copy_bars[self.tree]
        item = self.click_row(4)
        self.assertEqual(self.tree.selection(), (item,))
        self.assertEqual(str(button.cget("state")), "normal")
        values = self.tree.item(item, "values")
        self.assertIn(values[1], info.cget("text"))
        button.invoke()
        self.assertEqual(self.root.clipboard_get(), values[1])
        self.assertTrue(values[1].startswith("https://target.example/item/"))
        self.assertNotIn("source.example", self.root.clipboard_get())
        self.assertIn("Copied", info.cget("text"))

    def test_right_click_offers_copy_url(self):
        menu = self.report.url_context_menu
        self.assertEqual(menu.entrycget(0, "label"), "Copy URL")
        with mock.patch.object(menu, "tk_popup") as popup:
            item = self.click_row(7, button=3)
        popup.assert_called_once()
        self.assertEqual(self.tree.selection(), (item,))        # row got selected
        menu.invoke(0)                                          # choose "Copy URL"
        expected = self.tree.item(item, "values")[1]
        self.assertEqual(self.root.clipboard_get(), expected)
        self.assertEqual(expected, "https://target.example/item/7")

    def test_ctrl_c_still_copies_the_url(self):
        item = self.click_row(9)
        self.tree.focus_force()
        self.tree.event_generate("<Control-c>")
        pump(self.root, 0.1)
        self.assertEqual(self.root.clipboard_get(),
                         self.tree.item(item, "values")[1])

    def test_copy_uses_the_url_column_not_the_source_page(self):
        item = self.click_row(3)
        values = self.tree.item(item, "values")
        self.assertEqual(self.report.URL_COLUMN, list(self.tree["columns"]).index("url"))
        self.assertEqual(self.report.selected_url(self.tree), values[1])
        self.assertNotEqual(values[1], values[2])               # url != source page


if __name__ == "__main__":
    unittest.main()
