"""
run_business_analysis.py

Purpose:
Run SQL-based business analysis queries against the Terp Protect
SQLite database and export the results as CSV files and a markdown report.

Current Scope:
- UMPD Daily Crime and Incident Logs: 2023-2025
- UMPD Arrest Logs: 2023-2025

Outputs:
- reports/sql_outputs/
- reports/sql_analysis_summary_2023_2025.md

Role in Pipeline:
This script belongs to the analysis stage. It uses SQL views to generate
reusable analysis outputs for documentation, dashboarding, and reporting.
"""

from pathlib import Path
import sqlite3

import pandas as pd


DATABASE_PATH = Path(
    "data/database/terp_protect.db"
)

VIEWS_PATH = Path(
    "sql/02_views.sql"
)

OUTPUT_DIR = Path(
    "reports/sql_outputs"
)

SUMMARY_PATH = Path(
    "reports/sql_analysis_summary_2023_2025.md"
)


BUSINESS_QUERIES = {
    "yearly_incident_summary": """
        SELECT
            occurred_year,
            COUNT(*) AS incident_count,
            SUM(is_arrest_related) AS arrest_related_count,
            SUM(is_pending) AS pending_count,
            SUM(is_closed) AS closed_count,
            ROUND(AVG(report_delay_hours), 2) AS avg_report_delay_hours
        FROM vw_incident_detail
        GROUP BY occurred_year
        ORDER BY occurred_year;
    """,

    "top_crime_groups": """
        SELECT
            occurred_year,
            crime_group,
            incident_count,
            arrest_related_count,
            arrest_related_percentage,
            avg_report_delay_hours
        FROM vw_crime_group_summary
        ORDER BY
            occurred_year,
            incident_count DESC;
    """,

    "top_crime_types": """
        SELECT
            occurred_year,
            crime_type,
            crime_group,
            COUNT(*) AS incident_count
        FROM vw_incident_detail
        GROUP BY
            occurred_year,
            crime_type,
            crime_group
        ORDER BY
            occurred_year,
            incident_count DESC;
    """,

    "disposition_summary": """
        SELECT
            occurred_year,
            disposition_group,
            disposition,
            incident_count,
            incident_percentage
        FROM vw_disposition_summary
        ORDER BY
            occurred_year,
            incident_count DESC;
    """,

    "monthly_incident_trends": """
        SELECT
            occurred_year,
            occurred_month,
            occurred_month_name,
            COUNT(*) AS incident_count
        FROM vw_incident_detail
        GROUP BY
            occurred_year,
            occurred_month,
            occurred_month_name
        ORDER BY
            occurred_year,
            occurred_month;
    """,

    "weekday_incident_trends": """
        SELECT
            occurred_year,
            occurred_weekday,
            COUNT(*) AS incident_count
        FROM vw_incident_detail
        GROUP BY
            occurred_year,
            occurred_weekday
        ORDER BY
            occurred_year,
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
    """,

    "hourly_incident_trends": """
        SELECT
            occurred_year,
            occurred_hour,
            COUNT(*) AS incident_count
        FROM vw_incident_detail
        GROUP BY
            occurred_year,
            occurred_hour
        ORDER BY
            occurred_year,
            occurred_hour;
    """,

    "location_group_summary": """
        SELECT
            occurred_year,
            location_group,
            COUNT(*) AS incident_count,
            SUM(is_arrest_related) AS arrest_related_count,
            ROUND(AVG(report_delay_hours), 2) AS avg_report_delay_hours
        FROM vw_incident_detail
        GROUP BY
            occurred_year,
            location_group
        ORDER BY
            occurred_year,
            incident_count DESC;
    """,

    "top_locations": """
        SELECT
            occurred_year,
            location_raw,
            location_group,
            COUNT(*) AS incident_count
        FROM vw_incident_detail
        GROUP BY
            occurred_year,
            location_raw,
            location_group
        ORDER BY
            occurred_year,
            incident_count DESC;
    """,

    "reporting_delay_summary": """
        SELECT
            occurred_year,
            delay_bucket,
            incident_count,
            avg_report_delay_hours,
            avg_report_delay_days
        FROM vw_reporting_delay_summary
        ORDER BY
            occurred_year,
            incident_count DESC;
    """,

    "academic_period_summary": """
        SELECT
            occurred_year,
            occurred_semester_period,
            COUNT(*) AS incident_count
        FROM vw_incident_detail
        GROUP BY
            occurred_year,
            occurred_semester_period
        ORDER BY
            occurred_year,
            incident_count DESC;
    """,

    "yearly_arrest_summary": """
        SELECT
            arrested_year,
            COUNT(*) AS arrest_count
        FROM vw_arrest_detail
        GROUP BY arrested_year
        ORDER BY arrested_year;
    """,

    "arrest_charge_category_summary": """
        SELECT
            arrested_year,
            charge_category,
            arrest_count,
            alcohol_related_count,
            drug_related_count,
            theft_related_count,
            arrest_percentage
        FROM vw_charge_category_summary
        ORDER BY
            arrested_year,
            arrest_count DESC;
    """,

    "arrest_demographic_summary": """
        SELECT
            arrested_year,
            race,
            sex,
            age_group,
            arrest_count,
            arrest_percentage
        FROM vw_demographic_summary
        ORDER BY
            arrested_year,
            arrest_count DESC;
    """,

    "monthly_arrest_trends": """
        SELECT
            arrested_year,
            arrested_month,
            arrested_month_name,
            COUNT(*) AS arrest_count
        FROM vw_arrest_detail
        GROUP BY
            arrested_year,
            arrested_month,
            arrested_month_name
        ORDER BY
            arrested_year,
            arrested_month;
    """,

    "incident_arrest_match_summary": """
        SELECT
            incident_source_year,
            has_matching_arrest,
            COUNT(*) AS incident_count,
            ROUND(
                COUNT(*) * 100.0
                / (
                    SELECT COUNT(*)
                    FROM vw_incident_arrest_match total_matches
                    WHERE total_matches.incident_source_year
                        = vw_incident_arrest_match.incident_source_year
                ),
                2
            ) AS incident_percentage
        FROM vw_incident_arrest_match
        GROUP BY
            incident_source_year,
            has_matching_arrest
        ORDER BY
            incident_source_year,
            has_matching_arrest DESC;
    """,

    "matched_incident_charge_summary": """
        SELECT
            incident_source_year,
            charge_category,
            COUNT(*) AS matched_incident_count,
            ROUND(
                AVG(hours_from_incident_to_arrest),
                2
            ) AS avg_hours_from_incident_to_arrest
        FROM vw_incident_arrest_match
        WHERE has_matching_arrest = 1
        GROUP BY
            incident_source_year,
            charge_category
        ORDER BY
            incident_source_year,
            matched_incident_count DESC;
    """,

    "data_quality_review": """
        SELECT
            source_year,
            'Incident Records' AS record_type,
            COUNT(*) AS total_records,
            SUM(
                CASE
                    WHEN has_valid_case_number = 0 THEN 1
                    ELSE 0
                END
            ) AS invalid_case_number_count,
            SUM(
                CASE
                    WHEN has_valid_occurred_datetime = 0 THEN 1
                    ELSE 0
                END
            ) AS invalid_datetime_count,
            SUM(
                CASE
                    WHEN has_valid_reported_datetime = 0 THEN 1
                    ELSE 0
                END
            ) AS invalid_reported_datetime_count,
            SUM(
                CASE
                    WHEN has_valid_reporting_delay = 0 THEN 1
                    ELSE 0
                END
            ) AS missing_or_invalid_detail_count
        FROM vw_incident_detail
        GROUP BY source_year

        UNION ALL

        SELECT
            source_year,
            'Arrest Records' AS record_type,
            COUNT(*) AS total_records,
            SUM(
                CASE
                    WHEN has_valid_case_number = 0 THEN 1
                    ELSE 0
                END
            ) AS invalid_case_number_count,
            SUM(
                CASE
                    WHEN has_valid_arrested_datetime = 0 THEN 1
                    ELSE 0
                END
            ) AS invalid_datetime_count,
            NULL AS invalid_reported_datetime_count,
            SUM(
                CASE
                    WHEN has_charge_text = 0 THEN 1
                    ELSE 0
                END
            ) AS missing_or_invalid_detail_count
        FROM vw_arrest_detail
        GROUP BY source_year

        ORDER BY
            source_year,
            record_type;
    """
}


def connect_database():
    """Create a SQLite database connection."""
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Database file not found: {DATABASE_PATH}"
        )

    return sqlite3.connect(DATABASE_PATH)


def refresh_views(connection):
    """Create or refresh SQL views before running queries."""
    if not VIEWS_PATH.exists():
        raise FileNotFoundError(
            f"Views file not found: {VIEWS_PATH}"
        )

    views_sql = VIEWS_PATH.read_text(
        encoding="utf-8"
    )

    connection.executescript(views_sql)
    connection.commit()


def run_query(connection, query_name, query_sql):
    """Run one SQL query and return the result."""
    print(f"Running query: {query_name}")

    return pd.read_sql_query(
        query_sql,
        connection
    )


def save_query_output(query_name, dataframe):
    """Save one query result as a CSV file."""
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = OUTPUT_DIR / f"{query_name}.csv"

    dataframe.to_csv(
        output_path,
        index=False
    )

    print(f"Saved output: {output_path}")


def create_markdown_summary(query_results):
    """Create a markdown report containing the SQL outputs."""
    summary_lines = [
        "# SQL Analysis Summary 2023-2025",
        "",
        "## Overview",
        "",
        (
            "This report summarizes SQL-based analysis outputs "
            "generated from the Terp Protect database."
        ),
        "",
        "Data included:",
        "- UMPD Daily Crime and Incident Logs, 2023-2025",
        "- UMPD Arrest Logs, 2023-2025",
        "",
        "## Database Analysis Areas",
        "",
        "- Yearly incident and arrest volume",
        "- Monthly, weekday, and hourly trends",
        "- Crime group and crime type distribution",
        "- Disposition and case outcome patterns",
        "- Reporting delay analysis",
        "- Location-based incident analysis",
        "- Arrest charge category analysis",
        "- Arrest demographic summary",
        "- Incident-to-arrest matching",
        "- Data quality checks",
        ""
    ]

    for query_name, dataframe in query_results.items():
        title = query_name.replace("_", " ").title()

        summary_lines.append(f"## {title}")
        summary_lines.append("")

        if dataframe.empty:
            summary_lines.append(
                "No records returned."
            )
        else:
            summary_lines.append(
                dataframe.head(30).to_markdown(
                    index=False
                )
            )

        summary_lines.append("")

    SUMMARY_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    SUMMARY_PATH.write_text(
        "\n".join(summary_lines),
        encoding="utf-8"
    )

    print(
        f"Saved markdown summary: {SUMMARY_PATH}"
    )


def main():
    """Run all business analysis queries."""
    print(
        "Running Terp Protect SQL business analysis..."
    )

    connection = connect_database()

    try:
        refresh_views(connection)

        query_results = {}

        for query_name, query_sql in BUSINESS_QUERIES.items():
            result = run_query(
                connection,
                query_name,
                query_sql
            )

            query_results[query_name] = result

            save_query_output(
                query_name,
                result
            )

        create_markdown_summary(
            query_results
        )

        print("")
        print(
            "SQL business analysis completed successfully."
        )

    finally:
        connection.close()


if __name__ == "__main__":
    main()