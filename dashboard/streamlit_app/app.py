"""
app.py

Main Streamlit application for the Terp Protect dashboard.

Responsibilities:
- Load dashboard-ready datasets
- Create and apply global filters
- Display active filter context
- Reset all filters
- Filter related arrest records
- Coordinate dashboard tabs and section modules
- Display compact record-review tables
"""

import html

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


FILTER_KEYS = [
    "filter_source_year",
    "filter_month",
    "filter_weekday",
    "filter_academic_period",
    "filter_crime_group",
    "filter_outcome_group",
    "filter_location_group",
    "filter_reporting_delay"
]


def get_unique_values(
    data,
    column
):
    """
    Return unique non-null values while preserving their data types.
    """
    if (
        data is None
        or data.empty
        or column not in data.columns
    ):
        return []

    return (
        data[column]
        .dropna()
        .drop_duplicates()
        .tolist()
    )


def get_year_options(data):
    """
    Return available source years in descending order.
    """
    year_column = None

    for candidate in [
        "source_year",
        "occurred_year",
        "year"
    ]:
        if candidate in data.columns:
            year_column = candidate
            break

    if year_column is None:
        return []

    values = get_unique_values(
        data,
        year_column
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


def get_year_column(data):
    """
    Return the available year column used by the dashboard.
    """
    for candidate in [
        "source_year",
        "occurred_year",
        "year"
    ]:
        if candidate in data.columns:
            return candidate

    return None


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
            key=lambda value: str(
                value
            ).lower()
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
        key=lambda value: str(
            value
        ).lower()
    )

    return (
        ordered_values
        + remaining_values
    )


def safe_multiselect(
    label,
    options,
    key
):
    """
    Create a global multiselect filter.

    An empty selection means that all available values are included.
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
    Apply a dataframe filter only when values are selected.
    """
    if not selected_values:
        return data

    if column not in data.columns:
        return data

    return data[
        data[column].isin(
            selected_values
        )
    ].copy()


def reset_all_filters():
    """
    Clear every global filter.
    """
    for key in FILTER_KEYS:
        st.session_state[key] = []


def show_sidebar_header():
    """
    Display the sidebar filter heading and help.
    """
    st.sidebar.markdown(
        '<div class="sidebar-filter-heading">Filters</div>',
        unsafe_allow_html=True
    )

    with st.sidebar:
        show_info_hint(
            "Filter guide",
            (
                "Filters narrow every dashboard section. Leave a filter "
                "empty to include all available values."
            )
        )


def format_filter_values(
    values,
    maximum_visible=3
):
    """
    Format selected filter values for compact display.
    """
    if not values:
        return ""

    formatted_values = [
        str(value)
        for value in values
    ]

    if len(formatted_values) <= maximum_visible:
        return ", ".join(
            formatted_values
        )

    visible_values = formatted_values[
        :maximum_visible
    ]

    remaining_count = (
        len(formatted_values)
        - maximum_visible
    )

    return (
        ", ".join(
            visible_values
        )
        + f" +{remaining_count}"
    )


def build_active_filter_details(
    filter_selections
):
    """
    Convert filter selections into readable labels and values.
    """
    filter_labels = {
        "source_year": "Year",
        "occurred_year": "Year",
        "year": "Year",
        "occurred_month_name": "Month",
        "occurred_weekday": "Weekday",
        "occurred_semester_period": "Academic Period",
        "crime_group": "Crime Group",
        "disposition_group": "Outcome Group",
        "location_group": "Location Group",
        "delay_bucket": "Reporting Delay"
    }

    active_filters = []

    for column, selected_values in filter_selections:
        if not selected_values:
            continue

        active_filters.append(
            {
                "label": filter_labels.get(
                    column,
                    column.replace(
                        "_",
                        " "
                    ).title()
                ),
                "values": selected_values,
                "display_value": format_filter_values(
                    selected_values
                )
            }
        )

    return active_filters


def show_sidebar_active_filters(
    active_filters
):
    """
    Display active filters in the sidebar.
    """
    if not active_filters:
        panel_html = (
            '<div class="active-filter-panel">'
            '<div class="active-filter-panel-title">'
            'Active Filters'
            '</div>'
            '<div class="active-filter-empty">'
            'No filters applied'
            '</div>'
            '</div>'
        )

        st.sidebar.markdown(
            panel_html,
            unsafe_allow_html=True
        )

        return

    filter_rows = []

    for filter_item in active_filters:
        safe_label = html.escape(
            str(
                filter_item["label"]
            )
        )

        safe_value = html.escape(
            str(
                filter_item["display_value"]
            )
        )

        filter_rows.append(
            (
                '<div class="active-filter-row">'
                '<span class="active-filter-label">'
                f'{safe_label}'
                '</span>'
                '<span class="active-filter-value">'
                f'{safe_value}'
                '</span>'
                '</div>'
            )
        )

    panel_html = (
        '<div class="active-filter-panel">'
        '<div class="active-filter-panel-title">'
        'Active Filters'
        '</div>'
        f'{"".join(filter_rows)}'
        '</div>'
    )

    st.sidebar.markdown(
        panel_html,
        unsafe_allow_html=True
    )


def show_main_active_filter_summary(
    active_filters,
    filtered_record_count
):
    """
    Display clean active-filter chips above the dashboard tabs.

    The HTML is intentionally built without indentation so Streamlit
    does not interpret it as a Markdown code block.
    """
    safe_record_count = html.escape(
        format_number(
            filtered_record_count
        )
    )

    if not active_filters:
        summary_html = (
            '<div class="main-filter-context">'
            '<div class="main-filter-context-label">'
            'Current View'
            '</div>'
            '<div class="main-filter-chip neutral">'
            'All records'
            '</div>'
            '<div class="main-filter-record-count">'
            f'{safe_record_count} incidents'
            '</div>'
            '</div>'
        )

        st.markdown(
            summary_html,
            unsafe_allow_html=True
        )

        return

    chips = []

    for filter_item in active_filters:
        safe_label = html.escape(
            str(
                filter_item["label"]
            )
        )

        safe_value = html.escape(
            str(
                filter_item["display_value"]
            )
        )

        chips.append(
            (
                '<div class="main-filter-chip">'
                '<span>'
                f'{safe_label}'
                '</span>'
                '<strong>'
                f'{safe_value}'
                '</strong>'
                '</div>'
            )
        )

    summary_html = (
        '<div class="main-filter-context">'
        '<div class="main-filter-context-label">'
        'Current View'
        '</div>'
        '<div class="main-filter-chip-wrapper">'
        f'{"".join(chips)}'
        '</div>'
        '<div class="main-filter-record-count">'
        f'{safe_record_count} incidents'
        '</div>'
        '</div>'
    )

    st.markdown(
        summary_html,
        unsafe_allow_html=True
    )


def apply_filter_summary_styles():
    """
    Add styles for active-filter panels and filter chips.
    """
    st.markdown(
        """
<style>
.active-filter-panel {
    margin-top: 0.55rem;
    margin-bottom: 0.75rem;
    padding: 0.75rem 0.78rem;

    background:
        linear-gradient(
            145deg,
            rgba(22, 32, 48, 0.92),
            rgba(12, 19, 30, 0.92)
        );

    border: 1px solid rgba(148, 163, 184, 0.20);
    border-radius: 10px;
}

.active-filter-panel-title {
    margin-bottom: 0.55rem;

    color: #F8FAFC;

    font-size: 0.77rem;
    font-weight: 700;
    letter-spacing: 0.045em;
    text-transform: uppercase;
}

.active-filter-row {
    display: flex;
    flex-direction: column;
    gap: 0.12rem;

    margin-top: 0.42rem;
    padding-top: 0.42rem;

    border-top: 1px solid rgba(148, 163, 184, 0.11);
}

.active-filter-row:first-of-type {
    margin-top: 0;
}

.active-filter-label {
    color: #94A3B8;

    font-size: 0.69rem;
    font-weight: 600;
    letter-spacing: 0.035em;
    text-transform: uppercase;
}

.active-filter-value {
    color: #E2E8F0;

    font-size: 0.79rem;
    line-height: 1.35;
}

.active-filter-empty {
    color: #94A3B8;

    font-size: 0.78rem;
}

.main-filter-context {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.48rem;

    width: 100%;
    box-sizing: border-box;

    margin: 0.55rem 0 0.85rem 0;
    padding: 0.58rem 0.7rem;

    background: rgba(15, 23, 38, 0.72);

    border: 1px solid rgba(148, 163, 184, 0.17);
    border-radius: 11px;
}

.main-filter-context-label {
    flex-shrink: 0;

    margin-right: 0.1rem;

    color: #94A3B8;

    font-size: 0.71rem;
    font-weight: 700;
    letter-spacing: 0.055em;
    text-transform: uppercase;
}

.main-filter-chip-wrapper {
    display: flex;
    align-items: center;
    flex: 1;
    flex-wrap: wrap;
    gap: 0.38rem;

    min-width: 0;
}

.main-filter-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;

    max-width: 100%;
    padding: 0.28rem 0.48rem;

    color: #CBD5E1;
    background: rgba(30, 58, 74, 0.42);

    border: 1px solid rgba(142, 216, 243, 0.22);
    border-radius: 8px;

    font-size: 0.73rem;
    line-height: 1.2;
}

.main-filter-chip span {
    color: #8ED8F3;

    font-weight: 600;
}

.main-filter-chip strong {
    max-width: 350px;
    overflow: hidden;

    color: #F8FAFC;

    font-weight: 600;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.main-filter-chip.neutral {
    color: #CBD5E1;
    background: rgba(51, 65, 85, 0.30);

    border-color: rgba(148, 163, 184, 0.20);
}

.main-filter-record-count {
    flex-shrink: 0;

    margin-left: auto;

    color: #CBD5E1;

    font-size: 0.75rem;
    font-weight: 600;
    white-space: nowrap;
}

div[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    min-height: 2.25rem;

    color: #F8D8DE;
    background: rgba(99, 37, 48, 0.28);

    border: 1px solid rgba(231, 138, 152, 0.42);
    border-radius: 9px;

    font-size: 0.78rem;
    font-weight: 650;
}

div[data-testid="stSidebar"] .stButton > button:hover {
    color: #FFFFFF;
    background: rgba(128, 45, 60, 0.40);

    border-color: rgba(231, 138, 152, 0.75);
}

div[data-testid="stSidebar"] .stButton > button:disabled {
    color: #64748B;
    background: rgba(51, 65, 85, 0.20);

    border-color: rgba(100, 116, 139, 0.25);
}

@media (max-width: 900px) {
    .main-filter-record-count {
        width: 100%;
        margin-left: 0;
    }

    .main-filter-chip strong {
        max-width: 230px;
    }
}
</style>
        """,
        unsafe_allow_html=True
    )


def apply_incident_filters(data):
    """
    Create and apply global incident filters.

    Returns:
    - filtered incident dataframe
    - active filter details
    """
    show_sidebar_header()

    year_column = get_year_column(
        data
    )

    year_options = get_year_options(
        data
    )

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

    filter_definitions = []

    if year_column is not None:
        filter_definitions.append(
            (
                year_column,
                selected_years
            )
        )

    filter_definitions.extend(
        [
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
    )

    filtered_data = data.copy()

    for column, selected_values in filter_definitions:
        filtered_data = filter_if_selected(
            filtered_data,
            column,
            selected_values
        )

    active_filters = build_active_filter_details(
        filter_definitions
    )

    st.sidebar.divider()

    show_sidebar_active_filters(
        active_filters
    )

    st.sidebar.button(
        "Reset All Filters",
        key="reset_all_dashboard_filters",
        on_click=reset_all_filters,
        disabled=(
            len(active_filters)
            == 0
        ),
        use_container_width=True
    )

    st.sidebar.divider()

    with st.sidebar:
        show_filter_summary(
            total_records=len(
                data
            ),
            filtered_records=len(
                filtered_data
            ),
            active_filter_count=len(
                active_filters
            )
        )

    return (
        filtered_data,
        active_filters
    )


def filter_related_arrest_data(
    arrest_data,
    match_data,
    filtered_incident_data
):
    """
    Restrict arrest and match records to the selected incidents.
    """
    if (
        filtered_incident_data is None
        or filtered_incident_data.empty
        or "case_number" not in filtered_incident_data.columns
    ):
        return (
            arrest_data.iloc[
                0:0
            ].copy(),
            match_data.iloc[
                0:0
            ].copy()
        )

    selected_case_numbers = (
        filtered_incident_data[
            "case_number"
        ]
        .dropna()
        .drop_duplicates()
        .tolist()
    )

    if "case_number" in match_data.columns:
        filtered_match_data = match_data[
            match_data["case_number"].isin(
                selected_case_numbers
            )
        ].copy()

    else:
        filtered_match_data = match_data.iloc[
            0:0
        ].copy()

    if (
        "arrest_id" in filtered_match_data.columns
        and "arrest_id" in arrest_data.columns
    ):
        matched_arrest_ids = (
            filtered_match_data[
                "arrest_id"
            ]
            .dropna()
            .drop_duplicates()
            .tolist()
        )

        filtered_arrest_data = arrest_data[
            arrest_data["arrest_id"].isin(
                matched_arrest_ids
            )
        ].copy()

    elif (
        "case_number" in arrest_data.columns
        and selected_case_numbers
    ):
        filtered_arrest_data = arrest_data[
            arrest_data["case_number"].isin(
                selected_case_numbers
            )
        ].copy()

    else:
        filtered_arrest_data = arrest_data.iloc[
            0:0
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
    Display compact record samples for dashboard validation.
    """
    st.divider()

    show_data_review_heading(
        (
            "Use this panel to inspect sample incident, arrest, and "
            "matched records from the current filtered view."
        )
    )

    with st.expander(
        "Open record samples",
        expanded=False
    ):
        if "has_matching_arrest" in match_data.columns:
            match_flag = pd.to_numeric(
                match_data[
                    "has_matching_arrest"
                ],
                errors="coerce"
            ).fillna(0)

            matched_data = match_data[
                match_flag == 1
            ].copy()

        elif "arrest_id" in match_data.columns:
            matched_data = match_data[
                match_data["arrest_id"].notna()
            ].copy()

        else:
            matched_data = match_data.iloc[
                0:0
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
                "Showing the first 25 incident records from the "
                "current filtered view."
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
                    "No arrest records are available for the current "
                    "incident selection."
                )

            else:
                show_compact_record_note(
                    "Showing the first 25 arrest records linked to "
                    "the current incident view."
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
                    "No matched incident-arrest records are available "
                    "for the current selection."
                )

            else:
                show_compact_record_note(
                    "Showing the first 25 incident-arrest match rows."
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


def show_dashboard_sections(
    incident_data,
    arrest_data,
    match_data,
    charge_summary,
    demographic_summary
):
    """
    Create the main navigation tabs.
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
            incident_data=incident_data,
            arrest_data=arrest_data,
            match_data=match_data,
            charge_summary=charge_summary,
            demographic_summary=demographic_summary
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
    apply_filter_summary_styles()

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

    charge_summary = dashboard_data.get(
        "charge_summary",
        pd.DataFrame()
    )

    demographic_summary = dashboard_data.get(
        "demographic_summary",
        pd.DataFrame()
    )

    show_dashboard_header()

    (
        filtered_incident_data,
        active_filters
    ) = apply_incident_filters(
        incident_data
    )

    show_main_active_filter_summary(
        active_filters=active_filters,
        filtered_record_count=len(
            filtered_incident_data
        )
    )

    if filtered_incident_data.empty:
        st.warning(
            "No incident records match the selected filters. "
            "Use Reset All Filters or adjust the sidebar selections."
        )

        return

    (
        filtered_arrest_data,
        filtered_match_data
    ) = filter_related_arrest_data(
        arrest_data=arrest_data,
        match_data=match_data,
        filtered_incident_data=filtered_incident_data
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