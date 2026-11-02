# Postman — Notes

## 00. Golden Rule — Always Save Every Request

After creating or modifying a request, click **Save** and make sure it is saved inside the correct collection. Unsaved requests may disappear after refreshing Postman or may not work correctly in Collection Runner.

**Schema:**
```
Create → Configure → Save → <collection name>
```

---

## 01. HTTP Methods

| Method | What it's for | Example |
|---|---|---|
| `GET` | Retrieving data | Get a user |
| `POST` | Creating data | Create a user |
| `PUT` | Full resource update | Update a user |
| `PATCH` | Partial update | Change only the email |
| `DELETE` | Deleting data | Delete a user |
| `HEAD` | Retrieves header information without a body | Check whether a resource exists |
| `OPTIONS` | Checks available methods/options | Check which methods an endpoint supports |

> **Important:** JSONPlaceholder is a test/mock API. Because of this, some operations, e.g. `POST`/`PUT`/`PATCH`/`DELETE`, don't persist real changes to a permanent database.

---

## 02. HTTP Status Codes

| Code | Name | Meaning |
|---|---|---|
| 🟢 200 | OK | Request completed successfully |
| 🟢 201 | Created | A new resource was created |
| 🟢 204 | No Content | Success, but no response body |
| 🔵 301 | Moved Permanently | The resource has been permanently moved |
| 🔵 302 | Found | Temporary redirect |
| 🔴 400 | Bad Request | Invalid request |
| 🔴 401 | Unauthorized | No valid authentication |
| 🔴 403 | Forbidden | No permission |
| 🔴 404 | Not Found | Resource not found |
| 🔴 405 | Method Not Allowed | HTTP method not allowed |
| 🔴 409 | Conflict | Conflict with the current state of the resource |
| 🔴 422 | Unprocessable Content | Data is logically invalid |
| ⚫ 500 | Internal Server Error | Internal server error |
| ⚫ 502 | Bad Gateway | Problem with an intermediary server |
| ⚫ 503 | Service Unavailable | Server temporarily unavailable |
| ⚫ 504 | Gateway Timeout | The response timed out |

**Code ranges:**

| Range | Meaning |
|---|---|
| 2xx | ✅ Success |
| 3xx | 🔄 Redirection |
| 4xx | ❌ Client error |
| 5xx | 💥 Server error |

---

## 03. Parameters

### 1. Path Parameters
A parameter located in the URL path that points to a specific resource.
```
GET /users/5
```
`5` → the user's ID.

> Path Parameter = a specific resource

### 2. Query Parameters
A parameter located after `?` that passes additional information to the API.
```
GET /posts?userId=1
```

| Example | Use case |
|---|---|
| `?userId=1` | filtering |
| `?search=test` | searching |
| `?limit=10` | limiting results |
| `?page=2` | page selection |
| `?sort=name` | sorting |

> Query Parameter = a filter / option / additional criterion

### 3. Multiple Query Parameters
Multiple parameters can be used at once, separated by `&`.
```
GET /posts?userId=1&id=5
```

### 4. Pagination
Splitting a large number of results into pages.
```
GET /posts?_page=2&_limit=5
```

| Parameter | Meaning |
|---|---|
| `_page=2` | second page |
| `_limit=5` | max. 5 results |

> The API does not automatically move to the next page — the application has to send the next request itself.

### 5. Filtering
Most commonly implemented through Query Parameters.
```
GET /posts?userId=1
```
→ returns posts belonging to user 1.

### 6. Sorting
```
GET /users?sort=name&order=asc
```
→ sorts by name in ascending order. Parameter names depend on the specific API.

### Path vs Query

| Path | Query |
|---|---|
| `/users/5` | `/users?id=5` |
| a specific resource | an additional criterion |
| part of the path | after `?` |

---

## 04. Headers & Body

**Headers** — additional information sent with a request, e.g. data format or authorization.

**Content-Type** — specifies the data format of the Body.
```
Content-Type: application/json
```

**Body** — data sent to the API, e.g. with `POST`, `PUT`, `PATCH`.
```json
{
  "name": "Test User",
  "email": "test@example.com"
}
```

**Request** → Method, URL, Headers, Body
**Response** → Status Code, Headers, Body

---

## 05. Authentication

**Authentication** — the process of verifying whether a client is allowed to access the API.

### Bearer Token / JWT
The token obtained after logging in is sent in the Header:
```
Authorization: Bearer <token>
```

| Case | Result |
|---|---|
| No token | 401 Unauthorized |
| Invalid token | 401 Unauthorized |
| Valid token | 200 OK |

### API Key
A key used to identify/authenticate the client. It can be passed e.g. as:
```
X-API-Key: <key>
```
or as a Query Parameter:
```
?api_key=<key>
```

### Basic Auth
Authentication using:
```
Username + Password
```
Postman sends:
```
Authorization: Basic <credentials>
```

> Basic Auth does not encrypt data — it should be used with HTTPS.

---

## 06. Variables

**Variables** store values that are reused across multiple requests.

### Basic usage
```
{{baseUrl}}/users
{{accessToken}}
{{userId}}
```

**Example:**

| Variable | Value |
|---|---|
| `baseUrl` | `https://api.example.com` |
| `accessToken` | `eyJ...` |

Instead of typing the full URL:
```
https://api.example.com/users
```
we use:
```
{{baseUrl}}/users
```

### Token
A token can be stored as a variable:
```
accessToken = eyJ...
```
and used as:
```
Authorization: Bearer {{accessToken}}
```
This way, the token only needs to be changed in one place.

**Key takeaway:** `{{variable}}` is the syntax for referencing a variable in Postman.

Variables can be used in, among others:
- URL
- Headers
- Authorization
- Body

---

## 07. Postman API Testing Cookbook

Tests in Postman are used to automatically verify API responses.

| # | Test | What it checks | Example |
|---|---|---|---|
| 01 | Status Code | Whether the API returned the expected HTTP code | 200, 201, 404 |
| 02 | Response Body | Whether the response contains the expected data | `json.id` exists |
| 03 | Field Value | Whether a field has a specific value | `id = 1` |
| 04 | Data Type | Whether a field has the correct data type | `id` → number |
| 05 | Response Time | Whether the API responds fast enough | < 1000 ms |
| 06 | Headers | Whether the response contains required headers | `Content-Type` |
| 07 | JSON Structure | Whether the response has the expected structure | `id`, `name`, `email` |
| 08 | Array Is Not Empty | Whether the returned array contains data | `[]` → FAIL |
| 09 | Array Element Exists | Whether an array element contains a required field | `json[0].id` |
| 10 | Required Fields | Whether all required fields exist | `id`, `name`, `email` |
| 11 | Empty / Null | Whether a required field is not empty / null | `email` |
| 12 | String Validation | Whether a value is text | `name` → string |
| 13 | Number Validation | Whether a value is a number | `id` → number |
| 14 | Boolean Validation | Whether a value is true / false | `active` → boolean |
| 15 | Authentication | Whether the API correctly handles authorization | 200 / 401 |
| 16 | Negative Test | Whether the API correctly rejects an invalid request | 400, 401, 404 |
| 17 | Error Response | Whether an error has the correct structure | `error.code`, `message` |
| 18 | POST Validation | Whether resource creation completed successfully | 201 Created |
| 19 | PUT/PATCH Validation | Whether a resource update completed successfully | 200 / 204 |
| 20 | DELETE Validation | Whether resource deletion completed successfully | 200 / 204 |
| 21 | Combined Test | Several independent checks on a single response | status + body + fields + time |

### Most commonly used snippets

```js
const json = pm.response.json();
```
Retrieves the Response Body as JSON.

```js
pm.expect(json.id).to.exist;
```
Checks whether a field exists.

```js
pm.expect(json.id).to.eql(1);
```
Checks a specific value.

```js
pm.expect(json.id).to.be.a("number");
```
Checks the data type.

```js
pm.response.to.have.status(200);
```
Checks the HTTP status.

> **Golden rule:** a test's purpose is not just to confirm that the request "works." It has to verify that the actual response matches the expectation/specification.

---

## 08. Scripts

Scripts in Postman are mainly used to automate work with requests and responses.

| # | Topic | Use case | Schema |
|---|---|---|---|
| 01 | Response → Variable | Extracting a value from the response and saving it as a Variable | Response → Script → Variable |
| 02 | Variable → Request | Using a saved value in a subsequent request | `{{variable}}` |
| 03 | Simple If Logic | Running code only when a condition is met | `if (condition) { ... }` |
| 04 | Iterate Through Array | Performing an operation for each array element | `array.forEach(...)` |
| 05 | Debugging with console.log() | Inspecting a value while the script runs | `console.log(value)` |

Scripts fall into two main types, depending on when they run (see also section 14):

- **Pre-request Script** — runs **before** the request is sent
- **Post-request / Test Script** — runs **after** the response is received

Working with scripts relies on the global **`pm`** object (see section 14).

---

## 09. Collection Runner

Collection Runner lets you run multiple requests from a collection automatically, instead of sending them one by one. Each request can have its own tests, and the Runner shows a **PASS / FAIL** result for each of them.

`Iterations` defines how many times the entire collection will be executed.

> **Important:** requests must be saved inside the collection, otherwise the Runner may not see their URLs and may not execute them correctly.

**Schema:**
```
Collection → Runner → Requests → Tests → PASS / FAIL
```

The Runner can additionally:
- run the entire collection sequentially,
- persist variables between requests (e.g. a token saved in request #1 is available in request #5),
- run tests multiple times (`Iterations`),
- schedule runs.

> **Collection Runner ≠ CLI.** The Runner is for interactive running/debugging inside the Postman app. Postman CLI is needed when tests must run without Postman open — e.g. in CI/CD (see section 21).

---

## 10. Workspaces

A **Workspace** is a space for organizing work related to an API.

It can contain, among others: **collections, environments, monitors, mock servers, and documentation**.

**Workspace types:**

| Type | Meaning |
|---|---|
| Internal | for a team |
| Partner | for invited partners |
| Public | publicly accessible |

The workspace type can be changed under: **Workspace Overview → Settings**.

Collaboration within a workspace/project can happen through comments (see section 12).

---

## 11. Collections — extended

A **Collection** is a group of related API requests together with scripts, variables, documentation, and examples.

Main use cases:
- organizing requests,
- storing **tests and scripts**,
- documentation,
- automation via **Collection Runner**,
- sharing and versioning.

**Good practice:** organize requests by **resource** (e.g. *Users*, *Tasks*, *Books*), not by HTTP method — see section 28 (organizing a collection by domain).

---

## 12. Environments & Variable Scopes

An Environment lets you store variables used across multiple requests, so instead of:
```
https://api.example.com
```
you use:
```
{{baseUrl}}
```

This makes it possible to switch between, e.g., **development / staging / production** without editing requests.

### Variable scopes — from broadest to narrowest

1. **Global**
2. **Environment**
3. **Collection**
4. **Local**

> **Important:** a narrower scope can override a variable of the same name from a broader scope.

`{{variable}}` → Postman substitutes the variable's value when the request is executed.

> **Naming note:** `baseURL` and `baseUrl` are **two different variables** — case matters.

---

## 13. Mock Servers

A **Mock Server** lets you **simulate a working API**, returning pre-prepared responses — the backend doesn't have to exist yet.

The mock relies on the **Example Responses** saved in the Collection, which define:
- method,
- path,
- status code,
- headers,
- body.

**Typical use case:** the frontend can be tested before the backend is ready.

The mock server's URL can be set as the value of an environment variable (e.g. `baseURL`), which means the same collection of requests can be run against either the mock or the real API.

---

## 14. Testing Scripts — pm, pre-request and post-request

Postman lets you use **JavaScript** to automate requests and test responses. Working with Postman relies on the global **`pm`** object.

### Pre-request Script
- runs **before** the request is sent
- typical use case: preparing data, setting a variable, generating a dynamic value

### Post-request Script (Test Script)
- runs **after** the response is received
- can, among other things:
  - check the status code,
  - check the body,
  - validate the JSON structure,
  - extract values from the response,
  - save a value (e.g. a **token**) to a variable, to use it in the next request.

> This makes it possible to run a dozen or so precise, chained requests instead of manually creating dozens of nearly identical tests.

---

## 15. First Project — good organizational practices

### Test Scripts in practice
- Postman lets you write JavaScript scripts to automatically verify responses.
- Typical example: a **post-response script** that checks the status code.
- If a test doesn't pass, it's worth checking in order:
  1. HTTP method
  2. endpoint URL
  3. expected status code
  4. the status code saved in the Example Response

### HTTP methods when extending a collection
When extending a project, additional methods typically get added: **POST**, **PUT**, **DELETE** (in addition to the basic GET).

---

## 16. Collaboration

Postman enables direct team collaboration on collections:
- comments on an entire collection/request,
- inline comments on a specific fragment of a request,
- `@mentioning` other team members,
- replying in a thread and marking comments as resolved.

---

## 17. API Testing — Scope of Quality

API testing isn't limited to checking whether an endpoint returns correct data. It covers, among others:

| Area | What it checks |
|---|---|
| **Functionality** | whether the API works according to requirements |
| **Reliability** | whether it behaves stably |
| **Performance** | response time, throughput, behavior under load |
| **Security** | authorization, vulnerabilities, data exposure |

### Different roles → different testing goals

| Role | Testing goal |
|---|---|
| Developer | correctness of individual endpoints |
| QA | end-to-end behavior + regression |
| Automation Engineer | repeatable tests in CI/CD |
| Security | vulnerabilities, configuration, data exposure |
| Performance Engineer | response time, throughput, load |
| API Designer/Architect | contract consistency and correctness |
| Product Owner | compliance with product requirements |

> API testing is therefore **cross-functional**, not exclusively QA's domain.

---

## 18. Areas API Testing Should Cover

### Rate limiting
We check:
- request limits,
- `429 Too Many Requests`,
- the `Retry-After` header.

### Response accuracy
Whether the response contains:
- correct values,
- correct calculations,
- correct relationships between data.

### Data validation
The API should validate:
- required fields,
- data types,
- min/max,
- format,
- enum values.

> Example tested on DummyJSON: `price: "free"`, `age: "twenty"`, `quantity: -1` — i.e. values that are invalid in type/logic, which the API should either reject or handle correctly.

### Response time
We test response speed both under normal traffic and under heavier load.

### Edge cases
Examples:
- empty arrays,
- `null`,
- very long strings,
- maximum values,
- Unicode,
- concurrent updates (simultaneous updates to the same resource).

### Response format / schema
We check the stability of:
- JSON schema,
- field names,
- data types,
- pagination structure.

> This is especially important, since API clients may depend on a specific response structure.

---

## 19. Four Basic Types of Testing

| Test type | What it checks |
|---|---|
| **Unit testing** | a small, isolated piece of code; fast and very specific tests |
| **Contract testing** | whether the API honors an established contract (request/response structure) |
| **End-to-end testing** | the entire flow through several components/systems |
| **Load testing** | the API's behavior under heavy load |

> Not every test needs to be done at every level — the type of test is chosen to fit the goal.

---

## 20. API Test Automation

API automation = tests executed automatically via tools/scripts instead of manually running every case.

### Why do we automate?

1. **Less manual work** — especially with regression testing
2. **Consistency** — the exact same checks are performed every time
3. **CI/CD** — tests can run automatically after code changes and block faulty code before deployment

### 4 main benefits of automation (expanded)

- **Speed** — hundreds of tests in a short amount of time
- **Consistency** — the same tests always executed the same way
- **Early detection** — fast detection of regressions
- **Coverage** — easier testing of many data combinations

> **Manual → Automation:** automation does not replace QA. It automates the repeatable execution of tests, while QA remains responsible for designing tests, interpreting results, and choosing scenarios.

---

## 21. A Typical API Testing Pipeline

```
Developer writes code
        ↓
   Commit / Push
        ↓
  CI triggers tests
        ↓
     Unit tests
        ↓
Contract / Integration / E2E tests
        ↓
 Performance / Load tests
        ↓
       Deploy
        ↓
Smoke tests + monitoring
```

This flow shows the full cycle: unit tests during development → CI after push → integration/contract/E2E on staging → performance/load → deployment → smoke testing and monitoring in production.

---

## 22. Generating a Collection from OpenAPI

Instead of manually creating dozens of requests, you can import an **OpenAPI/Swagger YAML** file — Postman will generate a collection based on the specification. The specification describes, among other things, endpoints, methods, parameters, and response schemas.

---

## 23. Forking a Collection

If there's a collection acting as a source/reference, you create a **fork** for your own tests instead of modifying the original.

```
Original collection → Fork → your own tests
```

This lets you develop the test version independently from the source.

---

## 24. Collection-Level vs Request-Level Tests

This is one of the key distinctions in designing a test suite.

### Collection / Folder level
A test shared across many requests, e.g.:
```
status === 200
response time < 2000 ms
Content-Type === application/json
```
It doesn't need to be copied into every single request.

### Request level
A test specific to a particular endpoint, e.g. `/weather/{airportCode}` must return:
```
temperature
wind
visibility
```

### The rule

> **Shared → collection/folder. Specific → request.**

This is the **DRY — Don't Repeat Yourself** approach, very useful when building a real test suite rather than just individual requests.

---

## 25. False Positives

**A passing test ≠ a good test.** You have to check whether the test would actually catch the problem.

Good practices:
- analyzing the root cause of a failure,
- checking dependencies between data,
- properly chaining requests,
- **deliberately breaking something and checking whether the test fails**.

```
The test should PASS
        ↓
deliberately change the expected value
        ↓
the test should FAIL
        ↓
if it still PASSes → the test is broken
```

> **The most important meta-pattern:** a test should be able to detect a failure, not just pass.

---

## 26. Postman Snippets

Postman has a library of ready-made test fragments — you can quickly add things like:
- status code,
- response time,
- JSON schema,
- headers.

> **Important:** a snippet is only a starting point. The assertion has to be adjusted to the API's actual contract.

---

## 27. Agent Mode

Postman can generate tests based on API responses.

```
Agent
  ↓
generates a test
  ↓
QA review
  ↓
fix
  ↓
verification
  ↓
only then is the test valuable
```

> The Agent generates a **first draft**, and QA has to review it. Generated tests should never be dropped into a collection without review.

---

## 28. Error Handling — Testing Failures

Test not only the happy path — deliberately trigger errors (e.g. 404, 401, 403, 500).

For every tested error, check the same set of elements:
```
status → Content-Type → required headers → body/schema → the specific message
```

Check:
- status code,
- Content-Type,
- required headers,
- the structure of the error body,
- whether the error message is useful.

**RFC 7807** → the standard format for error responses: `application/problem+json`.

### Example error-testing pattern

```js
pm.test("Status code is 404", () => {
    pm.response.to.have.status(404);
});

pm.test("Content-Type is problem+json", () => {
    pm.expect(pm.response.headers.get("Content-Type"))
        .to.include("application/problem+json");
});

pm.test("Correlation ID exists", () => {
    pm.response.to.have.header("x-correlation-id");
});
```

The same schema works for different error codes (404, 401, 403, 500) — mainly the expected status and error details change, which lets you cut down on test duplication.

---

## 29. Data Validation Pattern

`200 OK` alone doesn't mean the response is correct. A single test can check several aspects of the response contract at once:
```
required field + format + enum + data type
```

```js
pm.expect(data).to.have.property("airportCode");
pm.expect(data.airportCode).to.match(/^[A-Z]{4}$/);
pm.expect(data.status).to.be.oneOf(["active", "closed"]);
pm.expect(data.temperature).to.be.a("number");
```

Validate:
- required fields,
- data types,
- formats,
- ranges,
- enum / allowed values.

---

## 30. skipTest Pattern

If a request unexpectedly returns `404`, tests validating the body can be skipped instead of producing a false FAIL.

```js
if (pm.response.code === 404) {
    console.warn("Skipping validation — test data unavailable");
} else {
    // validation tests
}
```

Decision schema:
```
request
   ↓
  404?
 ├── YES → skip validation
 └── NO → run validation
```

> **Don't apply this to tests whose actual purpose is to verify a 404** — in that case you want the test to genuinely verify that error code, not skip it.

---

## 31. Performance Testing in Postman

- `pm.response.responseTime` → response time
- `pm.response.size` → response size

```js
pm.test("Response time is below 500 ms", () => {
    pm.expect(pm.response.responseTime).to.be.below(500);
});
```

A broader pattern for evaluating performance:
```
response time + response size + multiple iterations + result analysis
```

**Rules:**
- Don't judge performance based on a single request — a single spike may be caused by e.g. the network.
- With a larger number of iterations, you can analyze a pattern, e.g. whether 95% of responses fall within a given threshold.
- Collection Runner can be used to run multiple iterations / simulate multiple users.

---

## 32. Data-Driven Testing

Instead of writing a separate test for every case:
```
test 1 → airport = WAW
test 2 → airport = LHR
test 3 → airport = JFK
test 4 → airport = CDG
```

you do this:
```
ONE TEST
    ↓
  CSV / JSON
    ↓
 multiple data rows
    ↓
multiple iterations
```

Postman runs the same collection once for every row of data in the file.

> **Write tests once, add scenarios by adding data.**

**Good practice:** don't create 500 test cases right away. Start with **5–10 representative cases → run → analyze → expand the dataset**.

---

## 33. Postman CLI and CI/CD

```
Postman Collection
        ↓
    Postman CLI
        ↓
  GitHub Actions
        ↓
 automated tests
        ↓
PASS → continue
FAIL → the pipeline can stop
```

Postman CLI runs **the same collections and tests** that were created inside the Postman app — you don't build a separate set of tests specifically for the CLI.

### Collection Runner vs CLI vs Postman API

| Tool | Use case |
|---|---|
| **Collection Runner** | Running and debugging tests inside Postman |
| **Data files** | Testing multiple scenarios against different data |
| **Postman CLI** | Running collections from the terminal / CI/CD |
| **Postman API** | Programmatically managing Postman resources |

> **The key distinction:** the CLI runs tests. The Postman API manages Postman.

### Postman API
Lets you programmatically manage, among others:
- Workspaces,
- Collections,
- Environments,
- Monitors,
- access/roles.

This means you can automate even **the setup of the test environment**, not just the execution of tests.

### The bigger picture of the automation module
```
1. Collection Runner
        ↓
2. Data-driven testing
        ↓
3. Postman CLI
        ↓
4. Postman API
        ↓
5. CI/CD
```

> **Automation gives you speed, but it does not automatically give you good tests.** If the test assumptions are wrong or the documentation is outdated, automation simply produces incorrect results faster.

---

## 34. Reusable / Modular Tests

Instead of copying the same validation function into multiple requests:
```
❌ Request A → its own validation
❌ Request B → copied validation
❌ Request C → copied validation
```

you build a shared library:
```
Package library
        ↓
shared validation functions
   ↙     ↓     ↘
Request A  Request B  Request C
```

In other words: **write once → use everywhere**.

### module.exports as a public contract

```js
module.exports = {
    validateMetar,
    validateWindData
}
```

Exports should be treated like a **public API**:

| Change | Safe? |
|---|---|
| adding a new function | ✅ safe |
| adding an optional parameter | ✅ safe |
| fixing a bug | ✅ safe |
| renaming a function | ❌ breaking change |
| removing a function | ❌ breaking change |
| changing the shape of returned data | ❌ breaking change |

### A consistent shape for returned data

Every validation function should return data in the same, consistent shape, e.g.:
```js
{
    valid: true,
    error: null
}
```

This makes it possible to chain multiple validators into a single pipeline:
```
validateMetar()
validateWindData()
validateVisibility()
validateTemperature()
        ↓
the same result shape
        ↓
easy to combine into one pipeline
```

> **A uniform output = easy test composition.**

### pm.require() — importing shared logic

Instead of copying code between requests:
```js
const { validateMetar } = pm.require('@postair/metar-validators');
```

This corresponds to the mindset: **Library → import → test**, rather than **Library → copy code → paste → copy → paste**.

---

## 35. Chained / Dependent Requests

Request #1 returns data that Request #2 then uses:
```
GET /airports
       ↓
  airportCode
       ↓
GET /metars/{{airportCode}}
       ↓
GET /forecast/{{airportCode}}
```

Instead of hardcoding a value (e.g. `ATL`), it is fetched dynamically from the previous request and saved as a variable (e.g. in a Test Script via `pm.environment.set(...)` / `pm.collectionVariables.set(...)`).

---

## 36. Environment-Driven Testing

Environment-specific values **should not be hardcoded directly into the request**.

**❌ Wrong:**
```
https://test-api.example.com
API_KEY=123456
```

**✅ Correct:**
```
{{baseUrl}}
{{apiKey}}
```

The environment decides which values actually get substituted:
```
Test environment
      ↓
{{baseUrl}} = test-api...

Production
      ↓
{{baseUrl}} = api...
```

This means **the same collection can run against different environments** without manually editing requests.

---

## 37. Organizing a Collection by Domain

**Don't** use this as the main way to organize a collection:
```
GET
POST
PUT
DELETE
```

**Instead**, group by the API's functionality/domain:
```
📁 Airports
   ├── Get airports
   └── Get airport

📁 Weather
   ├── Get forecast
   └── Get METAR

📁 Reports
   └── ...
```

> Group by the functionality/domain of the API, not by HTTP method.

---

## 38. Setup → Test → Teardown

```
SETUP
   ↓
prepare a token / test data
   ↓
TEST
   ↓
run requests + assertions
   ↓
TEARDOWN
   ↓
clean up the data
```

This structure makes a folder/test more self-contained and safe to run repeatedly (e.g. in CI/CD, where test data shouldn't accumulate between runs).

---

## 39. Supplement — Standard Postman Features (likely shown in the video, not captured in the text notes)

The items below are standard features of the Postman platform that typically appear in the hands-on part of a course (shown on screen) but don't always make it into text notes. Worth knowing as a supplement to the patterns above:

### Postman Console
A tool for inspecting full requests and responses (raw headers, body, execution time) — useful for debugging when `console.log()` inside a script isn't enough. Usually opened as a separate panel in the app.

### Built-in dynamic variables
Postman provides ready-made variables that generate data on the fly, useful e.g. for tests requiring random/unique data:
```
{{$guid}}        — a random UUID
{{$timestamp}}   — the current Unix time
{{$randomEmail}} — a random email address
{{$randomInt}}   — a random integer
```

### Saving variables from a script
```js
pm.environment.set("token", jsonData.token);        // variable in the current environment
pm.collectionVariables.set("orderId", jsonData.id);  // variable at the collection level
pm.globals.set("sessionId", jsonData.session);        // global variable
```
This is the practical implementation of the chained requests pattern (section 35) — this is exactly how you save a value from one response so it can be used in the next request.

### Visualizer
Lets you render a response (e.g. JSON) as a readable HTML/table view inside Postman — useful for browsing larger responses without copying them into an external tool.

### Monitors
A feature that lets you run a collection on a scheduled, recurring basis (e.g. every hour) directly from Postman's servers, independent of the app being open — used, among other things, to monitor API availability over time.

### Importing specs and generating documentation
Beyond importing OpenAPI/Swagger (section 22), Postman can also automatically generate readable **collection documentation** (visible publicly or to the team) based on saved requests, examples, and descriptions.

---

## 🧠 Ultra-Short Cheat Sheet — 7 Key Test-Suite Design Patterns

```
1. Reusable tests          → shared logic instead of copying
2. module.exports          → functions as a public contract
3. Consistent output       → { valid, error }
4. pm.require()            → importing shared functions
5. Chained requests        → result of A → input for B
6. Environment variables   → {{baseUrl}}, {{apiKey}}, {{token}}
7. Setup → Test → Teardown → prepare → test → clean up
```

**The most important picture of the whole architecture:**
```
        Postman Package Library
                 ↓
             pm.require()
                 ↓
    ┌────────────┼────────────┐
    ↓            ↓            ↓
Request A    Request B    Request C
    ↓                          ↑
    └──────── data ─────────────┘
                 ↓
            Environment
        {{baseUrl}} {{token}}
```

This is already a **QA automation / test-framework design** mindset, not just clicking through individual requests in Postman.
