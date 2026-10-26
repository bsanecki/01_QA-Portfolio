# Stress Test Report

| Run detail | Value |
|---|---|
| **Status** | **PASSED** |
| Generated (UTC) | 2026-10-26T23:48:58.604Z |
| Run folder | 2026-10-27_00-47-57 |
| Target | https://dummyjson.com |
| Workload profile | Ramp up to 10 virtual users |

## Summary

| Metric | Result |
|---|---:|
| HTTP requests | 720 |
| Request rate | 11.88 requests/s |
| Failed request rate | 0.00% |
| Average response time | 68.62 ms |
| Median response time | 61.07 ms |
| Minimum response time | 20.59 ms |
| Maximum response time | 400.12 ms |
| p90 response time | 94.47 ms |
| p95 response time | 156.07 ms |
| Checks | 3360 of 3360 checks passed (100.00%). |
| Peak virtual users | 10 |
| Completed iterations | 240 |
| Test duration | 60.62 s |
| Thresholds passed | 3/3 |

## Threshold Results

| Metric | Threshold | Result |
|---|---|---|
| `checks` | `rate>0.95` | PASS |
| `http_req_duration` | `p(95)<3000` | PASS |
| `http_req_failed` | `rate<0.05` | PASS |

## Notes

- The status reflects the configured response checks and k6 thresholds for this run.
- DummyJSON is a public mock API. These measurements are affected by network conditions and shared infrastructure; they are not a reliable capacity benchmark.
- No performance conclusion should be generalized beyond the conditions of this execution.

## Raw Data

[Open the full k6 summary JSON](./jsons/stress-summary.json)

---

*Generated automatically by the project's k6 reporting helper.*
