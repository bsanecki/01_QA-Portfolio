# 06 - API Performance Testing with k6

Automated API performance testing of the public **DummyJSON** products API using **k6**. The project contains smoke, load, and stress scenarios, response validation checks, pass/fail thresholds, and timestamped Markdown and JSON reports for every run.

**API under test:** [dummyjson.com](https://dummyjson.com/)  
**Test stack:** k6 · JavaScript · Bash · GitHub Actions

The goal of this project is to demonstrate a practical performance testing workflow: verify that the API works correctly under minimal load, observe how response times behave as the number of virtual users increases, and document every run in a clear, repeatable report.

---

## Features

- Three test types: smoke, load, and stress
- Load profiles with 1, 5, and 10 virtual users, compared in a single report
- Functional response checks combined with performance thresholds
- Per-endpoint thresholds using k6 tags
- Timestamped Markdown and JSON reports for every run
- Configuration through environment variables
- Safety guards for non-public targets (authorization confirmation required)
- Capped profiles for the shared public API
- GitHub Actions workflow that runs the full suite and stores the reports

---

## Test scenarios

All three scenarios use the same request mix, making their results easier to compare under different load profiles.

| Test | Script | Profile | Purpose |
|---|---|---|---|
| Smoke | [`tests/smoke.js`](tests/smoke.js) | 1 VU, 3 iterations | Confirm that the API responds correctly under minimal load |
| Load | [`tests/load.js`](tests/load.js) | 1, 5, and 10 VUs (ramp-up, hold, ramp-down) | Observe response times under increasing load |
| Stress | [`tests/stress.js`](tests/stress.js) | Stepped ramp-up to 10 VUs on public DummyJSON | Observe how the API behaves as load increases |

### Endpoints and checks

Each iteration calls three endpoints and then waits for a short think time (1 second by default).

| Endpoint | Tag | Checks |
|---|---|---|
| `GET /products/{id}` | `product_by_id` | Status 200, JSON content type, ID matches the request, title and numeric price are present |
| `GET /products?limit=N` | `product_list` | Status 200, JSON content type, expected page size, `total` not smaller than the page, every product has an ID and title |
| `GET /products/search?q=...` | `product_search` | Status 200, JSON content type, at least one result, `total` not smaller than the page, every product has an ID and title |

This gives 14 checks per iteration.

### Thresholds

| Test | Thresholds |
|---|---|
| Smoke | `checks` rate = 100%, failed requests = 0%, p(90) < 1000 ms, p(95) < 1500 ms, at least 9 requests |
| Load | `checks` > 99%, failed requests < 1%, p(90) < 800 ms, p(95) < 1200 ms, plus p(95) limits per endpoint (1000 ms, 1200 ms, 1500 ms) |
| Stress | `checks` > 95%, failed requests < 5%, p(95) < 3000 ms |

Thresholds define the acceptance criteria for each test. A failed threshold should cause the corresponding k6 execution to fail.

---

## Test results

### Latest local results saved in the repository

The following results come from recorded local executions against public DummyJSON. They are not a guarantee of the service's general performance.

| Test | Status | Requests | Failed rate | Average | p95 | Checks | Thresholds |
|---|---|---:|---:|---:|---:|---:|---:|
| Smoke (1 VU, 3 iterations) | PASSED | 9 | 0.00% | 59.01 ms | 76.42 ms | 42/42 | 5/5 |
| Load - 1 VU | PASSED | 90 | 0.00% | 55.99 ms | 76.39 ms | 420/420 | 7/7 |
| Load - 5 VUs | PASSED | 336 | 0.00% | 62.95 ms | 90.29 ms | 1568/1568 | 7/7 |
| Load - 10 VUs | PASSED | 657 | 0.00% | 63.70 ms | 92.95 ms | 3066/3066 | 7/7 |
| Stress (up to 10 VUs) | PASSED | 720 | 0.00% | 68.62 ms | 156.07 ms | 3360/3360 | 3/3 |

### Observations

- The number of requests increases with the number of virtual users in the recorded load profiles: 90, 336, and 657 requests.
- Average response times remained relatively stable during these particular runs, ranging from approximately 56 to 64 ms.
- No failed requests or failed checks were recorded in the local runs listed above.
- The stress run had a higher p95 response time and a maximum response time of approximately 400 ms.
- Results can vary between runs because of network conditions and shared public infrastructure.

A subsequent GitHub Actions stress execution experienced intermittent connection resets and reported a failed stress test. This illustrates why results from a shared public API should be interpreted cautiously rather than treated as a reliable capacity benchmark.

### Recorded local runs

Reports from two complete local runs are included in [`results/`](results/).

| Run | Smoke | Load | Stress |
|---|---|---|---|
| Run 1 (00:17) | [smoke-report.md](results/smoke_data/2026-10-27_00-17-41/smoke-report.md) | [load-comparison.md](results/load_data/2026-10-27_00-17-45/load-comparison.md) | [stress-report.md](results/stress_data/2026-10-27_00-19-33/stress-report.md) |
| Run 2 (00:46) | [smoke-report.md](results/smoke_data/2026-10-27_00-46-05/smoke-report.md) | [load-comparison.md](results/load_data/2026-10-27_00-46-09/load-comparison.md) | [stress-report.md](results/stress_data/2026-10-27_00-47-57/stress-report.md) |

Run 1 had an average smoke response time of approximately 177 ms, compared with 59 ms in Run 2. Both local runs passed their configured thresholds, demonstrating how much results can vary between executions.

> DummyJSON is a shared public mock API. These short, capped runs are intended for learning and workflow validation. They are not a reliable capacity benchmark, and a passing result does not establish the maximum capacity of the service.

---

## Reports

Every run creates a timestamped folder under `results/<test>_data/` with a human-readable Markdown report and the full k6 summary in JSON.

```text
results/
├── smoke_data/
│   └── 2026-10-27_00-46-05/
│       ├── smoke-report.md
│       └── jsons/
│           └── smoke-summary.json
├── load_data/
│   └── 2026-10-27_00-46-09/
│       ├── load-comparison.md
│       └── jsons/
│           ├── load-1-vu-summary.json
│           ├── load-5-vu-summary.json
│           └── load-10-vu-summary.json
└── stress_data/
    └── 2026-10-27_00-47-57/
        ├── stress-report.md
        └── jsons/
            └── stress-summary.json
```

Each Markdown report contains run details, a metrics summary (requests, request rate, failed rate, average, median, minimum, maximum, p90, p95, checks, iterations, duration), threshold results, and a link to the raw JSON. The load report compares all three profiles side by side.

---

## Installation

Install [k6](https://grafana.com/docs/k6/latest/set-up/install-k6/) and make sure it is available on your `PATH`.

Verify the installation:

```bash
k6 version
```

No additional JavaScript libraries are required. The helper scripts are written in Bash, so on Windows they should be run in WSL or Git Bash.

---

## Running tests

Run commands from the `06_API_Performance_Testing_k6` directory.

```bash
# Smoke test
./scripts/run-test.sh smoke

# Load test (single profile, 5 VUs by default)
./scripts/run-test.sh load

# Load test with all profiles (1, 5, and 10 VUs) and a comparison report
./scripts/run-load-profiles.sh

# Stress test (the public API requires explicit confirmation)
ALLOW_PUBLIC_STRESS=yes ./scripts/run-test.sh stress
```

The runner creates a timestamped folder for each run, executes k6, and checks that the expected report files are created.

### Configuration

| Variable | Default | Description |
|---|---|---|
| `BASE_URL` | `https://dummyjson.com` | Target API |
| `PRODUCT_ID` | `1` | Product used by `GET /products/{id}` |
| `LIST_LIMIT` | `10` | Page size for `GET /products` |
| `SEARCH_QUERY` | `phone` | Query for `GET /products/search` |
| `THINK_TIME` | `1` | Pause between iterations, in seconds |
| `SMOKE_ITERATIONS` | `3` | Number of smoke iterations |
| `LOAD_VUS` | `5` | Virtual users in a single load run |
| `LOAD_RAMP` / `LOAD_HOLD` | `30s` / `1m` | Load stage durations for non-public targets |
| `STRESS_MAX_VUS` | `50` | Peak virtual users in the stress test for non-public targets |
| `STRESS_STEP_DURATION` | `1m` | Duration of each stress step for non-public targets |
| `CONFIRM_AUTHORIZED` | — | Must be `yes` for a non-public target, confirming authorization |
| `ALLOW_PUBLIC_STRESS` | — | Must be `yes` to run the stress test on public DummyJSON |

### Safety limits

Load testing a service without permission can cause harm, so the project includes built-in protection:

- **Public DummyJSON:** load profiles are capped at 10 virtual users with short stages (10-second ramp and 15-second hold). The stress test additionally requires `ALLOW_PUBLIC_STRESS=yes` and is capped at 10 VUs.
- **Other targets:** the tests refuse to start unless `CONFIRM_AUTHORIZED=yes` is set, confirming that the user is authorized to load-test the target.
- Input values such as `BASE_URL`, `PRODUCT_ID`, and `LOAD_VUS` are validated, and invalid values stop the test with a clear error.

---

## Continuous integration

The full workflow is located at [`../.github/workflows/performance-full.yml`](../.github/workflows/performance-full.yml). It runs the complete suite on demand using `workflow_dispatch`.

The workflow:

1. Sets up k6.
2. Runs the smoke test, all three load profiles, and the stress test.
3. Validates the generated Markdown report statuses.
4. Uploads the reports as a workflow artifact.
5. Commits generated reports back to the repository, when the workflow has write permission.
6. Fails the overall workflow if a test stage or report validation fails.

The lightweight smoke workflow is located at [`../.github/workflows/performance-smoke.yml`](../.github/workflows/performance-smoke.yml), if present. It is intended to run the smoke test automatically during routine CI checks.

Full load and stress tests are not run automatically on every push, avoiding unnecessary traffic to a shared public API.

---

## Project structure

```text
06_API_Performance_Testing_k6/
├── config/
│   └── config.js
├── lib/
│   ├── api.js
│   └── report.js
├── scripts/
│   ├── run-test.sh
│   └── run-load-profiles.sh
├── tests/
│   ├── smoke.js
│   ├── load.js
│   └── stress.js
├── results/
│   ├── smoke_data/
│   ├── load_data/
│   └── stress_data/
├── DEPENDENCIES.txt
└── README.md
```

---

## Skills demonstrated

- Performance test design: smoke, load, and stress scenarios
- Writing k6 tests in JavaScript, including checks, thresholds, tags, and stages
- Combining functional validation with performance metrics (average, p90, p95, failed rate)
- Interpreting results and understanding test limitations
- Custom reporting in Markdown and JSON
- Safe and responsible load testing practices
- Test automation with Bash scripts and GitHub Actions CI

**Project purpose:** demonstrate a repeatable performance testing workflow: define scenarios and thresholds, run them safely, generate clear reports, and interpret the results without overstating what they prove.
