PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS fact_arrest;
DROP TABLE IF EXISTS fact_incident;
DROP TABLE IF EXISTS dim_charge_category;
DROP TABLE IF EXISTS dim_demographic;
DROP TABLE IF EXISTS dim_location;
DROP TABLE IF EXISTS dim_disposition;
DROP TABLE IF EXISTS dim_crime_type;
DROP TABLE IF EXISTS dim_date;

CREATE TABLE dim_date (
    date_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_date DATE NOT NULL UNIQUE,
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
    crime_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    crime_type TEXT NOT NULL,
    crime_group TEXT NOT NULL,
    source_type TEXT,
    UNIQUE (crime_type, crime_group, source_type)
);

CREATE TABLE dim_disposition (
    disposition_id INTEGER PRIMARY KEY AUTOINCREMENT,
    disposition TEXT NOT NULL,
    disposition_group TEXT NOT NULL,
    is_arrest_related INTEGER DEFAULT 0,
    is_pending INTEGER DEFAULT 0,
    is_closed INTEGER DEFAULT 0,
    UNIQUE (disposition, disposition_group)
);

CREATE TABLE dim_location (
    location_id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_raw TEXT NOT NULL,
    location_group TEXT NOT NULL,
    jurisdiction_group TEXT DEFAULT 'Unknown',
    is_on_campus INTEGER,
    UNIQUE (location_raw, location_group)
);

CREATE TABLE dim_demographic (
    demographic_id INTEGER PRIMARY KEY AUTOINCREMENT,
    race TEXT NOT NULL,
    sex TEXT NOT NULL,
    age_group TEXT NOT NULL,
    UNIQUE (race, sex, age_group)
);

CREATE TABLE dim_charge_category (
    charge_category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    charge_category TEXT NOT NULL UNIQUE,
    is_alcohol_related INTEGER DEFAULT 0,
    is_drug_related INTEGER DEFAULT 0,
    is_theft_related INTEGER DEFAULT 0
);

CREATE TABLE fact_incident (
    incident_id TEXT PRIMARY KEY,
    case_number TEXT,
    occurred_date_id INTEGER,
    reported_date_id INTEGER,
    crime_type_id INTEGER,
    disposition_id INTEGER,
    location_id INTEGER,
    occurred_datetime TIMESTAMP,
    reported_datetime TIMESTAMP,
    report_delay_hours REAL,
    report_delay_days REAL,
    delay_bucket TEXT,
    hour INTEGER,
    source_type TEXT,
    source_url TEXT,
    scraped_at TIMESTAMP,
    has_valid_case_number INTEGER,
    has_valid_occurred_datetime INTEGER,
    has_valid_reported_datetime INTEGER,
    has_valid_reporting_delay INTEGER,
    FOREIGN KEY (occurred_date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (reported_date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (crime_type_id) REFERENCES dim_crime_type(crime_type_id),
    FOREIGN KEY (disposition_id) REFERENCES dim_disposition(disposition_id),
    FOREIGN KEY (location_id) REFERENCES dim_location(location_id)
);

CREATE TABLE fact_arrest (
    arrest_id TEXT PRIMARY KEY,
    arrest_number TEXT,
    case_number TEXT,
    arrest_date_id INTEGER,
    demographic_id INTEGER,
    charge_category_id INTEGER,
    arrested_datetime TIMESTAMP,
    arrested_charge TEXT,
    arrested_hour INTEGER,
    source_year INTEGER,
    source_url TEXT,
    scraped_at TIMESTAMP,
    has_valid_arrest_number INTEGER,
    has_valid_case_number INTEGER,
    has_valid_arrested_datetime INTEGER,
    has_charge_text INTEGER,
    FOREIGN KEY (arrest_date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (demographic_id) REFERENCES dim_demographic(demographic_id),
    FOREIGN KEY (charge_category_id) REFERENCES dim_charge_category(charge_category_id)
);

CREATE INDEX idx_fact_incident_case_number
ON fact_incident(case_number);

CREATE INDEX idx_fact_incident_occurred_date
ON fact_incident(occurred_date_id);

CREATE INDEX idx_fact_incident_reported_date
ON fact_incident(reported_date_id);

CREATE INDEX idx_fact_incident_crime_type
ON fact_incident(crime_type_id);

CREATE INDEX idx_fact_incident_disposition
ON fact_incident(disposition_id);

CREATE INDEX idx_fact_incident_location
ON fact_incident(location_id);

CREATE INDEX idx_fact_arrest_case_number
ON fact_arrest(case_number);

CREATE INDEX idx_fact_arrest_arrest_number
ON fact_arrest(arrest_number);

CREATE INDEX idx_fact_arrest_date
ON fact_arrest(arrest_date_id);

CREATE INDEX idx_fact_arrest_demographic
ON fact_arrest(demographic_id);

CREATE INDEX idx_fact_arrest_charge_category
ON fact_arrest(charge_category_id);