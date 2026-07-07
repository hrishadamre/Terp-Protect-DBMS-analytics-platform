"""
export_dashboard_data.py

Purpose:
Export dashboard-ready CSV files from the Terp Protect SQLite database.

Current Scope:
- UMPD Daily Crime and Incident Logs: 2025
- UMPD Arrest Logs: 2025

Outputs:
- dashboard/powerbi/data/

Role in Pipeline:
This script belongs to the analysis/presentation preparation stage. It exports SQL views
into CSV files that can be used by Streamlit, Power BI, or other dashboard tools.
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
        FROM vw_incident_detail;
    """,

    "arrest_detail": """
        SELECT *
        FROM vw_arrest_detail;
    """,

    "incident_arrest_match": """
        SELECT *
        FROM vw_incident_arrest_match;
    """,

    "monthly_incident_trends": """
        SELECT *
        FROM vw_monthly_incident_trends;
    """,

    "crime_group_summary": """
        SELECT *
        FROM vw_crime_group_summary;
    """,

    "disposition_summary": """
        SELECT *
        FROM vw_disposition_summary;
    """,

    "reporting_delay_summary": """
        SELECT *
        FROM vw_reporting_delay_summary;
    """,

    "location_summary": """
        SELECT *
        FROM vw_location_summary;
    """,

    "charge_category_summary": """
        SELECT *
        FROM vw_charge_category_summary;
    """,

    "demographic_summary": """
        SELECT *
        FROM vw_demographic_summary;
    """
}


def connect_database():
    """Create a SQLite database connection."""
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(f"Database file not found: {DATABASE_PATH}")

    connection = sqlite3.connect(DATABASE_PATH)

    return connection


def refresh_views(connection):
    """Create or refresh SQL views before exporting dashboard data."""
    if not VIEWS_PATH.exists():
        raise FileNotFoundError(f"Views file not found: {VIEWS_PATH}")

    views_sql = VIEWS_PATH.read_text(
        encoding="utf-8"
    )

    connection.executescript(views_sql)

    connection.commit()


def export_query(connection, export_name, query_sql):
    """Export one SQL query result to a dashboard CSV file."""
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

    print(f"Saved {len(dataframe):,} rows to {output_path}")


def main():
    """Export all dashboard-ready datasets."""
    print("Exporting Terp Protect dashboard datasets...")

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
        print(f"Dashboard data export completed successfully: {OUTPUT_DIR}")

    finally:
        connection.close()


if __name__ == "__main__":
    main()