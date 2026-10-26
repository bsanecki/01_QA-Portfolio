# 03 - Pandago Appium Automation

Automated UI testing of **Pandago**, an Android quiz battle game, using **Appium**, **UiAutomator2**, and **pytest**.

## Project Information

| Item | Details |
|---|---|
| Application | Pandago |
| Package | `com.pandago.app` |
| Platform | Android (real device) |
| Automation Stack | Python, Appium, UiAutomator2, pytest |
| Testing Type | Automated Functional / Smoke Testing |

## Test Execution Summary

The automated suite contains **47 tests**. The latest full run took about 12 minutes.

| Metric | Result |
|---|---:|
| Total Tests | 47 |
| Passed | 44 |
| Failed | 0 |
| Skipped | 3 |
| Total Duration | 719 s |

Three tests were skipped by design: Daily Quiz (feature not implemented yet), Lucky Wheel spin (24-hour cooldown active), and friend profile (no friends on the test account).

## Test Report

Each run generates a PDF report (`reports/<timestamp>/report.pdf`) with an overall summary, a per-test result table, and execution phases (setup, call, teardown).

![Pandago Appium - Full Test Run Report](screens/screen_1.png)

The console output of the same run:

![Pandago Appium - pytest console output](screens/screen_2.png)

## Test Coverage

| File | Tests | Scope |
|---|---:|---|
| `test_app_checks.py` | 11 | Appium server status, session creation, UiAutomator2 capabilities, device and Android version, screenshot capture, app installation and state |
| `test_game.py` | 5 | 1v1 duel: category picker, matchmaking, answering all 8 questions at random, result screen |
| `test_friends.py` | 3 | Ranking tab, sending a friend invitation, removing a friend |
| `test_navigation.py` | 28 | Home, game modes, rewarded ad, Ranking, Friends hub, Rewards, Profile |

Highlights from `test_navigation.py`:

- **Friends:** referral code copied to the clipboard, share chooser, Add Friend screen, received and sent invitations
- **Rewards:** Lucky Wheel, VIP Shop, Daily Tasks
- **Profile:** avatar, nickname, nationality, gender, language switch (PL / EN), Help, Privacy Policy, Terms
- **Rewarded ad:** verified through `logcat` messages

## Test Design

- Bilingual locators, so the tests work with both Polish and English app interfaces
- Tests that change data restore the original state (nickname, language)
- No purchases, and account deletion is only opened and cancelled, never confirmed
- Smart skips when the account state does not allow a test (empty friends list, spin cooldown)
- Custom pytest plugin (`pytest_pdf_report.py`) that builds the PDF report with ReportLab

## Project Structure

```text
03_Appium_Automation/
├── config/
│   └── settings.py
├── reports/
├── screens/
│   ├── screen_1.png
│   └── screen_2.png
├── tests/
│   ├── test_app_checks.py
│   ├── test_friends.py
│   ├── test_game.py
│   └── test_navigation.py
├── conftest.py
├── pytest.ini
├── pytest_pdf_report.py
├── requirements.txt
└── README.md
```

## How to Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start the Appium server in a separate terminal, then:
pytest -v
```

## Skills Demonstrated

- Mobile test automation with Appium and Python
- pytest fixtures, skips, and reusable helpers
- Locating elements by resource ID, text, and XPath
- Touch gestures and scrolling in a Jetpack Compose UI
- Testing real-time multiplayer flows
- Reading Android `logcat` output in tests
- Custom test reporting (PDF)

## Test Outcome

All 44 executed tests passed, with no failures. The 3 skipped tests depend on the app or account state and are marked with a reason in the report.
