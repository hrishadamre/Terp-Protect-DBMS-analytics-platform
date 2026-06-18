/*
Terp Protect DBMS
File: 03_business_questions.sql
Purpose:
Answer core business and analytical questions using the Terp Protect incident analytics database.
Current Scope:
- UMPD Daily Crime and Incident Logs
- Year: 2025
Notes:
Run sql/02_views.sql before running these queries.
*/

-- Question 1:
-- What are the most common incident categories?

SELECT
    crime_group,
    COUNT(*) AS incident_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS incident_percentage
FROM vw_incident_detail
GROUP BY
    crime_group
ORDER BY
    incident_count DESC;

-- Question 2:
-- Which detailed crime types appear most often?

SELECT
    crime_type,
    crime_group,
    COUNT(*) AS incident_count
FROM vw_incident_detail
GROUP BY
    crime_type,
    crime_group
ORDER BY
    incident_count DESC
LIMIT 20;

-- Question 3:
-- What are the most common case outcome groups?

SELECT
    disposition_group,
    COUNT(*) AS incident_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS incident_percentage
FROM vw_incident_detail
GROUP BY
    disposition_group
ORDER BY
    incident_count DESC;

-- Question 4:
-- What percentage of incidents are arrest-related?

SELECT
    COUNT(*) AS total_incidents,
    SUM(is_arrest_related) AS arrest_related_incidents,
    ROUND(100.0 * SUM(is_arrest_related) / COUNT(*), 2) AS arrest_related_percentage
FROM vw_incident_detail;

-- Question 5:
-- How do incidents vary by month?

SELECT
    occurred_month,
    occurred_month_name,
    COUNT(*) AS incident_count,
    SUM(is_arrest_related) AS arrest_related_count,
    ROUND(AVG(report_delay_hours), 2) AS avg_report_delay_hours
FROM vw_incident_detail
GROUP BY
    occurred_month,
    occurred_month_name
ORDER BY
    occurred_month;

-- Question 6:
-- How do incidents vary by weekday?

SELECT
    occurred_weekday,
    COUNT(*) AS incident_count,
    SUM(is_arrest_related) AS arrest_related_count,
    ROUND(AVG(report_delay_hours), 2) AS avg_report_delay_hours
FROM vw_incident_detail
GROUP BY
    occurred_weekday
ORDER BY
    CASE occurred_weekday
        WHEN 'Monday' THEN 1
        WHEN 'Tuesday' THEN 2
        WHEN 'Wednesday' THEN 3
        WHEN 'Thursday' THEN 4
        WHEN 'Friday' THEN 5
        WHEN 'Saturday' THEN 6
        WHEN 'Sunday' THEN 7
        ELSE 8
    END;

-- Question 7:
-- What time of day has the highest incident volume?

SELECT
    occurred_hour,
    COUNT(*) AS incident_count,
    SUM(is_arrest_related) AS arrest_related_count
FROM vw_incident_detail
GROUP BY
    occurred_hour
ORDER BY
    incident_count DESC;

-- Question 8:
-- Which locations have the highest incident volume?

SELECT
    location_raw,
    location_group,
    COUNT(*) AS incident_count,
    SUM(is_arrest_related) AS arrest_related_count
FROM vw_incident_detail
GROUP BY
    location_raw,
    location_group
ORDER BY
    incident_count DESC
LIMIT 20;

-- Question 9:
-- Which location groups have the highest incident volume?

SELECT
    location_group,
    COUNT(*) AS incident_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS incident_percentage,
    SUM(is_arrest_related) AS arrest_related_count
FROM vw_incident_detail
GROUP BY
    location_group
ORDER BY
    incident_count DESC;

-- Question 10:
-- Which incident categories have the highest arrest-related rate?

SELECT
    crime_group,
    COUNT(*) AS incident_count,
    SUM(is_arrest_related) AS arrest_related_count,
    ROUND(100.0 * SUM(is_arrest_related) / COUNT(*), 2) AS arrest_related_rate
FROM vw_incident_detail
GROUP BY
    crime_group
HAVING
    incident_count >= 10
ORDER BY
    arrest_related_rate DESC;

-- Question 11:
-- Which incident categories have the longest average reporting delay?

SELECT
    crime_group,
    COUNT(*) AS incident_count,
    ROUND(AVG(report_delay_hours), 2) AS avg_report_delay_hours,
    ROUND(AVG(report_delay_days), 2) AS avg_report_delay_days
FROM vw_incident_detail
WHERE
    has_valid_reporting_delay = 1
GROUP BY
    crime_group
HAVING
    incident_count >= 10
ORDER BY
    avg_report_delay_hours DESC;

-- Question 12:
-- How many incidents were reported within each delay bucket?

SELECT
    delay_bucket,
    COUNT(*) AS incident_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS incident_percentage
FROM vw_incident_detail
GROUP BY
    delay_bucket
ORDER BY
    CASE delay_bucket
        WHEN 'Same Day / Within 24 Hours' THEN 1
        WHEN '1-3 Days' THEN 2
        WHEN '4-7 Days' THEN 3
        WHEN 'Over 7 Days' THEN 4
        ELSE 5
    END;

-- Question 13:
-- How do incidents vary across academic periods?

SELECT
    occurred_semester_period,
    COUNT(*) AS incident_count,
    SUM(is_arrest_related) AS arrest_related_count,
    ROUND(AVG(report_delay_hours), 2) AS avg_report_delay_hours
FROM vw_incident_detail
GROUP BY
    occurred_semester_period
ORDER BY
    incident_count DESC;

-- Question 14:
-- Which records may need data quality review?

SELECT
    incident_id,
    case_number,
    occurred_datetime,
    reported_datetime,
    crime_type,
    disposition,
    location_raw,
    has_valid_case_number,
    has_valid_occurred_datetime,
    has_valid_reported_datetime,
    has_valid_reporting_delay
FROM vw_incident_detail
WHERE
    has_valid_case_number = 0
    OR has_valid_occurred_datetime = 0
    OR has_valid_reported_datetime = 0
    OR has_valid_reporting_delay = 0
LIMIT 50;