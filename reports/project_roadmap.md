# Terp Protect Project Roadmap

## Project 
Terp Protect: Campus Safety Analytics & Incident Intelligence DBMS

## Project Purpose
This project transforms public University of Maryland Police Department records into a structured analytics database and dashboard system. The goal is to integrate scattered public safety logs into one reusable DBMS that supports incident trend analysis, arrest outcome tracking, reporting delay analysis, charge categorization, and responsible predictive analytics.

## Business Problem
UMPD publishes public safety information across multiple sources, including daily crime and incident logs, arrest logs, campus security authority logs, uniform crime reports, and a public dashboard. These sources support transparency, but they are not presented as one integrated analytical system.

This project addresses that gap by creating a centralized database and analytics workflow that allows users to answer:
- What types of incidents are most common?
- Which locations have the highest incident volume?
- Which incidents result in arrests?
- What are the most common arrest charge categories?
- How long does it take for incidents to be reported?
- Which incident patterns change over time?
- Can historical records support responsible prediction of administrative outcomes?

## Improvement Over Official Dashboard
The official UMPD dashboard provides useful public-facing summaries, but this project extends the analysis by adding:
- Integrated incident, arrest, CSA, and crime-report datasets
- Relational DBMS design with fact and dimension tables
- SQL-based business analysis
- Incident-to-arrest conversion analysis
- Reporting delay analysis
- Charge text categorization
- Data quality checks
- Predictive analytics modules
- Executive-level insight summaries

## Build Phases

### Stage 1: Project Setup and Architecture
Create the VS Code project structure, Git repository, documentation folders, SQL files, data folders, and archive for original assignment files.

### Stage 2: Data Source Review and Inventory
Review UMPD data sources and document available fields, join keys, limitations, and possible analytical uses.

### Stage 3: Data Collection
Collect real public records from UMPD sources, beginning with Daily Crime and Incident Logs and Arrest Logs.

### Stage 4: Data Cleaning and Standardization
Clean dates, case numbers, crime types, locations, dispositions, arrest charges, and demographic fields.

### Stage 5: DBMS Design
Design a relational schema using fact and dimension tables based on real public data.

### Stage 6: Database Build and Load
Load cleaned data into SQLite or DuckDB and create reusable SQL views.

### Stage 7: SQL Business Analysis
Write SQL queries to answer core analytical and business questions.

### Stage 8: Power BI Dashboard
Build a dashboard with executive overview, incident outcomes, arrest analysis, location/time trends, reporting delays, and data quality.

### Stage 9: Predictive Analytics
Add responsible prediction modules such as incident disposition prediction, incident volume forecasting, and charge text classification.

### Stage 10: Final GitHub Packaging
Polish README, screenshots, ERD, dashboard previews, executive summary, data dictionary, SQL queries, and model documentation.

