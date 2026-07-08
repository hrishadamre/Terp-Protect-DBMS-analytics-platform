"""
reporting_delay.py

Purpose:
Display the Reporting Delay section for the Terp Protect Streamlit dashboard.

This section measures the time between when an incident occurred and when it was reported.
It includes reporting delay buckets, average delay by crime group, average delay by
location group, and high-delay records.
"""

import pandas as pd
import streamlit as st

from components.charts import (
    create_delay_bucket_chart,
    create_reporting_delay_by_group_chart
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


def show_reporting_delay(data):
    """Display the Reporting Delay section."""
    st.subheader("Reporting Delay Analysis")

    show_section_note(
        "Measure the time gap between when incidents occurred and when they were reported."
    )

    valid_delay_data = data[data["has_valid_reporting_delay"] == 1]

    avg_delay_hours = valid_delay_data["report_delay_hours"].mean()
    avg_delay_days = valid_delay_data["report_delay_days"].mean()

    same_day_count = len(
        valid_delay_data[
            valid_delay_data["delay_bucket"] == "Same Day / Within 24 Hours"
        ]
    )

    over_7_days_count = len(
        valid_delay_data[
            valid_delay_data["delay_bucket"] == "Over 7 Days"
        ]
    )

    same_day_percentage = (
        same_day_count / len(valid_delay_data) * 100
        if len(valid_delay_data) > 0
        else 0
    )

    card_1, card_2, card_3, card_4 = st.columns(4)

    card_1.metric(
        "Avg Delay Hours",
        f"{avg_delay_hours:.1f}" if not pd.isna(avg_delay_hours) else "N/A"
    )

    card_2.metric(
        "Avg Delay Days",
        f"{avg_delay_days:.1f}" if not pd.isna(avg_delay_days) else "N/A"
    )

    card_3.metric(
        "Same-Day Reporting %",
        format_percentage(same_day_percentage)
    )

    card_4.metric(
        "Over 7 Days Count",
        format_number(over_7_days_count)
    )

    if not pd.isna(avg_delay_hours):
        show_insight(
            f"The average reporting delay is {avg_delay_hours:.1f} hours. "
            f"{format_percentage(same_day_percentage)} of valid records were reported within the same day."
        )
    else:
        show_insight(
            "Reporting delay could not be calculated for the selected data."
        )

    st.divider()

    left_column, right_column = st.columns(2)

    with left_column:
        st.plotly_chart(
            create_delay_bucket_chart(data),
            use_container_width=True,
            key="delay_delay_bucket_chart"
        )

        top_delay_bucket, delay_bucket_count = get_top_value(
            data,
            "delay_bucket"
        )

        show_insight(
            f"{top_delay_bucket} is the most common reporting delay bucket, with "
            f"{format_number(delay_bucket_count)} records."
        )

    with right_column:
        st.plotly_chart(
            create_reporting_delay_by_group_chart(
                data,
                "crime_group",
                "Average Reporting Delay by Crime Group"
            ),
            use_container_width=True,
            key="delay_by_crime_group_chart"
        )

        if not valid_delay_data.empty:
            delay_by_crime = (
                valid_delay_data
                .groupby("crime_group")["report_delay_hours"]
                .mean()
                .sort_values(ascending=False)
            )

            show_insight(
                f"{delay_by_crime.index[0]} has the highest average reporting delay among crime groups."
            )

    st.plotly_chart(
        create_reporting_delay_by_group_chart(
            data,
            "location_group",
            "Average Reporting Delay by Location Group"
        ),
        use_container_width=True,
        key="delay_by_location_group_chart"
    )

    if not valid_delay_data.empty:
        delay_by_location = (
            valid_delay_data
            .groupby("location_group")["report_delay_hours"]
            .mean()
            .sort_values(ascending=False)
        )

        show_insight(
            f"{delay_by_location.index[0]} has the highest average reporting delay among location groups."
        )

    with st.expander("Highest Reporting Delay Records"):
        delay_columns = [
            "incident_id",
            "case_number",
            "occurred_datetime",
            "reported_datetime",
            "crime_group",
            "disposition_group",
            "location_group",
            "report_delay_hours",
            "report_delay_days"
        ]

        st.dataframe(
            valid_delay_data[delay_columns]
            .sort_values("report_delay_hours", ascending=False)
            .head(50),
            use_container_width=True
        )