# Terp Protect: Campus Safety Analytics & Incident Intelligence DBMS

## Overview
Terp Protect is a database and analytics project focused on organizing and analyzing public safety records from the University of Maryland Police Department. The project uses publicly available UMPD records to build a structured data pipeline, relational database, SQL analysis layer, and dashboard-ready reporting system.
The project began as a DBMS course assignment using synthetic data modeled after UMPD arrest log structures. This version rebuilds and expands the work using real public data sources, with a stronger focus on data cleaning, database design, analytical reporting, and responsible predictive analytics.

## Objective
The objective is to transform separate public safety records into a centralized analytics database that can help answer questions such as:
- What types of incidents are most commonly reported?
- Which locations have higher incident activity?
- How do incident volumes vary by month, weekday, and time of day?
- Which incidents result in arrests?
- What charge categories appear most frequently in arrest records?
- How long does it take for incidents to be reported?
- How can public safety records be structured for more consistent reporting and analysis?

## Data Sources
The project is designed around publicly available UMPD data sources:
- Daily Crime and Incident Logs
- Arrest Logs
- Campus Security Authority Logs
- Uniform Crime Reports
- Official UMPD Dashboard, used as a reference and benchmark
The first development phase focuses on 2025 Daily Crime and Incident Logs. Additional sources will be added in later phases after the core pipeline is complete.

## Planned Data Scope

### Initial Scope
- Daily Crime and Incident Logs: 2025 January through December
- Arrest Logs: 2025 annual arrest log

### Future Scope
- Campus Security Authority Logs
- Uniform Crime Reports
- Prior years such as 2024, 2023, and 2022
- Multi-year trend analysis and forecasting

## Key Improvements
This project extends basic public reporting by adding:
- Centralized relational database design
- Cleaned and standardized incident records
- Incident-to-arrest conversion analysis
- Reporting delay analysis
- Charge category standardization
- SQL-based business analysis
- Data quality checks
- Dashboard-ready analytical tables
- Responsible predictive analytics modules

## Project Architecture
    terp-protect-dbms/
    ├── data/
    │   ├── raw/
    │   ├── processed/
    │   └── database/
    ├── notebooks/
    ├── sql/
    ├── src/
    │   ├── extract/
    │   ├── transform/
    │   ├── load/
    │   ├── models/
    │   └── utils/
    ├── dashboard/
    │   ├── powerbi/
    │   └── streamlit_app/
    ├── reports/
    ├── visuals/
    └── archive/

## Methodology
The project follows a staged data workflow:
1. Review and document available UMPD data sources
2. Collect public records from selected source pages
3. Clean and standardize raw data fields
4. Design a relational database using fact and dimension tables
5. Load cleaned records into a local database
6. Write SQL queries for business and operational analysis
7. Build dashboard-ready analytical views
8. Add predictive modules where appropriate

## Planned Database Design
The database will use a structured analytical model with core fact and dimension tables.
Planned tables include:
- `fact_incident`
- `fact_arrest`
- `fact_csa_incident`
- `fact_monthly_crime_report`
- `dim_date`
- `dim_location`
- `dim_crime_type`
- `dim_disposition`
- `dim_demographic`
- `dim_charge_category`
- `bridge_arrest_charge`

## Analysis Areas
The project will focus on the following analysis areas:
- Incident volume trends
- Crime type distribution
- Location-based incident patterns
- Disposition and case outcome analysis
- Reporting delay analysis
- Arrest and charge analysis
- Incident-to-arrest matching
- Data quality and completeness checks
- Optional predictive modeling

## Tools and Technologies
- Python
- Pandas
- SQL
- SQLite or DuckDB
- Jupyter Notebook
- Power BI
- Scikit-learn
- VS Code
- Git and GitHub

## Notes
This project uses public records for educational and analytical purposes. It does not attempt to predict individual behavior or assign risk to individuals. Predictive work, if included, will focus on aggregate-level reporting support, administrative outcome classification, or trend forecasting.