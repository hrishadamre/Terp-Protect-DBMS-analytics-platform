# Data Source Inventory

## Project Context

Terp Protect uses public University of Maryland Police Department records to build a structured DBMS and analytics system for campus safety reporting. The project will begin with one clean year of data and then expand to additional years after the pipeline is stable.

The first complete version will focus on 2025 data because it allows the project to build and validate the full workflow before scaling to multi-year trend analysis.

---

# Source 1: Daily Crime and Incident Logs

## Purpose

The Daily Crime and Incident Logs provide incident-level records for criminal misconduct and incidents reported to or handled by UMPD.

This will be the main foundation dataset for the project because it contains the central incident record.

## Confirmed Fields

- UMPD Case Number
- Date Occurred
- Report Date
- Crime Type
- Disposition
- General Location

## Notes From Source Review

The Daily Crime and Incident Log displays criminal misconduct and incident reports. The log includes incident type, occurred date/time, reported date/time, general location, and disposition when known. Records are organized by year and month.

## Current Collection Scope

The first collection scope will use 2025 monthly Daily Crime and Incident Logs from January through December.

## Future Expansion Scope

After the 2025 pipeline is working, the project may expand to previous years such as 2024, 2023, and 2022. Multi-year incident data will support year-over-year comparisons, seasonal trend analysis, reporting delay analysis, and forecasting.

## Primary Join Key

- UMPD Case Number

## Derived Fields Planned

- occurred_datetime
- reported_datetime
- report_delay_hours
- report_delay_days
- year
- month
- month_name
- weekday
- hour
- is_weekend
- semester_period
- crime_group
- disposition_group
- location_group
- source_type

## Analytical Value

This dataset supports the main incident-level analytics layer.

## Possible Business Questions

- What incident types are most common?
- Which locations have the highest incident volume?
- How does incident volume vary by month, weekday, and hour?
- Which incidents are closed, pending, unfounded, or arrest-related?
- How long does it take for incidents to be reported?
- Which incidents can be linked to arrest records?
- Which incident types show unusual spikes or seasonal patterns?

## Planned Database Tables

- fact_incident
- dim_crime_type
- dim_location
- dim_disposition
- dim_date

---

# Source 2: Arrest Logs

## Purpose

The Arrest Logs provide arrest-level records processed by UMPD. This dataset will connect arrest outcomes and charge details to incident records when case numbers match.

## Confirmed Fields

- Arrest Number
- Arrested Date Time
- UMPD Case Number
- Age
- Race
- Sex
- Arrested Charge

## Notes From Source Review

The annual arrest logs list basic arrest information from UMPD records. Arrest charges may appear as long text fields and may include multiple charge descriptions in one record. Some demographic values may be missing or blank.

## Current Collection Scope

The first arrest log collection will use the 2025 annual Arrest Log.

## Future Expansion Scope

After the 2025 arrest log pipeline is working, the project may expand to prior annual arrest logs such as 2024, 2023, and 2022. Multi-year arrest data will support charge trend analysis, arrest conversion analysis, and long-term pattern detection.

## Primary Join Key

- UMPD Case Number

## Derived Fields Planned

- arrest_datetime
- arrest_year
- arrest_month
- arrest_month_name
- arrest_weekday
- arrest_hour
- age_group
- charge_text_clean
- charge_category
- has_multiple_charges
- source_type

## Analytical Value

This dataset supports arrest conversion analysis, charge category analysis, demographic analysis, and charge text classification.

## Possible Business Questions

- Which incidents resulted in arrests?
- What percentage of incident cases resulted in arrest?
- What are the most common arrest charge categories?
- How do arrests vary by month, weekday, and hour?
- Which arrest charge categories are increasing or decreasing?
- How long after an incident was the arrest recorded?
- Which incident types most often lead to arrests?
- Which charge descriptions can be standardized into clean analytical categories?

## Planned Database Tables

- fact_arrest
- dim_charge_category
- bridge_arrest_charge

---

# Source 3: Campus Security Authority Logs

## Purpose

Campus Security Authority Logs contain incidents reported through designated Campus Security Authorities. These incidents may not always involve direct UMPD response or investigation.

## Confirmed Fields

- Case Number
- Occurred Date Time
- Report Date
- Nature / Classification
- Disposition
- General Location

## Notes From Source Review

CSA logs contain incidents reported through Campus Security Authorities. Some records may not have a UMPD case number and may use N/A. This dataset should be handled as a separate reporting layer rather than being forced directly into the UMPD incident table.

## Current Collection Scope

CSA logs will be added after the Daily Crime and Incident Log and Arrest Log pipelines are working. The planned first CSA scope is 2025 monthly CSA logs from January through December.

## Future Expansion Scope

The project may expand CSA logs to previous years once the structure is confirmed and standardized. CSA logs will be useful for comparing direct UMPD incident records with CSA-reported incidents.

## Primary Join Key

- Case Number, when available

## Derived Fields Planned

- occurred_datetime
- reported_datetime
- report_delay_hours
- report_delay_days
- year
- month
- weekday
- hour
- source_type
- incident_group
- disposition_group
- location_group
- has_valid_case_number

## Analytical Value

This dataset supports comparison between police-response incidents and CSA-reported incidents.

## Possible Business Questions

- Which incident types appear more often in CSA logs?
- How do CSA reporting patterns differ from daily incident logs?
- Which locations appear frequently in CSA reports?
- What is the reporting delay for CSA records?
- Which CSA incidents have valid case numbers?
- Which CSA incidents are referred to other offices or agencies?

## Planned Database Tables

- fact_csa_incident
- dim_crime_type
- dim_location
- dim_disposition
- dim_date

---

# Source 4: Uniform Crime Reports

## Purpose

Uniform Crime Reports provide monthly crime statistics reported through FBI/NIBRS reporting categories.

## Confirmed / Expected Fields

- Year
- Month
- Crime category
- Offense count

## Notes From Source Review

Uniform Crime Reports are aggregate-level monthly crime statistics. They are not incident-level records, but they are useful for validation and high-level trend comparison.

## Current Collection Scope

Uniform Crime Reports will be added after incident-level and arrest-level datasets are cleaned. The planned first scope is 2025 monthly crime report summaries.

## Future Expansion Scope

The project may expand to 2023 onward because UMPD began using the NIBRS reporting format in January 2023. Multi-year UCR data will support trend validation and comparison with cleaned incident-level records.

## Primary Join Keys

- Year
- Month
- Crime Category

## Derived Fields Planned

- year_month
- crime_group
- monthly_total
- year_over_year_change
- month_over_month_change

## Analytical Value

This dataset supports validation of cleaned incident data and comparison with official aggregate reporting.

## Possible Business Questions

- Do detailed incident records align with official monthly summaries?
- Which broad crime categories are increasing or decreasing?
- How do monthly crime totals compare across years?
- Are there differences between incident-level records and aggregate reporting?

## Planned Database Tables

- fact_monthly_crime_report
- dim_crime_type
- dim_date

---

# Source 5: Official UMPD Dashboard

## Purpose

The official UMPD dashboard provides public-facing department statistics and visual summaries.

## Observed Dashboard Areas

- Introduction
- Overview
- Traffic Stops
- Arrests
- Calls for Service
- Complaints

## Current Use

The official UMPD dashboard is used as a benchmark for identifying reporting gaps, dashboard design opportunities, and possible improvement areas.

## Future Use

If downloadable dashboard data becomes available, it may be used for validation against collected records. Otherwise, it will remain a reference for comparison and project positioning.

## Analytical Value

The dashboard is useful for understanding how UMPD currently presents public safety statistics. This project will not copy the official dashboard. It will extend the idea by adding integrated data modeling, deeper drilldowns, reporting delay analysis, data quality checks, and predictive analytics.

## Improvement Opportunities Identified

- Add incident-to-arrest conversion analysis
- Add reporting delay analysis
- Add joined incident and arrest records
- Add data quality and refresh tracking
- Add charge text categorization
- Add predictive analytics modules
- Add executive insight summaries
- Add a reusable DBMS backend

---

# Current Project Data Scope Summary

## Version 1 Scope

- Daily Crime and Incident Logs: 2025 January through December
- Arrest Logs: 2025 annual arrest log
- CSA Logs: planned after first two pipelines
- Uniform Crime Reports: planned after incident and arrest datasets
- Official Dashboard: benchmark and comparison only

## Future Scope

- Expand Daily Crime and Incident Logs to 2024, 2023, and 2022
- Expand Arrest Logs to 2024, 2023, and 2022
- Expand CSA Logs to prior years
- Add Uniform Crime Reports from 2023 onward
- Add forecasting after sufficient multi-year data is collected

---

# Data Source Priority

## Priority 1

Daily Crime and Incident Logs

Reason: This is the central incident-level dataset and supports the first full analytics module.

## Priority 2

Arrest Logs

Reason: This connects arrest outcomes and charge details to incident cases.

## Priority 3

CSA Logs

Reason: This adds a comparison layer for incidents reported outside direct UMPD response.

## Priority 4

Uniform Crime Reports

Reason: This supports aggregate validation and multi-year reporting comparison.

## Priority 5

Official Dashboard

Reason: This is used as a benchmark and improvement reference.