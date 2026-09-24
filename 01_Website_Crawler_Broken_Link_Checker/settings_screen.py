"""Settings screen: request timeout, follow redirects, respect robots.txt."""

import tkinter as tk

from gui_common import BG, FG, MUTED, make_button, make_title
from settings import (
    DEFAULT_REQUEST_TIMEOUT,
    AppSettings,
    SettingsError,
    parse_timeout,
)


class SettingsFrame(tk.Frame):
    def __init__(self, parent, store, show_menu):
        super().__init__(parent, bg=BG)
        self.store = store            # the one shared SettingsStore
        self.show_menu = show_menu

        self.timeout_var = tk.StringVar()
        self.redirects_var = tk.BooleanVar()
        self.robots_var = tk.BooleanVar()

        self.build_ui()
        self.load()

    def build_ui(self):
        make_title(self, "Settings", size=30, pady=(40, 30))

        form = tk.Frame(self, bg=BG)
        form.pack()

        # 1. Request timeout
        tk.Label(
            form, text="Request timeout", font=("Arial", 14, "bold"),
            fg=FG, bg=BG, anchor="w", width=20
        ).grid(row=0, column=0, sticky="w", pady=10)
        entry_row = tk.Frame(form, bg=BG)
        entry_row.grid(row=0, column=1, sticky="w")
        self.timeout_entry = tk.Entry(
            entry_row, textvariable=self.timeout_var, width=6,
            font=("Arial", 13), justify="center")
        self.timeout_entry.pack(side="left")
        tk.Label(
            entry_row, text="seconds", font=("Arial", 12), fg=FG, bg=BG
        ).pack(side="left", padx=8)

        # 2. Follow redirects
        tk.Label(
            form, text="Follow redirects", font=("Arial", 14, "bold"),
            fg=FG, bg=BG, anchor="w", width=20
        ).grid(row=1, column=0, sticky="w", pady=10)
        self.redirects_check = self._checkbox(form, self.redirects_var, 1)

        # 3. Respect robots.txt
        tk.Label(
            form, text="Respect robots.txt", font=("Arial", 14, "bold"),
            fg=FG, bg=BG, anchor="w", width=20
        ).grid(row=2, column=0, sticky="w", pady=10)
        self.robots_check = self._checkbox(form, self.robots_var, 2)

        tk.Label(
            self,
            text=(
                f"Timeout {DEFAULT_REQUEST_TIMEOUT} s is the standard: lower "
                "= faster, higher = more patient.\n"
                "Follow redirects and timeout apply to Full Website Scan and "
                "Single Link Check.\n"
                "robots.txt applies to Full Website Scan."
            ),
            font=("Arial", 10), fg=MUTED, bg=BG, justify="center"
        ).pack(pady=(20, 5))

        self.message_label = tk.Label(
            self, text="", font=("Arial", 11, "bold"), fg="#ff5252", bg=BG)
        self.message_label.pack(pady=(5, 10))

        buttons = tk.Frame(self, bg=BG)
        buttons.pack()
        self.save_button = make_button(
            buttons, "Save", self.save, width=12, height=1)
        self.save_button.pack(side="left", padx=8)
        self.cancel_button = make_button(
            buttons, "Cancel", self.cancel, primary=False,
            width=12, height=1)
        self.cancel_button.pack(side="left", padx=8)

    @staticmethod
    def _checkbox(parent, variable, row):
        box = tk.Checkbutton(
            parent, variable=variable, bg=BG, activebackground=BG,
            fg=FG, selectcolor="#2b2b2b", activeforeground=FG,
            highlightthickness=0, bd=0)
        box.grid(row=row, column=1, sticky="w")
        return box

    # -- actions ---------------------------------------------------------------

    def load(self):
        """Show the values that are currently saved (also used by Cancel)."""
        current = self.store.current
        self.timeout_var.set(str(current.request_timeout))
        self.redirects_var.set(current.follow_redirects)
        self.robots_var.set(current.respect_robots)
        self.message_label.config(text="")

    def save(self):
        try:
            timeout = parse_timeout(self.timeout_var.get())
        except SettingsError as error:
            self.message_label.config(text=str(error), fg="#ff5252")
            return False

        saved = self.store.save(AppSettings(
            request_timeout=timeout,
            follow_redirects=bool(self.redirects_var.get()),
            respect_robots=bool(self.robots_var.get()),
        ))
        self.message_label.config(text="")
        self.show_menu()
        return saved

    def cancel(self):
        self.load()
        self.show_menu()
