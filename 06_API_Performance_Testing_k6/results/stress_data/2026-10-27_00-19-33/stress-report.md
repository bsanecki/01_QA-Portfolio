# Stress Test Report

| Run detail | Value |
|---|---|
| **Status** | **PASSED** |
| Generated (UTC) | 2026-10-27T00:20:34.384Z |
| Run folder | 2026-10-27_00-19-33 |
| Target | https://dummyjson.com |
| Workload profile | Ramp up to 10 virtual users |

## Summary

| Metric | Result |
|---|---:|
| HTTP requests | 651 |
| Request rate | 10.75 requests/s |
| Failed request rate | 0.00% |
| Average response time | 115.72 ms |
| Median response time | 155.53 ms |
| Minimum response time | 16.91 ms |
| Maximum response time | 738.04 ms |
| p90 response time | 165.00 ms |
| p95 response time | 168.11 ms |
| Checks | 3038 of 3038 checks passed (100.00%). |
| Peak virtual users | 10 |
| Completed iterations | 217 |
| Test duration | 60.55 s |
| Thresholds passed | 3/3 |

## Threshold Results

| Metric | Threshold | Result |
|---|---|---|
| `checks` | `rate>0.95` | PASS |
| `http_req_failed` | `rate<0.05` | PASS |
| `http_req_duration` | `p(95)<3000` | PASS |

## Notes

- The status reflects the configured response checks and k6 thresholds for this run.
- DummyJSON is a public mock API. These measurements are affected by network conditions and shared infrastructure; they are not a reliable capacity benchmark.
- No performance conclusion should be generalized beyond the conditions of this execution.

## Raw Data

[Open the full k6 summary JSON](./jsons/stress-summary.json)

---

*Generated automatically by the project's k6 reporting helper.*
