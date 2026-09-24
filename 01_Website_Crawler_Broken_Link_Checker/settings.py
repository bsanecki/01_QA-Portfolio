"""The three user-facing settings, shared by the whole application.

One immutable AppSettings value is owned by a SettingsStore. The GUI edits it
through the Settings screen; Full Website Scan and Single Link Check both read
it when they start, so a running scan is never changed half-way.

Defaults reproduce the behaviour of the application before Settings existed:

* request_timeout  15 s = the built-in per-request timeouts (connect/read
                   values in models.py). Other values scale them
                   proportionally: 30 doubles every timeout, 5 divides them
                   by three. The browser page-load timeout is set to the
                   value itself (15 s by default, as before).
* follow_redirects on  = redirects are followed and the chain is reported.
                   Off: the first response (e.g. 301) is reported as it is.
* respect_robots   on  = robots.txt rules / Crawl-delay are honoured.
"""

import json
from dataclasses import dataclass
from pathlib import Path

DEFAULT_REQUEST_TIMEOUT = 15
MIN_REQUEST_TIMEOUT = 1
MAX_REQUEST_TIMEOUT = 120

DEFAULT_SETTINGS_PATH = Path.home() / ".website_crawler_settings.json"


class SettingsError(ValueError):
    """A submitted setting value is not valid."""


def scale_timeout(timeout, scale):
    """Scale a requests timeout (float or (connect, read)) by `scale`.
    scale == 1 returns the value unchanged (default behaviour)."""
    if scale == 1:
        return timeout
    if isinstance(timeout, tuple):
        return tuple(scale_timeout(value, scale) for value in timeout)
    return max(1.0, float(timeout) * scale)


def parse_timeout(value):
    """Validate the timeout typed by the user; returns an int (seconds)."""
    text = str(value).strip()
    try:
        seconds = int(text)
    except ValueError:
        raise SettingsError(
            "Request timeout must be a whole number of seconds.") from None
    if not MIN_REQUEST_TIMEOUT <= seconds <= MAX_REQUEST_TIMEOUT:
        raise SettingsError(
            f"Request timeout must be between {MIN_REQUEST_TIMEOUT} and "
            f"{MAX_REQUEST_TIMEOUT} seconds.")
    return seconds


@dataclass(frozen=True)
class AppSettings:
    request_timeout: int = DEFAULT_REQUEST_TIMEOUT
    follow_redirects: bool = True
    respect_robots: bool = True

    @property
    def timeout_scale(self):
        return self.request_timeout / DEFAULT_REQUEST_TIMEOUT

    def to_dict(self):
        return {
            "request_timeout": self.request_timeout,
            "follow_redirects": self.follow_redirects,
            "respect_robots": self.respect_robots,
        }

    @classmethod
    def from_dict(cls, data):
        """Lenient: any missing/invalid field falls back to its default."""
        data = data if isinstance(data, dict) else {}
        try:
            timeout = parse_timeout(data.get("request_timeout"))
        except SettingsError:
            timeout = DEFAULT_REQUEST_TIMEOUT

        def flag(name):
            value = data.get(name, True)
            return value if isinstance(value, bool) else True

        return cls(timeout, flag("follow_redirects"), flag("respect_robots"))


class SettingsStore:
    """Holds the current settings and saves them to a small JSON file.
    Reading or writing the file can fail silently: the app then simply runs
    with defaults / without persistence."""

    def __init__(self, path=None, load=True):
        self.path = Path(path) if path is not None else DEFAULT_SETTINGS_PATH
        self.current = AppSettings()
        if load:
            self.load()

    def load(self):
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            data = None
        self.current = AppSettings.from_dict(data)
        return self.current

    def save(self, settings):
        """Make `settings` current and persist them. Returns True if the
        file could be written (the values are applied either way)."""
        self.current = settings
        try:
            self.path.write_text(
                json.dumps(settings.to_dict(), indent=2), encoding="utf-8")
            return True
        except OSError:
            return False
