# Bug Report — Renewable Energy Monitoring Data QA

Findings from running `01_data_integrity_checks.sql` against `oze_qa.db`.

| Bug ID | Description | Query | Expected | Actual | Severity |
|---|---|---|---|---|---|
| BUG-001 | Installation with zero or negative rated power | Check 1 | `rated_power_kw` is always > 0 | "Broken Config Unit" has `rated_power_kw = -50.0`; "Zero Power Unit" has `rated_power_kw = 0.0` | High |
| BUG-002 | Energy reading with a negative produced value | Check 2 | `energy_produced_kwh` is always ≥ 0 | Installation id 1 has a reading of `-45.0 kWh` | High |
| BUG-003 | Energy reading with a missing (NULL) produced value | Check 3 | Every reading has a recorded energy value | Installation id 1 has a reading with `energy_produced_kwh = NULL` | Medium |
| BUG-004 | Energy reading exceeding the installation's rated power | Check 4 | `energy_produced_kwh` never exceeds `rated_power_kw` | Installation id 2 (rated 2000 kW) has a reading of `5000 kWh` | Critical |
| BUG-005 | Duplicate reading for the same installation and date | Check 5 | Each installation has at most one reading per date | Installation id 1 has two identical readings dated 2023-06-01 | Medium |
| BUG-006 | Reading dated before the installation's commissioning date | Check 6 | `reading_date` is always on or after `commissioning_date` | Installation id 3 (commissioned 2022-06-10) has a reading dated 2022-01-01 | Medium |
| BUG-007 | Energy reading linked to an installation ID that doesn't exist | Check 7 | Every reading references a valid, existing installation | A reading references `installation_id = 99`, which is not in `installations` | Critical |
| BUG-008 | Maintenance log linked to an installation ID that doesn't exist | Check 8 | Every maintenance log references a valid, existing installation | A log references `installation_id = 99`, which is not in `installations` | Critical |

## Observations (not classified as bugs)

- **Check 9** — several installations have no maintenance log at all. This is not a data integrity bug, but an operational finding worth flagging to the maintenance team, since it may indicate installations that have never been serviced.

## Summary

- **8 issues found**, spanning invalid value ranges, physically implausible readings, duplicate records, and broken referential integrity.
- **3 Critical**, **2 High**, **3 Medium** — no issues were rated Low, as each finding could either corrupt reported energy production figures or break the link between telemetry data and its source installation.
- All issues would need to be raised with the development/data team before this dataset could be considered reliable for reporting or dashboards.
