"""Tiny style helpers shared by the added screens (same look as the rest of
the application: dark background, blue primary buttons, grey secondary)."""

import tkinter as tk

BG = "#1e1e1e"
FG = "white"
MUTED = "#aaaaaa"
PRIMARY = "#2d89ef"
PRIMARY_ACTIVE = "#1f6fca"
SECONDARY = "#444444"
SECONDARY_ACTIVE = "#333333"
FIELD_BG = "#2b2b2b"

CATEGORY_COLORS = {
    "ok": "#2ecc71",
    "redirect": "#f5a623",
    "broken": "#ff5252",
    "unverified": "#ff8a3d",
}


def make_button(parent, text, command, primary=True, **options):
    colors = (
        (PRIMARY, PRIMARY_ACTIVE) if primary
        else (SECONDARY, SECONDARY_ACTIVE)
    )
    settings = {
        "font": ("Arial", 13, "bold"),
        "width": 20,
        "height": 2,
        "relief": "flat",
        "bd": 0,
        "fg": FG,
        "activeforeground": FG,
        "bg": colors[0],
        "activebackground": colors[1],
    }
    settings.update(options)
    return tk.Button(parent, text=text, command=command, **settings)


def make_title(parent, text, size=26, pady=(30, 15)):
    label = tk.Label(
        parent, text=text, font=("Arial", size, "bold"), fg=FG, bg=BG)
    label.pack(pady=pady)
    return label


def make_text_view(parent, height=10):
    """Read-only, scrollable, selectable text area. Returns the Text widget;
    use set_text_view_content()/append helpers to fill it."""
    frame = tk.Frame(parent, bg=BG)
    text = tk.Text(
        frame, wrap="word", height=height, bg=FIELD_BG, fg=FG,
        insertbackground=FG, relief="flat", bd=0, padx=16, pady=12,
        font=("Arial", 12), cursor="arrow", highlightthickness=0)
    scrollbar = tk.Scrollbar(frame, orient="vertical", command=text.yview)
    text.configure(yscrollcommand=scrollbar.set)
    text.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    text.container = frame
    return text
