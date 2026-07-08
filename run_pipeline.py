"""
run_pipeline.py

Purpose:
Run the full Terp Protect data pipeline from raw public data extraction
to dashboard-ready exports.

Pipeline Steps:
1. Scrape UMPD Daily Crime and Incident Logs
2. Clean daily incident records
3. Scrape UMPD Arrest Logs
4. Clean arrest records
5. Build the SQLite database
6. Run SQL business analysis
7. Export dashboard-ready CSV files

Usage:
python3 run_pipeline.py

Note:
This script rebuilds the data and analytics outputs.
To launch the Streamlit dashboard, run:

streamlit run dashboard/streamlit_app/app.py
"""

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent


PIPELINE_STEPS = [
    {
        "name": "Scrape daily incident logs",
        "command": ["python3", "src/extract/scrape_daily_logs.py"]
    },
    {
        "name": "Clean daily incident logs",
        "command": ["python3", "src/transform/clean_daily_incidents.py"]
    },
    {
        "name": "Scrape arrest logs",
        "command": ["python3", "src/extract/scrape_arrest_logs.py"]
    },
    {
        "name": "Clean arrest logs",
        "command": ["python3", "src/transform/clean_arrest_logs.py"]
    },
    {
        "name": "Build SQLite database",
        "command": ["python3", "src/load/build_database.py"]
    },
    {
        "name": "Run SQL business analysis",
        "command": ["python3", "src/analysis/run_business_analysis.py"]
    },
    {
        "name": "Export dashboard-ready data",
        "command": ["python3", "src/analysis/export_dashboard_data.py"]
    }
]


def run_command(step_number, total_steps, step):
    """Run one pipeline command and stop the pipeline if it fails."""
    step_name = step["name"]
    command = step["command"]

    print("\n" + "=" * 80)
    print(f"Step {step_number}/{total_steps}: {step_name}")
    print("=" * 80)
    print(f"Running command: {' '.join(command)}\n")

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True
    )

    if result.returncode != 0:
        print("\nPipeline failed.")
        print(f"Failed step: {step_name}")
        print(f"Exit code: {result.returncode}")
        sys.exit(result.returncode)

    print(f"\nCompleted: {step_name}")


def main():
    """Run all Terp Protect pipeline steps."""
    print("\nStarting Terp Protect data pipeline...")
    print(f"Project root: {PROJECT_ROOT}")

    total_steps = len(PIPELINE_STEPS)

    for index, step in enumerate(PIPELINE_STEPS, start=1):
        run_command(index, total_steps, step)

    print("\n" + "=" * 80)
    print("Pipeline completed successfully.")
    print("=" * 80)

    print("\nGenerated key outputs:")
    print("- data/raw/daily_incident_logs_2025.csv")
    print("- data/processed/clean_daily_incidents_2025.csv")
    print("- data/raw/arrest_logs_2025.csv")
    print("- data/processed/clean_arrest_logs_2025.csv")
    print("- data/database/terp_protect.db")
    print("- reports/sql_analysis_summary_2025.md")
    print("- dashboard/powerbi/data/")

    print("\nTo launch the dashboard, run:")
    print("python3 -m streamlit run dashboard/streamlit_app/app.py")


if __name__ == "__main__":
    main()