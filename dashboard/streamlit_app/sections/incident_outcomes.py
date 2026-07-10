"""
incident_outcomes.py

Purpose:
Display the case resolution profile section for the Terp Protect Streamlit dashboard.

This section compares case dispositions, arrest-related outcomes, pending/active
cases, closed/cleared cases, and crime group to outcome relationships.
"""

import streamlit as st

from components.charts import (
    create_crime_disposition_heatmap,
    create_horizontal_bar_chart,
    create_soft_donut_chart,
    create_status_bar_chart,
    get_chart_config
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
    """Display the case resolution profile section."""
    st.subheader("Case Resolution Profile")

    show_section_note(
        "Review how reported incidents move through outcome categories such as arrest-related, pending, active, closed, cleared, or other dispositions."
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

    pending_percentage = (
        pending_count / total_incidents * 100
        if total_incidents > 0
        else 0
    )

    closed_percentage = (
        closed_count / total_incidents * 100
        if total_incidents > 0
        else 0
    )

    top_disposition, disposition_count = get_top_value(
        data,
        "disposition_group"
    )

    top_detailed_disposition, detailed_count = get_top_value(
        data,
        "disposition"
    )

    card_1, card_2, card_3, card_4 = st.columns(4)

    card_1.metric(
        "Selected Incidents",
        format_number(total_incidents)
    )

    card_2.metric(
        "Arrest-Related",
        format_number(arrest_count)
    )

    card_3.metric(
        "Pending / Active",
        format_number(pending_count)
    )

    card_4.metric(
        "Closed / Cleared",
        format_number(closed_count)
    )

    card_5, card_6, card_7 = st.columns(3)

    card_5.metric(
        "Arrest Share",
        format_percentage(arrest_percentage)
    )

    card_6.metric(
        "Pending Share",
        format_percentage(pending_percentage)
    )

    card_7.metric(
        "Closed Share",
        format_percentage(closed_percentage)
    )

    show_insight(
        f"{format_percentage(arrest_percentage)} of selected incident records are arrest-related, "
        f"{format_percentage(pending_percentage)} are pending or active, and "
        f"{format_percentage(closed_percentage)} are closed or cleared."
    )

    st.divider()

    outcome_summary = (
        data.groupby("disposition_group")
        .size()
        .reset_index(name="incident_count")
        .sort_values("incident_count", ascending=False)
    )

    left_column, right_column = st.columns(2)

    with left_column:
        st.plotly_chart(
            create_status_bar_chart(
                data=data,
                group_column="disposition_group",
                title="Case Outcome Volume",
                count_label="Incident Count"
            ),
            use_container_width=True,
            key="outcomes_disposition_group_chart",
            config=get_chart_config()
        )

        show_insight(
            f"{top_disposition} is the leading outcome category, appearing in "
            f"{format_number(disposition_count)} selected records."
        )

    with right_column:
        st.plotly_chart(
            create_soft_donut_chart(
                data=outcome_summary,
                label_column="disposition_group",
                value_column="incident_count",
                title="Outcome Share"
            ),
            use_container_width=True,
            key="outcomes_share_donut_chart",
            config=get_chart_config()
        )

        show_insight(
            "The donut chart gives a compact view of how selected incidents are distributed across major outcome groups."
        )

    left_column, right_column = st.columns(2)

    with left_column:
        st.plotly_chart(
            create_horizontal_bar_chart(
                data=data,
                group_column="disposition",
                title="Detailed Disposition Volume",
                max_categories=15,
                count_label="Incident Count",
                chart_type="neutral"
            ),
            use_container_width=True,
            key="outcomes_detailed_disposition_chart",
            config=get_chart_config()
        )

        show_insight(
            f"The most common detailed disposition is {top_detailed_disposition}, "
            f"with {format_number(detailed_count)} records."
        )

    with right_column:
        st.plotly_chart(
            create_horizontal_bar_chart(
                data=data,
                group_column="crime_group",
                title="Incident Volume by Crime Group",
                max_categories=15,
                count_label="Incident Count",
                chart_type="incident_soft"
            ),
            use_container_width=True,
            key="outcomes_crime_group_chart",
            config=get_chart_config()
        )

        top_crime_group, crime_group_count = get_top_value(
            data,
            "crime_group"
        )

        show_insight(
            f"{top_crime_group} is the highest-volume crime group in the selected outcome view, "
            f"with {format_number(crime_group_count)} incidents."
        )

    st.plotly_chart(
        create_crime_disposition_heatmap(data),
        use_container_width=True,
        key="outcomes_crime_disposition_heatmap",
        config=get_chart_config()
    )

    show_insight(
        "The heatmap shows which crime groups are most often associated with each case outcome."
    )