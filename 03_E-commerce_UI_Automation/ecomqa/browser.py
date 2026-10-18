"""Chromium launcher with a system browser fallback for Linux."""
from __future__ import annotations

import os
import shutil
from pathlib import Path

from playwright.sync_api import Error as PlaywrightError


def launch_chromium(playwright, *, headless: bool, slow_mo: int = 0):
    """Prefer Playwright-managed Chromium; use a system installation as fallback."""
    try:
        return playwright.chromium.launch(headless=headless, slow_mo=slow_mo)
    except PlaywrightError as managed_error:
        configured_path = os.getenv("PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH")
        candidates = [configured_path] if configured_path else []
        candidates.extend([
            shutil.which("chromium"),
            shutil.which("chromium-browser"),
            shutil.which("google-chrome"),
        ])
        for candidate in candidates:
            if not candidate or not Path(candidate).exists():
                continue
            args = ["--no-sandbox"] if hasattr(os, "geteuid") and os.geteuid() == 0 else []
            try:
                return playwright.chromium.launch(
                    headless=headless,
                    slow_mo=slow_mo,
                    executable_path=candidate,
                    args=args,
                )
            except PlaywrightError:
                continue
        raise managed_error
