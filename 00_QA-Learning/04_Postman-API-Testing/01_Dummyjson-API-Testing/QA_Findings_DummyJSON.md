# QA Findings & Observations — DummyJSON REST API

**Manual & Exploratory API Testing** | QA Portfolio Documentation

---

## Overview

| Field | Value |
|---|---|
| **Prepared by** | Bartosz Sanecki — Manual QA / API Testing |
| **Target API** | DummyJSON (https://dummyjson.com) — public demo/testing REST API |
| **Scope** | Authorization, Products, Carts, and Users endpoints |
| **Testing Type** | Manual API testing — functional, validation, and negative test cases |
| **Document Type** | Findings / Bug Report compilation |

### Important Classification Note

DummyJSON is a public demo/testing API, not a production system, and does not persist most write operations. Throughout this document, findings are conservatively classified as **Bug**, **Finding**, or **Observation** based on the strength of evidence available. Severity/Priority values are **illustrative examples** of how each item would be triaged in a real production application — not an assertion about DummyJSON's own severity.

### Classification Legend

| Label | Meaning |
|---|---|
| **Bug** | A clear, confirmed deviation from expected/documented behavior |
| **Finding** | A potential validation or logic problem observed during testing, supported by a well-formed test request |
| **Observation** | A behavior that may be intentional or a consequence of the demo/test environment, documented without an official specification to confirm intended behavior |

---

## ISSUE-001 — Refresh Token Validation Accepts Arbitrary Tokens

| Field | Value |
|---|---|
| **Project / API** | DummyJSON |
| **Module** | Authorization |
| **Endpoint** | POST /auth/refresh |
| **Test Case** | POST 12 — Refresh with invalid token |
| **Type** | Finding |
| **Environment** | DummyJSON (demo/test API) |
| **Status** | Documented |
| **Date** | 28.08.2026 |
| **Reporter** | Bartosz Sanecki |

**Severity / Priority**

| Severity | Priority | Justification |
|---|---|---|
| Medium *(illustrative — see QA Analysis)* | Medium | In a real production auth system this pattern would warrant investigation; rated Medium rather than High since DummyJSON has no real token/session backend and this is not a confirmed vulnerability |

**Description**
Testing verifies whether the refresh-token endpoint validates the supplied `refreshToken` value before issuing new tokens.

**Preconditions**
No prior valid authentication session was required for this test.

**Steps to Reproduce**
1. Send `POST /auth/refresh` with an arbitrary, non-issued value in the `refreshToken` field (e.g. `"abc"`).
2. Observe the HTTP status code and response body.
3. Repeat with additional arbitrary values (`"123"`, `"invalid-refresh-token"`, and other arbitrary strings).
4. Compare results across all attempts.

**Test Data**
Confirmed invalid values used for `refreshToken`: `"abc"`, `"123"`, `"invalid-refresh-token"`, and other arbitrary strings. *(Exact full request payload was not preserved in source material.)*

**Expected Result**
An invalid or expired refresh token should be rejected (e.g. `401 Unauthorized`), with no new access token issued.

**Actual Result**
The API returned `200 OK` and generated a new `accessToken` and `refreshToken` for every invalid value tested — no rejection observed.

**QA Analysis**
The endpoint does not appear to validate the `refreshToken` value prior to issuing new tokens. In a real production authentication system this pattern would warrant serious concern. However, DummyJSON is a demo/testing API without a real backing token store or session model, so this is documented as an API behavior observation rather than a confirmed security vulnerability.

**Notes / Limitations**
> Severity/Priority above are illustrative values for how this would be triaged in a real production system — not an assertion about DummyJSON itself. Do not treat as a confirmed security vulnerability without further verification against an official specification.

---

## ISSUE-002 — Search with Empty Query Returns All Products

| Field | Value |
|---|---|
| **Module** | Products |
| **Endpoint** | GET /products/search |
| **Test Case** | GET 05 — Search with empty query |
| **Type** | Observation |
| **Environment** | DummyJSON (demo/test API) |
| **Status** | Documented |

**Severity / Priority**

| Severity | Priority | Justification |
|---|---|---|
| Low *(illustrative)* | Low | Behavior is plausible by design; no spec available to confirm intent |

**Description**
Testing evaluates API behavior when the search query parameter (`q`) is submitted empty.

**Steps to Reproduce**
1. Send `GET /products/search` with `q` set to an empty string.
2. Observe the returned result set.

**Test Data**
`q = ""` (empty string)

**Expected Result**
Not formally defined. Depending on product specification, an empty query could reasonably result in: all products returned, an empty list, `400 Bad Request`, or the frontend not issuing the request at all.

**Actual Result**
The API returned the full product list.

**QA Analysis**
Without an official API specification defining intended behavior for an empty search query, this cannot be classified as a confirmed bug. Expected behavior here is a product/specification decision, not purely a technical correctness question.

**Notes / Limitations**
> Do not classify as a confirmed defect. Flag for clarification against product requirements if this were a real project.

---

## ISSUE-003 — Invalid Data Type Accepted for Price During Product Creation

| Field | Value |
|---|---|
| **Module** | Products |
| **Endpoint** | POST /products/add |
| **Test Case** | POST 19 |
| **Type** | Finding |
| **Environment** | DummyJSON (demo/test API) |
| **Status** | Documented |

**Severity / Priority**

| Severity | Priority | Justification |
|---|---|---|
| Medium | Medium | Missing type validation on a core commerce field (price) |

**Description**
Testing verifies whether the product creation endpoint validates the data type of the `price` field.

**Steps to Reproduce**
1. Send `POST /products/add` with `price` set to a non-numeric string value.
2. Observe the HTTP status code and response body.

**Test Data**
```json
{ "price": "free" }
```

**Expected Result**
The API should reject the request since `price` should be numeric (e.g. `400 Bad Request`).

**Actual Result**
The API accepted `"price": "free"` and returned `201 Created`.

**QA Analysis**
The request itself was correctly configured (valid JSON, correct field name), which isolates the issue to missing data-type validation on the `price` field. This is a valid API validation finding.

**Notes / Limitations**
> The request was syntactically valid and contained an intentionally invalid field type; the endpoint did not reject it, isolating this as a validation gap.

---

## ISSUE-004 — Invalid Data Type Accepted for Price During Product Update

| Field | Value |
|---|---|
| **Module** | Products |
| **Endpoint** | PATCH /products/1 |
| **Test Case** | PATCH 24 |
| **Type** | Finding |
| **Environment** | DummyJSON (demo/test API) |
| **Status** | Documented |

**Severity / Priority**

| Severity | Priority | Justification |
|---|---|---|
| Medium | Medium | Mirrors ISSUE-003 for the update path |

**Description**
Testing verifies whether the product update endpoint validates the data type of the `price` field, mirroring ISSUE-003 for the update path.

**Steps to Reproduce**
1. Send `PATCH /products/1` with `price` set to a non-numeric string value.
2. Observe the HTTP status code and response body.

**Test Data**
```json
{ "price": "free" }
```

**Expected Result**
The API should reject the invalid price type (e.g. `400 Bad Request`).

**Actual Result**
The API accepted `"price": "free"` and returned a modified product response containing the invalid value.

**QA Analysis**
Consistent with ISSUE-003 — both creation and update paths for products lack type validation on the `price` field.

**Notes / Limitations**
> DummyJSON simulates updates; this finding does not imply the invalid value was permanently stored in a database (see ISSUE-005).

---

## ISSUE-005 — Product Update Is Not Persistent

| Field | Value |
|---|---|
| **Module** | Products |
| **Endpoint** | PATCH /products/1 |
| **Test Case** | PATCH 27A, GET 27 |
| **Type** | Observation |
| **Environment** | DummyJSON (demo/test API) |
| **Status** | Documented |

**Severity / Priority**

| Severity | Priority | Justification |
|---|---|---|
| Low (informational) | Low | Expected behavior for a mock/demo API, not a defect |

**Description**
Testing verifies whether a successful PATCH update is reflected in a subsequent GET request for the same resource.

**Steps to Reproduce**
1. Send `PATCH /products/1` updating `price` to `7777`.
2. Confirm the PATCH response reflects the new value.
3. Send `GET /products/1` to retrieve the resource again.
4. Compare the GET response value against the PATCH response value.

**Test Data**
PATCH response value: `price = 7777`

**Expected Result**
If the API claims to persist updates, a subsequent GET should return `price = 7777`.

**Actual Result**
The PATCH response returned `price = 7777`, but the subsequent GET returned the original value, `price = 19.99`.

**QA Analysis**
The update appears to be simulated at the response level and is not persistently stored server-side. This is expected behavior for a mock/demo API and reflects DummyJSON's documented design rather than a defect.

**Notes / Limitations**
> Do not describe this as a confirmed production bug.

---

## ISSUE-006 — Floating-Point Precision in Cart Total

| Field | Value |
|---|---|
| **Module** | Carts |
| **Endpoint** | POST /carts/add |
| **Test Case** | POST 06 |
| **Type** | Observation |
| **Environment** | DummyJSON (demo/test API) |
| **Status** | Documented |

**Severity / Priority**

| Severity | Priority | Justification |
|---|---|---|
| Low *(illustrative)* | Low | Not exaggerated given the demo nature of the API |

**Description**
Testing evaluates the numeric precision of calculated monetary totals returned when adding items to a cart.

**Steps to Reproduce**
1. Send `POST /carts/add` with cart items producing a fractional total.
2. Inspect the `total` and `discountedTotal` fields in the response.

**Test Data**
Observed response values: `total = 29.979999999999997`, `discountedTotal = 25`.

**Expected Result**
Monetary values should typically use appropriate decimal precision, e.g. `29.98` rather than `29.979999999999997`.

**Actual Result**
The API returned a raw floating-point representation: `total = 29.979999999999997`.

**QA Analysis**
This is a floating-point precision/representation issue rather than a functional defect in the underlying calculation. Especially relevant for real-world payment or e-commerce systems, where display and rounding of monetary values matters.

**Notes / Limitations**
> Severity intentionally not exaggerated given the demo nature of the API.

---

## ISSUE-007 — Non-Existing Product ID Accepted During Cart Creation

| Field | Value |
|---|---|
| **Module** | Carts |
| **Endpoint** | POST /carts/add |
| **Test Case** | POST 08 |
| **Type** | Observation |
| **Environment** | DummyJSON (demo/test API) |
| **Status** | Documented |

**Severity / Priority**

| Severity | Priority | Justification |
|---|---|---|
| Low *(illustrative)* | Low | No spec requiring product ID validation |

**Description**
Testing evaluates how the cart creation endpoint handles a product ID that does not exist in the catalog.

**Steps to Reproduce**
1. Send `POST /carts/add` including at least one non-existing product ID among the cart items.
2. Observe the HTTP status code and returned cart contents.
3. Inspect the returned cart ID.

**Test Data**
Known to have contained a non-existing product ID (full payload not preserved).

**Expected Result**
If the specification requires validation of product IDs, the request should be rejected with an indication that the product does not exist.

**Actual Result**
The request was accepted and a cart was returned; the non-existing product was silently omitted. The returned cart ID was `209`, a value also observed in other create/update operations.

**QA Analysis**
Without an official specification requiring rejection of unknown product IDs, this cannot be classified as a confirmed bug. The repeated cart ID (209) is noted for completeness but not automatically classified as a bug — may be part of DummyJSON's simulation behavior.

**Notes / Limitations**
> Flag for clarification against product requirements if this were a real project; do not classify as confirmed defect.

---

## ISSUE-008 — Negative Product Quantity Accepted

| Field | Value |
|---|---|
| **Module** | Carts |
| **Endpoint** | POST /carts/add |
| **Test Case** | POST 09 |
| **Type** | Finding |
| **Environment** | DummyJSON (demo/test API) |
| **Status** | Documented |

**Severity / Priority**

| Severity | Priority | Justification |
|---|---|---|
| Medium | Medium | Could cause incorrect cart/order calculations in a real system |

**Description**
Testing verifies whether the cart endpoint validates that product quantity is non-negative.

**Steps to Reproduce**
1. Send `POST /carts/add` with `quantity = -1` for a cart item.
2. Observe the HTTP status code, response body, and calculated totals.

**Test Data**
```json
{ "quantity": -1 }
```

**Expected Result**
The API should reject a negative quantity (e.g. `400 Bad Request`), since quantity cannot logically be negative.

**Actual Result**
The API returned `201 Created` and accepted `quantity = -1`. Response contained negative calculated values: `total = -9.99`, `discountedPrice = -9`, `totalQuantity = -1`.

**QA Analysis**
In a real e-commerce application, accepting negative quantities could cause incorrect cart calculations and downstream financial or business-logic issues (e.g. incorrect order totals, inventory counts, or discounts).

**Notes / Limitations**
> Severity/Priority are suggested illustrative values for a real production system.

---

## ISSUE-009 — Zero Product Quantity Normalized to One

| Field | Value |
|---|---|
| **Module** | Carts |
| **Endpoint** | POST /carts/add |
| **Test Case** | POST 10 |
| **Type** | Observation |
| **Environment** | DummyJSON (demo/test API) |
| **Status** | Documented |

**Severity / Priority**

| Severity | Priority | Justification |
|---|---|---|
| Low *(illustrative)* | Low | No spec defining zero-quantity handling |

**Description**
Testing verifies how the cart endpoint handles a submitted quantity of zero.

**Steps to Reproduce**
1. Send `POST /carts/add` with `quantity = 0` for a cart item.
2. Observe the quantity value returned in the response.

**Test Data**
```json
{ "quantity": 0 }
```

**Expected Result**
Depending on specification, the API should either reject `quantity = 0` (`400 Bad Request`), remove the product from the cart, or otherwise explicitly define zero-quantity handling.

**Actual Result**
`quantity = 0` was not preserved; the response instead contained `quantity = 1`.

**QA Analysis**
Without a formal specification defining intended behavior for zero quantity, this cannot be called a confirmed bug — it is documented behavior that should be verified against product requirements.

**Notes / Limitations**
> Do not classify as a confirmed bug without a specification.

---

## ISSUE-010 — Missing First Name Accepted During User Creation

| Field | Value |
|---|---|
| **Module** | Users |
| **Endpoint** | POST /users/add |
| **Test Case** | POST 08 |
| **Type** | Observation |
| **Environment** | DummyJSON (demo/test API) |
| **Status** | Documented |

**Severity / Priority**

| Severity | Priority | Justification |
|---|---|---|
| Low *(illustrative)* | Low | No spec confirming firstName is mandatory |

**Description**
Testing verifies whether the user creation endpoint enforces `firstName` as a required field.

**Steps to Reproduce**
1. Send `POST /users/add` omitting the `firstName` field from the request body.
2. Observe the HTTP status code and the `firstName` value in the created user.

**Test Data**
Known to have omitted the `firstName` field (full payload not preserved).

**Expected Result**
If `firstName` is required, the API should reject the request with `400 Bad Request`.

**Actual Result**
The API returned `201 Created` and created a user with an empty `firstName`.

**QA Analysis**
There is no formal API specification confirming `firstName` is mandatory. Classified as an Observation / Potential Validation Issue rather than a confirmed Finding, since the "correct" behavior here depends entirely on an unstated business rule.

**Notes / Limitations**
> Do not classify as a confirmed bug without a specification defining required fields.

---

## ISSUE-011 — Invalid Data Type Accepted for Age During User Creation

| Field | Value |
|---|---|
| **Module** | Users |
| **Endpoint** | POST /users/add |
| **Test Case** | POST 09 |
| **Type** | Finding |
| **Environment** | DummyJSON (demo/test API) |
| **Status** | Documented |

**Severity / Priority**

| Severity | Priority | Justification |
|---|---|---|
| Low *(illustrative)* | Low | Well-formed request isolates this to a validation gap |

**Description**
Testing verifies whether the user creation endpoint validates the data type of the `age` field.

**Steps to Reproduce**
1. Send `POST /users/add` with `age` set to a non-numeric string value.
2. Observe the HTTP status code and the `age` value in the created user.

**Test Data**
```json
{ "age": "twenty" }
```

**Expected Result**
If `age` is defined as numeric, the API should reject the request with `400 Bad Request`.

**Actual Result**
The API returned `201 Created` and accepted `"age": "twenty"`.

**QA Analysis**
This is a clear example of schema/type validation testing: a well-formed request with an intentionally incorrect field type was accepted without rejection.

**Notes / Limitations**
> The request was syntactically valid and contained an intentionally invalid field type; the endpoint did not reject it, isolating this as a validation gap.

---

## ISSUE-012 — User Update Is Not Persistent

| Field | Value |
|---|---|
| **Module** | Users |
| **Endpoint** | PATCH /users/1 |
| **Test Case** | PATCH 11, GET 15 |
| **Type** | Observation |
| **Environment** | DummyJSON (demo/test API) |
| **Status** | Documented |

**Severity / Priority**

| Severity | Priority | Justification |
|---|---|---|
| Low (informational) | Low | Consistent with ISSUE-005, expected for a mock API |

**Description**
Testing verifies whether a successful PATCH update to a user resource is reflected in a subsequent GET request.

**Steps to Reproduce**
1. Send `PATCH /users/1` updating `age` to `35`.
2. Confirm the PATCH response reflects the new value.
3. Send `GET /users/1` to retrieve the resource again.
4. Compare the GET response value against the PATCH response value.

**Test Data**
PATCH response value: `age = 35`. A separate, earlier PUT request also changed `firstName`, with the same non-persistence behavior on a subsequent GET.

**Expected Result**
If the update is persistent, GET after PATCH should return `age = 35`.

**Actual Result**
The PATCH response showed the updated value (`age = 35`), but the subsequent GET returned the original value, `age = 29`. A previously tested PUT request showed the same pattern for `firstName`.

**QA Analysis**
DummyJSON appears to simulate PUT/PATCH operations by echoing the submitted change in the response, without persistently storing the change server-side. Consistent with ISSUE-005 for the Products module.

**Notes / Limitations**
> Do not present this as a confirmed production defect.

---

## Summary Table

| ID | Module | Finding | Type | Severity | Priority |
|---|---|---|---|---|---|
| ISSUE-001 | Authorization | Refresh Token Validation Accepts Arbitrary Tokens | Finding | Medium | Medium |
| ISSUE-002 | Products | Search with Empty Query Returns All Products | Observation | Low | Low |
| ISSUE-003 | Products | Invalid Data Type Accepted for Price (Create) | Finding | Medium | Medium |
| ISSUE-004 | Products | Invalid Data Type Accepted for Price (Update) | Finding | Medium | Medium |
| ISSUE-005 | Products | Product Update Is Not Persistent | Observation | Low | Low |
| ISSUE-006 | Carts | Floating-Point Precision in Cart Total | Observation | Low | Low |
| ISSUE-007 | Carts | Non-Existing Product ID Accepted | Observation | Low | Low |
| ISSUE-008 | Carts | Negative Product Quantity Accepted | Finding | Medium | Medium |
| ISSUE-009 | Carts | Zero Product Quantity Normalized to One | Observation | Low | Low |
| ISSUE-010 | Users | Missing First Name Accepted | Observation | Low | Low |
| ISSUE-011 | Users | Invalid Data Type Accepted for Age | Finding | Low | Low |
| ISSUE-012 | Users | User Update Is Not Persistent | Observation | Low | Low |

---

## Overall QA Assessment

**Scope of Testing**
Testing covered four functional areas of the DummyJSON API — Authorization, Products, Carts, and Users — using manual, exploratory API test cases. Coverage included positive-path functional checks as well as negative and boundary tests: invalid tokens, invalid or missing field types, empty query parameters, negative and zero quantities, and verification of update persistence across PATCH/PUT and subsequent GET requests.

**Validation Problems Observed**
Multiple endpoints across Products (`price`) and Users (`age`, `firstName`) accepted requests with incorrect data types or missing fields that would typically be expected to fail input validation (ISSUE-003, 004, 010, 011). The `/auth/refresh` endpoint issued new tokens for arbitrary, non-issued `refreshToken` values without rejecting the request (ISSUE-001). The Carts endpoint accepted a negative quantity and produced negative calculated totals (ISSUE-008), and normalized a zero quantity to one without documented justification (ISSUE-009).

**Persistence Behavior Observed**
Both Products and Users update operations (`PATCH /products/1`, `PATCH /users/1`) echoed the submitted change in the immediate response but did not persist the change: a subsequent GET request returned the original, pre-update value in each case (ISSUE-005, ISSUE-012). This pattern is consistent with a simulated/mocked write layer rather than a genuine data store.

**What Should Not Be Considered a Confirmed Production Bug**
Several items are documented as Observations rather than Bugs or confirmed Findings because their correct behavior depends on business rules or an official specification that was not available during this testing effort: the empty-query search result (ISSUE-002), acceptance of a non-existing product ID in a cart (ISSUE-007), zero-quantity normalization (ISSUE-009), and the persistence behavior of Products and Users updates (ISSUE-005, ISSUE-012), which reflects DummyJSON's demo-API design rather than a defect. The `/auth/refresh` behavior (ISSUE-001) is documented as unexpected behavior specific to this demo API and is explicitly **not** classified as a confirmed security vulnerability, since DummyJSON does not implement a real token/session backend.

**What These Findings Demonstrate**
This testing effort demonstrates a structured, evidence-based manual API testing approach: functional verification, negative testing of input validation, boundary-value testing (zero/negative quantities), and cross-request consistency checks (PATCH response vs. subsequent GET) to detect persistence issues. Findings are consistently classified according to the strength of available evidence (Bug / Finding / Observation) rather than assumed severity, and severity/priority ratings are presented as illustrative examples for a production context rather than definitive judgments about a demo API.
