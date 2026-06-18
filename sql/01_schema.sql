/*
Purpose:
Create the core relational database schema for the Terp Protect campus safety analytics project.
Current Scope:
This schema supports the first completed data pipeline:
- UMPD Daily Crime and Incident Logs
- Year: 2025
- Clean input file: data/processed/clean_daily_incidents_2025.csv
Design Notes:
The schema uses a simple star-schema structure:
- fact_incident stores incident-level events
- dimension tables store reusable date, crime type, disposition, and location attributes
Future sources such as Arrest Logs, CSA Logs, and Uniform Crime Reports will be added in later schema versions.
*/
PRAGMA foreign_keys = ON;
DROP TABLE IF EXISTS fact_incident;
DROP TABLE IF EXISTS dim_location;
DROP TABLE IF EXISTS dim_disposition;
DROP TABLE IF EXISTS dim_crime_type;
DROP TABLE IF EXISTS dim_date;
CREATE TABLE dim_date (
    date_id INTEGER PRIMARY KEY,
    full_date TEXT NOT NULL UNIQUE,
    year INTEGER,
    quarter INTEGER,
    month INTEGER,
    month_name TEXT,
    day INTEGER,
    weekday TEXT,
    day_of_week_number INTEGER,
    is_weekend INTEGER,
    semester_period TEXT
);
CREATE TABLE dim_crime_type (
    crime_type_id INTEGER PRIMARY KEY,
    crime_type TEXT NOT NULL,
    crime_group TEXT NOT NULL,
    source_type TEXT NOT NULL,
    UNIQUE (crime_type, crime_group, source_type)
);
CREATE TABLE dim_disposition (
    disposition_id INTEGER PRIMARY KEY,
    disposition TEXT NOT NULL,
    disposition_group TEXT NOT NULL,
    is_arrest_related INTEGER DEFAULT 0,
    is_pending INTEGER DEFAULT 0,
    is_closed INTEGER DEFAULT 0,
    UNIQUE (disposition, disposition_group)
);
CREATE TABLE dim_location (
    location_id INTEGER PRIMARY KEY,
    location_raw TEXT NOT NULL,
    location_group TEXT NOT NULL,
    jurisdiction_group TEXT DEFAULT 'Unknown',
    is_on_campus INTEGER DEFAULT NULL,
    UNIQUE (location_raw, location_group)
);
CREATE TABLE fact_incident (
    incident_id TEXT PRIMARY KEY,
    case_number TEXT,
    occurred_date_id INTEGER,
    reported_date_id INTEGER,
    crime_type_id INTEGER,
    disposition_id INTEGER,
    location_id INTEGER,
    occurred_datetime TEXT,
    reported_datetime TEXT,
    report_delay_hours REAL,
    report_delay_days REAL,
    delay_bucket TEXT,
    hour INTEGER,
    source_type TEXT,
    source_url TEXT,
    scraped_at TEXT,
    has_valid_case_number INTEGER,
    has_valid_occurred_datetime INTEGER,
    has_valid_reported_datetime INTEGER,
    has_valid_reporting_delay INTEGER,
    FOREIGN KEY (occurred_date_id) REFERENCES dim_date (date_id),
    FOREIGN KEY (reported_date_id) REFERENCES dim_date (date_id),
    FOREIGN KEY (crime_type_id) REFERENCES dim_crime_type (crime_type_id),
    FOREIGN KEY (disposition_id) REFERENCES dim_disposition (disposition_id),
    FOREIGN KEY (location_id) REFERENCES dim_location (location_id)
);
CREATE INDEX idx_fact_incident_case_number
ON fact_incident (case_number);
CREATE INDEX idx_fact_incident_occurred_date
ON fact_incident (occurred_date_id);
CREATE INDEX idx_fact_incident_reported_date
ON fact_incident (reported_date_id);
CREATE INDEX idx_fact_incident_crime_type
ON fact_incident (crime_type_id);
CREATE INDEX idx_fact_incident_disposition
ON fact_incident (disposition_id);
CREATE INDEX idx_fact_incident_location
ON fact_incident (location_id);