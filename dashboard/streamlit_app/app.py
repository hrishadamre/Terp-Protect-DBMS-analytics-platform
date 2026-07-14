"""
app.py

Main Streamlit application for the Terp Protect dashboard.

Responsibilities:
- Load dashboard-ready datasets
- Create and apply global filters
- Filter related arrest records
- Coordinate dashboard tabs and section modules
- Display the compact data-review panel
"""

import pandas as pd
import streamlit as st

from components.layout import (
    apply_custom_styles,
    show_compact_record_note,
    show_dashboard_header,
    show_data_review_heading,
    show_filter_summary,
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


MONTH_ORDER = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
]


WEEKDAY_ORDER = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]


ACADEMIC_PERIOD_ORDER = [
    "Winter Break",
    "Spring Semester",
    "Summer Break",
    "Fall Semester"
]


REPORTING_DELAY_ORDER = [
    "Same Day / Within 24 Hours",
    "1-3 Days",
    "4-7 Days",
    "Over 7 Days",
    "Unknown"
]


def get_unique_values(data, column):
    """
    Return unique non-null values while preserving their data types.
    """
    if column not in data.columns:
        return []

    return (
        data[column]
        .dropna()
        .drop_duplicates()
        .tolist()
    )


def get_year_options(data):
    """
    Return source years in descending order.
    """
    values = get_unique_values(
        data,
        "source_year"
    )

    years = []

    for value in values:
        numeric_value = pd.to_numeric(
            value,
            errors="coerce"
        )

        if pd.notna(numeric_value):
            years.append(
                int(numeric_value)
            )

    return sorted(
        set(years),
        reverse=True
    )


def get_ordered_options(
    data,
    column,
    preferred_order=None
):
    """
    Return unique values in a meaningful display order.
    """
    available_values = get_unique_values(
        data,
        column
    )

    if not available_values:
        return []

    if preferred_order is None:
        return sorted(
            available_values,
            key=lambda value: str(value).lower()
        )

    ordered_values = [
        value
        for value in preferred_order
        if value in available_values
    ]

    remaining_values = sorted(
        [
            value
            for value in available_values
            if value not in preferred_order
        ],
        key=lambda value: str(value).lower()
    )

    return ordered_values + remaining_values


def safe_multiselect(
    label,
    options,
    key
):
    """
    Create a global multiselect filter.
    """
    return st.multiselect(
        label=label,
        options=options,
        default=[],
        key=key,
        placeholder="All"
    )


def filter_if_selected(
    data,
    column,
    selected_values
):
    """
    Filter a dataframe only when values are selected.
    """
    if not selected_values:
        return data

    if column not in data.columns:
        return data

    return data[
        data[column].isin(selected_values)
    ]


def show_sidebar_header():
    """
    Display the filter title and centralized help tooltip.
    """
    theme = get_theme()

    st.sidebar.markdown(
        '<div class="sidebar-filter-heading">Filters</div>',
        unsafe_allow_html=True
    )

    with st.sidebar:
        show_info_hint(
            "Filter guide",
            theme["copy"]["sidebar_filter_help"]
        )


def apply_incident_filters(data):
    """
    Create and apply all global incident filters.
    """
    show_sidebar_header()

    year_options = get_year_options(data)

    month_options = get_ordered_options(
        data,
        "occurred_month_name",
        MONTH_ORDER
    )

    weekday_options = get_ordered_options(
        data,
        "occurred_weekday",
        WEEKDAY_ORDER
    )

    academic_period_options = get_ordered_options(
        data,
        "occurred_semester_period",
        ACADEMIC_PERIOD_ORDER
    )

    crime_group_options = get_ordered_options(
        data,
        "crime_group"
    )

    outcome_group_options = get_ordered_options(
        data,
        "disposition_group"
    )

    location_group_options = get_ordered_options(
        data,
        "location_group"
    )

    reporting_delay_options = get_ordered_options(
        data,
        "delay_bucket",
        REPORTING_DELAY_ORDER
    )

    with st.sidebar.expander(
        "Time",
        expanded=True
    ):
        selected_years = safe_multiselect(
            label="Year",
            options=year_options,
            key="filter_source_year"
        )

        selected_months = safe_multiselect(
            label="Month",
            options=month_options,
            key="filter_month"
        )

        selected_weekdays = safe_multiselect(
            label="Weekday",
            options=weekday_options,
            key="filter_weekday"
        )

        selected_academic_periods = safe_multiselect(
            label="Academic Period",
            options=academic_period_options,
            key="filter_academic_period"
        )

    with st.sidebar.expander(
        "Incident Type",
        expanded=False
    ):
        selected_crime_groups = safe_multiselect(
            label="Crime Group",
            options=crime_group_options,
            key="filter_crime_group"
        )

        selected_outcome_groups = safe_multiselect(
            label="Outcome Group",
            options=outcome_group_options,
            key="filter_outcome_group"
        )

    with st.sidebar.expander(
        "Location",
        expanded=False
    ):
        selected_location_groups = safe_multiselect(
            label="Location Group",
            options=location_group_options,
            key="filter_location_group"
        )

    with st.sidebar.expander(
        "Reporting",
        expanded=False
    ):
        selected_reporting_delays = safe_multiselect(
            label="Reporting Delay",
            options=reporting_delay_options,
            key="filter_reporting_delay"
        )

    filtered_data = data.copy()

    filter_definitions = [
        (
            "source_year",
            selected_years
        ),
        (
            "occurred_month_name",
            selected_months
        ),
        (
            "occurred_weekday",
            selected_weekdays
        ),
        (
            "occurred_semester_period",
            selected_academic_periods
        ),
        (
            "crime_group",
            selected_crime_groups
        ),
        (
            "disposition_group",
            selected_outcome_groups
        ),
        (
            "location_group",
            selected_location_groups
        ),
        (
            "delay_bucket",
            selected_reporting_delays
        )
    ]

    for column, selected_values in filter_definitions:
        filtered_data = filter_if_selected(
            filtered_data,
            column,
            selected_values
        )

    active_filter_count = sum(
        bool(selected_values)
        for _, selected_values in filter_definitions
    )

    st.sidebar.divider()

    with st.sidebar:
        show_filter_summary(
            total_records=len(data),
            filtered_records=len(filtered_data),
            active_filter_count=active_filter_count
        )

    return filtered_data


def filter_related_arrest_data(
    arrest_data,
    match_data,
    filtered_incident_data
):
    """
    Restrict arrest records to cases included in the current incident view.
    """
    selected_case_numbers = (
        filtered_incident_data["case_number"]
        .dropna()
        .drop_duplicates()
        .tolist()
    )

    filtered_match_data = match_data[
        match_data["case_number"].isin(
            selected_case_numbers
        )
    ].copy()

    matched_arrest_ids = (
        filtered_match_data["arrest_id"]
        .dropna()
        .drop_duplicates()
        .tolist()
    )

    filtered_arrest_data = arrest_data[
        arrest_data["arrest_id"].isin(
            matched_arrest_ids
        )
    ].copy()

    return (
        filtered_arrest_data,
        filtered_match_data
    )


def show_compact_data_review(
    incident_data,
    arrest_data,
    match_data
):
    """
    Display record samples for data validation.
    """
    theme = get_theme()

    st.divider()

    show_data_review_heading(
        theme["copy"].get(
            "data_review_help",
            (
                "Use this panel to inspect sample incident, arrest, "
                "and matched records from the current filtered view. "
                "It supports quick validation of the dashboard data."
            )
        )
    )

    st.markdown(
        '<div class="data-review-panel">',
        unsafe_allow_html=True
    )

    with st.expander(
        "Open record samples",
        expanded=False
    ):
        if "has_matching_arrest" in match_data.columns:
            matched_data = match_data[
                match_data["has_matching_arrest"] == 1
            ].copy()
        else:
            matched_data = match_data[
                match_data["arrest_id"].notna()
            ].copy()

        incident_tab, arrest_tab, match_tab = st.tabs(
            [
                (
                    "Incident sample "
                    f"({format_number(len(incident_data))})"
                ),
                (
                    "Arrest sample "
                    f"({format_number(len(arrest_data))})"
                ),
                (
                    "Matched cases "
                    f"({format_number(len(matched_data))})"
                )
            ]
        )

        with incident_tab:
            show_compact_record_note(
                "Showing the first 25 incident records from "
                "the current filtered view."
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

            visible_columns = [
                column
                for column in incident_columns
                if column in incident_data.columns
            ]

            st.dataframe(
                incident_data[
                    visible_columns
                ].head(25),
                use_container_width=True,
                hide_index=True
            )

        with arrest_tab:
            if arrest_data.empty:
                st.info(
                    "No arrest records are available for "
                    "the current incident selection."
                )
            else:
                show_compact_record_note(
                    "Showing the first 25 arrest records linked "
                    "to the current incident view."
                )

                arrest_columns = [
                    "arrest_id",
                    "arrest_number",
                    "case_number",
                    "arrested_datetime",
                    "charge_category",
                    "race",
                    "sex"
                ]

                visible_columns = [
                    column
                    for column in arrest_columns
                    if column in arrest_data.columns
                ]

                st.dataframe(
                    arrest_data[
                        visible_columns
                    ].head(25),
                    use_container_width=True,
                    hide_index=True
                )

        with match_tab:
            if matched_data.empty:
                st.info(
                    "No matched incident-arrest records are "
                    "available for the current selection."
                )
            else:
                show_compact_record_note(
                    "Showing the first 25 incidents with "
                    "matching arrest records."
                )

                match_columns = [
                    "incident_id",
                    "case_number",
                    "occurred_datetime",
                    "crime_group",
                    "disposition_group",
                    "arrest_id",
                    "arrested_datetime",
                    "charge_category"
                ]

                visible_columns = [
                    column
                    for column in match_columns
                    if column in matched_data.columns
                ]

                st.dataframe(
                    matched_data[
                        visible_columns
                    ].head(25),
                    use_container_width=True,
                    hide_index=True
                )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


def show_dashboard_sections(
    incident_data,
    arrest_data,
    match_data,
    charge_summary,
    demographic_summary
):
    """
    Create the main navigation tabs and render each dashboard section.
    """
    (
        command_tab,
        time_tab,
        location_tab,
        outcome_tab,
        delay_tab,
        arrest_tab,
        quality_tab
    ) = st.tabs(
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

    with command_tab:
        show_executive_overview(
            incident_data
        )

    with time_tab:
        show_incident_trends(
            incident_data
        )

    with location_tab:
        show_location_analysis(
            incident_data
        )

    with outcome_tab:
        show_incident_outcomes(
            incident_data
        )

    with delay_tab:
        show_reporting_delay(
            incident_data
        )

    with arrest_tab:
        show_arrest_analysis(
            arrest_data,
            match_data,
            charge_summary,
            demographic_summary
        )

    with quality_tab:
        show_data_quality(
            incident_data,
            arrest_data
        )


def main():
    """
    Run the Terp Protect Streamlit dashboard.
    """
    apply_custom_styles()

    dashboard_data = load_dashboard_data()

    incident_data = dashboard_data[
        "incident_data"
    ]

    arrest_data = dashboard_data[
        "arrest_data"
    ]

    match_data = dashboard_data[
        "match_data"
    ]

    charge_summary = dashboard_data[
        "charge_summary"
    ]

    demographic_summary = dashboard_data[
        "demographic_summary"
    ]

    show_dashboard_header()

    filtered_incident_data = apply_incident_filters(
        incident_data
    )

    if filtered_incident_data.empty:
        st.warning(
            "No incident records match the selected filters. "
            "Adjust the sidebar filters to continue."
        )

        return

    (
        filtered_arrest_data,
        filtered_match_data
    ) = filter_related_arrest_data(
        arrest_data,
        match_data,
        filtered_incident_data
    )

    show_dashboard_sections(
        incident_data=filtered_incident_data,
        arrest_data=filtered_arrest_data,
        match_data=filtered_match_data,
        charge_summary=charge_summary,
        demographic_summary=demographic_summary
    )

    show_compact_data_review(
        incident_data=filtered_incident_data,
        arrest_data=filtered_arrest_data,
        match_data=filtered_match_data
    )


if __name__ == "__main__":
    main()