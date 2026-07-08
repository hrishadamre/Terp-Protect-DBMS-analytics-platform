"""
app.py

Purpose:
Main entry point for the Terp Protect Streamlit dashboard.

This file acts as the dashboard controller:
- Loads dashboard-ready data
- Applies sidebar filters
- Filters related arrest records
- Creates dashboard tabs
- Calls each dashboard section module

Most section logic, chart logic, layout helpers, metrics, and data loading functions
are stored in separate modules to keep the app modular and maintainable.
"""

import streamlit as st

from components.layout import (
    apply_custom_styles,
    show_dashboard_header
)

from components.metrics import format_number

from sections.arrest_analysis import show_arrest_analysis
from sections.data_quality import show_data_quality
from sections.executive_overview import show_executive_overview
from sections.incident_outcomes import show_incident_outcomes
from sections.incident_trends import show_incident_trends
from sections.location_analysis import show_location_analysis
from sections.reporting_delay import show_reporting_delay

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


def filter_if_selected(data, column, selected_values):
    """Filter a dataframe only when selected values are provided."""
    if not selected_values:
        return data

    return data[data[column].isin(selected_values)]


def show_sidebar_intro(total_records):
    """Display a clean sidebar introduction."""
    st.sidebar.markdown("## Incident Filters")

    st.sidebar.caption(
        "Leave a filter empty to include all values. Select values only when you want to narrow the dashboard."
    )

    st.sidebar.metric(
        "Available Records",
        format_number(total_records)
    )

    st.sidebar.divider()


def apply_incident_filters(data):
    """Create sidebar filters for incident data and return filtered data."""
    show_sidebar_intro(len(data))

    month_options = get_month_order(data)
    crime_group_options = sorted(data["crime_group"].dropna().unique().tolist())
    disposition_options = sorted(data["disposition_group"].dropna().unique().tolist())
    location_options = sorted(data["location_group"].dropna().unique().tolist())
    semester_options = sorted(data["occurred_semester_period"].dropna().unique().tolist())

    with st.sidebar.expander("Time", expanded=True):
        selected_months = st.multiselect(
            "Month",
            options=month_options,
            default=[],
            placeholder="All months",
            help="Leave empty to include all months."
        )

        selected_semesters = st.multiselect(
            "Academic Period",
            options=semester_options,
            default=[],
            placeholder="All academic periods",
            help="Leave empty to include all academic periods."
        )

    with st.sidebar.expander("Incident Type", expanded=True):
        selected_crime_groups = st.multiselect(
            "Crime Group",
            options=crime_group_options,
            default=[],
            placeholder="All crime groups",
            help="Leave empty to include all crime groups."
        )

        selected_dispositions = st.multiselect(
            "Outcome Group",
            options=disposition_options,
            default=[],
            placeholder="All outcomes",
            help="Leave empty to include all outcome groups."
        )

    with st.sidebar.expander("Location", expanded=False):
        selected_locations = st.multiselect(
            "Location Group",
            options=location_options,
            default=[],
            placeholder="All location groups",
            help="Leave empty to include all location groups."
        )

    filtered_data = data.copy()

    filtered_data = filter_if_selected(
        filtered_data,
        "occurred_month_name",
        selected_months
    )

    filtered_data = filter_if_selected(
        filtered_data,
        "occurred_semester_period",
        selected_semesters
    )

    filtered_data = filter_if_selected(
        filtered_data,
        "crime_group",
        selected_crime_groups
    )

    filtered_data = filter_if_selected(
        filtered_data,
        "disposition_group",
        selected_dispositions
    )

    filtered_data = filter_if_selected(
        filtered_data,
        "location_group",
        selected_locations
    )

    st.sidebar.divider()

    st.sidebar.markdown("### Current View")

    st.sidebar.metric(
        "Filtered Incidents",
        format_number(len(filtered_data))
    )

    active_filter_count = sum(
        [
            bool(selected_months),
            bool(selected_semesters),
            bool(selected_crime_groups),
            bool(selected_dispositions),
            bool(selected_locations)
        ]
    )

    st.sidebar.caption(
        f"{active_filter_count} active filter group(s)"
    )

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
        st.warning(
            "No incident records match the selected filters. Adjust the sidebar filters to continue."
        )
        return

    filtered_arrest_data, filtered_match_data = filter_related_arrest_data(
        arrest_data,
        match_data,
        filtered_incident_data
    )

    tab_1, tab_2, tab_3, tab_4, tab_5, tab_6, tab_7 = st.tabs(
        [
            "🏛️ Command Center",
            "⏱️ Time Patterns",
            "📍 Location Hotspots",
            "📂 Case Outcomes",
            "🕒 Reporting Delay",
            "⚖️ Arrests & Charges",
            "✅ Data Quality"
        ]
    )

    with tab_1:
        show_executive_overview(filtered_incident_data)

    with tab_2:
        show_incident_trends(filtered_incident_data)

    with tab_3:
        show_location_analysis(filtered_incident_data)

    with tab_4:
        show_incident_outcomes(filtered_incident_data)

    with tab_5:
        show_reporting_delay(filtered_incident_data)

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