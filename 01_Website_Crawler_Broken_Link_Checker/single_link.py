"""Single Link Check.

The request is made by the existing link_checker.check_link() and classified
by the existing LinkResult / describe_result(), so a URL gets exactly the same
category here as in a Full Website Scan. The network call runs in a worker
thread; the Tk main loop only polls a queue.
"""

import queue
import threading
import tkinter as tk

from app_info import CATEGORY_LABELS
from gui_common import (
    BG, CATEGORY_COLORS, FG, FIELD_BG, MUTED, make_button, make_title,
)
from link_checker import ThreadSessions, check_link
from models import LINK_RETRY_TIMEOUT, LINK_TIMEOUT, DiscoveredLink, describe_result
from settings import AppSettings, scale_timeout
from utils import host_key, normalize_url

FIELDS = (
    "URL", "HTTP Status", "Status Category", "Response Time",
    "Final URL", "Redirects", "Details",
)


def prepare_url(text):
    """Validate what the user typed. Returns the normalized URL or raises
    ValueError with a message that can be shown as it is."""
    url = (text or "").strip()
    if not url:
        raise ValueError("Enter a URL first.")
    if not url.lower().startswith(("http://", "https://")):
        raise ValueError("URL must start with http:// or https://")
    try:
        url = normalize_url(url)
    except ValueError:
        raise ValueError("This is not a valid URL.") from None
    if not host_key(url):
        raise ValueError("The URL has no host name.")
    return url


def check_single_link(url, settings=None, stop_event=None):
    """Check one URL with the shared HTTP core. Returns a LinkResult (or None
    if stop_event was set). Never raises for network problems: those come
    back as a result with status None."""
    settings = settings or AppSettings()
    sessions = ThreadSessions()
    try:
        return check_link(
            sessions.get(),
            url,
            timeout=scale_timeout(LINK_TIMEOUT, settings.timeout_scale),
            retry_timeout=scale_timeout(
                LINK_RETRY_TIMEOUT, settings.timeout_scale),
            stop_event=stop_event,
            follow_redirects=settings.follow_redirects,
        )
    finally:
        sessions.close_all()


def summarize_result(result):
    """Display rows for a LinkResult: {"rows": [(label, value)], "category"}."""
    link = DiscoveredLink(
        url=result.url, source_url="(single link check)", source_text="")
    row = describe_result(link, result)

    if result.status is not None:
        status = result.status_text
    else:
        status = f"No response ({result.error_type or 'ERROR'})"

    hops = len(result.redirect_history)
    if hops:
        redirects = (
            f"{hops} redirect{'s' if hops != 1 else ''}: "
            f"{result.redirect_chain_text}"
        )
    elif result.status is not None and 300 <= result.status < 400:
        redirects = "Redirect response (not followed)"
    else:
        redirects = "None"

    values = {
        "URL": result.url,
        "HTTP Status": status,
        "Status Category": CATEGORY_LABELS[result.category],
        "Response Time": row["response_time"],
        "Final URL": result.final_url,
        "Redirects": redirects,
        "Details": row["details"],
    }
    return {
        "rows": [(label, values[label]) for label in FIELDS],
        "category": result.category,
    }


class SingleLinkFrame(tk.Frame):
    POLL_MS = 100

    def __init__(self, parent, show_menu, get_settings):
        super().__init__(parent, bg=BG)
        self.show_menu = show_menu
        self.get_settings = get_settings   # -> AppSettings (shared config)

        self.checking = False
        self._queue = queue.Queue()
        self._stop = threading.Event()
        self.last_result = None
        self.values = {}

        self.build_ui()

    # -- GUI ---------------------------------------------------------------

    def build_ui(self):
        # Packed first so it always keeps its place at the bottom.
        make_button(
            self, "← MAIN MENU", self.show_menu, primary=False,
            width=16, height=1, font=("Arial", 11, "bold")
        ).pack(side="bottom", pady=(0, 20))

        make_title(self, "Single Link Check", size=30, pady=(25, 15))

        tk.Label(
            self, text="URL", font=("Arial", 16, "bold"), fg=FG, bg=BG
        ).pack()

        self.url_entry = tk.Entry(self, width=70, font=("Arial", 13))
        self.url_entry.pack(pady=(5, 2))
        self.url_entry.bind("<Return>", lambda _event: self.start_check())

        tk.Label(
            self, text="e.g. https://example.com",
            font=("Arial", 10), fg=MUTED, bg=BG
        ).pack(pady=(0, 8))

        self.check_button = make_button(
            self, "CHECK", self.start_check,
            width=14, font=("Arial", 16, "bold"))
        self.check_button.pack(pady=5)

        self.status_label = tk.Label(
            self, text="", font=("Arial", 12), fg=MUTED, bg=BG,
            wraplength=800)
        self.status_label.pack(pady=(8, 8))

        grid = tk.Frame(self, bg=BG)
        grid.pack(padx=40, pady=5, fill="x")
        grid.grid_columnconfigure(1, weight=1)

        for index, label in enumerate(FIELDS):
            tk.Label(
                grid, text=f"{label}:", font=("Arial", 12, "bold"),
                fg=FG, bg=BG, anchor="ne", width=15
            ).grid(row=index, column=0, sticky="ne", padx=(0, 10), pady=3)

            height = 3 if label in ("Redirects", "Details") else 1
            value = tk.Text(
                grid, height=height, wrap="word", font=("Arial", 12),
                bg=FIELD_BG, fg=FG, relief="flat", bd=0, padx=8, pady=4,
                highlightthickness=0, cursor="arrow")
            value.grid(row=index, column=1, sticky="ew", pady=3)
            value.configure(state="disabled")
            self.values[label] = value

    def _set_value(self, label, text, color=FG):
        widget = self.values[label]
        widget.configure(state="normal", fg=color)
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.configure(state="disabled")

    def clear_result(self):
        for label in FIELDS:
            self._set_value(label, "")

    # -- checking ------------------------------------------------------------

    def start_check(self):
        if self.checking:
            return
        try:
            url = prepare_url(self.url_entry.get())
        except ValueError as error:
            self.clear_result()
            self.status_label.config(text=str(error), fg="#ff5252")
            return

        self.checking = True
        self._stop.clear()
        self.clear_result()
        self.check_button.config(state="disabled")
        self.status_label.config(text="Checking...", fg=MUTED)

        settings = self.get_settings()    # snapshot for this check
        threading.Thread(
            target=self._worker, args=(url, settings),
            name="single-link-check", daemon=True).start()
        self.after(self.POLL_MS, self._poll)

    def _worker(self, url, settings):
        try:
            self._queue.put(
                ("result", check_single_link(url, settings, self._stop)))
        except Exception as error:   # safety net: never leave the GUI waiting
            self._queue.put(("error", f"{type(error).__name__}: {error}"))

    def _poll(self):
        try:
            kind, payload = self._queue.get_nowait()
        except queue.Empty:
            if self.checking:
                self.after(self.POLL_MS, self._poll)
            return
        self.checking = False
        self.check_button.config(state="normal")

        if kind == "result" and payload is not None:
            self.show_result(payload)
        elif kind == "error":
            self.status_label.config(
                text=f"Check failed: {payload}", fg="#ff5252")
        else:
            self.status_label.config(text="", fg=MUTED)

    def show_result(self, result):
        self.last_result = result
        summary = summarize_result(result)
        color = CATEGORY_COLORS.get(summary["category"], FG)
        for label, value in summary["rows"]:
            self._set_value(
                label, value,
                color if label in ("HTTP Status", "Status Category") else FG)
        self.status_label.config(text="Check completed", fg=MUTED)

    def shutdown(self):
        """Called when the application closes."""
        self._stop.set()
