"""
run_pipeline.py

Purpose:
Run the full Terp Protect data pipeline from raw public data extraction
to dashboard-ready exports.

Pipeline Steps:
1. Scrape UMPD Daily Crime and Incident Logs
2. Scrape UMPD Arrest Logs
3. Clean daily incident records
4. Clean arrest records
5. Build the SQLite database
6. Run SQL business analysis
7. Export dashboard-ready CSV files

Usage:
python run_pipeline.py

To launch the Streamlit dashboard:

python -m streamlit run dashboard/streamlit_app/app.py
"""

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent


PIPELINE_STEPS = [
    (
        "Scrape daily incident logs",
        "src/extract/scrape_daily_logs.py"
    ),
    (
        "Scrape arrest logs",
        "src/extract/scrape_arrest_logs.py"
    ),
    (
        "Clean daily incident logs",
        "src/transform/clean_daily_incidents.py"
    ),
    (
        "Clean arrest logs",
        "src/transform/clean_arrest_logs.py"
    ),
    (
        "Build SQLite database",
        "src/load/build_database.py"
    ),
    (
        "Run SQL business analysis",
        "src/analysis/run_business_analysis.py"
    ),
    (
        "Export dashboard-ready data",
        "src/analysis/export_dashboard_data.py"
    )
]


def run_step(step_number, total_steps, step_name, script_path):
    """Run one pipeline script and stop if it fails."""
    print(
        f"[{step_number}/{total_steps}] "
        f"{step_name}"
    )

    result = subprocess.run(
        [
            sys.executable,
            script_path
        ],
        cwd=PROJECT_ROOT
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Pipeline failed during: {step_name}"
        )


def main():
    """Run all Terp Protect pipeline steps."""
    print("Starting Terp Protect data pipeline...")

    total_steps = len(PIPELINE_STEPS)

    for step_number, step in enumerate(
        PIPELINE_STEPS,
        start=1
    ):
        step_name, script_path = step

        run_step(
            step_number,
            total_steps,
            step_name,
            script_path
        )

    print("\nPipeline completed successfully.")

    print("\nKey outputs:")
    print(
        "- data/raw/"
        "daily_incident_logs_2023_2025.csv"
    )
    print(
        "- data/raw/"
        "arrest_logs_2023_2025.csv"
    )
    print(
        "- data/processed/"
        "clean_daily_incidents_2023_2025.csv"
    )
    print(
        "- data/processed/"
        "clean_arrest_logs_2023_2025.csv"
    )
    print(
        "- data/database/"
        "terp_protect.db"
    )
    print(
        "- reports/"
        "sql_analysis_summary_2023_2025.md"
    )
    print(
        "- dashboard/powerbi/data/"
    )

    print("\nLaunch dashboard with:")
    print(
        "python -m streamlit run "
        "dashboard/streamlit_app/app.py"
    )


if __name__ == "__main__":
    try:
        main()

    except Exception as error:
        print(f"\n{error}")
        sys.exit(1)