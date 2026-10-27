# QA / Test Engineer Portfolio

A collection of my QA, test automation, and software testing projects.

## Technologies

Python • pytest • Playwright • Appium • Requests • SQL • REST API • Postman • JSON Schema • Allure • k6 • ADB • Git • GitHub Actions

## Projects

### 01. Website Crawler & Broken Link Checker

A Python-based QA tool for crawling websites and checking discovered URLs.

The application can perform full website scans, detect broken links, redirects and unverified responses, measure response times, and generate reports with Excel export.

It also supports single-link checking, crawl depth control and JavaScript-enabled pages using Playwright.

### 02. REST API Testing Framework

A Python-based REST API testing framework built with pytest and Requests.

The framework tests API endpoints, validates response data and JSON Schemas, covers positive, negative and edge-case scenarios, and generates HTML and Allure reports. It also includes parameterized tests, data integrity checks, and GitHub Actions CI integration.

### 03. E-commerce UI Automation Suite

A Python-based UI test automation framework built with pytest and Playwright.

The project tests an e-commerce storefront, covering homepage navigation, product pages, available product options, shopping cart operations, quantity updates, item removal, and checkout navigation.

The suite includes automated assertions, timestamped HTML and JSON reports, screenshots for test evidence, and failure diagnostics. It focuses on realistic user workflows and regression testing without submitting orders or processing payments.

**Technologies:** Python • pytest • Playwright • HTML Reports • JSON • Git

### 04. Website Manual QA & API Testing

A manual QA portfolio project focused on functional testing of an e-commerce website and REST API testing using Postman.

The project includes 26 manual web test cases, 14 API requests, structured Excel documentation, and two documented website defects with supporting screen recordings.

**Technologies:** Postman • Excel • Chromium • Git • GitHub

### 05. Android Mobile Testing

A Python-based Android UI test automation project built with pytest and Appium.

The project tests the Pandago mobile application, covering app navigation, game workflows, matchmaking and quiz results, friends and invitations, rewards, the Lucky Wheel, and profile settings. It also verifies language switching, profile changes, external links, and rewarded-ad interactions.

The suite includes automated assertions, synchronization with dynamic UI states, Android log monitoring for ad-related checks, and safety checks to avoid unintended account deletion or purchases.

It also generates a timestamped PDF report for each complete test run, combining test results, execution times, statuses, and failure details into a single document.

**Technologies:** Python • pytest • Appium • Android • ADB • ReportLab • PDF Reports • Git

### 06. API Performance Testing with k6
 
A k6-based API performance testing project for the public DummyJSON products API.
 
The project includes smoke, load, and stress scenarios that run the same request mix, so results are comparable between test types. Load tests run with 1, 5, and 10 virtual users and are compared in a single report.
 
Each test combines response checks with performance thresholds (failed request rate, p90 and p95 response times, including per-endpoint limits). Timestamped Markdown and JSON reports are generated for every run.
 
The project includes safety limits for public and non-public targets, configuration through environment variables, Bash runner scripts, and a GitHub Actions workflow that runs the full suite and stores the reports.
 
**Technologies:** k6 • JavaScript • Bash • Markdown and JSON Reports • GitHub Actions • Git
 
