# 05 - Android Mobile Testing: Pandago

QA portfolio project covering **manual**, **API**, and **automated** testing of **Pandago**, an Android quiz battle game.

| Item | Details |
|---|---|
| Application | Pandago ([Google Play](https://play.google.com/store/apps/details?id=com.pandago.app)) |
| Package | `com.pandago.app` |
| App Version | 1.6.4 |
| Platform | Android 15 (Motorola Moto G power 5G, 2024) |
| Test Period | October 2026 |

## Projects

| # | Project | Type | Main Artifact | Scope |
|---|---|---|---|---|
| 01 | [Manual Testing](01_Manual_Testing/README.md) | Functional, manual | Excel workbook | 77 test cases |
| 02 | [API Testing](02_API_Testing/README.md) | Backend, security-oriented | Excel workbook | 20 scenarios |
| 03 | [Appium Automation](03_Appium_Automation/README.md) | UI automation | Python + pytest + PDF report | 47 automated tests |

## Overall Test Report

| Metric | 01 Manual | 02 API | 03 Automation | Total |
|---|---:|---:|---:|---:|
| Tests / Scenarios | 77 | 20 | 47 | **144** |
| Passed | 77 | 20 | 44 | **141** |
| Failed | 0 | 0 | 0 | **0** |
| Skipped | 0 | 0 | 3 | **3** |
| Defects Reported | 0 | 0 | 0 | **0** |
| Pass Rate (all tests) | 100% | 100% | 93.6% | **97.9%** |
| Pass Rate (executed only) | 100% | 100% | 100% | **100%** |

Skipped tests are counted in the first pass rate (passed / all tests) and excluded from the second (passed / executed tests).

The 3 skipped automated tests depend on the account or app state: Daily Quiz (feature not implemented yet), Lucky Wheel spin (24-hour cooldown), and friend profile (no friends on the test account).

## Coverage Across Projects

| Application Area | 01 Manual | 02 API | 03 Automation |
|---|:---:|:---:|:---:|
| Sign-in and offline behavior | ✔ | ✔ | |
| Onboarding and input validation | ✔ | ✔ | |
| Home and navigation | ✔ | | ✔ |
| Quiz Battle (1v1 duel, results) | ✔ | | ✔ |
| Play with Friends, invitations | ✔ | | ✔ |
| Ranking | ✔ | | ✔ |
| Profile and settings | ✔ | ✔ | ✔ |
| Rewards (Lucky Wheel, VIP, Tasks) | ✔ | | ✔ |
| Authentication and access control | | ✔ | |
| Data integrity and error handling | | ✔ | |
| Device and Appium environment checks | | | ✔ |

## Summary

- **Manual testing** gives broad functional coverage, including onboarding, multiplayer, and edge cases that are hard to automate.
- **API testing** focuses on authentication, authorization, validation, and data integrity. Sensitive details are intentionally left out of the public documentation.
- **Automation** turns the most important user flows into repeatable regression tests with a PDF report for each run.
- Of 144 checks, 141 passed and 3 were skipped, with **no failures and no defects**. These results apply to the tested app version and device configuration.

## Tools and Skills Demonstrated

- Manual test design, execution, and reporting (Microsoft Excel)
- API and backend testing concepts, security-conscious documentation
- Mobile test automation: Python, Appium, UiAutomator2, pytest
- Positive and negative testing, input validation
- Testing real-time multiplayer features
- Custom test reporting (PDF)

## Repository Structure

```text
05_Android_Mobile_Testing/
├── 01_Manual_Testing/
│   ├── screens/
│   ├── Pandago_Manual_Test_Cases.xlsx
│   └── README.md
├── 02_API_Testing/
│   ├── screens/
│   ├── Pandago_API_Testing_Summary.xlsx
│   └── README.md
├── 03_Appium_Automation/
│   ├── config/
│   ├── reports/
│   ├── screens/
│   ├── tests/
│   ├── conftest.py
│   ├── pytest.ini
│   ├── pytest_pdf_report.py
│   ├── requirements.txt
│   └── README.md
└── README.md
```
