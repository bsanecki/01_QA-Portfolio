# Renewable Energy Monitoring — Data QA

SQL project focused on validating data integrity in a renewable energy monitoring database (solar and wind installations) — the kind of checks a QA tester would run on telemetry and sensor data before it reaches a monitoring dashboard.

## Dataset

Custom SQLite database (`oze_qa.db`) simulating a renewable energy monitoring system: `installations`, `energy_readings`, `maintenance_logs`. The dataset was seeded with intentionally injected data issues to simulate real-world QA validation scenarios on sensor/telemetry data (invalid values, physically impossible readings, duplicate records, and broken relationships between tables).

## Files

- `01_data_integrity_checks.sql`
- `oze_qa.db`
- `BUG_REPORT.md`

## Checks Performed

1. Installations with zero or negative rated power
2. Energy readings with a negative produced value
3. Energy readings with a missing (NULL) produced value
4. Energy readings exceeding the installation's rated power (physically impossible)
5. Duplicate readings for the same installation and date
6. Readings dated before the installation's commissioning date
7. Energy readings referencing a non-existent installation (orphaned foreign key)
8. Maintenance logs referencing a non-existent installation (orphaned foreign key)
9. Installations with no maintenance log recorded (operational check, not a data bug)

## Skills Used

- SELECT
- JOIN (INNER, LEFT)
- GROUP BY
- HAVING
- COUNT()
- WHERE
- Data validation
- Referential integrity checks
- Duplicate detection
- NULL handling
- Range/plausibility checks
