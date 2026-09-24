import tkinter as tk

from full_scanner import FullScannerFrame
from gui_common import make_button
from more_screens import (
    AboutFrame,
    HowToUseFrame,
    MoreFrame,
    StatusCodesFrame,
)
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

        container = tk.Frame(
            self,
            bg="#1e1e1e"
        )

        container.pack(
            fill="both",
            expand=True
        )

        container.grid_rowconfigure(
            0,
            weight=1
        )

        container.grid_columnconfigure(
            0,
            weight=1
        )

        self.settings_store = SettingsStore(
            settings_path
        )

        # ---------------------------------------------------------
        # FRAMES
        # ---------------------------------------------------------

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

        self.how_to_frame = HowToUseFrame(
            container,
            go_back=self.show_more
        )

        self.status_frame = StatusCodesFrame(
            container,
            go_back=self.show_more
        )

        self.about_frame = AboutFrame(
            container,
            go_back=self.show_more
        )

        # ---------------------------------------------------------
        # PLACE FRAMES
        # ---------------------------------------------------------

        for frame in (
            self.menu_frame,
            self.scanner_frame,
            self.report_frame,
            self.single_frame,
            self.settings_frame,
            self.more_frame,
            self.how_to_frame,
            self.status_frame,
            self.about_frame,
        ):
            frame.grid(
                row=0,
                column=0,
                sticky="nsew"
            )

        self.protocol(
            "WM_DELETE_WINDOW",
            self.on_close
        )

        self.show_menu()

    # =============================================================
    # WINDOW / NAVIGATION
    # =============================================================

    def on_close(self):
        """Close the application."""

        self.scanner_frame.shutdown()
        self.single_frame.shutdown()

        self.destroy()

    def show_menu(self):
        """Show Main Menu."""

        self.geometry("800x500")
        self.menu_frame.tkraise()

    def show_scanner(self):
        """Show Full Website Scanner."""

        self.geometry("1100x750")
        self.scanner_frame.tkraise()

    def show_report(
        self,
        website_url,
        elapsed,
        pages_scanned,
        results,
        scan_info=None
    ):
        """Show scan report."""

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
        """Return from report to scanner."""

        self.scanner_frame.reset_after_report()
        self.show_scanner()

    def show_single_check(self):
        """Show Single Link Check."""

        self.geometry("900x680")
        self.single_frame.tkraise()

    def show_settings(self):
        """Show Settings."""

        self.settings_frame.load()

        self.geometry("800x560")
        self.settings_frame.tkraise()

    def show_more(self):
        """Show More menu."""

        self.geometry("800x500")
        self.more_frame.tkraise()

    def show_how_to(self):
        """Show How To Use."""

        self.geometry("900x700")
        self.how_to_frame.tkraise()

    def show_status_codes(self):
        """Show HTTP Status Codes."""

        self.geometry("900x700")
        self.status_frame.tkraise()

    def show_about(self):
        """Show About."""

        self.geometry("800x520")
        self.about_frame.tkraise()


# =================================================================
# MAIN MENU
# =================================================================

class MainMenuFrame(tk.Frame):
    def __init__(
        self,
        parent,
        open_full_scanner,
        open_single_check,
        open_settings,
        open_more,
        exit_app,
    ):
        super().__init__(
            parent,
            bg="#1e1e1e"
        )

        # =========================================================
        # TITLE
        # =========================================================

        self.title_label = tk.Label(
            self,
            text="What would you like to do?",
            font=("Arial", 22, "bold"),
            fg="white",
            bg="#1e1e1e",
            padx=18,
            pady=8
        )

        self.title_label.place(
            relx=0.5,
            rely=0.08,
            anchor="n"
        )

        # =========================================================
        # BUTTONS
        # =========================================================

        self.buttons = {}

        self.button_frame = tk.Frame(
            self,
            bg="#1e1e1e",
            padx=14,
            pady=10
        )

        self.button_frame.place(
            relx=0.5,
            rely=0.34,
            anchor="n"
        )

        buttons = (
            (
                "Full Website Scan",
                open_full_scanner,
                True
            ),
            (
                "Single Link Check",
                open_single_check,
                True
            ),
            (
                "Settings",
                open_settings,
                True
            ),
            (
                "More",
                open_more,
                True
            ),
            (
                "Exit",
                exit_app,
                False
            ),
        )

        for text, command, primary in buttons:

            button = make_button(
                self.button_frame,
                text,
                command,
                primary=primary,
                font=("Arial", 14, "bold")
            )

            if text == "Exit":
                button.pack(
                    pady=(4, 10)
                )
            else:
                button.pack(
                    pady=4
                )

            self.buttons[text] = button


# =================================================================
# START APPLICATION
# =================================================================

if __name__ == "__main__":
    WebsiteCrawlerApp().mainloop()