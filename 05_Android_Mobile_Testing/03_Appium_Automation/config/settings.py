"""Settings read from environment variables."""

import os

APPIUM_SERVER_URL = os.getenv("APPIUM_SERVER_URL", "http://127.0.0.1:4723")
ANDROID_DEVICE_NAME = os.getenv("ANDROID_DEVICE_NAME", "Android")
ANDROID_UDID = os.getenv("ANDROID_UDID", "").strip() or None
PANDAGO_APP_PACKAGE = os.getenv("PANDAGO_APP_PACKAGE", "com.pandago.app")
