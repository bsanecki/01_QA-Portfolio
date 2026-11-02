import os
import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options


@pytest.fixture
def driver():
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = os.getenv("ANDROID_DEVICE_NAME", "Android Device")
    options.udid = os.getenv("ANDROID_UDID", "ZY22KFW9KH")
    options.no_reset = True
    options.new_command_timeout = 120

    driver = webdriver.Remote(
        os.getenv("APPIUM_SERVER_URL", "http://127.0.0.1:4723"),
        options=options,
    )
    yield driver
    driver.quit()
