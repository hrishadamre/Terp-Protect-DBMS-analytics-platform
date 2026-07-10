"""
incident_trends.py

Purpose:
Display the temporal activity profile section for the Terp Protect Streamlit dashboard.

This section helps analysts understand when incidents occur by month, weekday,
hour of day, weekend share, and academic period.
"""

import streamlit as st

from components.charts import (
    create_hourly_chart,
    create_monthly_line_chart,
    create_vertical_bar_chart,
    create_weekday_chart,
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


def show_incident_trends(data):
    """Display the temporal activity profile section."""
    st.subheader("Temporal Activity Profile")

    show_section_note(
        "Analyze when incidents occur across months, weekdays, hours, and academic periods to support staffing, patrol planning, and operational awareness."
    )

    peak_month, peak_month_count = get_top_value(
        data,
        "occurred_month_name"
    )

    peak_weekday, peak_weekday_count = get_top_value(
        data,
        "occurred_weekday"
    )

    peak_hour, peak_hour_count = get_top_value(
        data,
        "occurred_hour"
    )

    top_period, period_count = get_top_value(
        data,
        "occurred_semester_period"
    )

    weekend_percentage = (
        data["occurred_is_weekend"].sum() / len(data) * 100
        if len(data) > 0
        else 0
    )

    card_1, card_2, card_3, card_4 = st.columns(4)

    card_1.metric(
        "Peak Month",
        peak_month
    )

    card_2.metric(
        "Peak Weekday",
        peak_weekday
    )

    card_3.metric(
        "Peak Hour",
        peak_hour
    )

    card_4.metric(
        "Weekend Share",
        format_percentage(weekend_percentage)
    )

    card_5, card_6 = st.columns(2)

    card_5.metric(
        "Top Academic Period",
        top_period
    )

    card_6.metric(
        "Top Period Volume",
        format_number(period_count)
    )

    show_insight(
        f"Incident activity is highest in {peak_month}, on {peak_weekday}s, and around hour {peak_hour} in the selected data."
    )

    st.divider()

    left_column, right_column = st.columns(2)

    with left_column:
        st.plotly_chart(
            create_monthly_line_chart(data),
            use_container_width=True,
            key="time_monthly_line_chart",
            config=get_chart_config()
        )

        show_insight(
            f"{peak_month} has the highest selected incident volume with {format_number(peak_month_count)} incidents."
        )

    with right_column:
        st.plotly_chart(
            create_weekday_chart(data),
            use_container_width=True,
            key="time_weekday_chart",
            config=get_chart_config()
        )

        show_insight(
            f"{peak_weekday} has the highest weekday incident count with {format_number(peak_weekday_count)} incidents."
        )

    left_column, right_column = st.columns(2)

    with left_column:
        st.plotly_chart(
            create_hourly_chart(data),
            use_container_width=True,
            key="time_hourly_chart",
            config=get_chart_config()
        )

        show_insight(
            f"Hour {peak_hour} has the highest hourly incident volume with {format_number(peak_hour_count)} incidents."
        )

    with right_column:
        st.plotly_chart(
            create_vertical_bar_chart(
                data=data,
                group_column="occurred_semester_period",
                title="Incident Volume by Academic Period",
                count_label="Incident Count",
                chart_type="incident_soft"
            ),
            use_container_width=True,
            key="time_academic_period_chart",
            config=get_chart_config()
        )

        show_insight(
            f"{top_period} is the leading academic period with {format_number(period_count)} incidents."
        )