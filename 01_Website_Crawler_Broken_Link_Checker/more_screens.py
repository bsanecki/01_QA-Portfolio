"""The "More" area: menu + How to Use, HTTP Status Codes and About."""

import tkinter as tk
import webbrowser
from tkinter import messagebox

import app_info
from gui_common import (
    BG, CATEGORY_COLORS, FG, MUTED, make_button, make_text_view,
    make_title,
)

# The PayPal button opens the author's PayPal.Me page.
PAYPAL_LOGIN_URL = "https://paypal.me/bsanecki"


class MoreFrame(tk.Frame):
    def __init__(self, parent, open_how_to, open_status_codes, open_about,
                 show_menu):
        super().__init__(parent, bg=BG)
        make_title(self, "More", size=28, pady=(70, 30))

        self.buttons = {}
        for text, command in (
            ("How to Use", open_how_to),
            ("HTTP Status Codes", open_status_codes),
            ("About", open_about),
        ):
            button = make_button(self, text, command, font=("Arial", 14, "bold"))
            button.pack(pady=6)
            self.buttons[text] = button

        make_button(
            self, "← MAIN MENU", show_menu, primary=False,
            width=16, height=1, font=("Arial", 11, "bold")
        ).pack(pady=(25, 0))


class _TextScreen(tk.Frame):
    """Title + read-only scrollable text + back button."""

    def __init__(self, parent, title, go_back, back_text="← BACK"):
        super().__init__(parent, bg=BG)
        make_title(self, title, size=26, pady=(25, 10))

        self.text = make_text_view(self)
        self.text.container.pack(fill="both", expand=True, padx=40, pady=(0, 10))
        self.text.tag_configure(
            "heading", font=("Arial", 13, "bold"), foreground="#6fb1ff",
            spacing1=8)
        self.text.tag_configure("body", spacing3=4, lmargin1=0, lmargin2=0)
        self.text.tag_configure("note", foreground=MUTED, spacing1=10)

        make_button(
            self, back_text, go_back, primary=False,
            width=16, height=1, font=("Arial", 11, "bold")
        ).pack(pady=(0, 20))

    def read_text(self):
        return self.text.get("1.0", "end").strip()

    def _fill(self, writer):
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        writer(self.text)
        self.text.configure(state="disabled")


class HowToUseFrame(_TextScreen):
    def __init__(self, parent, go_back):
        super().__init__(parent, "How to Use", go_back)
        self._fill(self._write)

    @staticmethod
    def _write(text):
        for heading, body in app_info.HOW_TO_USE:
            text.insert("end", heading + "\n", "heading")
            text.insert("end", body + "\n\n", "body")


class StatusCodesFrame(_TextScreen):
    def __init__(self, parent, go_back):
        super().__init__(parent, "HTTP Status Codes", go_back)
        for category, color in CATEGORY_COLORS.items():
            self.text.tag_configure(f"cat_{category}", foreground=color)
        self.rows = app_info.status_code_reference()
        self._fill(self._write)

    def _write(self, text):
        for row in self.rows:
            text.insert("end", f"{row.code}  {row.name}", "heading")
            text.insert(
                "end", f"   [{row.category_label}]\n", f"cat_{row.category}")
            text.insert("end", row.text + "\n\n", "body")
        text.insert("end", app_info.STATUS_NOTE + "\n", "note")


class AboutFrame(tk.Frame):
    def __init__(self, parent, go_back, paypal_url=None):
        super().__init__(parent, bg=BG)
        self.paypal_url = PAYPAL_LOGIN_URL if paypal_url is None else paypal_url

        make_title(self, app_info.APP_NAME, size=24, pady=(35, 10))

        tk.Label(
            self, text="Developed by:", font=("Arial", 12), fg=MUTED, bg=BG
        ).pack()

        self.author_label = tk.Label(
            self, text=app_info.AUTHOR_NAME, font=("Arial", 15, "bold"),
            fg=FG, bg=BG
        )
        self.author_label.pack(pady=(0, 15))

        tk.Label(
            self, text=app_info.ABOUT_DESCRIPTION, font=("Arial", 12),
            fg=FG, bg=BG, justify="center"
        ).pack(pady=(0, 15))

        tk.Label(
            self, text="Technologies", font=("Arial", 13, "bold"),
            fg=FG, bg=BG
        ).pack()

        tk.Label(
            self, text="  •  ".join(app_info.TECHNOLOGIES),
            font=("Arial", 12), fg=MUTED, bg=BG
        ).pack(pady=(2, 20))

        tk.Label(
            self, text="Support the Developer", font=("Arial", 14, "bold"),
            fg=FG, bg=BG
        ).pack()

        tk.Label(
            self, text=app_info.SUPPORT_TEXT, font=("Arial", 11), fg=MUTED,
            bg=BG, wraplength=560, justify="center"
        ).pack(pady=(4, 10))

        self.paypal_button = make_button(
            self,
            "Support via PayPal",
            self.open_paypal,
            width=22,
            height=1,
            font=("Arial", 13, "bold")
        )
        self.paypal_button.pack(pady=(0, 20))

        make_button(
            self, "← BACK", go_back, primary=False,
            width=16, height=1, font=("Arial", 11, "bold")
        ).pack(pady=(0, 15))

    def open_paypal(self):
        """Open the author's PayPal.Me page in the default browser."""
        try:
            return bool(webbrowser.open(self.paypal_url))
        except Exception:
            messagebox.showwarning(
                "Could not open browser",
                "Please open the PayPal support link manually:\n"
                f"{self.paypal_url}"
            )
            return False