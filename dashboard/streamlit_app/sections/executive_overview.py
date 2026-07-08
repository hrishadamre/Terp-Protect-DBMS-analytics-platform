"""
executive_overview.py

Purpose:
Display the Executive Overview section for the Terp Protect Streamlit dashboard.

This section summarizes incident volume, arrest-related outcomes, reporting delays,
common crime groups, common dispositions, and high-volume location groups.
"""

import pandas as pd
import streamlit as st

from components.charts import (
    create_delay_bucket_chart,
    create_horizontal_bar_chart,
    create_monthly_line_chart
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
    """Display the Executive Overview section."""
    st.subheader("Executive Overview")

    show_section_note(
        "A quick operational summary of incident volume, outcomes, reporting delay, and high-activity categories."
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

    card_1.metric("Total Incidents", format_number(total_incidents))
    card_2.metric("Arrest-Related Incidents", format_number(arrest_related_incidents))
    card_3.metric("Arrest-Related %", format_percentage(arrest_related_percentage))

    card_4.metric(
        "Avg Reporting Delay",
        f"{average_reporting_delay:.1f} hrs" if not pd.isna(average_reporting_delay) else "N/A"
    )

    card_5, card_6, card_7 = st.columns(3)

    card_5.metric("Top Crime Group", most_common_crime_group)
    card_6.metric("Top Outcome Group", most_common_disposition)
    card_7.metric("Top Location Group", top_location_group)

    show_insight(
        f"{most_common_crime_group} is the most common crime group with "
        f"{format_number(crime_count)} incidents. The leading outcome group is "
        f"{most_common_disposition}."
    )

    st.divider()

    left_column, right_column = st.columns(2)

    with left_column:
        st.plotly_chart(
            create_monthly_line_chart(data),
            use_container_width=True,
            key="executive_monthly_line_chart"
        )

        peak_month, peak_month_count = get_top_value(data, "occurred_month_name")

        show_insight(
            f"{peak_month} has the highest incident count in the selected filter range "
            f"with {format_number(peak_month_count)} incidents."
        )

    with right_column:
        st.plotly_chart(
            create_horizontal_bar_chart(
                data,
                "crime_group",
                "Incidents by Crime Group"
            ),
            use_container_width=True,
            key="executive_crime_group_chart"
        )

        show_insight(
            f"{most_common_crime_group} is the strongest contributor to total incident volume."
        )

    left_column, right_column = st.columns(2)

    with left_column:
        st.plotly_chart(
            create_horizontal_bar_chart(
                data,
                "disposition_group",
                "Incidents by Outcome Group"
            ),
            use_container_width=True,
            key="executive_disposition_group_chart"
        )

        show_insight(
            f"{most_common_disposition} is the leading outcome category, appearing in "
            f"{format_number(disposition_count)} records."
        )

    with right_column:
        st.plotly_chart(
            create_horizontal_bar_chart(
                data,
                "location_group",
                "Incidents by Location Group"
            ),
            use_container_width=True,
            key="executive_location_group_chart"
        )

        show_insight(
            f"{top_location_group} is the highest-volume location group in the selected data."
        )

    st.plotly_chart(
        create_delay_bucket_chart(data),
        use_container_width=True,
        key="executive_delay_bucket_chart"
    )

    top_delay_bucket, delay_bucket_count = get_top_value(data, "delay_bucket")

    show_insight(
        f"The most common reporting delay bucket is {top_delay_bucket}, with "
        f"{format_number(delay_bucket_count)} records."
    )