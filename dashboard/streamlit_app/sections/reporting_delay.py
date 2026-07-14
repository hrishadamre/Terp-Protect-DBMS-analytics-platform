"""
reporting_delay.py

Purpose:
Display the reporting timeliness profile for the Terp Protect dashboard.

Responsibilities:
- Measure valid reporting delays
- Summarize same-day and delayed reporting
- Compare reporting delay across crime and location groups
- Provide a collapsed high-delay review table
"""

import pandas as pd
import streamlit as st

from components.charts import (
    create_delay_bucket_chart,
    create_reporting_delay_by_group_chart,
    get_chart_config
)
from components.layout import (
    show_compact_overview_strip,
    show_compact_record_note,
    show_info_hint,
    show_insight,
    show_section_banner
)
from components.metrics import (
    format_number,
    format_percentage,
    get_top_value
)


PRIMARY_CHART_HEIGHT = 460


def standardize_chart_height(
    figure,
    height=PRIMARY_CHART_HEIGHT
):
    """
    Apply consistent dimensions to paired charts.
    """
    figure.update_layout(
        height=height,
        margin={
            "l": 58,
            "r": 24,
            "t": 68,
            "b": 60
        }
    )

    return figure


def get_valid_delay_data(data):
    """
    Return records with valid reporting-delay values.
    """
    if (
        data.empty
        or "has_valid_reporting_delay" not in data.columns
    ):
        return data.iloc[0:0].copy()

    valid_flag = pd.to_numeric(
        data["has_valid_reporting_delay"],
        errors="coerce"
    ).fillna(0)

    return data[
        valid_flag == 1
    ].copy()


def calculate_bucket_count(
    data,
    bucket
):
    """
    Count records in a reporting-delay bucket.
    """
    if (
        data.empty
        or "delay_bucket" not in data.columns
    ):
        return 0

    return int(
        (
            data["delay_bucket"] == bucket
        ).sum()
    )


def calculate_percentage(
    count,
    total
):
    """
    Calculate a safe percentage.
    """
    if total == 0:
        return 0.0

    return count / total * 100


def format_average_delay(hours):
    """
    Format average reporting delay.
    """
    if pd.isna(hours):
        return "N/A"

    if hours < 48:
        return f"{hours:.1f} hrs"

    return f"{hours / 24:.1f} days"


def show_delay_summary(data):
    """
    Display compact reporting-delay summary cards.
    """
    valid_delay_data = get_valid_delay_data(
        data
    )

    valid_count = len(
        valid_delay_data
    )

    avg_delay_hours = pd.to_numeric(
        valid_delay_data.get(
            "report_delay_hours",
            pd.Series(dtype=float)
        ),
        errors="coerce"
    ).mean()

    same_day_count = calculate_bucket_count(
        valid_delay_data,
        "Same Day / Within 24 Hours"
    )

    one_to_three_count = calculate_bucket_count(
        valid_delay_data,
        "1-3 Days"
    )

    four_to_seven_count = calculate_bucket_count(
        valid_delay_data,
        "4-7 Days"
    )

    over_seven_count = calculate_bucket_count(
        valid_delay_data,
        "Over 7 Days"
    )

    same_day_percentage = calculate_percentage(
        same_day_count,
        valid_count
    )

    over_seven_percentage = calculate_percentage(
        over_seven_count,
        valid_count
    )

    top_delay_bucket, delay_bucket_count = get_top_value(
        data,
        "delay_bucket"
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
            "label": "Valid Delay Records",
            "value": format_number(
                valid_count
            ),
            "meta": "Usable delay values",
            "numeric": True
        },
        {
            "label": "Average Delay",
            "value": format_average_delay(
                avg_delay_hours
            ),
            "meta": "Across valid records",
            "numeric": True
        },
        {
            "label": "Same-Day Share",
            "value": format_percentage(
                same_day_percentage
            ),
            "meta": f"{format_number(same_day_count)} records",
            "numeric": True
        },
        {
            "label": "Over 7 Days",
            "value": format_percentage(
                over_seven_percentage
            ),
            "meta": f"{format_number(over_seven_count)} records",
            "numeric": True
        },
        {
            "label": "Top Delay Bucket",
            "value": top_delay_bucket,
            "meta": "Most common range",
            "badge": format_number(
                delay_bucket_count
            )
        }
    ]

    show_compact_overview_strip(
        overview_items
    )

    if pd.isna(avg_delay_hours):
        show_insight(
            "A valid average reporting delay is unavailable for the "
            "current filtered selection."
        )
    else:
        show_insight(
            f"The average valid reporting delay is "
            f"{format_average_delay(avg_delay_hours)}. "
            f"{format_percentage(same_day_percentage)} were reported "
            f"within 24 hours, while "
            f"{format_percentage(over_seven_percentage)} were reported "
            f"more than seven days later."
        )

    return {
        "valid_delay_data": valid_delay_data,
        "top_delay_bucket": top_delay_bucket,
        "delay_bucket_count": delay_bucket_count,
        "one_to_three_count": one_to_three_count,
        "four_to_seven_count": four_to_seven_count
    }


def get_highest_average_group(
    valid_delay_data,
    group_column
):
    """
    Return the group with the highest average delay.
    """
    required_columns = {
        group_column,
        "report_delay_hours"
    }

    if (
        valid_delay_data.empty
        or not required_columns.issubset(
            valid_delay_data.columns
        )
    ):
        return "N/A", pd.NA

    grouped_delay = (
        valid_delay_data
        .groupby(
            group_column
        )["report_delay_hours"]
        .mean()
        .sort_values(
            ascending=False
        )
    )

    if grouped_delay.empty:
        return "N/A", pd.NA

    return (
        grouped_delay.index[0],
        grouped_delay.iloc[0]
    )


def show_primary_delay_charts(
    data,
    summary
):
    """
    Display delay distribution and crime-group comparison.
    """
    delay_bucket_chart = standardize_chart_height(
        create_delay_bucket_chart(
            data
        )
    )

    crime_delay_chart = standardize_chart_height(
        create_reporting_delay_by_group_chart(
            data=data,
            group_column="crime_group",
            title="Average Delay by Crime Group"
        )
    )

    top_crime_group, top_crime_delay = get_highest_average_group(
        summary["valid_delay_data"],
        "crime_group"
    )

    chart_left, chart_right = st.columns(
        2,
        gap="small"
    )

    with chart_left:
        st.plotly_chart(
            delay_bucket_chart,
            use_container_width=True,
            key="delay_delay_bucket_chart",
            config=get_chart_config()
        )

    with chart_right:
        st.plotly_chart(
            crime_delay_chart,
            use_container_width=True,
            key="delay_by_crime_group_chart",
            config=get_chart_config()
        )

    insight_left, insight_right = st.columns(
        2,
        gap="small"
    )

    with insight_left:
        show_insight(
            f"{summary['top_delay_bucket']} is the most common "
            f"delay bucket with "
            f"{format_number(summary['delay_bucket_count'])} records."
        )

    with insight_right:
        if pd.isna(top_crime_delay):
            show_insight(
                "Average reporting delay by crime group is unavailable "
                "for the selected records."
            )
        else:
            show_insight(
                f"{top_crime_group} has the highest average delay "
                f"among crime groups at "
                f"{format_average_delay(top_crime_delay)}."
            )


def show_location_delay_chart(
    data,
    valid_delay_data
):
    """
    Display reporting delay by location group.
    """
    location_delay_chart = create_reporting_delay_by_group_chart(
        data=data,
        group_column="location_group",
        title="Average Delay by Location Group"
    )

    location_delay_chart.update_layout(
        height=475
    )

    st.plotly_chart(
        location_delay_chart,
        use_container_width=True,
        key="delay_by_location_group_chart",
        config=get_chart_config()
    )

    top_location_group, top_location_delay = get_highest_average_group(
        valid_delay_data,
        "location_group"
    )

    if pd.isna(top_location_delay):
        show_insight(
            "Average reporting delay by location group is unavailable "
            "for the selected records."
        )
    else:
        show_insight(
            f"{top_location_group} has the highest average reporting "
            f"delay among location groups at "
            f"{format_average_delay(top_location_delay)}."
        )


def show_high_delay_review(valid_delay_data):
    """
    Display a collapsed table of the longest reporting delays.
    """
    with st.expander(
        "High-Delay Record Review",
        expanded=False
    ):
        show_info_hint(
            "About this review panel",
            (
                "Use this table to inspect records with the longest "
                "valid reporting delays. It is intended for validation "
                "and follow-up investigation."
            )
        )

        if valid_delay_data.empty:
            st.info(
                "No valid reporting-delay records are available for "
                "the selected filters."
            )

            return

        show_compact_record_note(
            "Showing the 25 records with the longest valid reporting "
            "delays in the current filtered view."
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
            column
            for column in delay_columns
            if column in valid_delay_data.columns
        ]

        st.dataframe(
            valid_delay_data[
                available_columns
            ]
            .sort_values(
                "report_delay_hours",
                ascending=False
            )
            .head(25),
            use_container_width=True,
            hide_index=True
        )


def show_reporting_delay(data):
    """
    Display the complete reporting-timeliness section.
    """
    show_section_banner(
        eyebrow="",
        title="Reporting Timeliness Profile",
        description=(
            "Measure how quickly incidents are reported and identify "
            "same-day reports, late reports, and high-delay patterns."
        )
    )

    summary = show_delay_summary(
        data
    )

    st.divider()

    show_primary_delay_charts(
        data,
        summary
    )

    show_location_delay_chart(
        data,
        summary["valid_delay_data"]
    )

    show_high_delay_review(
        summary["valid_delay_data"]
    )