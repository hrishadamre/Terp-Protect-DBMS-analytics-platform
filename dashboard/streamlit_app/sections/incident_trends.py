"""
incident_trends.py

Purpose:
Display the Incident Trends section for the Terp Protect Streamlit dashboard.

This section analyzes when incidents occur by month, weekday, hour of day,
and academic period.
"""

import streamlit as st

from components.charts import (
    create_hourly_chart,
    create_monthly_line_chart,
    create_vertical_bar_chart,
    create_weekday_chart
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


def show_incident_trends(data):
    """Display the Incident Trends section."""
    st.subheader("Incident Trends")

    show_section_note(
        "Explore when incidents occur across months, weekdays, hours, and academic periods."
    )

    peak_month, peak_month_count = get_top_value(data, "occurred_month_name")
    peak_weekday, peak_weekday_count = get_top_value(data, "occurred_weekday")
    peak_hour, peak_hour_count = get_top_value(data, "occurred_hour")

    weekend_percentage = (
        data["occurred_is_weekend"].sum() / len(data) * 100
        if len(data) > 0
        else 0
    )

    card_1, card_2, card_3, card_4 = st.columns(4)

    card_1.metric("Peak Month", peak_month)
    card_2.metric("Peak Weekday", peak_weekday)
    card_3.metric("Peak Hour", peak_hour)
    card_4.metric("Weekend Incident %", format_percentage(weekend_percentage))

    show_insight(
        f"Incident activity peaks in {peak_month}, on {peak_weekday}s, "
        f"and around hour {peak_hour} in the selected filter range."
    )

    st.divider()

    left_column, right_column = st.columns(2)

    with left_column:
        st.plotly_chart(
            create_monthly_line_chart(data),
            use_container_width=True,
            key="trends_monthly_line_chart"
        )

        show_insight(
            f"{peak_month} is the peak month with {format_number(peak_month_count)} incidents."
        )

    with right_column:
        st.plotly_chart(
            create_weekday_chart(data),
            use_container_width=True,
            key="trends_weekday_chart"
        )

        show_insight(
            f"{peak_weekday} has the highest incident count with "
            f"{format_number(peak_weekday_count)} incidents."
        )

    left_column, right_column = st.columns(2)

    with left_column:
        st.plotly_chart(
            create_hourly_chart(data),
            use_container_width=True,
            key="trends_hourly_chart"
        )

        show_insight(
            f"Hour {peak_hour} has the highest incident count with "
            f"{format_number(peak_hour_count)} incidents."
        )

    with right_column:
        st.plotly_chart(
            create_vertical_bar_chart(
                data,
                "occurred_semester_period",
                "Incidents by Academic Period"
            ),
            use_container_width=True,
            key="trends_academic_period_chart"
        )

        top_period, period_count = get_top_value(data, "occurred_semester_period")

        show_insight(
            f"{top_period} has the highest incident volume among academic periods, "
            f"with {format_number(period_count)} incidents."
        )