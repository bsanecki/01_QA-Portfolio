# Appium Android Basics

Automated Android UI testing using Python, Pytest, Appium, and UiAutomator2 on a real Android device.

## Test Coverage

- Settings app launch and homepage verification
- Settings categories visibility
- Settings search functionality
- Navigation between settings screens
- Network and internet settings
- Android version and device information
- Screen orientation and unlock status
- Battery level and screen dimensions

## Tech Stack

- Python 3
- Pytest
- Appium
- UiAutomator2
- Android Debug Bridge (ADB)

## Test Results

**44 passed · 0 failed**

- Total tests: 44
- Passed: 44
- Failed: 0
- Execution time: 8 minutes 28 seconds

Detailed results are available in [`result.txt`](result.txt).

## Run Tests

Start the Appium server:

```bash
appium
```

Activate the virtual environment and run the test suite:

```bash
source .venv/bin/activate
python -m pytest -v
```
