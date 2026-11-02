**ISTQB CTFL 4.0 - Personal Notes**

**Source: ISTQB Certified Tester — Foundation Level Syllabus, version 4.0.1 (SJSI) Personal notes**

**Table of contents:**

1. Fundamentals of testing

2. Testing throughout the software development lifecycle

3. Static testing

4. Test analysis and design

5. Managing the test activities

6. Test tools

**1. Fundamentals of testing.**

**1.1 Key concepts:**

| **Concept** | **Definition** |
| :-: | :-: |
| **Testing** | A set of activities aimed at finding defects and evaluating the quality of a work product. It includes not only test execution, but also planning, analysis and design of tests. |
| **Verification** | Confirmation that the system has been built according to the specification. |
| **Validation** | Confirmation that the system actually meets the user's needs. |
| **Static testing** | Testing without executing the code (e.g. reviews and static analysis). |
| **Dynamic testing** | Testing carried out while the software is running. |
| **Debugging** | Finding and removing the cause of a failure: reproduction → diagnosis → fixing the problem. |
| **Confirmation testing** | Checking after a fix whether a specific defect has been removed. |
| **Regression testing** | Checking whether changes introduced have not caused new problems in other areas of the system. |
| **Error** | A human mistake resulting e.g. from time pressure, fatigue or lack of knowledge. |
| **Defect** | A flaw in the software resulting from an error. |
| **Failure** | Observable incorrect behaviour of the system caused by a defect. |
| **Root cause** | The actual cause of a problem, the removal of which prevents its recurrence. |
| **Testware** | Work products from testing (test plan, test cases, test data, scripts, reports). |
| **Traceability** | Linking requirements to test cases, results and risks. |


**1.2 Seven testing principles:**

| **Principle 1 - Testing shows the presence of defects** | Finding defects does not mean it is possible to prove their complete absence. |
| :-: | - |
| **Principle 2 - Exhaustive testing is impossible** | It is not possible to check all cases, priorities must be set. |
| **Principle 3 - Early testing** | The earlier a defect is found, the cheaper it is to fix. |
| **Principle 4 - Defect clustering** | Most defects are usually found in a small number of modules. |
| **Principle 5 - Pesticide paradox** | The same tests eventually stop finding new defects. |
| **Principle 6 - Testing is context dependent** | The way of testing depends on the type of system, risk and users. |
| **Principle 7 - Absence-of-errors is a fallacy** | Meeting the requirements does not mean meeting the real needs. |


**1.3 Test process - activities (logical order, iterative in practice):**

- **Test monitoring and control** - checking progress against the plan

- **Test analysis** - WHAT to test (test conditions)

- **Test design** - HOW to test (test cases)

- **Test implementation** - data, environment, scripts

- **Test execution** - running tests, recording results

- **Test completion** - summary, archiving, report


**2. Testing throughout the software development lifecycle.**

**2.1 SDLC models**:

| Model | Characteristics |
| :-: | :-: |
| Sequential | Stages one after another (Waterfall, V-Model) |
| Iterative | Repeating cycles |
| Incremental | Building the product piece by piece |
| Agile | Frequent delivery, collaboration, embracing change |


**2.2 "Test-first" approaches:**

| **Approach** | **Principle** |
| :-: | :-: |
| **TDD** | **test → code → refactoring** |
| **ATDD** | **acceptance tests before implementation, based on acceptance criteria** |
| **BDD** | **behaviour described in a way understandable to the business, Given/When/Then format** |


**2.3 DevOps and shift left:**

| **Concept** | **Definition** |
| :-: | :-: |
| DevOps | Combining development and operations, automation, CI/CD, fast feedback |
| CI (Continuous Integration) | Frequent integration of changes + automated checks (e.g. tests) |
| CD (Continuous Delivery/Deployment) | Automation of delivery/deployment |
| Shift Left | Testing as early as possible in the development lifecycle |
| Retrospective | Meeting after an iteration: what worked, what to improve |


**2.4 Five test levels:**

| Level | Checks | Performed by |
| :-: | :-: | :-: |
| Component (unit) testing | Individual modules in isolation | developers |
| Component integration testing | Interactions/interfaces between modules | developers |
| System testing | The whole system against the requirements | test team |
| System integration testing | Cooperation with other systems/services | test team |
| Acceptance testing | Readiness for deployment, business needs | business/users |

**2.5 Test types:**

| Type | Definition |
| :-: | :-: |
| Functional | Check WHAT the system does |
| Non-functional | Check HOW WELL the system performs (performance, usability, security, compatibility) |
| Black-box | Without knowledge of the internal structure |
| White-box | Taking the structure into account (code, architecture) |


**2.6 Confirmation testing vs regression testing and maintenance testing:**

| **Concept** | **Definition** |
| :-: | :-: |
| Confirmation testing | Checks a SPECIFIC fixed defect |
| Regression testing | Checks whether a change has not broken anything else in the system |
| Maintenance testing | After deployment, triggered by a change, migration or system retirement |
| Impact analysis | Precedes maintenance testing - assessment of the consequences of a change for the rest of the system |


**3. Static testing.**

**3.1 Fundamentals:**

| Concept | Definition |
| :-: | :-: |
| Static testing | Detecting defects without executing the software |
| Review | Manual evaluation of a work product by people |
| Static analysis | Tool-based, automated analysis of code/structure |
| Dynamic testing | Testing by running the program |


**Static testing detects defects directly, dynamic testing detects failures that still need to be diagnosed.**

**3.2 Review process (order):**

| Stage | Description |
| :-: | :-: |
| Planning | Objective, scope, criteria, time |
| Kick-off | Materials and roles ready |
| Individual review | Everyone analyses independently |
| Communication and analysis | Discussion of anomalies |
| Fixing and reporting | Corrections + documentation |


**3.3 Roles in a review:**

| Role | Responsibility |
| :-: | :-: |
| Manager | Decides what and when to review, resources |
| Author | Created the product, removes the defects |
| Moderator/facilitator | Leads the meeting |
| Scribe | Records anomalies and decisions |
| Reviewer | Analyses the product |
| Review leader | Organisation and overall conduct of the review |


**3.4 Types of reviews:**

| Type | Characteristics |
| :-: | :-: |
| Informal review | No defined process |
| Walkthrough | Led by the author |
| Technical review | People with technical knowledge + moderator |
| Inspection | The most formal, collects metrics, the author cannot be the leader or the scribe |

**4. Test analysis and design.**

**4.1 Black-box techniques - the 4 most important:**

| Technique | What it consists of | When to use |
| :-: | :-: | :-: |
| Equivalence Partitioning | You divide input data into groups treated the same way — you test 1 value from each group instead of all possible ones | Fields with ranges of values (e.g. age 18-65) |
| Boundary Value Analysis | You test values at the boundaries of the classes — that is where programmers' errors most often occur | Always together with equivalence partitioning |
| Decision table testing | You test all combinations of conditions and the resulting actions | Complex business rules (e.g. discounts, permissions) |
| State transition testing | You model the system as states + events causing transitions | A system with clearly defined states (e.g. order status, login) |


**4.2 Boundary Value Analysis - two variants:**

| Variant | What you test |
| :-: | :-: |
| Two-point | The boundary + the nearest value on the other side |
| Three-point | The value below + at the boundary + above (more precise) |


**4.3 White-box techniques:**

| Technique | Goal |
| :-: | :-: |
| Statement testing | Every line of code executed ≥1 time |
| Branch testing | Every IF/ELSE branch (TRUE and FALSE) executed ≥1 time |


**5. Managing the test activities.**

**5.1 A test plan includes:**

| Element | Description |
| :-: | :-: |
| Scope and objectives | What and why we are testing |
| Approach | Levels, types, testing techniques |
| Resources | People, tools, environment |
| Schedule | When what happens |
| Risks | Register of identified risks |
| Entry/exit criteria | Conditions for starting/finishing |
| Communication | How we report progress |


**5.2 Test quadrants:**

| **Quadrant** | **Purpose** | **Nature** |
| :-: | :-: | :-: |
| Q1 | Technology-facing, supports the team | Component tests, integration tests |
| Q2 | Business-facing, supports the team | Functional tests, story tests |
| Q3 | Business-facing, critiques the product | Exploratory, usability, acceptance testing |
| Q4 | Technology-facing, critiques the product | Performance testing, other non-functional testing |


**5.3 Risk management:**

| Concept | Definition |
| :-: | :-: |
| Risk | A possible event with a negative effect |
| Risk level | Likelihood × impact |
| Project risk | Threatens the delivery of the project (delays, budget, staffing) |
| Product risk | Threatens the quality of the product (defects, security gaps) |
| Residual risk | What remains after mitigation actions |


**5.4 Reports and metrics:**

| Concept | Definition |
| :-: | :-: |
| Test progress report | Regular, ongoing |
| Test summary report | A single report, at the end of a phase/project |
| Test metrics | Number of defects, coverage, tests executed, residual risk |


**5.5 Severity vs Priority:**

| Concept | Definition |
| :-: | :-: |
| Severity | How serious the impact of the defect is on the system |
| Priority | How quickly it needs to be fixed |


**6. Test tools.**

### **6.1 Tool categories:**

| Category | Examples |
| :-: | :-: |
| Test management | Jira, TestRail, Xray |
| Static testing | SonarQube, ESLint, Pylint |
| Test design/implementation | TestRail, Xray, Zephyr |
| Test execution | Selenium, Playwright, Cypress, Appium |
| Coverage measurement | JaCoCo (Java), coverage.py (Python), Istanbul/nyc (JS) |
| Non-functional testing | Apache JMeter, Gatling, k6 |
| DevOps / CI/CD | Jenkins, GitHub Actions, GitLab CI/CD, Azure DevOps |
| Collaboration | Slack, Microsoft Teams, Confluence |
| Code and version control | Git, GitHub, GitLab, Bitbucket |
| Containerization | Docker, Kubernetes |
| API | Postman, Insomnia, SoapUI |
| Mobile test automation | Appium, Espresso, XCUITest |
| Results reporting | Allure Report, TestRail, Zephyr |
