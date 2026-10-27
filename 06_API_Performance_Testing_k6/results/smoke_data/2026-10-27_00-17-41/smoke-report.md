# Smoke Test Report

| Run detail | Value |
|---|---|
| **Status** | **PASSED** |
| Generated (UTC) | 2026-10-27T00:17:45.709Z |
| Run folder | 2026-10-27_00-17-41 |
| Target | https://dummyjson.com |
| Workload profile | 1 VU, 3 iterations |

## Summary

| Metric | Result |
|---|---:|
| HTTP requests | 9 |
| Request rate | 1.92 requests/s |
| Failed request rate | 0.00% |
| Average response time | 177.01 ms |
| Median response time | 175.64 ms |
| Minimum response time | 36.21 ms |
| Maximum response time | 604.60 ms |
| p90 response time | 265.30 ms |
| p95 response time | 434.95 ms |
| Checks | 42 of 42 checks passed (100.00%). |
| Peak virtual users | 1 |
| Completed iterations | 3 |
| Test duration | 4.69 s |
| Thresholds passed | 5/5 |

## Threshold Results

| Metric | Threshold | Result |
|---|---|---|
| `http_req_failed` | `rate==0` | PASS |
| `checks` | `rate==1` | PASS |
| `http_reqs` | `count>=9` | PASS |
| `http_req_duration` | `p(90)<1000` | PASS |
| `http_req_duration` | `p(95)<1500` | PASS |

## Notes

- The status reflects the configured response checks and k6 thresholds for this run.
- DummyJSON is a public mock API. These measurements are affected by network conditions and shared infrastructure; they are not a reliable capacity benchmark.
- No performance conclusion should be generalized beyond the conditions of this execution.

## Raw Data

[Open the full k6 summary JSON](./jsons/smoke-summary.json)

---

*Generated automatically by the project's k6 reporting helper.*
