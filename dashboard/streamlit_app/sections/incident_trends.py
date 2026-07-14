"""
incident_trends.py

Purpose:
Display the temporal activity profile section for the Terp Protect dashboard.

Responsibilities:
- Summarize peak time periods
- Compare monthly, weekday, hourly, and academic-period activity
- Keep paired charts and insights horizontally aligned
"""

import pandas as pd
import streamlit as st

from components.charts import (
    create_hourly_chart,
    create_monthly_line_chart,
    create_vertical_bar_chart,
    create_weekday_chart,
    get_chart_config
)
from components.layout import (
    show_compact_overview_strip,
    show_insight,
    show_section_banner
)
from components.metrics import (
    format_number,
    format_percentage,
    get_top_value
)


PRIMARY_CHART_HEIGHT = 455


def standardize_chart_height(
    figure,
    height=PRIMARY_CHART_HEIGHT
):
    """
    Apply a consistent chart height and margin.

    This keeps charts and their insight bars aligned across a row.
    """
    figure.update_layout(
        height=height,
        margin={
            "l": 48,
            "r": 20,
            "t": 68,
            "b": 58
        }
    )

    return figure


def format_peak_hour(hour):
    """
    Format a numeric hour as a readable time label.
    """
    numeric_hour = pd.to_numeric(
        hour,
        errors="coerce"
    )

    if pd.isna(numeric_hour):
        return str(hour)

    numeric_hour = int(numeric_hour)

    if numeric_hour == 0:
        return "12 AM"

    if numeric_hour < 12:
        return f"{numeric_hour} AM"

    if numeric_hour == 12:
        return "12 PM"

    return f"{numeric_hour - 12} PM"


def calculate_weekend_percentage(data):
    """
    Calculate the percentage of incidents occurring on weekends.
    """
    if (
        data.empty
        or "occurred_is_weekend" not in data.columns
    ):
        return 0.0

    weekend_values = pd.to_numeric(
        data["occurred_is_weekend"],
        errors="coerce"
    ).fillna(0)

    return weekend_values.mean() * 100


def show_temporal_summary(data):
    """
    Display compact temporal summary cards.
    """
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

    weekend_percentage = calculate_weekend_percentage(
        data
    )

    overview_items = [
        {
            "label": "Selected Incidents",
            "value": format_number(
                len(data)
            ),
            "meta": "Current filtered view",
            "numeric": True
        },
        {
            "label": "Peak Month",
            "value": peak_month,
            "meta": "Highest monthly volume",
            "badge": format_number(
                peak_month_count
            )
        },
        {
            "label": "Peak Weekday",
            "value": peak_weekday,
            "meta": "Highest weekday volume",
            "badge": format_number(
                peak_weekday_count
            )
        },
        {
            "label": "Peak Hour",
            "value": format_peak_hour(
                peak_hour
            ),
            "meta": "Highest hourly volume",
            "badge": format_number(
                peak_hour_count
            )
        },
        {
            "label": "Weekend Share",
            "value": format_percentage(
                weekend_percentage
            ),
            "meta": "Saturday and Sunday",
            "numeric": True
        },
        {
            "label": "Top Academic Period",
            "value": top_period,
            "meta": "Leading academic period",
            "badge": format_number(
                period_count
            )
        }
    ]

    show_compact_overview_strip(
        overview_items
    )

    show_insight(
        f"Activity peaks in {peak_month}, on {peak_weekday}, "
        f"and around {format_peak_hour(peak_hour)}. "
        f"{top_period} has the highest academic-period volume."
    )

    return {
        "peak_month": peak_month,
        "peak_month_count": peak_month_count,
        "peak_weekday": peak_weekday,
        "peak_weekday_count": peak_weekday_count,
        "peak_hour": peak_hour,
        "peak_hour_count": peak_hour_count,
        "top_period": top_period,
        "period_count": period_count
    }


def show_temporal_charts(
    data,
    summary
):
    """
    Display time-pattern charts in aligned rows.
    """
    monthly_chart = standardize_chart_height(
        create_monthly_line_chart(
            data
        )
    )

    weekday_chart = standardize_chart_height(
        create_weekday_chart(
            data
        )
    )

    chart_left, chart_right = st.columns(
        2,
        gap="small"
    )

    with chart_left:
        st.plotly_chart(
            monthly_chart,
            use_container_width=True,
            key="time_monthly_line_chart",
            config=get_chart_config()
        )

    with chart_right:
        st.plotly_chart(
            weekday_chart,
            use_container_width=True,
            key="time_weekday_chart",
            config=get_chart_config()
        )

    insight_left, insight_right = st.columns(
        2,
        gap="small"
    )

    with insight_left:
        show_insight(
            f"{summary['peak_month']} has the highest monthly "
            f"volume with "
            f"{format_number(summary['peak_month_count'])} incidents."
        )

    with insight_right:
        show_insight(
            f"{summary['peak_weekday']} has the highest weekday "
            f"volume with "
            f"{format_number(summary['peak_weekday_count'])} incidents."
        )

    hourly_chart = standardize_chart_height(
        create_hourly_chart(
            data
        )
    )

    academic_period_chart = standardize_chart_height(
        create_vertical_bar_chart(
            data=data,
            group_column="occurred_semester_period",
            title="Incident Volume by Academic Period",
            count_label="Incident Count",
            chart_type="incident_soft"
        )
    )

    chart_left, chart_right = st.columns(
        2,
        gap="small"
    )

    with chart_left:
        st.plotly_chart(
            hourly_chart,
            use_container_width=True,
            key="time_hourly_chart",
            config=get_chart_config()
        )

    with chart_right:
        st.plotly_chart(
            academic_period_chart,
            use_container_width=True,
            key="time_academic_period_chart",
            config=get_chart_config()
        )

    insight_left, insight_right = st.columns(
        2,
        gap="small"
    )

    with insight_left:
        show_insight(
            f"{format_peak_hour(summary['peak_hour'])} has the "
            f"highest hourly volume with "
            f"{format_number(summary['peak_hour_count'])} incidents."
        )

    with insight_right:
        show_insight(
            f"{summary['top_period']} is the leading academic "
            f"period with "
            f"{format_number(summary['period_count'])} incidents."
        )


def show_incident_trends(data):
    """
    Display the complete temporal activity section.
    """
    show_section_banner(
        eyebrow="",
        title="Temporal Activity Profile",
        description=(
            "Identify when incident activity increases across months, "
            "weekdays, hours, weekends, and academic periods."
        )
    )

    summary = show_temporal_summary(
        data
    )

    st.divider()

    show_temporal_charts(
        data,
        summary
    )