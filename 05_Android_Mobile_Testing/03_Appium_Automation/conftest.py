"""Shared pytest fixtures for the minimal Appium project."""

import pytest

pytest_plugins = ("pytest_pdf_report",)

from config.settings import ANDROID_DEVICE_NAME, ANDROID_UDID, APPIUM_SERVER_URL


@pytest.fixture

def driver():
    """Create an Appium session without launching or resetting Pandago."""
    # Keep Appium imports inside the fixture so pytest can collect tests even
    # before the mobile dependencies are installed.
    from appium import webdriver
    from appium.options.android import UiAutomator2Options

    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = ANDROID_DEVICE_NAME
    options.no_reset = True
    options.new_command_timeout = 60

    if ANDROID_UDID:
        options.udid = ANDROID_UDID

    # Intentionally do not set appPackage/appActivity: this project only
    # checks package installation and must not launch the app under test.
    session = webdriver.Remote(
        command_executor=APPIUM_SERVER_URL,
        options=options,
    )
    try:
        yield session
    finally:
        session.quit()
