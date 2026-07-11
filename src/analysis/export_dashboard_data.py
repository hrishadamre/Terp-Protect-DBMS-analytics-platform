"""
export_dashboard_data.py

Purpose:
Export dashboard-ready CSV files from the Terp Protect SQLite database.

Current Scope:
- UMPD Daily Crime and Incident Logs: 2023-2025
- UMPD Arrest Logs: 2023-2025

Outputs:
- dashboard/powerbi/data/

Role in Pipeline:
This script belongs to the analysis and presentation stage.
It exports SQL views into CSV files for Streamlit, Power BI,
or other dashboard tools.
"""

from pathlib import Path
import sqlite3

import pandas as pd


DATABASE_PATH = Path("data/database/terp_protect.db")
VIEWS_PATH = Path("sql/02_views.sql")
OUTPUT_DIR = Path("dashboard/powerbi/data")


DASHBOARD_EXPORTS = {
    "incident_detail": """
        SELECT *
        FROM vw_incident_detail
        ORDER BY occurred_year, occurred_month, occurred_datetime;
    """,

    "arrest_detail": """
        SELECT *
        FROM vw_arrest_detail
        ORDER BY arrested_year, arrested_month, arrested_datetime;
    """,

    "incident_arrest_match": """
        SELECT *
        FROM vw_incident_arrest_match
        ORDER BY incident_source_year, occurred_datetime;
    """,

    "monthly_incident_trends": """
        SELECT *
        FROM vw_monthly_incident_trends
        ORDER BY occurred_year, occurred_month, crime_group;
    """,

    "crime_group_summary": """
        SELECT *
        FROM vw_crime_group_summary
        ORDER BY occurred_year, incident_count DESC;
    """,

    "disposition_summary": """
        SELECT *
        FROM vw_disposition_summary
        ORDER BY occurred_year, incident_count DESC;
    """,

    "reporting_delay_summary": """
        SELECT *
        FROM vw_reporting_delay_summary
        ORDER BY occurred_year, incident_count DESC;
    """,

    "location_summary": """
        SELECT *
        FROM vw_location_summary
        ORDER BY occurred_year, incident_count DESC;
    """,

    "charge_category_summary": """
        SELECT *
        FROM vw_charge_category_summary
        ORDER BY arrested_year, arrest_count DESC;
    """,

    "demographic_summary": """
        SELECT *
        FROM vw_demographic_summary
        ORDER BY arrested_year, arrest_count DESC;
    """,

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

    "yearly_arrest_summary": """
        SELECT
            arrested_year,
            COUNT(*) AS arrest_count
        FROM vw_arrest_detail
        GROUP BY arrested_year
        ORDER BY arrested_year;
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
    """Create or refresh SQL views before exporting data."""
    if not VIEWS_PATH.exists():
        raise FileNotFoundError(
            f"Views file not found: {VIEWS_PATH}"
        )

    views_sql = VIEWS_PATH.read_text(
        encoding="utf-8"
    )

    connection.executescript(views_sql)
    connection.commit()


def export_query(connection, export_name, query_sql):
    """Export one SQL query result to a CSV file."""
    print(f"Exporting dashboard dataset: {export_name}")

    dataframe = pd.read_sql_query(
        query_sql,
        connection
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = OUTPUT_DIR / f"{export_name}.csv"

    dataframe.to_csv(
        output_path,
        index=False
    )

    print(
        f"Saved {len(dataframe):,} rows to {output_path}"
    )


def main():
    """Export all dashboard-ready datasets."""
    print(
        "Exporting Terp Protect dashboard datasets..."
    )

    connection = connect_database()

    try:
        refresh_views(connection)

        for export_name, query_sql in DASHBOARD_EXPORTS.items():
            export_query(
                connection,
                export_name,
                query_sql
            )

        print("")
        print(
            f"Dashboard data export completed successfully: "
            f"{OUTPUT_DIR}"
        )

    finally:
        connection.close()


if __name__ == "__main__":
    main()