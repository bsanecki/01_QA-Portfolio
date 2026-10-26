
import json
import re
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import urlopen

import pytest

from config.settings import (
    ANDROID_UDID,
    APPIUM_SERVER_URL,
    PANDAGO_APP_PACKAGE,
)


def _capability(capabilities, name):
    return capabilities.get(name) or capabilities.get(f"appium:{name}")


def test_appium_server_url_is_valid():
    parsed = urlsplit(APPIUM_SERVER_URL)

    assert parsed.scheme in {"http", "https"}
    assert parsed.hostname
    assert parsed.port is None or 1 <= parsed.port <= 65535


def test_appium_server_is_available_and_ready():
    status_url = f"{APPIUM_SERVER_URL.rstrip('/')}/status"

    try:
        with urlopen(status_url, timeout=3) as response:
            assert response.status == 200
            payload = json.loads(response.read().decode("utf-8"))
    except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        pytest.fail(f"Appium status request failed: {exc}")

    assert isinstance(payload, dict)
    value = payload.get("value")

    assert isinstance(value, dict)
    assert value.get("ready") is True
    assert isinstance(value.get("build", {}).get("version"), str)


def test_appium_session_is_created(driver):
    assert driver.session_id
    assert driver.session_id.strip()


def test_android_uiautomator2_capabilities(driver):
    capabilities = driver.capabilities

    assert str(capabilities.get("platformName", "")).lower() == "android"
    assert str(_capability(capabilities, "automationName")).lower() == "uiautomator2"


def test_connected_device_id_is_reported_and_matches_configuration(driver):
    capabilities = driver.capabilities

    device_id = (
        _capability(capabilities, "udid")
        or capabilities.get("deviceUDID")
        or capabilities.get("appium:deviceUDID")
    )

    assert isinstance(device_id, str)
    assert device_id.strip()

    if ANDROID_UDID:
        assert device_id == ANDROID_UDID


def test_android_version_is_reported(driver):
    version = _capability(driver.capabilities, "platformVersion")

    assert isinstance(version, str)
    assert re.fullmatch(r"\d+(?:\.\d+)*", version)


def test_display_dimensions_are_available(driver):
    dimensions = driver.get_window_size()

    assert dimensions["width"] > 0
    assert dimensions["height"] > 0


def test_device_screenshot_can_be_captured(driver):
    screenshot = driver.get_screenshot_as_png()

    assert isinstance(screenshot, bytes)
    assert screenshot.startswith(b"\x89PNG\r\n\x1a\n")
    assert len(screenshot) > 100


def test_pandago_package_configuration_is_valid():
    assert re.fullmatch(
        r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+",
        PANDAGO_APP_PACKAGE,
    )


def test_pandago_is_installed_on_device(driver):
    assert driver.is_app_installed(PANDAGO_APP_PACKAGE), (
        f"Package {PANDAGO_APP_PACKAGE!r} is not installed on the device."
    )


def test_pandago_app_state_can_be_queried_without_launching(driver):
    state = driver.query_app_state(PANDAGO_APP_PACKAGE)
    state_value = getattr(state, "value", state)

    assert state_value in {1, 2, 3, 4}, (
        f"Unexpected Pandago application state: {state!r}"
    )
