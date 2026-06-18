"""
export_dashboard_data.py

Purpose:
Export dashboard-ready CSV files from the Terp Protect SQLite database.

Current Scope:
- Source: UMPD Daily Crime and Incident Logs
- Year: 2025
- Database: data/database/terp_protect.db
- Views File: sql/02_views.sql
- Output Folder: dashboard/powerbi/data/

Role in Pipeline:
This script prepares clean analytical datasets for Power BI. It exports joined and summarized
SQL view outputs so the dashboard can be built without repeatedly writing SQL queries.
"""

from pathlib import Path
import sqlite3
import pandas as pd


DATABASE_PATH = Path("data/database/terp_protect.db")
VIEWS_SQL_PATH = Path("sql/02_views.sql")
OUTPUT_FOLDER = Path("dashboard/powerbi/data")


DASHBOARD_EXPORTS = {
    "incident_detail": """
        SELECT
            *
        FROM vw_incident_detail;
    """,

    "monthly_incident_trends": """
        SELECT
            *
        FROM vw_monthly_incident_trends;
    """,

    "crime_group_summary": """
        SELECT
            *
        FROM vw_crime_group_summary;
    """,

    "disposition_summary": """
        SELECT
            *
        FROM vw_disposition_summary;
    """,

    "reporting_delay_summary": """
        SELECT
            *
        FROM vw_reporting_delay_summary;
    """,

    "location_summary": """
        SELECT
            *
        FROM vw_location_summary;
    """
}


def connect_database():
    """Connect to the SQLite database."""
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(f"Database file not found: {DATABASE_PATH}")

    connection = sqlite3.connect(DATABASE_PATH)

    return connection


def refresh_views(connection):
    """Create or refresh SQL views before exporting dashboard data."""
    if not VIEWS_SQL_PATH.exists():
        raise FileNotFoundError(f"Views SQL file not found: {VIEWS_SQL_PATH}")

    views_sql = VIEWS_SQL_PATH.read_text()

    connection.executescript(views_sql)
    connection.commit()


def export_dashboard_tables(connection):
    """Export each dashboard query result as a CSV file."""
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    for export_name, query in DASHBOARD_EXPORTS.items():
        print(f"Exporting: {export_name}")

        df = pd.read_sql_query(query, connection)

        output_path = OUTPUT_FOLDER / f"{export_name}.csv"

        df.to_csv(output_path, index=False)

        print(f"Saved {len(df):,} rows to {output_path}")


def main():
    """Run the full dashboard export process."""
    print("Connecting to database...")
    connection = connect_database()

    print("Refreshing SQL views...")
    refresh_views(connection)

    print("Exporting dashboard-ready CSV files...")
    export_dashboard_tables(connection)

    connection.close()

    print("")
    print(f"Dashboard exports complete: {OUTPUT_FOLDER}")


if __name__ == "__main__":
    main()