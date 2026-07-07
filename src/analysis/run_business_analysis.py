"""
run_business_analysis.py

Purpose:
Run SQL-based business analysis queries against the Terp Protect SQLite database
and export the results as CSV files and a markdown summary report.

Current Scope:
- UMPD Daily Crime and Incident Logs: 2025
- UMPD Arrest Logs: 2025

Outputs:
- reports/sql_outputs/
- reports/sql_analysis_summary_2025.md

Role in Pipeline:
This script belongs to the analysis stage. It uses SQL views to generate reusable
analysis outputs for documentation, dashboarding, and project reporting.
"""

from pathlib import Path
import sqlite3

import pandas as pd


YEAR = 2025

DATABASE_PATH = Path("data/database/terp_protect.db")
VIEWS_PATH = Path("sql/02_views.sql")
OUTPUT_DIR = Path("reports/sql_outputs")
SUMMARY_PATH = Path(f"reports/sql_analysis_summary_{YEAR}.md")


BUSINESS_QUERIES = {
    "top_crime_groups": """
        SELECT
            crime_group,
            incident_count,
            arrest_related_count,
            arrest_related_percentage,
            avg_report_delay_hours
        FROM vw_crime_group_summary
        ORDER BY incident_count DESC;
    """,

    "top_crime_types": """
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
    """,

    "disposition_summary": """
        SELECT
            disposition_group,
            disposition,
            incident_count,
            incident_percentage
        FROM vw_disposition_summary
        ORDER BY incident_count DESC;
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
            occurred_weekday,
            COUNT(*) AS incident_count
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
    """,

    "hourly_incident_trends": """
        SELECT
            occurred_hour,
            COUNT(*) AS incident_count
        FROM vw_incident_detail
        GROUP BY
            occurred_hour
        ORDER BY
            occurred_hour;
    """,

    "location_group_summary": """
        SELECT
            location_group,
            COUNT(*) AS incident_count,
            SUM(is_arrest_related) AS arrest_related_count,
            ROUND(AVG(report_delay_hours), 2) AS avg_report_delay_hours
        FROM vw_incident_detail
        GROUP BY
            location_group
        ORDER BY
            incident_count DESC;
    """,

    "top_locations": """
        SELECT
            location_raw,
            location_group,
            COUNT(*) AS incident_count
        FROM vw_incident_detail
        GROUP BY
            location_raw,
            location_group
        ORDER BY
            incident_count DESC
        LIMIT 25;
    """,

    "reporting_delay_summary": """
        SELECT
            delay_bucket,
            incident_count,
            avg_report_delay_hours,
            avg_report_delay_days
        FROM vw_reporting_delay_summary
        ORDER BY
            incident_count DESC;
    """,

    "academic_period_summary": """
        SELECT
            occurred_semester_period,
            COUNT(*) AS incident_count
        FROM vw_incident_detail
        GROUP BY
            occurred_semester_period
        ORDER BY
            incident_count DESC;
    """,

    "arrest_charge_category_summary": """
        SELECT
            charge_category,
            arrest_count,
            alcohol_related_count,
            drug_related_count,
            theft_related_count,
            arrest_percentage
        FROM vw_charge_category_summary
        ORDER BY
            arrest_count DESC;
    """,

    "arrest_demographic_summary": """
        SELECT
            race,
            sex,
            age_group,
            arrest_count,
            arrest_percentage
        FROM vw_demographic_summary
        ORDER BY
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
            has_matching_arrest,
            COUNT(*) AS incident_count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM vw_incident_arrest_match), 2) AS incident_percentage
        FROM vw_incident_arrest_match
        GROUP BY
            has_matching_arrest
        ORDER BY
            has_matching_arrest DESC;
    """,

    "matched_incident_charge_summary": """
        SELECT
            charge_category,
            COUNT(*) AS matched_incident_count,
            ROUND(AVG(hours_from_incident_to_arrest), 2) AS avg_hours_from_incident_to_arrest
        FROM vw_incident_arrest_match
        WHERE has_matching_arrest = 1
        GROUP BY
            charge_category
        ORDER BY
            matched_incident_count DESC;
    """,

    "data_quality_review": """
        SELECT
            'Incident Records' AS record_type,
            COUNT(*) AS total_records,
            SUM(CASE WHEN has_valid_case_number = 0 THEN 1 ELSE 0 END) AS invalid_case_number_count,
            SUM(CASE WHEN has_valid_occurred_datetime = 0 THEN 1 ELSE 0 END) AS invalid_occurred_datetime_count,
            SUM(CASE WHEN has_valid_reported_datetime = 0 THEN 1 ELSE 0 END) AS invalid_reported_datetime_count,
            SUM(CASE WHEN has_valid_reporting_delay = 0 THEN 1 ELSE 0 END) AS invalid_reporting_delay_count
        FROM vw_incident_detail

        UNION ALL

        SELECT
            'Arrest Records' AS record_type,
            COUNT(*) AS total_records,
            SUM(CASE WHEN has_valid_case_number = 0 THEN 1 ELSE 0 END) AS invalid_case_number_count,
            SUM(CASE WHEN has_valid_arrested_datetime = 0 THEN 1 ELSE 0 END) AS invalid_occurred_datetime_count,
            NULL AS invalid_reported_datetime_count,
            SUM(CASE WHEN has_charge_text = 0 THEN 1 ELSE 0 END) AS invalid_reporting_delay_count
        FROM vw_arrest_detail;
    """
}


def connect_database():
    """Create a SQLite database connection."""
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(f"Database file not found: {DATABASE_PATH}")

    connection = sqlite3.connect(DATABASE_PATH)

    return connection


def refresh_views(connection):
    """Create or refresh SQL views before running analysis queries."""
    if not VIEWS_PATH.exists():
        raise FileNotFoundError(f"Views file not found: {VIEWS_PATH}")

    views_sql = VIEWS_PATH.read_text(
        encoding="utf-8"
    )

    connection.executescript(views_sql)

    connection.commit()


def run_query(connection, query_name, query_sql):
    """Run one SQL query and return the result as a dataframe."""
    print(f"Running query: {query_name}")

    result = pd.read_sql_query(
        query_sql,
        connection
    )

    return result


def save_query_output(query_name, dataframe):
    """Save a query result dataframe as CSV."""
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
    """Create a markdown summary file with selected SQL outputs."""
    summary_lines = [
        f"# SQL Analysis Summary {YEAR}",
        "",
        "## Overview",
        "This report summarizes SQL-based analysis outputs generated from the Terp Protect database.",
        "",
        "Current data included:",
        "- UMPD Daily Crime and Incident Logs, 2025",
        "- UMPD Arrest Logs, 2025",
        "",
        "## Database Analysis Areas",
        "- Incident volume and trends",
        "- Crime group distribution",
        "- Disposition and case outcome patterns",
        "- Reporting delay analysis",
        "- Location-based incident analysis",
        "- Arrest charge category analysis",
        "- Arrest demographic summary",
        "- Incident-to-arrest matching using UMPD case number",
        "- Data quality checks",
        ""
    ]

    for query_name, dataframe in query_results.items():
        summary_lines.append(f"## {query_name.replace('_', ' ').title()}")
        summary_lines.append("")

        if dataframe.empty:
            summary_lines.append("No records returned.")
        else:
            summary_lines.append(
                dataframe.head(20).to_markdown(
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

    print(f"Saved markdown summary: {SUMMARY_PATH}")


def main():
    """Run all business analysis queries."""
    print("Running Terp Protect SQL business analysis...")

    connection = connect_database()

    try:
        refresh_views(connection)

        query_results = {}

        for query_name, query_sql in BUSINESS_QUERIES.items():
            dataframe = run_query(
                connection,
                query_name,
                query_sql
            )

            query_results[query_name] = dataframe

            save_query_output(
                query_name,
                dataframe
            )

        create_markdown_summary(query_results)

        print("")
        print("SQL business analysis completed successfully.")

    finally:
        connection.close()


if __name__ == "__main__":
    main()