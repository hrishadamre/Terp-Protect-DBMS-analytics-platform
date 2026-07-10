"""
data_quality.py

Purpose:
Display the pipeline reliability profile section for the Terp Protect Streamlit dashboard.

This section checks whether key incident and arrest fields are valid, complete,
and usable for reliable analysis.
"""

import pandas as pd
import streamlit as st

from components.charts import (
    create_quality_bar_chart,
    get_chart_config
)

from components.layout import (
    show_compact_record_note,
    show_info_hint,
    show_insight,
    show_section_note
)

from components.metrics import (
    format_number,
    format_percentage
)


def count_valid_records(data, column):
    """Count valid records for a binary quality flag column."""
    if data.empty or column not in data.columns:
        return 0

    return int(data[column].fillna(0).sum())


def calculate_percentage(valid_count, total_count):
    """Calculate a safe percentage."""
    if total_count == 0:
        return 0

    return valid_count / total_count * 100


def get_review_records(data, quality_columns):
    """Return records where at least one quality check failed."""
    if data.empty:
        return data

    available_quality_columns = [
        column for column in quality_columns
        if column in data.columns
    ]

    if not available_quality_columns:
        return data.iloc[0:0]

    review_mask = pd.Series(False, index=data.index)

    for column in available_quality_columns:
        review_mask = review_mask | (data[column].fillna(0) == 0)

    return data[review_mask]


def show_data_quality(incident_data, arrest_data):
    """Display the pipeline reliability profile section."""
    st.subheader("Pipeline Reliability Profile")

    show_section_note(
        "Check whether key incident and arrest fields are complete, consistent, and usable for reliable analysis."
    )

    total_incident_records = len(incident_data)
    total_arrest_records = len(arrest_data)

    valid_incident_case_numbers = count_valid_records(
        incident_data,
        "has_valid_case_number"
    )

    valid_incident_dates = count_valid_records(
        incident_data,
        "has_valid_occurred_datetime"
    )

    valid_incident_reported_dates = count_valid_records(
        incident_data,
        "has_valid_reported_datetime"
    )

    valid_reporting_delay = count_valid_records(
        incident_data,
        "has_valid_reporting_delay"
    )

    valid_arrest_numbers = count_valid_records(
        arrest_data,
        "has_valid_arrest_number"
    )

    valid_arrest_case_numbers = count_valid_records(
        arrest_data,
        "has_valid_case_number"
    )

    valid_arrest_dates = count_valid_records(
        arrest_data,
        "has_valid_arrested_datetime"
    )

    arrest_charge_text_count = count_valid_records(
        arrest_data,
        "has_charge_text"
    )

    incident_case_validity = calculate_percentage(
        valid_incident_case_numbers,
        total_incident_records
    )

    incident_date_validity = calculate_percentage(
        valid_incident_dates,
        total_incident_records
    )

    incident_reported_date_validity = calculate_percentage(
        valid_incident_reported_dates,
        total_incident_records
    )

    reporting_delay_validity = calculate_percentage(
        valid_reporting_delay,
        total_incident_records
    )

    arrest_number_validity = calculate_percentage(
        valid_arrest_numbers,
        total_arrest_records
    )

    arrest_case_validity = calculate_percentage(
        valid_arrest_case_numbers,
        total_arrest_records
    )

    arrest_date_validity = calculate_percentage(
        valid_arrest_dates,
        total_arrest_records
    )

    arrest_charge_text_validity = calculate_percentage(
        arrest_charge_text_count,
        total_arrest_records
    )

    card_1, card_2, card_3, card_4 = st.columns(4)

    card_1.metric(
        "Incident Records",
        format_number(total_incident_records)
    )

    card_2.metric(
        "Incident Case Validity",
        format_percentage(incident_case_validity)
    )

    card_3.metric(
        "Arrest Records",
        format_number(total_arrest_records)
    )

    card_4.metric(
        "Arrest Case Validity",
        format_percentage(arrest_case_validity)
    )

    card_5, card_6, card_7, card_8 = st.columns(4)

    card_5.metric(
        "Incident Date Validity",
        format_percentage(incident_date_validity)
    )

    card_6.metric(
        "Reported Date Validity",
        format_percentage(incident_reported_date_validity)
    )

    card_7.metric(
        "Reporting Delay Validity",
        format_percentage(reporting_delay_validity)
    )

    card_8.metric(
        "Charge Text Validity",
        format_percentage(arrest_charge_text_validity)
    )

    show_insight(
        f"{format_percentage(incident_case_validity)} of selected incident records have valid case numbers. "
        f"{format_percentage(arrest_case_validity)} of selected arrest records have valid case numbers."
    )

    show_info_hint(
        "How to read quality checks",
        "Green means the field passed the quality check. Red means the record needs review or has missing, invalid, or unusable values for that field."
    )

    st.divider()

    quality_data = {
        "Quality Check": [
            "Incident Valid Case Number",
            "Incident Valid Occurred Datetime",
            "Incident Valid Reported Datetime",
            "Incident Valid Reporting Delay",
            "Arrest Valid Arrest Number",
            "Arrest Valid Case Number",
            "Arrest Valid Arrested Datetime",
            "Arrest Has Charge Text"
        ],
        "Valid Count": [
            valid_incident_case_numbers,
            valid_incident_dates,
            valid_incident_reported_dates,
            valid_reporting_delay,
            valid_arrest_numbers,
            valid_arrest_case_numbers,
            valid_arrest_dates,
            arrest_charge_text_count
        ],
        "Invalid Count": [
            total_incident_records - valid_incident_case_numbers,
            total_incident_records - valid_incident_dates,
            total_incident_records - valid_incident_reported_dates,
            total_incident_records - valid_reporting_delay,
            total_arrest_records - valid_arrest_numbers,
            total_arrest_records - valid_arrest_case_numbers,
            total_arrest_records - valid_arrest_dates,
            total_arrest_records - arrest_charge_text_count
        ]
    }

    st.plotly_chart(
        create_quality_bar_chart(quality_data),
        use_container_width=True,
        key="quality_summary_chart",
        config=get_chart_config()
    )

    show_insight(
        "Valid records support reliable dashboard analysis. Invalid records should be reviewed before using them for operational conclusions."
    )

    incident_quality_columns = [
        "has_valid_case_number",
        "has_valid_occurred_datetime",
        "has_valid_reported_datetime",
        "has_valid_reporting_delay"
    ]

    arrest_quality_columns = [
        "has_valid_arrest_number",
        "has_valid_case_number",
        "has_valid_arrested_datetime",
        "has_charge_text"
    ]

    incident_review_data = get_review_records(
        incident_data,
        incident_quality_columns
    )

    arrest_review_data = get_review_records(
        arrest_data,
        arrest_quality_columns
    )

    left_column, right_column = st.columns(2)

    with left_column:
        st.metric(
            "Incident Records Needing Review",
            format_number(len(incident_review_data))
        )

    with right_column:
        st.metric(
            "Arrest Records Needing Review",
            format_number(len(arrest_review_data))
        )

    with st.expander("Records Needing Attention", expanded=False):
        show_info_hint(
            "About this review panel",
            "Detailed records are hidden by default to keep the dashboard focused. Use this panel only when validating records that failed one or more quality checks."
        )

        review_tab_1, review_tab_2 = st.tabs(
            [
                f"Incident review ({format_number(len(incident_review_data))})",
                f"Arrest review ({format_number(len(arrest_review_data))})"
            ]
        )

        with review_tab_1:
            incident_review_columns = [
                "incident_id",
                "case_number",
                "occurred_datetime",
                "reported_datetime",
                "crime_group",
                "disposition_group",
                "location_group",
                "has_valid_case_number",
                "has_valid_occurred_datetime",
                "has_valid_reported_datetime",
                "has_valid_reporting_delay"
            ]

            available_incident_columns = [
                column for column in incident_review_columns
                if column in incident_review_data.columns
            ]

            if incident_review_data.empty:
                st.success(
                    "No selected incident records require review based on the current quality checks."
                )
            else:
                show_compact_record_note(
                    "Showing the first 25 incident records that failed at least one quality check."
                )

                st.dataframe(
                    incident_review_data[available_incident_columns].head(25),
                    use_container_width=True,
                    hide_index=True
                )

        with review_tab_2:
            arrest_review_columns = [
                "arrest_id",
                "arrest_number",
                "case_number",
                "arrested_datetime",
                "charge_category",
                "race",
                "sex",
                "age_group",
                "has_valid_arrest_number",
                "has_valid_case_number",
                "has_valid_arrested_datetime",
                "has_charge_text"
            ]

            available_arrest_columns = [
                column for column in arrest_review_columns
                if column in arrest_review_data.columns
            ]

            if arrest_data.empty:
                st.info(
                    "No arrest records are available for the selected filters."
                )
            elif arrest_review_data.empty:
                st.success(
                    "No selected arrest records require review based on the current quality checks."
                )
            else:
                show_compact_record_note(
                    "Showing the first 25 arrest records that failed at least one quality check."
                )

                st.dataframe(
                    arrest_review_data[available_arrest_columns].head(25),
                    use_container_width=True,
                    hide_index=True
                )