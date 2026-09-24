import queue
import time
import tkinter as tk
from tkinter import messagebox, ttk

from browser_crawler import check_browser
from models import CRAWL_MODES, DEFAULT_CRAWL_MODE, describe_result
from scan_engine import (
    CRAWL_MODE_AUTO,
    CRAWL_MODE_BROWSER,
    CRAWL_MODE_HTTP,
    ScanConfig,
    ScanEngine,
)
from settings import AppSettings
from utils import format_time


def mode_for_label(label):
    """Crawl-mode selector label -> (engine crawl_mode, browser id)."""
    if label == "HTTP":
        return CRAWL_MODE_HTTP, "chromium"
    if label == "Auto":
        return CRAWL_MODE_AUTO, "chromium"
    return CRAWL_MODE_BROWSER, label.lower()


class FullScannerFrame(tk.Frame):
    """GUI for a full-site scan.

    Everything that touches the network runs inside ScanEngine's threads.
    This class only (a) starts/stops the engine, (b) drains its event queue
    and (c) polls engine.snapshot() a few times per second, so the Tk main
    loop is never blocked.
    """

    EVENTS_PER_TICK = 400        # upper bound of events handled per tick
    TICK_BUDGET_SECONDS = 0.04   # ...and of time spent in one tick
    LIVE_TABLE_MAX_ROWS = 5000   # live view only; the report keeps everything

    def __init__(self, parent, show_report, show_menu, get_settings=None):
        super().__init__(parent, bg="#1e1e1e")
        self.show_report = show_report
        self.show_menu = show_menu
        # Shared Settings (timeout / redirects / robots.txt), read per scan.
        self.get_settings = get_settings or AppSettings

        self.event_queue = queue.Queue()
        self.engine = None
        self.scanning = False
        self.stop_requested = False
        self.finished = False
        self.results = []
        self.max_depth = 5
        self.crawl_mode_label = DEFAULT_CRAWL_MODE
        self.notice = ""

        self.build_ui()
        self.process_events()

    # ---------------------------------------------------------
    # GUI
    # ---------------------------------------------------------

    def build_ui(self):
        tk.Label(
            self,
            text="Full Website Scan",
            font=("Arial", 30, "bold"),
            fg="white",
            bg="#1e1e1e"
        ).pack(pady=(25, 15))

        tk.Label(
            self,
            text="Website URL",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#1e1e1e"
        ).pack()

        self.url_entry = tk.Entry(
            self,
            width=75,
            font=("Arial", 13)
        )
        self.url_entry.pack(pady=5)

        depth_frame = tk.Frame(self, bg="#1e1e1e")
        depth_frame.pack(pady=(5, 8))

        tk.Label(
            depth_frame,
            text="Crawl depth",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#1e1e1e"
        ).pack(side="left", padx=(0, 8))

        self.depth_var = tk.StringVar(value="5")
        self.depth_combo = ttk.Combobox(
            depth_frame,
            textvariable=self.depth_var,
            values=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Unlimited"],
            state="readonly",
            width=12
        )
        self.depth_combo.pack(side="left")

        tk.Label(
            depth_frame,
            text="(0 = only start page)",
            font=("Arial", 10),
            fg="#aaaaaa",
            bg="#1e1e1e"
        ).pack(side="left", padx=8)

        tk.Label(
            depth_frame,
            text="Crawl mode",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#1e1e1e"
        ).pack(side="left", padx=(20, 8))

        self.mode_var = tk.StringVar(value=DEFAULT_CRAWL_MODE)
        self.mode_combo = ttk.Combobox(
            depth_frame,
            textvariable=self.mode_var,
            values=list(CRAWL_MODES),
            state="readonly",
            width=12
        )
        self.mode_combo.pack(side="left")

        self.button_frame = tk.Frame(
            self,
            bg="#1e1e1e"
        )
        self.button_frame.pack(pady=10)

        self.start_button = tk.Button(
            self.button_frame,
            text="START SCAN",
            font=("Arial", 16, "bold"),
            bg="#2d8cf0",
            fg="white",
            width=14,
            height=2,
            command=self.start_scan
        )
        self.start_button.pack(side="left", padx=5)

        self.stop_button = tk.Button(
            self.button_frame,
            text="STOP",
            font=("Arial", 16, "bold"),
            bg="#444444",
            fg="white",
            width=14,
            height=2,
            command=self.stop_scan
        )
        self.stop_button.pack(side="left", padx=5)
        self.stop_button.pack_forget()

        self.status_label = tk.Label(
            self,
            text="Status: Ready",
            font=("Arial", 14, "bold"),
            fg="white",
            bg="#1e1e1e"
        )
        self.status_label.pack(pady=5)

        self.stats_label = tk.Label(
            self,
            text=self.format_stats(None),
            font=("Arial", 12),
            fg="white",
            bg="#1e1e1e",
            justify="center"
        )
        self.stats_label.pack(pady=5)

        self.now_label = tk.Label(
            self,
            text="",
            font=("Arial", 10),
            fg="#aaaaaa",
            bg="#1e1e1e",
            wraplength=1000
        )
        self.now_label.pack(pady=(0, 2))

        self.time_label = tk.Label(
            self,
            text="Elapsed: 0s | Estimated: 0s",
            font=("Arial", 12),
            fg="white",
            bg="#1e1e1e"
        )
        self.time_label.pack(pady=5)

        table_frame = tk.Frame(
            self,
            bg="#1e1e1e"
        )
        table_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=15
        )

        columns = (
            "status",
            "url",
            "source",
            "details"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        self.tree.heading("status", text="Status")
        self.tree.heading("url", text="URL")
        self.tree.heading("source", text="Source link text")
        self.tree.heading("details", text="Details")

        self.tree.column("status", width=130, anchor="center")
        self.tree.column("url", width=450)
        self.tree.column("source", width=220)
        self.tree.column("details", width=220)

        self.tree.tag_configure("ok", foreground="green")
        self.tree.tag_configure("redirect", foreground="orange")
        self.tree.tag_configure("error", foreground="red")

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        tk.Button(
            self,
            text="← MAIN MENU",
            font=("Arial", 11, "bold"),
            bg="#444444",
            fg="white",
            width=16,
            command=self.open_main_menu
        ).pack(pady=(0, 15))

    # ---------------------------------------------------------
    # START
    # ---------------------------------------------------------

    def start_scan(self):
        if self.scanning:
            return

        url = self.url_entry.get().strip()

        if not url:
            messagebox.showwarning(
                "Missing URL",
                "Enter a website URL first."
            )
            return

        if not url.startswith(("http://", "https://")):
            messagebox.showwarning(
                "Invalid URL",
                "URL must start with http:// or https://"
            )
            return

        depth_value = self.depth_var.get()
        self.max_depth = None if depth_value == "Unlimited" else int(depth_value)

        self.crawl_mode_label = self.mode_var.get()
        crawl_mode, browser = mode_for_label(self.crawl_mode_label)

        if crawl_mode == CRAWL_MODE_BROWSER:
            check = check_browser(browser)
            if not check.ok:
                proceed = messagebox.askyesno(
                    f"{check.label} not available",
                    f"{check.message}\n\n"
                    "Continue with the normal HTTP crawler instead?"
                )
                if not proceed:
                    return
                crawl_mode = CRAWL_MODE_HTTP
                self.crawl_mode_label = "HTTP"

        settings = self.get_settings()

        try:
            engine = ScanEngine(
                ScanConfig(
                    start_url=url,
                    max_depth=self.max_depth,
                    crawl_mode=crawl_mode,
                    browser=browser,
                    request_timeout=settings.request_timeout,
                    follow_redirects=settings.follow_redirects,
                    respect_robots=settings.respect_robots,
                ),
                events=queue.Queue(),
            )
        except ValueError as error:
            messagebox.showwarning("Invalid URL", str(error))
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.results = []
        self.notice = ""
        self.scanning = True
        self.stop_requested = False
        self.finished = False
        self.engine = engine
        self.event_queue = engine.events

        self.start_button.pack_forget()
        self.stop_button.pack(side="left", padx=5)

        self.status_label.config(
            text="Status: Scanning..."
        )
        self.now_label.config(text="")

        engine.start()

    # ---------------------------------------------------------
    # STOP
    # ---------------------------------------------------------

    def stop_scan(self):
        if not self.scanning or self.engine is None:
            return

        self.stop_requested = True
        self.engine.stop()
        self.stop_button.config(state="disabled")
        self.status_label.config(text="Status: Stopping...")

    def shutdown(self):
        """Called when the application window is closed."""
        if self.engine is not None and self.scanning:
            self.engine.stop()

    # ---------------------------------------------------------
    # EVENT LOOP
    # ---------------------------------------------------------

    def process_events(self):
        handled = 0
        inserted = False
        deadline = time.monotonic() + self.TICK_BUDGET_SECONDS

        while handled < self.EVENTS_PER_TICK and time.monotonic() < deadline:
            try:
                event = self.event_queue.get_nowait()
            except queue.Empty:
                break
            handled += 1
            event_type = event[0]

            if event_type == "result":
                link, result = event[1], event[2]
                self.results.append((link, result))
                row = describe_result(link, result)
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        row["status"],
                        row["url"],
                        row["link_text"],
                        row["details"]
                    ),
                    tags=(row["tag"],)
                )
                inserted = True

            elif event_type == "notice":
                self.notice = event[1]

            elif event_type == "finished":
                self.finish_scan(bool(event[1]))

            elif event_type == "fatal_error":
                messagebox.showerror(
                    "Scanner Error",
                    event[1]
                )

        if inserted:
            self.trim_live_table()
            self.tree.yview_moveto(1)

        self.update_stats()

        delay = 30 if not self.event_queue.empty() else 100
        self.after(delay, self.process_events)

    def trim_live_table(self):
        children = self.tree.get_children()
        excess = len(children) - self.LIVE_TABLE_MAX_ROWS
        if excess > 0:
            self.tree.delete(*children[:excess])

    # ---------------------------------------------------------
    # STATS  (real queue/worker state, read from the engine)
    # ---------------------------------------------------------

    @staticmethod
    def format_stats(snapshot):
        s = snapshot or {}
        return (
            f"Pages scanned: {s.get('pages_scanned', 0)}     "
            f"Pages queued: {s.get('pages_queued', 0)}     "
            f"Links discovered: {s.get('links_discovered', 0)}     "
            f"Links checked: {s.get('links_checked', 0)}/{s.get('links_discovered', 0)}\n"
            f"OK: {s.get('ok', 0)}     "
            f"Redirects: {s.get('redirects', 0)}     "
            f"Broken: {s.get('broken', 0)}     "
            f"Unverified: {s.get('unverified', 0)}"
        )

    def update_stats(self):
        engine = self.engine
        if engine is None or not self.scanning:
            return

        snapshot = engine.snapshot()
        self.stats_label.config(text=self.format_stats(snapshot))

        if self.stop_requested:
            self.status_label.config(text="Status: Stopping...")
        else:
            checked = snapshot["links_checked"]
            total = snapshot["links_discovered"]
            self.status_label.config(
                text=f"Status: Scanning... (checked {checked}/{total})"
            )

        current = snapshot["current_pages"]
        if self.notice:
            now_text = f"ℹ {self.notice}"
        elif current:
            extra = f"  (+{len(current) - 1} more)" if len(current) > 1 else ""
            now_text = f"Now scanning: {current[0]}{extra}"
        else:
            now_text = ""
        self.now_label.config(text=now_text)

        estimated = snapshot["estimated"]
        if estimated is None:
            estimated_text = "Estimating..."
        else:
            estimated_text = f"~{format_time(estimated)} (may grow while new pages are found)"

        self.time_label.config(
            text=(
                f"Elapsed: {format_time(snapshot['elapsed'])} "
                f"| Estimated: {estimated_text}"
            )
        )

    # ---------------------------------------------------------
    # FINISH
    # ---------------------------------------------------------

    def finish_scan(self, stopped):
        if self.finished:
            return

        self.finished = True
        self.scanning = False

        engine = self.engine
        snapshot = engine.snapshot() if engine else {}
        elapsed = snapshot.get("elapsed", 0)

        self.stats_label.config(text=self.format_stats(snapshot))
        self.now_label.config(text="")

        # STOP disappears once the scan is over
        self.stop_button.pack_forget()
        self.stop_button.config(state="normal")

        if stopped:
            self.start_button.pack(side="left", padx=5)
            self.status_label.config(text="Status: Scan stopped")
            self.time_label.config(
                text=f"Elapsed: {format_time(elapsed)}"
            )
            return

        self.status_label.config(text="Status: Scan completed")
        self.time_label.config(
            text=f"Elapsed: {format_time(elapsed)} | Estimated: 0s"
        )

        self.show_report(
            self.url_entry.get().strip(),
            elapsed,
            snapshot.get("pages_scanned", 0),
            engine.results,
            {
                "Crawl depth": (
                    "Unlimited" if self.max_depth is None else str(self.max_depth)
                ),
                "Crawl mode": (
                    f"Auto ({engine.browser_label})"
                    if self.crawl_mode_label == "Auto" and engine.browser_label
                    else self.crawl_mode_label
                ),
            },
        )

    # ---------------------------------------------------------
    # BACK FROM REPORT
    # ---------------------------------------------------------

    def reset_after_report(self):
        self.scanning = False
        self.stop_requested = False
        self.finished = False
        self.engine = None
        self.results = []
        self.notice = ""
        self.event_queue = queue.Queue()

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.status_label.config(text="Status: Ready")
        self.stats_label.config(text=self.format_stats(None))
        self.now_label.config(text="")
        self.time_label.config(text="Elapsed: 0s | Estimated: 0s")

        self.stop_button.pack_forget()
        self.start_button.pack(side="left", padx=5)

    def open_main_menu(self):
        if self.scanning:
            return

        self.show_menu()

    @staticmethod
    def format_time(seconds):
        return format_time(seconds)
