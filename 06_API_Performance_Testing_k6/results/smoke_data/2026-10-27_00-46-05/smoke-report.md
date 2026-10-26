# Smoke Test Report

| Run detail | Value |
|---|---|
| **Status** | **PASSED** |
| Generated (UTC) | 2026-10-26T23:46:09.542Z |
| Run folder | 2026-10-27_00-46-05 |
| Target | https://dummyjson.com |
| Workload profile | 1 VU, 3 iterations |

## Summary

| Metric | Result |
|---|---:|
| HTTP requests | 9 |
| Request rate | 2.45 requests/s |
| Failed request rate | 0.00% |
| Average response time | 59.01 ms |
| Median response time | 60.03 ms |
| Minimum response time | 39.34 ms |
| Maximum response time | 81.00 ms |
| p90 response time | 71.84 ms |
| p95 response time | 76.42 ms |
| Checks | 42 of 42 checks passed (100.00%). |
| Peak virtual users | 1 |
| Completed iterations | 3 |
| Test duration | 3.67 s |
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
