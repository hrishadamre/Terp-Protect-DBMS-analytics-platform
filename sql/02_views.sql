DROP VIEW IF EXISTS vw_incident_arrest_match;
DROP VIEW IF EXISTS vw_arrest_detail;
DROP VIEW IF EXISTS vw_charge_category_summary;
DROP VIEW IF EXISTS vw_demographic_summary;
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
    od.year AS occurred_year,
    od.month AS occurred_month,
    od.month_name AS occurred_month_name,
    od.weekday AS occurred_weekday,
    od.is_weekend AS occurred_is_weekend,
    od.semester_period AS occurred_semester_period,

    rd.full_date AS reported_date,
    rd.year AS reported_year,
    rd.month AS reported_month,
    rd.month_name AS reported_month_name,
    rd.weekday AS reported_weekday,

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

    fi.report_delay_hours,
    fi.report_delay_days,
    fi.delay_bucket,

    fi.source_year,
    fi.source_month,
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


CREATE VIEW vw_arrest_detail AS
SELECT
    fa.arrest_id,
    fa.arrest_number,
    fa.case_number,

    fa.arrested_datetime,

    ad.full_date AS arrested_date,
    ad.year AS arrested_year,
    ad.month AS arrested_month,
    ad.month_name AS arrested_month_name,
    ad.weekday AS arrested_weekday,
    ad.is_weekend AS arrested_is_weekend,
    ad.semester_period AS arrested_semester_period,

    fa.arrested_hour,

    ddem.race,
    ddem.sex,
    ddem.age_group,

    dcc.charge_category,
    dcc.is_alcohol_related,
    dcc.is_drug_related,
    dcc.is_theft_related,

    fa.arrested_charge,

    fa.source_year,
    fa.source_url,
    fa.scraped_at,

    fa.has_valid_arrest_number,
    fa.has_valid_case_number,
    fa.has_valid_arrested_datetime,
    fa.has_charge_text

FROM fact_arrest fa

LEFT JOIN dim_date ad
    ON fa.arrest_date_id = ad.date_id

LEFT JOIN dim_demographic ddem
    ON fa.demographic_id = ddem.demographic_id

LEFT JOIN dim_charge_category dcc
    ON fa.charge_category_id = dcc.charge_category_id;


CREATE VIEW vw_incident_arrest_match AS
SELECT
    vi.incident_id,
    vi.case_number,

    vi.occurred_datetime,
    vi.reported_datetime,
    vi.occurred_year,
    vi.occurred_month,

    vi.crime_type,
    vi.crime_group,

    vi.disposition,
    vi.disposition_group,

    vi.location_raw,
    vi.location_group,

    vi.report_delay_hours,
    vi.delay_bucket,

    vi.source_year AS incident_source_year,

    va.arrest_id,
    va.arrest_number,
    va.arrested_datetime,
    va.arrested_year,

    va.charge_category,
    va.arrested_charge,

    va.race,
    va.sex,
    va.age_group,

    va.source_year AS arrest_source_year,

    CASE
        WHEN va.arrest_id IS NOT NULL THEN 1
        ELSE 0
    END AS has_matching_arrest,

    CASE
        WHEN va.arrested_datetime IS NOT NULL
             AND vi.occurred_datetime IS NOT NULL
        THEN ROUND(
            (
                julianday(va.arrested_datetime)
                - julianday(vi.occurred_datetime)
            ) * 24,
            2
        )
        ELSE NULL
    END AS hours_from_incident_to_arrest

FROM vw_incident_detail vi

LEFT JOIN vw_arrest_detail va
    ON vi.case_number = va.case_number;


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

    ROUND(
        AVG(report_delay_hours),
        2
    ) AS avg_report_delay_hours

FROM vw_incident_detail

GROUP BY
    occurred_year,
    occurred_month,
    occurred_month_name,
    crime_group;


CREATE VIEW vw_disposition_summary AS
SELECT
    occurred_year,
    disposition_group,
    disposition,

    COUNT(*) AS incident_count,

    ROUND(
        COUNT(*) * 100.0
        / (
            SELECT COUNT(*)
            FROM vw_incident_detail total_incidents
            WHERE total_incidents.occurred_year
                = vw_incident_detail.occurred_year
        ),
        2
    ) AS incident_percentage

FROM vw_incident_detail

GROUP BY
    occurred_year,
    disposition_group,
    disposition

ORDER BY
    occurred_year,
    incident_count DESC;


CREATE VIEW vw_reporting_delay_summary AS
SELECT
    occurred_year,
    delay_bucket,

    COUNT(*) AS incident_count,

    ROUND(
        AVG(report_delay_hours),
        2
    ) AS avg_report_delay_hours,

    ROUND(
        AVG(report_delay_days),
        2
    ) AS avg_report_delay_days

FROM vw_incident_detail

GROUP BY
    occurred_year,
    delay_bucket

ORDER BY
    occurred_year,
    incident_count DESC;


CREATE VIEW vw_location_summary AS
SELECT
    occurred_year,
    location_group,
    location_raw,

    COUNT(*) AS incident_count,

    SUM(
        is_arrest_related
    ) AS arrest_related_count,

    ROUND(
        AVG(report_delay_hours),
        2
    ) AS avg_report_delay_hours

FROM vw_incident_detail

GROUP BY
    occurred_year,
    location_group,
    location_raw

ORDER BY
    occurred_year,
    incident_count DESC;


CREATE VIEW vw_crime_group_summary AS
SELECT
    occurred_year,
    crime_group,

    COUNT(*) AS incident_count,

    SUM(
        is_arrest_related
    ) AS arrest_related_count,

    ROUND(
        SUM(is_arrest_related) * 100.0
        / COUNT(*),
        2
    ) AS arrest_related_percentage,

    ROUND(
        AVG(report_delay_hours),
        2
    ) AS avg_report_delay_hours

FROM vw_incident_detail

GROUP BY
    occurred_year,
    crime_group

ORDER BY
    occurred_year,
    incident_count DESC;


CREATE VIEW vw_charge_category_summary AS
SELECT
    arrested_year,
    charge_category,

    COUNT(*) AS arrest_count,

    SUM(
        is_alcohol_related
    ) AS alcohol_related_count,

    SUM(
        is_drug_related
    ) AS drug_related_count,

    SUM(
        is_theft_related
    ) AS theft_related_count,

    ROUND(
        COUNT(*) * 100.0
        / (
            SELECT COUNT(*)
            FROM vw_arrest_detail total_arrests
            WHERE total_arrests.arrested_year
                = vw_arrest_detail.arrested_year
        ),
        2
    ) AS arrest_percentage

FROM vw_arrest_detail

GROUP BY
    arrested_year,
    charge_category

ORDER BY
    arrested_year,
    arrest_count DESC;


CREATE VIEW vw_demographic_summary AS
SELECT
    arrested_year,
    race,
    sex,
    age_group,

    COUNT(*) AS arrest_count,

    ROUND(
        COUNT(*) * 100.0
        / (
            SELECT COUNT(*)
            FROM vw_arrest_detail total_arrests
            WHERE total_arrests.arrested_year
                = vw_arrest_detail.arrested_year
        ),
        2
    ) AS arrest_percentage

FROM vw_arrest_detail

GROUP BY
    arrested_year,
    race,
    sex,
    age_group

ORDER BY
    arrested_year,
    arrest_count DESC;