# Data Dictionary

## Purpose

This data dictionary documents the planned raw, cleaned, and modeled fields for the Terp Protect DBMS and analytics project.

The project will begin with 2025 Daily Crime and Incident Logs, then add 2025 Arrest Logs, followed by CSA Logs and Uniform Crime Reports in later stages.

---

# Raw Tables

## Table: raw_daily_incident_logs

This table stores the raw incident records collected from UMPD Daily Crime and Incident Log pages.

| Field Name | Description | Source Field | Notes |
|---|---|---|---|
| source_year | Year from source page | Page URL / year | Example: 2025 |
| source_month | Month from source page | Page URL / month | Example: January |
| case_number | UMPD case number | UMPD Case Number | Main incident identifier when available |
| occurred_datetime_raw | Raw occurred date/time | Date Occurred | Needs datetime parsing |
| reported_datetime_raw | Raw report date/time | Report Date | Needs datetime parsing |
| crime_type_raw | Original incident type | Crime Type | Will be standardized |
| disposition_raw | Original disposition | Disposition | Will be standardized and grouped |
| location_raw | Original location text | General Location | Will be standardized and grouped |
| source_url | URL used for collection | Web page URL | Useful for traceability |
| scraped_at | Timestamp when data was collected | System generated | Useful for refresh tracking |

---

## Table: raw_arrest_logs

This table stores the raw arrest records collected from UMPD annual Arrest Log pages.

| Field Name | Description | Source Field | Notes |
|---|---|---|---|
| source_year | Year from source page | Page URL / year | Example: 2025 |
| arrest_number | Unique arrest number | Arrest Number | Main arrest identifier |
| arrested_datetime_raw | Raw arrest date/time | Arrested Date Time | Needs datetime parsing |
| case_number | UMPD case number | UMPD Case Number | Used to join with incident logs when available |
| age_raw | Raw age value | Age | May contain missing values |
| race_raw | Raw race value | Race | May contain missing values |
| sex_raw | Raw sex value | Sex | May contain missing values |
| arrested_charge_raw | Original arrested charge text | Arrested Charge | May contain multiple long charge descriptions |
| source_url | URL used for collection | Web page URL | Useful for traceability |
| scraped_at | Timestamp when data was collected | System generated | Useful for refresh tracking |

---

## Table: raw_csa_logs

This table stores the raw records collected from UMPD Campus Security Authority Incident Log pages.

| Field Name | Description | Source Field | Notes |
|---|---|---|---|
| source_year | Year from source page | Page URL / year | Example: 2025 |
| source_month | Month from source page | Page URL / month | Example: January |
| case_number | Case number when available | Case Number | Some records may show N/A |
| occurred_datetime_raw | Raw occurred date/time | Occurred Date Time | Needs datetime parsing |
| reported_datetime_raw | Raw report date/time | Report Date | Needs datetime parsing |
| incident_type_raw | Original incident classification | Nature / Classification | Will be standardized |
| disposition_raw | Original disposition/referral status | Disposition | Will be standardized and grouped |
| location_raw | Original location text | General Location | Will be standardized and grouped |
| source_url | URL used for collection | Web page URL | Useful for traceability |
| scraped_at | Timestamp when data was collected | System generated | Useful for refresh tracking |

---

## Table: raw_uniform_crime_reports

This table stores aggregate monthly crime report values.

| Field Name | Description | Source Field | Notes |
|---|---|---|---|
| source_year | Report year | Year | Example: 2025 |
| source_month | Report month | Month | Example: January |
| crime_category_raw | Original crime category | Crime category | Will be standardized |
| offense_count_raw | Original offense count | Offense count | Needs numeric validation |
| source_url | URL used for collection | Web page URL | Useful for traceability |
| scraped_at | Timestamp when data was collected | System generated | Useful for refresh tracking |

---

# Clean Tables

## Table: clean_daily_incidents

This table stores cleaned incident-level records from the Daily Crime and Incident Logs.

| Field Name | Description |
|---|---|
| incident_id | Internal generated incident ID |
| case_number | Standardized UMPD case number |
| occurred_datetime | Parsed occurred datetime |
| reported_datetime | Parsed reported datetime |
| report_delay_hours | Hours between occurred and reported datetime |
| report_delay_days | Days between occurred and reported datetime |
| crime_type | Standardized crime type |
| crime_group | Broader incident group |
| disposition | Standardized disposition |
| disposition_group | Broader disposition category |
| location_raw | Original location value |
| location_group | Standardized location group |
| year | Year from occurred date |
| month | Month from occurred date |
| month_name | Month name from occurred date |
| weekday | Weekday from occurred date |
| hour | Hour from occurred date |
| is_weekend | Weekend indicator |
| semester_period | Academic period grouping |
| source_type | Daily Crime and Incident Log |
| source_url | Original source page |
| scraped_at | Data collection timestamp |

---

## Table: clean_arrests

This table stores cleaned arrest-level records from the Arrest Logs.

| Field Name | Description |
|---|---|
| arrest_id | Internal generated arrest ID |
| arrest_number | Standardized arrest number |
| case_number | Standardized UMPD case number |
| arrest_datetime | Parsed arrest datetime |
| age | Numeric age value |
| age_group | Age group category |
| race | Standardized race value |
| sex | Standardized sex value |
| raw_charge_text | Original arrest charge text |
| clean_charge_text | Cleaned charge text |
| charge_category | Primary charge category |
| has_multiple_charges | Indicator for multiple charge descriptions |
| arrest_year | Year from arrest date |
| arrest_month | Month from arrest date |
| arrest_month_name | Month name from arrest date |
| arrest_weekday | Weekday from arrest date |
| arrest_hour | Hour from arrest date |
| source_type | Arrest Log |
| source_url | Original source page |
| scraped_at | Data collection timestamp |

---

## Table: clean_csa_incidents

This table stores cleaned records from Campus Security Authority Logs.

| Field Name | Description |
|---|---|
| csa_incident_id | Internal generated CSA incident ID |
| case_number | Standardized case number when available |
| has_valid_case_number | Indicator for whether case number is available |
| occurred_datetime | Parsed occurred datetime |
| reported_datetime | Parsed reported datetime |
| report_delay_hours | Hours between occurred and reported datetime |
| report_delay_days | Days between occurred and reported datetime |
| incident_type | Standardized CSA incident type |
| incident_group | Broader incident group |
| disposition | Standardized disposition/referral status |
| disposition_group | Broader disposition group |
| location_raw | Original location value |
| location_group | Standardized location group |
| year | Year from occurred date |
| month | Month from occurred date |
| month_name | Month name from occurred date |
| weekday | Weekday from occurred date |
| hour | Hour from occurred date |
| is_weekend | Weekend indicator |
| semester_period | Academic period grouping |
| source_type | CSA Log |
| source_url | Original source page |
| scraped_at | Data collection timestamp |

---

## Table: clean_uniform_crime_reports

This table stores cleaned aggregate crime report data.

| Field Name | Description |
|---|---|
| monthly_report_id | Internal generated monthly report ID |
| year | Report year |
| month | Report month |
| month_name | Report month name |
| year_month | Combined year-month field |
| crime_category | Standardized crime category |
| crime_group | Broader crime group |
| offense_count | Numeric offense count |
| source_type | Uniform Crime Report |
| source_url | Original source page |
| scraped_at | Data collection timestamp |

---

# Core Database Tables

## Table: fact_incident

Main fact table for UMPD Daily Crime and Incident Log records.

| Field Name | Description |
|---|---|
| incident_id | Primary key |
| case_number | UMPD case number |
| occurred_date_id | Foreign key to dim_date |
| reported_date_id | Foreign key to dim_date |
| crime_type_id | Foreign key to dim_crime_type |
| disposition_id | Foreign key to dim_disposition |
| location_id | Foreign key to dim_location |
| occurred_datetime | Full occurred timestamp |
| reported_datetime | Full reported timestamp |
| report_delay_hours | Time between occurrence and report |
| report_delay_days | Delay in days |
| source_type | Source dataset name |

---

## Table: fact_arrest

Main fact table for arrest records.

| Field Name | Description |
|---|---|
| arrest_id | Primary key |
| arrest_number | Arrest number from UMPD log |
| case_number | UMPD case number |
| arrest_date_id | Foreign key to dim_date |
| demographic_id | Foreign key to dim_demographic |
| arrest_datetime | Full arrest timestamp |
| age | Age at arrest |
| raw_charge_text | Original charge text |
| clean_charge_text | Cleaned charge text |
| source_type | Source dataset name |

---

## Table: fact_csa_incident

Main fact table for CSA-reported incidents.

| Field Name | Description |
|---|---|
| csa_incident_id | Primary key |
| case_number | Case number when available |
| has_valid_case_number | Indicator for valid case number |
| occurred_date_id | Foreign key to dim_date |
| reported_date_id | Foreign key to dim_date |
| crime_type_id | Foreign key to dim_crime_type |
| disposition_id | Foreign key to dim_disposition |
| location_id | Foreign key to dim_location |
| occurred_datetime | Full occurred timestamp |
| reported_datetime | Full reported timestamp |
| report_delay_hours | Time between occurrence and report |
| report_delay_days | Delay in days |
| source_type | Source dataset name |

---

## Table: fact_monthly_crime_report

Aggregate monthly crime reporting table.

| Field Name | Description |
|---|---|
| monthly_report_id | Primary key |
| date_id | Foreign key to dim_date |
| crime_type_id | Foreign key to dim_crime_type |
| offense_count | Monthly offense count |
| source_type | Source dataset name |

---

# Dimension Tables

## Table: dim_date

| Field Name | Description |
|---|---|
| date_id | Primary key |
| full_date | Date value |
| year | Year |
| quarter | Quarter |
| month | Month number |
| month_name | Month name |
| weekday | Weekday name |
| day_of_week_number | Day of week number |
| is_weekend | Weekend indicator |
| semester_period | Academic period grouping |

---

## Table: dim_crime_type

| Field Name | Description |
|---|---|
| crime_type_id | Primary key |
| crime_type | Standardized crime or incident type |
| crime_group | Broader crime group |
| source_type | Source where the crime type appears |

---

## Table: dim_disposition

| Field Name | Description |
|---|---|
| disposition_id | Primary key |
| disposition | Standardized disposition |
| disposition_group | Broader disposition group |
| is_arrest_related | Indicator for arrest-related dispositions |
| is_pending | Indicator for pending/open cases |
| is_closed | Indicator for closed cases |

---

## Table: dim_location

| Field Name | Description |
|---|---|
| location_id | Primary key |
| location_raw | Original location text |
| location_group | Standardized location group |
| jurisdiction_group | UMD, Prince George’s County, Unknown, or other grouping if available |
| is_on_campus | Indicator for on-campus locations when identifiable |

---

## Table: dim_demographic

| Field Name | Description |
|---|---|
| demographic_id | Primary key |
| age_group | Age group category |
| race | Standardized race value |
| sex | Standardized sex value |

---

## Table: dim_charge_category

| Field Name | Description |
|---|---|
| charge_category_id | Primary key |
| charge_category | Standardized charge category |
| charge_subcategory | More specific charge grouping when available |
| category_keywords | Keywords used for rule-based classification |

---

# Bridge Tables

## Table: bridge_arrest_charge

This table supports arrest records with multiple charge categories.

| Field Name | Description |
|---|---|
| arrest_id | Foreign key to fact_arrest |
| charge_category_id | Foreign key to dim_charge_category |
| charge_text | Charge text linked to the category |

---

# Planned Analytical Marts

## Table: mart_incident_outcomes

Used for dashboarding incident outcomes and dispositions.

| Field Name | Description |
|---|---|
| case_number | UMPD case number |
| crime_type | Standardized crime type |
| crime_group | Broader crime group |
| disposition | Standardized disposition |
| disposition_group | Broader disposition group |
| location_group | Standardized location group |
| occurred_datetime | Incident occurrence timestamp |
| reported_datetime | Report timestamp |
| report_delay_hours | Reporting delay |
| year | Year |
| month | Month |
| weekday | Weekday |
| hour | Hour |
| has_matching_arrest | Whether case number appears in arrest log |

---

## Table: mart_arrest_conversion

Used to analyze which incidents result in arrests.

| Field Name | Description |
|---|---|
| case_number | UMPD case number |
| incident_id | Incident ID |
| arrest_id | Arrest ID when matched |
| crime_type | Incident type |
| charge_category | Arrest charge category |
| incident_datetime | Occurred datetime |
| arrest_datetime | Arrest datetime |
| time_to_arrest_hours | Time between incident and arrest |
| location_group | Standardized location |
| disposition_group | Disposition group |

---

## Table: mart_reporting_delay

Used to analyze reporting delays.

| Field Name | Description |
|---|---|
| source_type | Source dataset |
| case_number | Case number when available |
| incident_type | Incident type |
| location_group | Standardized location |
| occurred_datetime | Occurrence datetime |
| reported_datetime | Report datetime |
| report_delay_hours | Reporting delay in hours |
| report_delay_days | Reporting delay in days |
| delay_bucket | Same day, 1-3 days, 4-7 days, over 7 days |

---

## Table: mart_monthly_trends

Used for trend and forecasting analysis.

| Field Name | Description |
|---|---|
| year_month | Year-month field |
| year | Year |
| month | Month |
| source_type | Dataset source |
| crime_group | Crime group |
| incident_count | Count of incidents |
| arrest_count | Count of arrests |
| offense_count | Official monthly offense count when available |

---

# Planned Target Variables for Modeling

## Model 1: Incident Disposition Prediction

| Field | Description |
|---|---|
| Target Variable | disposition_group |
| Prediction Type | Classification |
| Use Case | Predict administrative case outcome category for reporting support |
| Ethical Note | This model does not predict individual behavior or crime risk |

## Model 2: Incident Volume Forecasting

| Field | Description |
|---|---|
| Target Variable | monthly_incident_count or weekly_incident_count |
| Prediction Type | Time-series forecasting |
| Use Case | Support aggregate-level operational planning |
| Requirement | Needs multiple years of data |

## Model 3: Arrest Charge Text Classification

| Field | Description |
|---|---|
| Target Variable | charge_category |
| Prediction Type | Text classification |
| Use Case | Convert long charge descriptions into structured reporting categories |
| First Approach | Rule-based keyword classification |
| Optional Approach | TF-IDF + Logistic Regression |