# Terp Protect: Campus Safety Analytics & Incident Intelligence DBMS
## Overview
Terp Protect is a database and analytics project focused on organizing, modeling, and analyzing public safety records from the University of Maryland Police Department. The project uses publicly available UMPD records to build a structured data pipeline, relational database, SQL analysis layer, and interactive Streamlit dashboard.
The project began as a DBMS course assignment using synthetic data modeled after UMPD arrest log structures. This version rebuilds and expands the work using real public data sources, with a stronger focus on data extraction, data cleaning, database design, SQL analytics, dashboarding, and responsible future predictive analytics.
## Objective
The objective is to transform separate public safety records into a centralized analytics database that can help answer questions such as:
- What types of incidents are most commonly reported?
- Which locations have higher incident activity?
- How do incident volumes vary by month, weekday, and time of day?
- Which incidents are arrest-related?
- What are the most common case outcome categories?
- How long does it take for incidents to be reported?
- How can public safety records be structured for consistent reporting and analysis?
## Current Project Scope
The current version focuses on the first completed data pipeline:
- Source: UMPD Daily Crime and Incident Logs
- Year: 2025
- Records collected: 1,886 incidents
- Main output: Cleaned incident dataset, SQLite database, SQL analysis outputs, and Streamlit dashboard
Additional UMPD data sources such as Arrest Logs, Campus Security Authority Logs, and Uniform Crime Reports are planned for future phases.
## Data Sources
The project is designed around publicly available UMPD data sources:
- Daily Crime and Incident Logs
- Arrest Logs
- Campus Security Authority Logs
- Uniform Crime Reports
- Official UMPD Dashboard, used as a reference and benchmark
The first implemented source is the 2025 Daily Crime and Incident Logs. Other sources will be added after the current incident-level pipeline is finalized.
## Key Improvements
This project extends basic public reporting by adding:
- Centralized relational database design
- Automated data extraction from public web pages
- Cleaned and standardized incident records
- SQL-based business analysis
- Reporting delay analysis
- Disposition and incident outcome analysis
- Location and time-based incident analysis
- Data quality checks
- Dashboard-ready analytical exports
- Interactive Streamlit dashboard
- Future support for arrest matching, forecasting, and charge text classification
## Project Architecture
```text
terp-protect-dbms/
├── archive/
│   ├── original_assignment/
│   └── screenshots/
├── dashboard/
│   ├── powerbi/
│   │   └── data/
│   └── streamlit_app/
│       ├── README.md
│       └── app.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── database/
├── notebooks/
├── reports/
│   ├── data_dictionary.md
│   ├── data_source_inventory.md
│   ├── dashboard_design_plan.md
│   ├── daily_incident_cleaning_summary_2025.md
│   ├── improvement_over_official_dashboard.md
│   ├── project_roadmap.md
│   ├── sql_analysis_summary_2025.md
│   └── sql_outputs/
├── sql/
│   ├── 01_schema.sql
│   ├── 02_views.sql
│   ├── 03_business_questions.sql
│   └── 04_data_quality_checks.sql
├── src/
│   ├── analysis/
│   │   ├── export_dashboard_data.py
│   │   └── run_business_analysis.py
│   ├── extract/
│   │   └── scrape_daily_logs.py
│   ├── load/
│   │   └── build_database.py
│   ├── models/
│   ├── transform/
│   │   └── clean_daily_incidents.py
│   └── utils/
├── visuals/
├── .gitignore
├── README.md
└── requirements.txt
```
## Workflow
The project follows a staged data workflow:
1. Review and document available UMPD data sources
2. Scrape public Daily Crime and Incident Log records
3. Save raw records as CSV
4. Clean and standardize raw fields
5. Create derived analytical fields
6. Design and build a relational SQLite database
7. Load cleaned records into fact and dimension tables
8. Create SQL views for business analysis
9. Run SQL analysis queries and export results
10. Export dashboard-ready datasets
11. Build an interactive Streamlit dashboard
## Current Data Pipeline
```text
UMPD public web pages
→ Python scraping script
→ raw CSV
→ cleaning and standardization script
→ processed CSV
→ SQLite database
→ SQL views and business queries
→ dashboard-ready CSV exports
→ Streamlit dashboard
```
## Database Design
The current database uses a simple star-schema structure for incident analytics.
Current tables:
- `fact_incident`
- `dim_date`
- `dim_crime_type`
- `dim_disposition`
- `dim_location`
Planned future tables:
- `fact_arrest`
- `fact_csa_incident`
- `fact_monthly_crime_report`
- `dim_demographic`
- `dim_charge_category`
- `bridge_arrest_charge`
## Analysis Areas
The current version supports analysis in the following areas:
- Incident volume trends
- Crime type distribution
- Location-based incident patterns
- Disposition and case outcome analysis
- Reporting delay analysis
- Arrest-related incident percentage
- Month, weekday, hour, and academic-period trends
- Data quality and completeness checks
## Streamlit Dashboard
The Streamlit dashboard provides an interactive local UI for exploring the cleaned and modeled incident data.
Current dashboard tabs:
- Executive Overview
- Incident Trends
- Incident Outcomes
- Reporting Delay
- Location Analysis
- Data Quality
To run the dashboard:
```bash
streamlit run dashboard/streamlit_app/app.py
```
If needed, use:
```bash
python3 -m streamlit run dashboard/streamlit_app/app.py
```
## How to Run This Project
### 1. Install dependencies
```bash
python3 -m pip install -r requirements.txt
```
### 2. Scrape Daily Crime and Incident Logs
```bash
python3 src/extract/scrape_daily_logs.py
```
Output:
```text
data/raw/daily_incident_logs_2025.csv
```
### 3. Clean the raw incident data
```bash
python3 src/transform/clean_daily_incidents.py
```
Outputs:
```text
data/processed/clean_daily_incidents_2025.csv
reports/daily_incident_cleaning_summary_2025.md
```
### 4. Build and load the SQLite database
```bash
python3 src/load/build_database.py
```
Output:
```text
data/database/terp_protect.db
```
### 5. Run SQL analysis outputs
```bash
python3 src/analysis/run_business_analysis.py
```
Outputs:
```text
reports/sql_outputs/
reports/sql_analysis_summary_2025.md
```
### 6. Export dashboard-ready data
```bash
python3 src/analysis/export_dashboard_data.py
```
Output:
```text
dashboard/powerbi/data/
```
### 7. Launch the Streamlit dashboard
```bash
streamlit run dashboard/streamlit_app/app.py
```
## Important Files
| File | Purpose |
|---|---|
| `src/extract/scrape_daily_logs.py` | Scrapes 2025 UMPD Daily Crime and Incident Logs |
| `src/transform/clean_daily_incidents.py` | Cleans raw incident data and creates derived fields |
| `src/load/build_database.py` | Builds and loads the SQLite database |
| `src/analysis/run_business_analysis.py` | Runs SQL-based business analysis queries |
| `src/analysis/export_dashboard_data.py` | Exports dashboard-ready CSV files |
| `sql/01_schema.sql` | Defines the core database schema |
| `sql/02_views.sql` | Creates reusable SQL views |
| `sql/03_business_questions.sql` | Contains analytical SQL questions |
| `dashboard/streamlit_app/app.py` | Main Streamlit dashboard application |
| `reports/data_source_inventory.md` | Documents source datasets and planned scope |
| `reports/data_dictionary.md` | Documents raw, cleaned, and modeled fields |
| `reports/project_roadmap.md` | Describes the staged project roadmap |
## Tools and Technologies
- Python
- Pandas
- BeautifulSoup
- Requests
- SQL
- SQLite
- Plotly
- Streamlit
- Jupyter Notebook
- VS Code
- Git and GitHub
- Power BI, planned as a later reporting layer
## Notes on Data and Ethics
This project uses public records for educational and analytical purposes. It does not attempt to predict individual behavior, assign risk to individuals, or make enforcement decisions.
Future predictive work, if included, will focus only on aggregate-level reporting support, administrative outcome classification, incident volume forecasting, or charge text categorization.
## Project Background
This project began as a DBMS course assignment called Terp Protect. The original assignment used synthetic data based on the structure of UMPD arrest logs. The current version rebuilds the project using real public data and expands it into a full analytics pipeline with data collection, cleaning, relational modeling, SQL analysis, and dashboarding.
