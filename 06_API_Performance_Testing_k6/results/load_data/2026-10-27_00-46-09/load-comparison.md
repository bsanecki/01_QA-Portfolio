# Load Test Profile Comparison

| Run detail | Value |
|---|---|
| **Overall status** | **PASSED** |
| Generated | 2026-10-26 23:47:57 UTC |
| Target | https://dummyjson.com |
| Profiles | 1, 5, and 10 virtual users |
| Ramp / hold | 10s / 15s |

## Results by profile

| Profile | Status | Requests | Failed rate | Average | p90 | p95 | Checks | Thresholds |
|---:|---|---:|---:|---:|---:|---:|---|---:|
| 1 VU(s) | PASSED | 90 | 0.00% | 55.99 ms | 70.16 ms | 76.39 ms | 420/420 (100.00%) | 7/7 |
| 5 VU(s) | PASSED | 336 | 0.00% | 62.95 ms | 82.93 ms | 90.29 ms | 1568/1568 (100.00%) | 7/7 |
| 10 VU(s) | PASSED | 657 | 0.00% | 63.70 ms | 83.01 ms | 92.95 ms | 3066/3066 (100.00%) | 7/7 |

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
