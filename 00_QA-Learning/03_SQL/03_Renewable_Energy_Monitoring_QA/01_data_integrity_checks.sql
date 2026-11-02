-- Installations with zero or negative rated power
SELECT id,name,rated_power_kw FROM installations
WHERE rated_power_kw <= 0;

-- Energy readings with a negative produced value
SELECT installation_id,energy_produced_kwh FROM energy_readings
WHERE energy_produced_kwh < 0;

-- Energy readings with a missing (NULL) produced value
SELECT installation_id,energy_produced_kwh FROM energy_readings
WHERE energy_produced_kwh IS NULL;

-- Energy readings exceeding the installation's rated power
SELECT energy_readings.installation_id,energy_readings.energy_produced_kwh,installations.rated_power_kw FROM energy_readings
JOIN installations
ON energy_readings.installation_id = installations.id
WHERE energy_readings.energy_produced_kwh > installations.rated_power_kw;

-- Duplicate readings (same installation, same date)
SELECT installation_id, reading_date, COUNT(*) AS occurrences
FROM energy_readings
GROUP BY installation_id, reading_date
HAVING COUNT(*) > 1;

-- Readings dated before the installation's commissioning date
SELECT energy_readings.reading_date,installations.commissioning_date FROM installations
JOIN energy_readings
ON installations.id = energy_readings.installation_id
WHERE installations.commissioning_date > energy_readings.reading_date;

-- Energy readings referencing a non-existent installation
SELECT energy_readings.id, energy_readings.installation_id
FROM energy_readings
LEFT JOIN installations
ON energy_readings.installation_id = installations.id
WHERE installations.id IS NULL;

-- Maintenance logs referencing a non-existent installation
SELECT maintenance_logs.id, maintenance_logs.installation_id
FROM maintenance_logs
LEFT JOIN installations
ON maintenance_logs.installation_id = installations.id
WHERE installations.id IS NULL;

-- Installations with no maintenance log recorded
SELECT installations.id, installations.name
FROM installations
LEFT JOIN maintenance_logs
ON installations.id = maintenance_logs.installation_id
WHERE maintenance_logs.id IS NULL;

