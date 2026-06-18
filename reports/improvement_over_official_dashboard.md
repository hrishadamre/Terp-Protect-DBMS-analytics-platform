# Improvement Over the Official UMPD Dashboard

## Context
The official UMPD dashboard provides a public-facing summary of department statistics such as calls for service, traffic stops, complaints, and arrests. It is useful for transparency and high-level reporting.

This project does not replace the official dashboard. Instead, it extends the analytical layer by building a structured DBMS and deeper business intelligence workflow using publicly available records.

## Observed Limitations

### 1. Mostly Descriptive Reporting
The official dashboard mainly shows totals and category breakdowns. It answers what happened, but provides limited diagnostic analysis about why trends changed, where patterns are concentrated, or which categories need attention.

### 2. Limited Incident-to-Arrest Tracking
The dashboard does not clearly show the full funnel from incident report to case outcome to arrest. This project adds incident-to-arrest conversion analysis using case numbers where available.

### 3. Separate Public Data Sources
UMPD publishes multiple public datasets separately, including Daily Crime and Incident Logs, Arrest Logs, Campus Security Authority Logs, Uniform Crime Reports, and dashboard summaries. This project integrates these sources into a centralized database.

### 4. Limited Reporting Delay Analysis
Daily incident logs include occurred and reported timestamps. This project uses those fields to calculate reporting delay and identify incident types or locations with longer reporting gaps.

### 5. Limited Data Quality Transparency
The official dashboard does not visibly show missing values, duplicate records, unmatched case numbers, data cleaning rules, or refresh checks. This project adds a dedicated data quality layer.

### 6. Limited Predictive or Forward-Looking Analysis
The official dashboard is backward-looking. This project adds responsible predictive modules such as administrative disposition prediction, incident volume forecasting, and arrest charge text classification.

### 7. Limited Backend Visibility
The dashboard does not show the underlying database model. This project includes an ERD, normalized schema, SQL views, analytics marts, and business rules.

## Project Improvements

This project adds:
- Integrated public safety data model
- Fact and dimension table design
- Incident-to-arrest conversion metrics
- Reporting delay analysis
- Charge text categorization
- Data quality checks
- SQL-based business questions
- Power BI dashboard storytelling
- Responsible predictive analytics
- Clear GitHub documentation


The official UMPD dashboard is designed for public transparency and high-level reporting. Terp Protect extends this idea by adding a reusable DBMS backend, deeper analytical drilldowns, data validation, and predictive analytics for campus safety operations.