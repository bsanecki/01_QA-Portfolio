# Load Test Profile Comparison

| Run detail | Value |
|---|---|
| **Overall status** | **PASSED** |
| Generated | 2026-10-27 00:19:33 UTC |
| Target | https://dummyjson.com |
| Profiles | 1, 5, and 10 virtual users |
| Ramp / hold | 10s / 15s |

## Results by profile

| Profile | Status | Requests | Failed rate | Average | p90 | p95 | Checks | Thresholds |
|---:|---|---:|---:|---:|---:|---:|---|---:|
| 1 VU(s) | PASSED | 81 | 0.00% | 113.22 ms | 160.60 ms | 162.43 ms | 378/378 (100.00%) | 7/7 |
| 5 VU(s) | PASSED | 297 | 0.00% | 116.90 ms | 165.34 ms | 171.58 ms | 1386/1386 (100.00%) | 7/7 |
| 10 VU(s) | PASSED | 582 | 0.00% | 116.07 ms | 170.91 ms | 174.79 ms | 2716/2716 (100.00%) | 7/7 |

## Interpretation

- The profiles ran sequentially against the same target with the same request mix.
- Compare request counts and response-time percentiles across profiles; the elapsed wall-clock runs and public network conditions can affect results.
- DummyJSON is a shared public mock API. These short, capped runs are for learning and workflow validation, not a reliable capacity benchmark.
- A passing result means the configured checks and thresholds passed for that run; it does not establish the maximum capacity of the service.

## Raw data

- [1 VU profile JSON](./jsons/load-1-vu-summary.json)
- [5 VU profile JSON](./jsons/load-5-vu-summary.json)
- [10 VU profile JSON](./jsons/load-10-vu-summary.json)

---

*Generated automatically by scripts/run-load-profiles.sh.*
