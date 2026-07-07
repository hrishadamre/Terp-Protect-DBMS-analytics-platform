"""
data_quality.py

Purpose:
Display the Data Quality tab for the Terp Protect Streamlit dashboard.

This page checks whether key incident and arrest fields are valid, complete,
and ready for analysis.
"""

import plotly.express as px
import streamlit as st

from components.layout import (
    show_insight,
    show_section_note
)

from components.metrics import (
    format_number,
    format_percentage
)


def show_data_quality(incident_data, arrest_data):
    """Display the Data Quality tab."""
    st.subheader("Data Quality")

    show_section_note(
        "This page checks whether key incident and arrest fields are valid, complete, and ready for analysis."
    )

    total_incident_records = len(incident_data)
    total_arrest_records = len(arrest_data)

    valid_incident_case_numbers = int(incident_data["has_valid_case_number"].sum())
    valid_incident_dates = int(incident_data["has_valid_occurred_datetime"].sum())

    valid_arrest_case_numbers = (
        int(arrest_data["has_valid_case_number"].sum())
        if not arrest_data.empty
        else 0
    )

    valid_arrest_dates = (
        int(arrest_data["has_valid_arrested_datetime"].sum())
        if not arrest_data.empty
        else 0
    )

    incident_case_validity = (
        valid_incident_case_numbers / total_incident_records * 100
        if total_incident_records > 0
        else 0
    )

    arrest_case_validity = (
        valid_arrest_case_numbers / total_arrest_records * 100
        if total_arrest_records > 0
        else 0
    )

    card_1, card_2, card_3, card_4, card_5, card_6 = st.columns(6)

    card_1.metric("Incident Records", format_number(total_incident_records))
    card_2.metric("Arrest Records", format_number(total_arrest_records))
    card_3.metric("Valid Incident Cases", format_number(valid_incident_case_numbers))
    card_4.metric("Valid Incident Dates", format_number(valid_incident_dates))
    card_5.metric("Valid Arrest Cases", format_number(valid_arrest_case_numbers))
    card_6.metric("Valid Arrest Dates", format_number(valid_arrest_dates))

    show_insight(
        f"{format_percentage(incident_case_validity)} of selected incident records have valid case numbers. "
        f"{format_percentage(arrest_case_validity)} of selected arrest records have valid case numbers."
    )

    st.divider()

    arrest_charge_text_count = (
        int(arrest_data["has_charge_text"].sum())
        if not arrest_data.empty
        else 0
    )

    quality_data = {
        "Quality Check": [
            "Incident Valid Case Number",
            "Incident Valid Occurred Datetime",
            "Incident Valid Reported Datetime",
            "Incident Valid Reporting Delay",
            "Arrest Valid Case Number",
            "Arrest Valid Arrested Datetime",
            "Arrest Has Charge Text"
        ],
        "Valid Count": [
            valid_incident_case_numbers,
            int(incident_data["has_valid_occurred_datetime"].sum()),
            int(incident_data["has_valid_reported_datetime"].sum()),
            int(incident_data["has_valid_reporting_delay"].sum()),
            valid_arrest_case_numbers,
            valid_arrest_dates,
            arrest_charge_text_count
        ],
        "Invalid Count": [
            total_incident_records - valid_incident_case_numbers,
            total_incident_records - int(incident_data["has_valid_occurred_datetime"].sum()),
            total_incident_records - int(incident_data["has_valid_reported_datetime"].sum()),
            total_incident_records - int(incident_data["has_valid_reporting_delay"].sum()),
            total_arrest_records - valid_arrest_case_numbers,
            total_arrest_records - valid_arrest_dates,
            total_arrest_records - arrest_charge_text_count
        ]
    }

    figure = px.bar(
        quality_data,
        x="Quality Check",
        y=["Valid Count", "Invalid Count"],
        title="Data Quality Summary",
        barmode="group",
        labels={
            "value": "Record Count",
            "variable": "Status"
        }
    )

    figure.update_layout(
        height=500,
        margin=dict(l=10, r=10, t=55, b=10)
    )

    st.plotly_chart(
        figure,
        use_container_width=True,
        key="quality_summary_chart"
    )

    show_insight(
        "Data quality checks confirm whether key identifiers, dates, reporting delays, and charge text are usable for analysis."
    )

    with st.expander("Incident Records Needing Review"):
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

        incident_review_data = incident_data[
            (incident_data["has_valid_case_number"] == 0)
            | (incident_data["has_valid_occurred_datetime"] == 0)
            | (incident_data["has_valid_reported_datetime"] == 0)
            | (incident_data["has_valid_reporting_delay"] == 0)
        ]

        st.dataframe(
            incident_review_data[incident_review_columns],
            use_container_width=True
        )

    with st.expander("Arrest Records Needing Review"):
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

        if arrest_data.empty:
            st.info("No arrest records are available for the selected filters.")
        else:
            arrest_review_data = arrest_data[
                (arrest_data["has_valid_arrest_number"] == 0)
                | (arrest_data["has_valid_case_number"] == 0)
                | (arrest_data["has_valid_arrested_datetime"] == 0)
                | (arrest_data["has_charge_text"] == 0)
            ]

            st.dataframe(
                arrest_review_data[arrest_review_columns],
                use_container_width=True
            )