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
- Keeps sample records compact and low-clutter
"""

import streamlit as st

from components.layout import (
    apply_custom_styles,
    show_compact_record_note,
    show_dashboard_header,
    show_info_hint
)

from components.metrics import format_number

from components.theme import get_theme

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
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
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


def safe_multiselect(label, options, help_text):
    """
    Create a multiselect filter.

    Empty selection means all values are included.
    """
    return st.multiselect(
        label,
        options=options,
        default=[],
        help=help_text
    )


def show_sidebar_intro(total_records):
    """Display a clean sidebar introduction."""
    theme = get_theme()

    st.sidebar.markdown("## Filters")

    show_info_hint(
        "How filters work",
        theme["copy"]["sidebar_filter_help"]
    )

    st.sidebar.metric(
        "Available Incidents",
        format_number(total_records)
    )

    st.sidebar.divider()


def apply_incident_filters(data):
    """
    Create sidebar filters for incident data and return filtered data.

    UX rule:
    - Empty filter means include all values.
    - Selected values narrow the dashboard.
    """
    show_sidebar_intro(len(data))

    month_options = get_month_order(data)
    crime_group_options = sorted(data["crime_group"].dropna().unique().tolist())
    disposition_options = sorted(data["disposition_group"].dropna().unique().tolist())
    location_options = sorted(data["location_group"].dropna().unique().tolist())
    semester_options = sorted(data["occurred_semester_period"].dropna().unique().tolist())

    with st.sidebar.expander("Time", expanded=True):
        selected_months = safe_multiselect(
            label="Month",
            options=month_options,
            help_text="Leave empty to include all months."
        )

        selected_semesters = safe_multiselect(
            label="Academic Period",
            options=semester_options,
            help_text="Leave empty to include all academic periods."
        )

    with st.sidebar.expander("Incident Type", expanded=True):
        selected_crime_groups = safe_multiselect(
            label="Crime Group",
            options=crime_group_options,
            help_text="Leave empty to include all crime groups."
        )

        selected_dispositions = safe_multiselect(
            label="Outcome Group",
            options=disposition_options,
            help_text="Leave empty to include all outcome groups."
        )

    with st.sidebar.expander("Location", expanded=False):
        selected_locations = safe_multiselect(
            label="Location Group",
            options=location_options,
            help_text="Leave empty to include all location groups."
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


def show_compact_data_review(incident_data, arrest_data, match_data):
    """
    Display sample records in a compact review panel.

    This keeps raw records available without making them dominate the dashboard.
    """
    theme = get_theme()

    st.divider()

    with st.expander("Data Review Panel", expanded=False):
        show_info_hint(
            "About this panel",
            theme["copy"]["data_review_help"]
        )

        matched_data = match_data[match_data["has_matching_arrest"] == 1]

        review_tab_1, review_tab_2, review_tab_3 = st.tabs(
            [
                f"Incident sample ({format_number(len(incident_data))})",
                f"Arrest sample ({format_number(len(arrest_data))})",
                f"Matched cases ({format_number(len(matched_data))})"
            ]
        )

        with review_tab_1:
            show_compact_record_note(
                "Showing the first 25 incident records from the current filtered view."
            )

            incident_columns = [
                "incident_id",
                "case_number",
                "occurred_datetime",
                "crime_group",
                "disposition_group",
                "location_group",
                "report_delay_hours"
            ]

            available_columns = [
                column for column in incident_columns
                if column in incident_data.columns
            ]

            st.dataframe(
                incident_data[available_columns].head(25),
                use_container_width=True,
                hide_index=True
            )

        with review_tab_2:
            if arrest_data.empty:
                st.info("No arrest records are available for the current filter selection.")
            else:
                show_compact_record_note(
                    "Showing the first 25 arrest records linked to the current filtered incident view."
                )

                arrest_columns = [
                    "arrest_id",
                    "arrest_number",
                    "case_number",
                    "arrested_datetime",
                    "charge_category",
                    "race",
                    "sex",
                    "age_group"
                ]

                available_columns = [
                    column for column in arrest_columns
                    if column in arrest_data.columns
                ]

                st.dataframe(
                    arrest_data[available_columns].head(25),
                    use_container_width=True,
                    hide_index=True
                )

        with review_tab_3:
            if matched_data.empty:
                st.info("No matched incident-arrest records are available for the current filter selection.")
            else:
                show_compact_record_note(
                    "Showing the first 25 incident records with matching arrest records."
                )

                matched_columns = [
                    "incident_id",
                    "case_number",
                    "occurred_datetime",
                    "crime_group",
                    "disposition_group",
                    "arrest_id",
                    "arrested_datetime",
                    "charge_category"
                ]

                available_columns = [
                    column for column in matched_columns
                    if column in matched_data.columns
                ]

                st.dataframe(
                    matched_data[available_columns].head(25),
                    use_container_width=True,
                    hide_index=True
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
            "Command Center",
            "Time Patterns",
            "Location Hotspots",
            "Case Outcomes",
            "Reporting Delay",
            "Arrests & Charges",
            "Data Quality"
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

    show_compact_data_review(
        filtered_incident_data,
        filtered_arrest_data,
        filtered_match_data
    )


if __name__ == "__main__":
    main()