"""
incident_outcomes.py

Purpose:
Display the Incident Outcomes tab for the Terp Protect Streamlit dashboard.

This page compares case dispositions, arrest-related outcomes, pending/active
cases, closed/cleared cases, and crime group to disposition relationships.
"""

import streamlit as st

from components.charts import (
    create_crime_disposition_heatmap,
    create_horizontal_bar_chart
)

from components.layout import (
    show_insight,
    show_section_note
)

from components.metrics import (
    format_number,
    format_percentage,
    get_top_value
)


def show_incident_outcomes(data):
    """Display the Incident Outcomes tab."""
    st.subheader("Incident Outcomes")

    show_section_note(
        "This page compares case dispositions and shows how incident categories relate to outcome groups."
    )

    total_incidents = len(data)
    arrest_count = int(data["is_arrest_related"].sum())
    pending_count = int(data["is_pending"].sum())
    closed_count = int(data["is_closed"].sum())

    arrest_percentage = (
        arrest_count / total_incidents * 100
        if total_incidents > 0
        else 0
    )

    card_1, card_2, card_3, card_4 = st.columns(4)

    card_1.metric("Total Incidents", format_number(total_incidents))
    card_2.metric("Arrest-Related", format_number(arrest_count))
    card_3.metric("Pending / Active", format_number(pending_count))
    card_4.metric("Closed / Cleared", format_number(closed_count))

    show_insight(
        f"{format_percentage(arrest_percentage)} of selected incident records are marked as arrest-related "
        f"based on their disposition category."
    )

    st.divider()

    left_column, right_column = st.columns(2)

    with left_column:
        st.plotly_chart(
            create_horizontal_bar_chart(
                data,
                "disposition_group",
                "Incidents by Disposition Group"
            ),
            use_container_width=True,
            key="outcomes_disposition_group_chart"
        )

        top_disposition, disposition_count = get_top_value(
            data,
            "disposition_group"
        )

        show_insight(
            f"{top_disposition} is the most common disposition group, appearing in "
            f"{format_number(disposition_count)} records."
        )

    with right_column:
        st.plotly_chart(
            create_horizontal_bar_chart(
                data,
                "disposition",
                "Incidents by Detailed Disposition",
                max_categories=15
            ),
            use_container_width=True,
            key="outcomes_detailed_disposition_chart"
        )

        top_detailed_disposition, detailed_count = get_top_value(
            data,
            "disposition"
        )

        show_insight(
            f"The most common detailed disposition is {top_detailed_disposition}, "
            f"with {format_number(detailed_count)} records."
        )

    st.plotly_chart(
        create_crime_disposition_heatmap(data),
        use_container_width=True,
        key="outcomes_crime_disposition_heatmap"
    )

    show_insight(
        "The heatmap helps identify which crime groups are most often associated with each disposition outcome."
    )