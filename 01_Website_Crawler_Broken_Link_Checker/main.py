import tkinter as tk

from full_scanner import FullScannerFrame
from gui_common import make_button
from more_screens import AboutFrame, HowToUseFrame, MoreFrame, StatusCodesFrame
from report import ScanReportFrame
from settings import SettingsStore
from settings_screen import SettingsFrame
from single_link import SingleLinkFrame


class WebsiteCrawlerApp(tk.Tk):
    def __init__(self, settings_path=None):
        super().__init__()

        self.title("Website Crawler & Broken Link Checker")
        self.configure(bg="#1e1e1e")
        self.resizable(True, True)

        container = tk.Frame(self, bg="#1e1e1e")
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # One shared configuration for Full Website Scan and Single Link Check.
        self.settings_store = SettingsStore(settings_path)

        self.menu_frame = MainMenuFrame(
            container,
            open_full_scanner=self.show_scanner,
            open_single_check=self.show_single_check,
            open_settings=self.show_settings,
            open_more=self.show_more,
            exit_app=self.on_close,
        )
        self.scanner_frame = FullScannerFrame(
            container,
            show_report=self.show_report,
            show_menu=self.show_menu,
            get_settings=lambda: self.settings_store.current
        )
        self.report_frame = ScanReportFrame(
            container,
            back_to_scanner=self.back_to_scanner
        )
        self.single_frame = SingleLinkFrame(
            container,
            show_menu=self.show_menu,
            get_settings=lambda: self.settings_store.current
        )
        self.settings_frame = SettingsFrame(
            container,
            store=self.settings_store,
            show_menu=self.show_menu
        )
        self.more_frame = MoreFrame(
            container,
            open_how_to=self.show_how_to,
            open_status_codes=self.show_status_codes,
            open_about=self.show_about,
            show_menu=self.show_menu
        )
        self.how_to_frame = HowToUseFrame(container, go_back=self.show_more)
        self.status_frame = StatusCodesFrame(container, go_back=self.show_more)
        self.about_frame = AboutFrame(container, go_back=self.show_more)

        for frame in (
            self.menu_frame,
            self.scanner_frame,
            self.report_frame,
            self.single_frame,
            self.settings_frame,
            self.more_frame,
            self.how_to_frame,
            self.status_frame,
            self.about_frame
        ):
            frame.grid(row=0, column=0, sticky="nsew")

        # Stop a running scan (and its worker threads) when the window closes.
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.show_menu()          # the application opens on the Main Menu

    def on_close(self):
        """Window close and the Exit button."""
        self.scanner_frame.shutdown()
        self.single_frame.shutdown()
        self.destroy()

    def show_menu(self):
        self.geometry("800x500")
        self.menu_frame.tkraise()

    def show_scanner(self):
        self.geometry("1100x750")
        self.scanner_frame.tkraise()

    def show_report(self, website_url, elapsed, pages_scanned, results,
                    scan_info=None):
        self.report_frame.load_report(
            website_url,
            elapsed,
            pages_scanned,
            results,
            scan_info
        )
        self.geometry("1100x750")
        self.report_frame.tkraise()

    def back_to_scanner(self):
        self.scanner_frame.reset_after_report()
        self.show_scanner()

    def show_single_check(self):
        self.geometry("900x680")
        self.single_frame.tkraise()

    def show_settings(self):
        self.settings_frame.load()      # always show the saved values
        self.geometry("800x560")
        self.settings_frame.tkraise()

    def show_more(self):
        self.geometry("800x500")
        self.more_frame.tkraise()

    def show_how_to(self):
        self.geometry("900x700")
        self.how_to_frame.tkraise()

    def show_status_codes(self):
        self.geometry("900x700")
        self.status_frame.tkraise()

    def show_about(self):
        self.geometry("800x520")
        self.about_frame.tkraise()


class MainMenuFrame(tk.Frame):
    def __init__(self, parent, open_full_scanner, open_single_check,
                 open_settings, open_more, exit_app):
        super().__init__(parent, bg="#1e1e1e")

        tk.Label(
            self,
            text="What would you like to do?",
            font=("Arial", 22, "bold"),
            fg="white",
            bg="#1e1e1e"
        ).pack(pady=(45, 25))

        self.buttons = {}
        for text, command, primary in (
            ("Full Website Scan", open_full_scanner, True),
            ("Single Link Check", open_single_check, True),
            ("Settings", open_settings, True),
            ("More", open_more, True),
            ("Exit", exit_app, False),
        ):
            button = make_button(
                self,
                text,
                command,
                primary=primary,
                font=("Arial", 14, "bold")
            )
            button.pack(pady=5)
            self.buttons[text] = button


if __name__ == "__main__":
    WebsiteCrawlerApp().mainloop()
