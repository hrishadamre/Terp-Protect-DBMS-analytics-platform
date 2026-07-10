"""
reporting_delay.py

Purpose:
Display the reporting timeliness profile section for the Terp Protect Streamlit dashboard.

This section measures the time between when an incident occurred and when it was reported.
It includes reporting delay buckets, average delay by crime group, average delay by
location group, and high-delay records.
"""

import pandas as pd
import streamlit as st

from components.charts import (
    create_delay_bucket_chart,
    create_reporting_delay_by_group_chart,
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
    format_percentage,
    get_top_value
)


def show_reporting_delay(data):
    """Display the reporting timeliness profile section."""
    st.subheader("Reporting Timeliness Profile")

    show_section_note(
        "Measure the gap between incident occurrence and reporting to identify late reports, same-day reports, and data timeliness patterns."
    )

    valid_delay_data = data[data["has_valid_reporting_delay"] == 1]

    avg_delay_hours = valid_delay_data["report_delay_hours"].mean()
    avg_delay_days = valid_delay_data["report_delay_days"].mean()

    same_day_count = len(
        valid_delay_data[
            valid_delay_data["delay_bucket"] == "Same Day / Within 24 Hours"
        ]
    )

    one_to_three_days_count = len(
        valid_delay_data[
            valid_delay_data["delay_bucket"] == "1-3 Days"
        ]
    )

    four_to_seven_days_count = len(
        valid_delay_data[
            valid_delay_data["delay_bucket"] == "4-7 Days"
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

    over_7_days_percentage = (
        over_7_days_count / len(valid_delay_data) * 100
        if len(valid_delay_data) > 0
        else 0
    )

    card_1, card_2, card_3, card_4 = st.columns(4)

    card_1.metric(
        "Avg Delay",
        f"{avg_delay_hours:.1f} hrs" if not pd.isna(avg_delay_hours) else "N/A"
    )

    card_2.metric(
        "Avg Delay Days",
        f"{avg_delay_days:.1f}" if not pd.isna(avg_delay_days) else "N/A"
    )

    card_3.metric(
        "Same-Day Share",
        format_percentage(same_day_percentage)
    )

    card_4.metric(
        "Over 7 Days",
        format_percentage(over_7_days_percentage)
    )

    card_5, card_6, card_7, card_8 = st.columns(4)

    card_5.metric(
        "Same-Day Records",
        format_number(same_day_count)
    )

    card_6.metric(
        "1-3 Day Records",
        format_number(one_to_three_days_count)
    )

    card_7.metric(
        "4-7 Day Records",
        format_number(four_to_seven_days_count)
    )

    card_8.metric(
        "Over 7 Day Records",
        format_number(over_7_days_count)
    )

    if not pd.isna(avg_delay_hours):
        show_insight(
            f"The average reporting delay is {avg_delay_hours:.1f} hours. "
            f"{format_percentage(same_day_percentage)} of valid records were reported on the same day, "
            f"while {format_percentage(over_7_days_percentage)} were reported over 7 days later."
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
            key="delay_delay_bucket_chart",
            config=get_chart_config()
        )

        top_delay_bucket, delay_bucket_count = get_top_value(
            data,
            "delay_bucket"
        )

        show_insight(
            f"{top_delay_bucket} is the most common reporting delay bucket, with "
            f"{format_number(delay_bucket_count)} selected records."
        )

    with right_column:
        st.plotly_chart(
            create_reporting_delay_by_group_chart(
                data=data,
                group_column="crime_group",
                title="Average Delay by Crime Group"
            ),
            use_container_width=True,
            key="delay_by_crime_group_chart",
            config=get_chart_config()
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
            data=data,
            group_column="location_group",
            title="Average Delay by Location Group"
        ),
        use_container_width=True,
        key="delay_by_location_group_chart",
        config=get_chart_config()
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

    with st.expander("High-Delay Record Review", expanded=False):
        show_info_hint(
            "About this review panel",
            "This table is hidden by default to keep the dashboard focused. Use it only when investigating records with the longest reporting delays."
        )

        show_compact_record_note(
            "Showing the top 25 records with the longest valid reporting delays in the current filtered view."
        )

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

        available_columns = [
            column for column in delay_columns
            if column in valid_delay_data.columns
        ]

        if valid_delay_data.empty:
            st.info("No valid reporting-delay records are available for the selected filters.")
        else:
            st.dataframe(
                valid_delay_data[available_columns]
                .sort_values("report_delay_hours", ascending=False)
                .head(25),
                use_container_width=True,
                hide_index=True
            )