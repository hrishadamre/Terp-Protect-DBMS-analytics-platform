/*
Terp Protect DBMS
File: 02_views.sql
Purpose:
Create reusable SQL views for incident analytics, dashboarding, and business analysis.
Current Scope:
- UMPD Daily Crime and Incident Logs
- Year: 2025
Database:
- data/database/terp_protect.db
Notes:
These views join the fact table with dimension tables so analysis can be done using readable business fields instead of only foreign key IDs.
*/

DROP VIEW IF EXISTS vw_incident_detail;
DROP VIEW IF EXISTS vw_monthly_incident_trends;
DROP VIEW IF EXISTS vw_disposition_summary;
DROP VIEW IF EXISTS vw_reporting_delay_summary;
DROP VIEW IF EXISTS vw_location_summary;
DROP VIEW IF EXISTS vw_crime_group_summary;

CREATE VIEW vw_incident_detail AS
SELECT
    fi.incident_id,
    fi.case_number,
    fi.occurred_datetime,
    fi.reported_datetime,
    od.full_date AS occurred_date,
    rd.full_date AS reported_date,
    od.year AS occurred_year,
    od.month AS occurred_month,
    od.month_name AS occurred_month_name,
    od.weekday AS occurred_weekday,
    od.is_weekend AS occurred_is_weekend,
    od.semester_period AS occurred_semester_period,
    fi.hour AS occurred_hour,
    dct.crime_type,
    dct.crime_group,
    dd.disposition,
    dd.disposition_group,
    dd.is_arrest_related,
    dd.is_pending,
    dd.is_closed,
    dl.location_raw,
    dl.location_group,
    dl.jurisdiction_group,
    dl.is_on_campus,
    fi.report_delay_hours,
    fi.report_delay_days,
    fi.delay_bucket,
    fi.source_type,
    fi.source_url,
    fi.scraped_at,
    fi.has_valid_case_number,
    fi.has_valid_occurred_datetime,
    fi.has_valid_reported_datetime,
    fi.has_valid_reporting_delay
FROM fact_incident fi
LEFT JOIN dim_date od
    ON fi.occurred_date_id = od.date_id
LEFT JOIN dim_date rd
    ON fi.reported_date_id = rd.date_id
LEFT JOIN dim_crime_type dct
    ON fi.crime_type_id = dct.crime_type_id
LEFT JOIN dim_disposition dd
    ON fi.disposition_id = dd.disposition_id
LEFT JOIN dim_location dl
    ON fi.location_id = dl.location_id;

CREATE VIEW vw_monthly_incident_trends AS
SELECT
    occurred_year,
    occurred_month,
    occurred_month_name,
    crime_group,
    COUNT(*) AS incident_count,
    SUM(is_arrest_related) AS arrest_related_count,
    SUM(is_pending) AS pending_count,
    SUM(is_closed) AS closed_count,
    ROUND(AVG(report_delay_hours), 2) AS avg_report_delay_hours
FROM vw_incident_detail
GROUP BY
    occurred_year,
    occurred_month,
    occurred_month_name,
    crime_group;

CREATE VIEW vw_disposition_summary AS
SELECT
    disposition_group,
    disposition,
    COUNT(*) AS incident_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS incident_percentage
FROM vw_incident_detail
GROUP BY
    disposition_group,
    disposition
ORDER BY
    incident_count DESC;

CREATE VIEW vw_reporting_delay_summary AS
SELECT
    delay_bucket,
    COUNT(*) AS incident_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS incident_percentage,
    ROUND(AVG(report_delay_hours), 2) AS avg_report_delay_hours,
    ROUND(AVG(report_delay_days), 2) AS avg_report_delay_days
FROM vw_incident_detail
GROUP BY
    delay_bucket
ORDER BY
    incident_count DESC;
    
CREATE VIEW vw_location_summary AS
SELECT
    location_group,
    location_raw,
    COUNT(*) AS incident_count,
    SUM(is_arrest_related) AS arrest_related_count,
    ROUND(AVG(report_delay_hours), 2) AS avg_report_delay_hours
FROM vw_incident_detail
GROUP BY
    location_group,
    location_raw
ORDER BY
    incident_count DESC;
    
CREATE VIEW vw_crime_group_summary AS
SELECT
    crime_group,
    COUNT(*) AS incident_count,
    SUM(is_arrest_related) AS arrest_related_count,
    SUM(is_pending) AS pending_count,
    SUM(is_closed) AS closed_count,
    ROUND(100.0 * SUM(is_arrest_related) / COUNT(*), 2) AS arrest_related_rate,
    ROUND(AVG(report_delay_hours), 2) AS avg_report_delay_hours
FROM vw_incident_detail
GROUP BY
    crime_group
ORDER BY
    incident_count DESC;