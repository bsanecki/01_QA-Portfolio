# 04 – Manual QA Documentation Suite

# About This Repository

I have completed numerous testing projects on crowdsourced testing platforms such as uTest and Test IO. Due to confidentiality requirements, I cannot publicly share the original test cases, reports or evidence from those projects.

This repository showcases selected independent QA projects demonstrating my practical testing skills, including test case design, test execution, defect reporting and test documentation. Each project includes an Excel workbook, screenshots and, where applicable, video evidence of reported defects.

<table>
  <tr>
    <td width="33%" align="center"><img src="01_Web_Game_Testing/screens/screen_3.png" alt="The Dig Game" /></td>
    <td width="33%" align="center"><img src="02_Website_Testing/screens/screen_1.png" alt="Automation Exercise" /></td>
    <td width="33%" align="center"><img src="03_Android_Mobile_Testing/screens/screen_1.png" alt="LocalLock" width="140" /></td>
  </tr>
  <tr>
    <td align="center"><b>Web Game</b></td>
    <td align="center"><b>Website + API</b></td>
    <td align="center"><b>Android App</b></td>
  </tr>
</table>

## At a Glance

| | Web Game | Website + API | Android App |
|---|---|---|---|
| **Application** | The Dig Game | Automation Exercise | LocalLock |
| **Platform** | Browser | Browser + Postman | Android |
| **Test cases** | 56 | 40 (26 web + 14 API) | 26 |
| **Defects reported** | 4 | 2 | 0 |
| **Video evidence** | Yes (4 recordings) | Yes (2 recordings) | – |
| **Project folder** | [01_Web_Game_Testing](01_Web_Game_Testing) | [02_Website_Testing](02_Website_Testing) | [03_Android_Mobile_Testing](03_Android_Mobile_Testing) |

**Total: 122 documented test cases and 6 defects across 3 projects.**

---

## 1. Web Game Testing – The Dig Game

Manual functional and exploratory testing of a browser-based 3D digging game from itch.io. Tests cover movement, collisions, digging, physics, gliding, camera, visual defects and UI.

- 56 test cases, 4 defects with Loom video recordings
- Defects: floating stones, glider flickering, shovel clipping, character passing through a fence

![The Dig Game – test cases](01_Web_Game_Testing/screens/screen_1.png)

![The Dig Game – bug reports](01_Web_Game_Testing/screens/screen_2.png)

👉 [Open project](01_Web_Game_Testing)

---

## 2. Website Testing – Automation Exercise

Manual testing of an e-commerce website (registration, login, products, cart) combined with REST API testing in Postman.

- 26 website test cases and 14 API requests
- 2 defects with video evidence: logout does not redirect to the Home page, and removed cart items reappear
- Postman collection included

<table>
  <tr>
    <td width="50%"><img src="02_Website_Testing/screens/screen_3.png" alt="Project overview" /></td>
    <td width="50%"><img src="02_Website_Testing/screens/screen_7.png" alt="Bug reports" /></td>
  </tr>
</table>

![Website test cases](02_Website_Testing/screens/screen_4.png)

👉 [Open project](02_Website_Testing)

---

## 3. Android Mobile Testing – LocalLock

Manual testing of [LocalLock](https://play.google.com/store/apps/details?id=com.locallock.app), an Android app locker. Tests cover onboarding, PIN/pattern setup and validation, locking and unlocking apps, lockout, intruder photos, anti-uninstall protection, recovery key, history and behavior after restart.

- 26 test cases, all executed and passed
- No defects found in this test run

<table>
  <tr>
    <td width="33%" align="center"><img src="03_Android_Mobile_Testing/screens/screen_1.png" alt="LocalLock screen 1" width="200" /></td>
    <td width="33%" align="center"><img src="03_Android_Mobile_Testing/screens/screen_2.png" alt="LocalLock screen 2" width="200" /></td>
    <td width="33%" align="center"><img src="03_Android_Mobile_Testing/screens/screen_3.png" alt="LocalLock screen 3" width="200" /></td>
  </tr>
</table>

![LocalLock test cases](03_Android_Mobile_Testing/screens/screen_4.png)

👉 [Open project](03_Android_Mobile_Testing)

---

## What Each Project Contains

- **Excel workbook** – project overview with an automatic execution summary, test cases (steps, expected and actual results, status) and bug reports
- **Screenshots** – the tested application and the documentation
- **Evidence** – screen recordings for reported defects (web game and website)
- **Postman collection** – API tests (website project)

## Skills Demonstrated

- Test case design and execution (positive, negative, boundary)
- Functional and exploratory testing
- Defect identification and reporting (steps, expected vs. actual result, severity, priority)
- Traceability between test cases and bug reports
- REST API testing with Postman
- Testing on web and Android
- Evidence collection (screenshots and screen recordings)
- Clear, structured QA documentation

## Tools

Chromium · Android · Postman · Microsoft Excel / LibreOffice Calc · Loom · Git & GitHub
