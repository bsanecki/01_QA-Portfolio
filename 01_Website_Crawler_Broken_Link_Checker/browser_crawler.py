"""Optional JavaScript-rendering page fetcher (Playwright) + browser detection.

This plugs into the crawler through the same PageFetcher interface as the
fast HTTP fetcher. It is only imported/used when the person picks a browser
(Chromium, Chrome, Firefox, Edge, Brave, Opera) or "Auto". Plain "HTTP" mode
never touches Playwright. If the chosen browser is missing, the scan reports
it clearly and falls back to plain HTTP - it never crashes.

Which browser runs what:
    Chromium -> Playwright's own Chromium   (python3 -m playwright install chromium)
    Firefox  -> Playwright's own Firefox    (python3 -m playwright install firefox)
    Chrome / Edge / Brave / Opera -> the copy installed on this computer,
    found in its usual install locations (see BROWSERS below), driven by
    Playwright's Chromium engine through its executable path.
Only ONE browser kind is ever started per scan.

Install Playwright itself:
    python3 -m pip install playwright

How it is used (see scan_engine.py): the page is first fetched over HTTP
(that gives the authoritative status / redirect chain and the static links).
This fetcher then renders the page and returns the resulting DOM, so links
created by JavaScript are discovered as well.

Playwright's sync API is bound to the thread that created it, so every crawl
worker lazily starts its own browser and closes it in close_thread().
"""

import glob
import importlib.util
import os
import shutil
import sys
import threading
from dataclasses import dataclass
from time import perf_counter

from crawler import PageFetcher
from link_checker import USER_AGENT, RequestOutcome
from models import LinkResult

NAVIGATION_TIMEOUT_MS = 15000
NETWORK_IDLE_TIMEOUT_MS = 4000


class BrowserUnavailable(RuntimeError):
    """Playwright or the chosen browser is not installed / cannot start."""


def playwright_installed():
    return importlib.util.find_spec("playwright") is not None


# ---------------------------------------------------------------------------
# Browser catalogue + detection
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BrowserSpec:
    id: str
    label: str
    engine: str           # Playwright engine: "chromium" | "firefox"
    bundled: bool         # True = Playwright's own download, False = installed app
    names: tuple = ()     # executable names looked up on PATH
    win: tuple = ()       # (env var, relative path) on Windows
    mac: tuple = ()       # absolute paths on macOS ("~" allowed)
    linux: tuple = ()     # absolute paths on Linux
    win_exe: str = ""     # exe name for the Windows "App Paths" registry lookup


BROWSERS = {
    "chromium": BrowserSpec("chromium", "Chromium", "chromium", True),
    "firefox": BrowserSpec("firefox", "Firefox", "firefox", True),
    "chrome": BrowserSpec(
        "chrome", "Google Chrome", "chromium", False,
        names=("google-chrome", "google-chrome-stable", "chrome"),
        win=(("PROGRAMFILES", r"Google\Chrome\Application\chrome.exe"),
             ("PROGRAMFILES(X86)", r"Google\Chrome\Application\chrome.exe"),
             ("LOCALAPPDATA", r"Google\Chrome\Application\chrome.exe")),
        mac=("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
             "~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        linux=("/opt/google/chrome/chrome", "/usr/bin/google-chrome",
               "/usr/bin/google-chrome-stable"),
        win_exe="chrome.exe"),
    "edge": BrowserSpec(
        "edge", "Microsoft Edge", "chromium", False,
        names=("microsoft-edge", "microsoft-edge-stable", "msedge"),
        win=(("PROGRAMFILES(X86)", r"Microsoft\Edge\Application\msedge.exe"),
             ("PROGRAMFILES", r"Microsoft\Edge\Application\msedge.exe"),
             ("LOCALAPPDATA", r"Microsoft\Edge\Application\msedge.exe")),
        mac=("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
             "~/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
        linux=("/opt/microsoft/msedge/msedge", "/usr/bin/microsoft-edge",
               "/usr/bin/microsoft-edge-stable"),
        win_exe="msedge.exe"),
    "brave": BrowserSpec(
        "brave", "Brave", "chromium", False,
        names=("brave-browser", "brave", "brave-browser-stable"),
        win=(("PROGRAMFILES", r"BraveSoftware\Brave-Browser\Application\brave.exe"),
             ("PROGRAMFILES(X86)", r"BraveSoftware\Brave-Browser\Application\brave.exe"),
             ("LOCALAPPDATA", r"BraveSoftware\Brave-Browser\Application\brave.exe")),
        mac=("/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
             "~/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"),
        linux=("/opt/brave.com/brave/brave", "/usr/bin/brave-browser",
               "/usr/bin/brave", "/snap/bin/brave"),
        win_exe="brave.exe"),
    "opera": BrowserSpec(
        "opera", "Opera", "chromium", False,
        names=("opera",),
        win=(("LOCALAPPDATA", r"Programs\Opera\opera.exe"),
             ("PROGRAMFILES", r"Opera\opera.exe"),
             ("PROGRAMFILES(X86)", r"Opera\opera.exe"),
             ("LOCALAPPDATA", r"Programs\Opera GX\opera.exe")),
        mac=("/Applications/Opera.app/Contents/MacOS/Opera",
             "~/Applications/Opera.app/Contents/MacOS/Opera"),
        linux=("/usr/bin/opera", "/snap/bin/opera", "/usr/lib/x86_64-linux-gnu/opera/opera"),
        win_exe="opera.exe"),
}

# What "Auto" tries, in this order (first one that is available wins).
AUTO_ORDER = ("chromium", "chrome", "edge", "brave", "firefox", "opera")


@dataclass(frozen=True)
class BrowserCheck:
    ok: bool
    browser_id: str
    label: str
    path: str | None = None     # executable of an installed browser
    message: str = ""           # human-readable reason when not ok


def _platform_key(platform=None):
    platform = platform or sys.platform
    if platform.startswith("win"):
        return "win"
    if platform == "darwin":
        return "mac"
    return "linux"


def _windows_registry_path(exe_name):
    try:
        import winreg
    except ImportError:
        return None
    key_path = rf"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{exe_name}"
    for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        try:
            with winreg.OpenKey(hive, key_path) as key:
                value, _kind = winreg.QueryValueEx(key, "")
                if value:
                    return value
        except OSError:
            continue
    return None


def candidate_paths(spec, platform=None, env=None, home=None):
    """Typical executable locations for an installed browser (no I/O)."""
    env = os.environ if env is None else env
    home = home if home is not None else os.path.expanduser("~")
    key = _platform_key(platform)
    paths = []
    if key == "win":
        for variable, relative in spec.win:
            base = env.get(variable)
            if base:
                paths.append(os.path.join(base, relative))
    elif key == "mac":
        paths += [p.replace("~", home, 1) if p.startswith("~") else p
                  for p in spec.mac]
    else:
        paths += list(spec.linux)
    return paths


def find_system_browser(browser_id, platform=None, env=None, home=None,
                        exists=os.path.isfile, which=shutil.which,
                        registry=_windows_registry_path):
    """Path of the installed browser, or None. Checks the usual install
    folders, then PATH, then (Windows) the App Paths registry key."""
    spec = BROWSERS[browser_id]
    for path in candidate_paths(spec, platform, env, home):
        if exists(path):
            return path
    for name in spec.names:
        found = which(name)
        if found:
            return found
    if _platform_key(platform) == "win" and spec.win_exe:
        path = registry(spec.win_exe)
        if path and exists(path):
            return path
    return None


def playwright_browsers_dirs(env=None, platform=None, home=None):
    env = os.environ if env is None else env
    home = home if home is not None else os.path.expanduser("~")
    custom = env.get("PLAYWRIGHT_BROWSERS_PATH")
    if custom and custom != "0":
        return [custom]
    key = _platform_key(platform)
    if key == "win":
        return [os.path.join(env.get("LOCALAPPDATA", home), "ms-playwright")]
    if key == "mac":
        return [os.path.join(home, "Library", "Caches", "ms-playwright")]
    return [os.path.join(home, ".cache", "ms-playwright")]


def playwright_browser_downloaded(engine, dirs=None):
    """True if Playwright's own Chromium/Firefox download exists. Pure file
    check: nothing is started."""
    prefixes = {"chromium": ("chromium-", "chromium_headless_shell-"),
                "firefox": ("firefox-",)}[engine]
    for root in (dirs if dirs is not None else playwright_browsers_dirs()):
        for prefix in prefixes:
            if glob.glob(os.path.join(root, prefix + "*")):
                return True
    return False


def check_browser(browser_id, **kwargs):
    """Can `browser_id` be used right now? Never raises."""
    spec = BROWSERS.get(browser_id)
    if spec is None:
        return BrowserCheck(False, browser_id, str(browser_id),
                            message=f"Unknown browser: {browser_id}")

    if not playwright_installed():
        return BrowserCheck(
            False, spec.id, spec.label,
            message="Playwright is not installed.\n\n"
                    "Install it with:\npython3 -m pip install playwright")

    if spec.bundled:
        if not playwright_browser_downloaded(
                spec.engine, kwargs.get("browser_dirs")):
            return BrowserCheck(
                False, spec.id, spec.label,
                message=f"{spec.label} (Playwright) is not downloaded yet.\n\n"
                        f"Install it with:\npython3 -m playwright install {spec.engine}")
        return BrowserCheck(True, spec.id, spec.label)

    path = find_system_browser(
        spec.id, **{k: v for k, v in kwargs.items() if k != "browser_dirs"})
    if not path:
        return BrowserCheck(
            False, spec.id, spec.label,
            message=f"{spec.label} was not found on this computer "
                    "(checked its usual install locations).\n\n"
                    "Install it, or pick another browser.")
    return BrowserCheck(True, spec.id, spec.label, path=path)


def resolve_auto(**kwargs):
    """First usable browser in AUTO_ORDER, or None."""
    for browser_id in AUTO_ORDER:
        check = check_browser(browser_id, **kwargs)
        if check.ok:
            return check
    return None


# ---------------------------------------------------------------------------
# Fetcher
# ---------------------------------------------------------------------------


class BrowserPageFetcher(PageFetcher):
    name = "browser"

    def __init__(self, limiter, browser_id="chromium", executable_path=None):
        self.limiter = limiter
        self.spec = BROWSERS.get(browser_id, BROWSERS["chromium"])
        self.executable_path = executable_path
        self.navigation_timeout_ms = NAVIGATION_TIMEOUT_MS   # Settings
        self._local = threading.local()

    def _context(self):
        context = getattr(self._local, "context", None)
        if context is not None:
            return context
        try:
            from playwright.sync_api import sync_playwright

            playwright = sync_playwright().start()
            try:
                launcher = getattr(playwright, self.spec.engine)
                options = {"headless": True}
                if self.executable_path:
                    options["executable_path"] = self.executable_path
                browser = launcher.launch(**options)
            except Exception:
                playwright.stop()
                raise
            context = browser.new_context(user_agent=USER_AGENT)
        except Exception as error:
            lines = str(error).splitlines()
            raise BrowserUnavailable(
                f"{self.spec.label}: {lines[0] if lines else 'cannot start'}"
            ) from error

        self._local.playwright = playwright
        self._local.browser = browser
        self._local.context = context
        return context

    def fetch(self, url, stop_event, kind="page"):
        """Render `url` and return an outcome whose body is the rendered DOM
        (str). Returns None when stopped. Raises BrowserUnavailable."""
        context = self._context()

        if stop_event is not None and stop_event.is_set():
            return None
        if self.limiter is not None and not self.limiter.acquire(url, stop_event, priority=True):
            return None

        page = None
        started = perf_counter()
        try:
            page = context.new_page()
            response = page.goto(
                url, wait_until="domcontentloaded",
                timeout=self.navigation_timeout_ms)
            try:
                page.wait_for_load_state(
                    "networkidle", timeout=NETWORK_IDLE_TIMEOUT_MS)
            except Exception:
                pass  # chatty pages never go idle; the DOM is still usable

            html = page.content()
            status = response.status if response is not None else None
            result = LinkResult(
                url=url,
                status=status,
                final_url=page.url,
                elapsed=perf_counter() - started,
                method="BROWSER",
            )
            return RequestOutcome(result, html, "text/html")
        except Exception as error:
            message = str(error).splitlines()[0] if str(error) else "error"
            error_type = "TIMEOUT" if "Timeout" in type(error).__name__ else "REQUEST ERROR"
            result = LinkResult(
                url=url, status=None, final_url=url,
                elapsed=perf_counter() - started,
                error_type=error_type, error_message=message,
                method="BROWSER",
            )
            return RequestOutcome(result, None, "")
        finally:
            if page is not None:
                try:
                    page.close()
                except Exception:
                    pass
            if self.limiter is not None:
                self.limiter.release(url)

    def close_thread(self):
        for name in ("context", "browser"):
            obj = getattr(self._local, name, None)
            if obj is not None:
                try:
                    obj.close()
                except Exception:
                    pass
        playwright = getattr(self._local, "playwright", None)
        if playwright is not None:
            try:
                playwright.stop()
            except Exception:
                pass
        self._local = threading.local()
