"""
run_business_analysis.py

Purpose:
Run SQL-based business analysis on the Terp Protect SQLite database and export the results.

Current Scope:
- Source: UMPD Daily Crime and Incident Logs
- Year: 2025
- Database: data/database/terp_protect.db
- Views File: sql/02_views.sql

Outputs:
- reports/sql_outputs/*.csv
- reports/sql_analysis_summary_2025.md

Role in Pipeline:
This script belongs to the analysis stage. It converts database tables and views into
clear business analysis outputs that can support documentation, dashboards, and reporting.
"""

from pathlib import Path
from datetime import datetime
import sqlite3
import pandas as pd


DATABASE_PATH = Path("data/database/terp_protect.db")
VIEWS_SQL_PATH = Path("sql/02_views.sql")
OUTPUT_FOLDER = Path("reports/sql_outputs")
SUMMARY_OUTPUT_PATH = Path("reports/sql_analysis_summary_2025.md")


BUSINESS_QUERIES = {
    "top_crime_groups": """
        SELECT
            crime_group,
            COUNT(*) AS incident_count,
            ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS incident_percentage
        FROM vw_incident_detail
        GROUP BY
            crime_group
        ORDER BY
            incident_count DESC;
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
            COUNT(*) AS incident_count,
            ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS incident_percentage
        FROM vw_incident_detail
        GROUP BY
            disposition_group
        ORDER BY
            incident_count DESC;
    """,

    "arrest_related_summary": """
        SELECT
            COUNT(*) AS total_incidents,
            SUM(is_arrest_related) AS arrest_related_incidents,
            ROUND(100.0 * SUM(is_arrest_related) / COUNT(*), 2) AS arrest_related_percentage
        FROM vw_incident_detail;
    """,

    "monthly_incident_trends": """
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
    """,

    "weekday_incident_trends": """
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
    """,

    "hourly_incident_trends": """
        SELECT
            occurred_hour,
            COUNT(*) AS incident_count,
            SUM(is_arrest_related) AS arrest_related_count
        FROM vw_incident_detail
        GROUP BY
            occurred_hour
        ORDER BY
            occurred_hour;
    """,

    "top_locations": """
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
    """,

    "location_group_summary": """
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
    """,

    "reporting_delay_summary": """
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
            CASE delay_bucket
                WHEN 'Same Day / Within 24 Hours' THEN 1
                WHEN '1-3 Days' THEN 2
                WHEN '4-7 Days' THEN 3
                WHEN 'Over 7 Days' THEN 4
                ELSE 5
            END;
    """,

    "academic_period_summary": """
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
    """,

    "data_quality_review": """
        SELECT
            COUNT(*) AS total_incidents,
            SUM(CASE WHEN has_valid_case_number = 0 THEN 1 ELSE 0 END) AS missing_case_number_count,
            SUM(CASE WHEN has_valid_occurred_datetime = 0 THEN 1 ELSE 0 END) AS invalid_occurred_datetime_count,
            SUM(CASE WHEN has_valid_reported_datetime = 0 THEN 1 ELSE 0 END) AS invalid_reported_datetime_count,
            SUM(CASE WHEN has_valid_reporting_delay = 0 THEN 1 ELSE 0 END) AS invalid_reporting_delay_count
        FROM vw_incident_detail;
    """
}


def connect_database():
    """Connect to the SQLite database."""
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(f"Database file not found: {DATABASE_PATH}")

    connection = sqlite3.connect(DATABASE_PATH)

    return connection


def apply_views(connection):
    """Create or refresh SQL views before running analysis queries."""
    if not VIEWS_SQL_PATH.exists():
        raise FileNotFoundError(f"Views SQL file not found: {VIEWS_SQL_PATH}")

    views_sql = VIEWS_SQL_PATH.read_text()

    connection.executescript(views_sql)
    connection.commit()


def run_queries(connection):
    """Run all business queries and return results as dataframes."""
    query_results = {}

    for query_name, query_sql in BUSINESS_QUERIES.items():
        print(f"Running query: {query_name}")

        result_df = pd.read_sql_query(query_sql, connection)
        query_results[query_name] = result_df

    return query_results


def export_query_results(query_results):
    """Export each query result to a CSV file."""
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    for query_name, result_df in query_results.items():
        output_path = OUTPUT_FOLDER / f"{query_name}.csv"
        result_df.to_csv(output_path, index=False)

        print(f"Saved: {output_path}")


def dataframe_to_markdown_table(df, max_rows=10):
    """Convert a dataframe to a markdown table with a row limit."""
    if df.empty:
        return "No records returned."

    preview_df = df.head(max_rows)

    return preview_df.to_markdown(index=False)


def create_summary_report(query_results):
    """Create a markdown summary report from selected query outputs."""
    summary_lines = []

    summary_lines.append("# SQL Analysis Summary")
    summary_lines.append("")
    summary_lines.append(f"Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary_lines.append("")
    summary_lines.append("## Scope")
    summary_lines.append("")
    summary_lines.append("- Dataset: UMPD Daily Crime and Incident Logs")
    summary_lines.append("- Year: 2025")
    summary_lines.append("- Database: `data/database/terp_protect.db`")
    summary_lines.append("")
    summary_lines.append("## Summary Tables")
    summary_lines.append("")

    sections = [
        ("Top Crime Groups", "top_crime_groups"),
        ("Top Crime Types", "top_crime_types"),
        ("Disposition Summary", "disposition_summary"),
        ("Arrest-Related Summary", "arrest_related_summary"),
        ("Monthly Incident Trends", "monthly_incident_trends"),
        ("Location Group Summary", "location_group_summary"),
        ("Reporting Delay Summary", "reporting_delay_summary"),
        ("Academic Period Summary", "academic_period_summary"),
        ("Data Quality Review", "data_quality_review")
    ]

    for section_title, query_name in sections:
        summary_lines.append(f"### {section_title}")
        summary_lines.append("")
        summary_lines.append(dataframe_to_markdown_table(query_results[query_name]))
        summary_lines.append("")

    SUMMARY_OUTPUT_PATH.write_text("\n".join(summary_lines))

    print(f"Summary report saved: {SUMMARY_OUTPUT_PATH}")


def main():
    """Run the full SQL analysis export process."""
    print("Connecting to database...")
    connection = connect_database()

    print("Creating or refreshing SQL views...")
    apply_views(connection)

    print("Running business analysis queries...")
    query_results = run_queries(connection)

    print("Exporting query results...")
    export_query_results(query_results)

    print("Creating markdown summary report...")
    create_summary_report(query_results)

    connection.close()

    print("")
    print("SQL analysis process complete.")


if __name__ == "__main__":
    main()