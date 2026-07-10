"""
executive_overview.py

Purpose:
Display the operational snapshot section for the Terp Protect Streamlit dashboard.

This section gives a high-level view of incident volume, arrest-related activity,
case outcomes, reporting delay, location patterns, and key incident categories.
"""

import pandas as pd
import streamlit as st

from components.charts import (
    create_delay_bucket_chart,
    create_horizontal_bar_chart,
    create_monthly_line_chart,
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


def show_executive_overview(data):
    """Display the operational snapshot section."""
    st.subheader("Operational Snapshot")

    show_section_note(
        "A high-level view of incident volume, case outcomes, reporting delay, and high-activity categories for the current filtered selection."
    )

    total_incidents = len(data)
    arrest_related_incidents = int(data["is_arrest_related"].sum())

    arrest_related_percentage = (
        arrest_related_incidents / total_incidents * 100
        if total_incidents > 0
        else 0
    )

    average_reporting_delay = data["report_delay_hours"].mean()

    most_common_crime_group, crime_count = get_top_value(data, "crime_group")
    most_common_disposition, disposition_count = get_top_value(data, "disposition_group")
    top_location_group, location_count = get_top_value(data, "location_group")

    card_1, card_2, card_3, card_4 = st.columns(4)

    card_1.metric(
        "Incidents",
        format_number(total_incidents)
    )

    card_2.metric(
        "Arrest-Related",
        format_number(arrest_related_incidents)
    )

    card_3.metric(
        "Arrest Share",
        format_percentage(arrest_related_percentage)
    )

    card_4.metric(
        "Avg Delay",
        f"{average_reporting_delay:.1f} hrs" if not pd.isna(average_reporting_delay) else "N/A"
    )

    card_5, card_6, card_7 = st.columns(3)

    card_5.metric(
        "Top Crime Group",
        most_common_crime_group
    )

    card_6.metric(
        "Top Outcome",
        most_common_disposition
    )

    card_7.metric(
        "Top Location Group",
        top_location_group
    )

    show_insight(
        f"{most_common_crime_group} is the most frequent crime group with "
        f"{format_number(crime_count)} incidents. The leading case outcome is "
        f"{most_common_disposition}."
    )

    st.divider()

    left_column, right_column = st.columns(2)

    with left_column:
        st.plotly_chart(
            create_monthly_line_chart(data),
            use_container_width=True,
            key="command_monthly_line_chart",
            config=get_chart_config()
        )

        peak_month, peak_month_count = get_top_value(
            data,
            "occurred_month_name"
        )

        show_insight(
            f"{peak_month} has the highest selected incident volume with "
            f"{format_number(peak_month_count)} incidents."
        )

    with right_column:
        st.plotly_chart(
            create_horizontal_bar_chart(
                data=data,
                group_column="crime_group",
                title="Incident Volume by Crime Group",
                count_label="Incident Count",
                chart_type="incident_soft"
            ),
            use_container_width=True,
            key="command_crime_group_chart",
            config=get_chart_config()
        )

        show_insight(
            f"{most_common_crime_group} contributes the largest share of selected incident volume."
        )

    left_column, right_column = st.columns(2)

    with left_column:
        st.plotly_chart(
            create_status_bar_chart(
                data=data,
                group_column="disposition_group",
                title="Case Outcomes by Volume",
                count_label="Incident Count"
            ),
            use_container_width=True,
            key="command_outcome_group_chart",
            config=get_chart_config()
        )

        show_insight(
            f"{most_common_disposition} is the leading outcome category, appearing in "
            f"{format_number(disposition_count)} selected records."
        )

    with right_column:
        st.plotly_chart(
            create_horizontal_bar_chart(
                data=data,
                group_column="location_group",
                title="Incident Volume by Location Group",
                count_label="Incident Count",
                chart_type="incident_soft"
            ),
            use_container_width=True,
            key="command_location_group_chart",
            config=get_chart_config()
        )

        show_insight(
            f"{top_location_group} is the highest-volume location group with "
            f"{format_number(location_count)} incidents."
        )

    st.plotly_chart(
        create_delay_bucket_chart(data),
        use_container_width=True,
        key="command_delay_bucket_chart",
        config=get_chart_config()
    )

    top_delay_bucket, delay_bucket_count = get_top_value(
        data,
        "delay_bucket"
    )

    show_insight(
        f"The most common reporting delay bucket is {top_delay_bucket}, with "
        f"{format_number(delay_bucket_count)} records."
    )