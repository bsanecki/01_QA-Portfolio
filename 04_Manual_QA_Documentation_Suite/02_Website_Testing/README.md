## Project Contents

### 1. Test Documentation

`Website_Manual_QA_Documentation.xlsx`

The Excel workbook contains three worksheets:

- **Test Info** - project information, testing scope, environment, and test summary.
- **Test Cases** - test scenarios, execution steps, expected and actual results, statuses, and related bug IDs.
- **Bug Reports** - defect descriptions, reproduction steps, expected and actual results, and supporting evidence links.

### 2. API Testing

API testing is performed using Postman to verify endpoint behavior, response status codes, response data, and error handling.

This section may include:

- Postman collections and requests
- HTTP method and status code validation
- Response body and data validation
- Positive and negative test scenarios
- API test scripts and assertions
- Evidence of test execution

### 3. Evidence Recordings

The `evidence/` directory contains video recordings demonstrating the reported website defects. The recordings are also available through Loom.

### 4. Reported Defects

| Bug ID | Title | Description | Evidence |
|---|---|---|---|
| WEB-BUG-001 | Logout Redirect | After clicking Logout, the user is logged out but is not redirected to the homepage. | [Watch on Loom](https://www.loom.com/share/739a707672634ec19aed6c72a5b1a24c) |
| WEB-BUG-002 | Shopping Cart Persistence | Products removed from the cart reappear after navigating to another page and returning to the cart. | [Watch on Loom](https://www.loom.com/share/d5828cb78e2a481d930a16ea6f3da6b8) |
