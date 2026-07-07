"""
data_loader.py

Purpose:
Load dashboard-ready CSV files for the Terp Protect Streamlit dashboard.

This file keeps data loading separate from dashboard display logic.
"""

from pathlib import Path

import pandas as pd
import streamlit as st


DATA_DIR = Path("dashboard/powerbi/data")

INCIDENT_DETAIL_PATH = DATA_DIR / "incident_detail.csv"
ARREST_DETAIL_PATH = DATA_DIR / "arrest_detail.csv"
INCIDENT_ARREST_MATCH_PATH = DATA_DIR / "incident_arrest_match.csv"
CHARGE_CATEGORY_SUMMARY_PATH = DATA_DIR / "charge_category_summary.csv"
DEMOGRAPHIC_SUMMARY_PATH = DATA_DIR / "demographic_summary.csv"


@st.cache_data
def load_csv(path):
    """Load a CSV file with a friendly error if the file does not exist."""
    if not path.exists():
        st.error(f"Data file not found: {path}")
        st.stop()

    return pd.read_csv(path)


@st.cache_data
def load_dashboard_data():
    """Load all dashboard-ready datasets."""
    incident_data = load_csv(INCIDENT_DETAIL_PATH)
    arrest_data = load_csv(ARREST_DETAIL_PATH)
    match_data = load_csv(INCIDENT_ARREST_MATCH_PATH)
    charge_summary = load_csv(CHARGE_CATEGORY_SUMMARY_PATH)
    demographic_summary = load_csv(DEMOGRAPHIC_SUMMARY_PATH)

    incident_data["occurred_datetime"] = pd.to_datetime(
        incident_data["occurred_datetime"],
        errors="coerce"
    )

    incident_data["reported_datetime"] = pd.to_datetime(
        incident_data["reported_datetime"],
        errors="coerce"
    )

    arrest_data["arrested_datetime"] = pd.to_datetime(
        arrest_data["arrested_datetime"],
        errors="coerce"
    )

    match_data["occurred_datetime"] = pd.to_datetime(
        match_data["occurred_datetime"],
        errors="coerce"
    )

    match_data["reported_datetime"] = pd.to_datetime(
        match_data["reported_datetime"],
        errors="coerce"
    )

    match_data["arrested_datetime"] = pd.to_datetime(
        match_data["arrested_datetime"],
        errors="coerce"
    )

    return {
        "incident_data": incident_data,
        "arrest_data": arrest_data,
        "match_data": match_data,
        "charge_summary": charge_summary,
        "demographic_summary": demographic_summary
    }