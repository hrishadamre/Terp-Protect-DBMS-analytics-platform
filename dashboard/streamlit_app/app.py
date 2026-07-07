"""
app.py

Purpose:
Main entry point for the Terp Protect Streamlit dashboard.

This file acts as the dashboard controller:
- Loads dashboard-ready data
- Applies sidebar filters
- Filters related arrest records
- Creates dashboard tabs
- Calls each page module

Most page logic, chart logic, layout helpers, metrics, and data loading functions
are stored in separate modules to keep the app modular and maintainable.
"""

import streamlit as st

from components.layout import (
    apply_custom_styles,
    show_dashboard_header
)

from pages.arrest_analysis import show_arrest_analysis
from pages.data_quality import show_data_quality
from pages.executive_overview import show_executive_overview
from pages.incident_outcomes import show_incident_outcomes
from pages.incident_trends import show_incident_trends
from pages.location_analysis import show_location_analysis
from pages.reporting_delay import show_reporting_delay

from utils.data_loader import load_dashboard_data


st.set_page_config(
    page_title="Terp Protect Dashboard",
    page_icon="🐢",
    layout="wide"
)


def get_month_order(data):
    """Return month names ordered by month number."""
    month_order = (
        data[["occurred_month", "occurred_month_name"]]
        .dropna()
        .drop_duplicates()
        .sort_values("occurred_month")
    )

    return month_order["occurred_month_name"].tolist()


def apply_incident_filters(data):
    """Create sidebar filters for incident data and return filtered data."""
    st.sidebar.header("Incident Filters")

    month_options = get_month_order(data)
    crime_group_options = sorted(data["crime_group"].dropna().unique().tolist())
    disposition_options = sorted(data["disposition_group"].dropna().unique().tolist())
    location_options = sorted(data["location_group"].dropna().unique().tolist())
    semester_options = sorted(data["occurred_semester_period"].dropna().unique().tolist())

    selected_months = st.sidebar.multiselect(
        "Month",
        options=month_options,
        default=month_options
    )

    selected_crime_groups = st.sidebar.multiselect(
        "Crime Group",
        options=crime_group_options,
        default=crime_group_options
    )

    selected_dispositions = st.sidebar.multiselect(
        "Disposition Group",
        options=disposition_options,
        default=disposition_options
    )

    selected_locations = st.sidebar.multiselect(
        "Location Group",
        options=location_options,
        default=location_options
    )

    selected_semesters = st.sidebar.multiselect(
        "Semester Period",
        options=semester_options,
        default=semester_options
    )

    filtered_data = data[
        data["occurred_month_name"].isin(selected_months)
        & data["crime_group"].isin(selected_crime_groups)
        & data["disposition_group"].isin(selected_dispositions)
        & data["location_group"].isin(selected_locations)
        & data["occurred_semester_period"].isin(selected_semesters)
    ]

    return filtered_data


def filter_related_arrest_data(arrest_data, match_data, filtered_incident_data):
    """Filter arrest and match datasets based on selected incident case numbers."""
    selected_case_numbers = (
        filtered_incident_data["case_number"]
        .dropna()
        .unique()
        .tolist()
    )

    filtered_match_data = match_data[
        match_data["case_number"].isin(selected_case_numbers)
    ]

    matched_arrest_ids = (
        filtered_match_data["arrest_id"]
        .dropna()
        .unique()
        .tolist()
    )

    filtered_arrest_data = arrest_data[
        arrest_data["arrest_id"].isin(matched_arrest_ids)
    ]

    return filtered_arrest_data, filtered_match_data


def show_sample_records(data):
    """Display sample incident records below the dashboard tabs."""
    with st.expander("View Sample Incident Records"):
        preview_columns = [
            "incident_id",
            "case_number",
            "occurred_datetime",
            "crime_group",
            "disposition_group",
            "location_group",
            "report_delay_hours"
        ]

        st.dataframe(
            data[preview_columns].head(100),
            use_container_width=True
        )


def main():
    """Run the Terp Protect Streamlit dashboard."""
    apply_custom_styles()

    dashboard_data = load_dashboard_data()

    incident_data = dashboard_data["incident_data"]
    arrest_data = dashboard_data["arrest_data"]
    match_data = dashboard_data["match_data"]
    charge_summary = dashboard_data["charge_summary"]
    demographic_summary = dashboard_data["demographic_summary"]

    show_dashboard_header()

    filtered_incident_data = apply_incident_filters(incident_data)

    if filtered_incident_data.empty:
        st.warning("No incident records match the selected filters.")
        return

    filtered_arrest_data, filtered_match_data = filter_related_arrest_data(
        arrest_data,
        match_data,
        filtered_incident_data
    )

    tab_1, tab_2, tab_3, tab_4, tab_5, tab_6, tab_7 = st.tabs(
        [
            "Executive Overview",
            "Incident Trends",
            "Incident Outcomes",
            "Reporting Delay",
            "Location Analysis",
            "Arrest & Charge Analysis",
            "Data Quality"
        ]
    )

    with tab_1:
        show_executive_overview(filtered_incident_data)

    with tab_2:
        show_incident_trends(filtered_incident_data)

    with tab_3:
        show_incident_outcomes(filtered_incident_data)

    with tab_4:
        show_reporting_delay(filtered_incident_data)

    with tab_5:
        show_location_analysis(filtered_incident_data)

    with tab_6:
        show_arrest_analysis(
            filtered_arrest_data,
            filtered_match_data,
            charge_summary,
            demographic_summary
        )

    with tab_7:
        show_data_quality(
            filtered_incident_data,
            filtered_arrest_data
        )

    st.divider()

    show_sample_records(filtered_incident_data)


if __name__ == "__main__":
    main()