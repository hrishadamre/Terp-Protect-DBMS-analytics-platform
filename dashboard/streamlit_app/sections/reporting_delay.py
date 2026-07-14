"""
reporting_delay.py

Purpose:
Display the reporting timeliness profile for the Terp Protect dashboard.

Responsibilities:
- Measure valid reporting delays
- Prioritize median and 90th-percentile delay over the mean
- Display reporting-delay buckets in a meaningful order
- Compare median delay across crime and location groups
- Exclude very small groups from grouped delay comparisons
- Provide a collapsed high-delay review table
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.charts import get_chart_config
from components.layout import (
    show_compact_overview_strip,
    show_compact_record_note,
    show_info_hint,
    show_insight,
    show_section_banner
)
from components.metrics import (
    format_number,
    format_percentage
)


DELAY_BUCKET_ORDER = [
    "Same Day / Within 24 Hours",
    "1-3 Days",
    "4-7 Days",
    "Over 7 Days",
    "Unknown"
]


DELAY_BUCKET_COLORS = {
    "Same Day / Within 24 Hours": "#6AC7B6",
    "1-3 Days": "#F2CC68",
    "4-7 Days": "#E9A85D",
    "Over 7 Days": "#D95F65",
    "Unknown": "#AAB7C8"
}


GROUP_CHART_HEIGHT = 440

DELAY_BUCKET_CHART_HEIGHT = 440

MINIMUM_GROUP_RECORDS = 20


def get_valid_delay_data(data):
    """
    Return records containing a valid non-negative reporting delay.
    """
    if data is None or data.empty:
        return pd.DataFrame()

    valid_data = data.copy()

    if "report_delay_hours" not in valid_data.columns:
        return valid_data.iloc[0:0].copy()

    valid_data["report_delay_hours"] = pd.to_numeric(
        valid_data["report_delay_hours"],
        errors="coerce"
    )

    valid_mask = (
        valid_data["report_delay_hours"].notna()
        & (
            valid_data["report_delay_hours"]
            >= 0
        )
    )

    if "has_valid_reporting_delay" in valid_data.columns:
        valid_flag = pd.to_numeric(
            valid_data["has_valid_reporting_delay"],
            errors="coerce"
        ).fillna(0)

        valid_mask = (
            valid_mask
            & (
                valid_flag == 1
            )
        )

    return valid_data[
        valid_mask
    ].copy()


def calculate_percentage(
    count,
    total
):
    """
    Calculate a safe percentage.
    """
    if total <= 0:
        return 0.0

    return (
        count
        / total
        * 100
    )


def format_delay(hours):
    """
    Format reporting delay using hours or days.

    Values below 48 hours are shown in hours.
    Larger values are shown in days.
    """
    numeric_hours = pd.to_numeric(
        hours,
        errors="coerce"
    )

    if pd.isna(numeric_hours):
        return "N/A"

    numeric_hours = float(
        numeric_hours
    )

    if numeric_hours < 48:
        return f"{numeric_hours:.1f} hrs"

    return f"{numeric_hours / 24:.1f} days"


def calculate_delay_statistics(valid_delay_data):
    """
    Calculate median, P90, and supporting delay metrics.
    """
    if (
        valid_delay_data.empty
        or "report_delay_hours" not in valid_delay_data.columns
    ):
        return {
            "median_hours": pd.NA,
            "p90_hours": pd.NA,
            "mean_hours": pd.NA
        }

    delay_values = pd.to_numeric(
        valid_delay_data["report_delay_hours"],
        errors="coerce"
    ).dropna()

    if delay_values.empty:
        return {
            "median_hours": pd.NA,
            "p90_hours": pd.NA,
            "mean_hours": pd.NA
        }

    return {
        "median_hours": delay_values.median(),
        "p90_hours": delay_values.quantile(0.90),
        "mean_hours": delay_values.mean()
    }


def count_delay_bucket(
    data,
    bucket_name
):
    """
    Count records in one delay bucket.
    """
    if (
        data is None
        or data.empty
        or "delay_bucket" not in data.columns
    ):
        return 0

    return int(
        (
            data["delay_bucket"]
            == bucket_name
        ).sum()
    )


def prepare_delay_bucket_data(data):
    """
    Prepare delay-bucket counts in the required chronological order.
    """
    if (
        data is None
        or data.empty
        or "delay_bucket" not in data.columns
    ):
        return pd.DataFrame(
            {
                "delay_bucket": DELAY_BUCKET_ORDER,
                "incident_count": [0] * len(
                    DELAY_BUCKET_ORDER
                ),
                "percentage": [0.0] * len(
                    DELAY_BUCKET_ORDER
                )
            }
        )

    cleaned_buckets = (
        data["delay_bucket"]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
        .replace(
            {
                "": "Unknown"
            }
        )
    )

    bucket_counts = (
        cleaned_buckets
        .value_counts()
        .reindex(
            DELAY_BUCKET_ORDER,
            fill_value=0
        )
    )

    total_records = int(
        bucket_counts.sum()
    )

    bucket_data = bucket_counts.rename(
        "incident_count"
    ).reset_index()

    bucket_data.columns = [
        "delay_bucket",
        "incident_count"
    ]

    bucket_data["percentage"] = (
        bucket_data["incident_count"]
        / total_records
        * 100
        if total_records > 0
        else 0.0
    )

    return bucket_data


def create_ordered_delay_bucket_chart(data):
    """
    Create an ordered reporting-delay bucket bar chart.

    The previous line overlay has been removed because delay buckets
    are discrete categories rather than a continuous time series.
    """
    bucket_data = prepare_delay_bucket_data(
        data
    )

    colors = [
        DELAY_BUCKET_COLORS.get(
            bucket,
            "#AAB7C8"
        )
        for bucket in bucket_data[
            "delay_bucket"
        ]
    ]

    figure = go.Figure()

    figure.add_trace(
        go.Bar(
            x=bucket_data[
                "delay_bucket"
            ],
            y=bucket_data[
                "incident_count"
            ],
            marker={
                "color": colors,
                "line": {
                    "color": "rgba(255, 255, 255, 0.10)",
                    "width": 1
                }
            },
            customdata=bucket_data[
                [
                    "percentage"
                ]
            ],
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Incidents: %{y:,}<br>"
                "Share: %{customdata[0]:.1f}%"
                "<extra></extra>"
            )
        )
    )

    figure.update_layout(
        title={
            "text": "Reporting Delay Distribution",
            "x": 0,
            "xanchor": "left",
            "font": {
                "size": 17,
                "color": "#F8FAFC"
            }
        },
        height=DELAY_BUCKET_CHART_HEIGHT,
        margin={
            "l": 60,
            "r": 24,
            "t": 68,
            "b": 75
        },
        paper_bgcolor="#0B111C",
        plot_bgcolor="#0B111C",
        showlegend=False,
        font={
            "color": "#F8FAFC"
        },
        xaxis={
            "title": {
                "text": "Reporting Delay"
            },
            "categoryorder": "array",
            "categoryarray": DELAY_BUCKET_ORDER,
            "tickfont": {
                "size": 11,
                "color": "#CBD5E1"
            },
            "showgrid": False,
            "showline": True,
            "linecolor": "#334155"
        },
        yaxis={
            "title": {
                "text": "Incident Count"
            },
            "rangemode": "tozero",
            "tickfont": {
                "size": 11,
                "color": "#CBD5E1"
            },
            "gridcolor": "rgba(71, 85, 105, 0.50)",
            "showline": True,
            "linecolor": "#334155"
        }
    )

    return figure


def prepare_group_delay_summary(
    valid_delay_data,
    group_column,
    minimum_records=MINIMUM_GROUP_RECORDS
):
    """
    Calculate grouped median, P90, mean, and valid-record count.

    Groups with fewer than minimum_records valid records are excluded
    to reduce misleading results caused by very small samples.
    """
    required_columns = {
        group_column,
        "report_delay_hours"
    }

    if (
        valid_delay_data is None
        or valid_delay_data.empty
        or not required_columns.issubset(
            valid_delay_data.columns
        )
    ):
        return pd.DataFrame()

    group_data = valid_delay_data[
        [
            group_column,
            "report_delay_hours"
        ]
    ].copy()

    group_data[group_column] = (
        group_data[group_column]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
        .replace(
            {
                "": "Unknown"
            }
        )
    )

    group_data["report_delay_hours"] = pd.to_numeric(
        group_data["report_delay_hours"],
        errors="coerce"
    )

    group_data = group_data.dropna(
        subset=[
            "report_delay_hours"
        ]
    )

    if group_data.empty:
        return pd.DataFrame()

    summary = (
        group_data
        .groupby(
            group_column
        )["report_delay_hours"]
        .agg(
            valid_records="count",
            median_delay_hours="median",
            mean_delay_hours="mean",
            p90_delay_hours=lambda values: values.quantile(
                0.90
            )
        )
        .reset_index()
    )

    summary = summary[
        summary["valid_records"]
        >= minimum_records
    ].copy()

    summary = summary.sort_values(
        [
            "median_delay_hours",
            "valid_records"
        ],
        ascending=[
            False,
            False
        ]
    )

    return summary


def get_group_display_name(group_column):
    """
    Return a readable group name for chart copy.
    """
    names = {
        "crime_group": "Crime Group",
        "location_group": "Location Group"
    }

    return names.get(
        group_column,
        group_column.replace(
            "_",
            " "
        ).title()
    )


def create_group_median_delay_chart(
    valid_delay_data,
    group_column,
    title,
    minimum_records=MINIMUM_GROUP_RECORDS,
    max_categories=15
):
    """
    Create a horizontal median-delay chart.

    Hover information includes:
    - median delay
    - 90th-percentile delay
    - mean delay
    - number of valid records
    """
    summary = prepare_group_delay_summary(
        valid_delay_data=valid_delay_data,
        group_column=group_column,
        minimum_records=minimum_records
    )

    figure = go.Figure()

    if summary.empty:
        figure.add_annotation(
            text=(
                "No groups meet the minimum "
                f"{minimum_records}-record threshold."
            ),
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font={
                "size": 14,
                "color": "#CBD5E1"
            }
        )

        figure.update_layout(
            title={
                "text": title,
                "x": 0,
                "xanchor": "left"
            },
            height=GROUP_CHART_HEIGHT,
            paper_bgcolor="#0B111C",
            plot_bgcolor="#0B111C"
        )

        return figure

    chart_data = summary.head(
        max_categories
    ).sort_values(
        "median_delay_hours",
        ascending=True
    )

    bar_colors = []

    maximum_median = chart_data[
        "median_delay_hours"
    ].max()

    for median_value in chart_data[
        "median_delay_hours"
    ]:
        if maximum_median <= 0:
            bar_colors.append(
                "#6AC7B6"
            )
        elif median_value >= maximum_median * 0.75:
            bar_colors.append(
                "#D95F65"
            )
        elif median_value >= maximum_median * 0.45:
            bar_colors.append(
                "#E9A85D"
            )
        elif median_value >= maximum_median * 0.20:
            bar_colors.append(
                "#F2CC68"
            )
        else:
            bar_colors.append(
                "#6AC7B6"
            )

    custom_data = chart_data[
        [
            "p90_delay_hours",
            "mean_delay_hours",
            "valid_records"
        ]
    ]

    figure.add_trace(
        go.Bar(
            x=chart_data[
                "median_delay_hours"
            ],
            y=chart_data[
                group_column
            ],
            orientation="h",
            marker={
                "color": bar_colors
            },
            customdata=custom_data,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Median: %{x:.1f} hours<br>"
                "P90: %{customdata[0]:.1f} hours<br>"
                "Mean: %{customdata[1]:.1f} hours<br>"
                "Valid records: %{customdata[2]:,}"
                "<extra></extra>"
            )
        )
    )

    figure.update_layout(
        title={
            "text": title,
            "x": 0,
            "xanchor": "left",
            "font": {
                "size": 17,
                "color": "#F8FAFC"
            }
        },
        height=GROUP_CHART_HEIGHT,
        margin={
            "l": 145,
            "r": 24,
            "t": 68,
            "b": 55
        },
        paper_bgcolor="#0B111C",
        plot_bgcolor="#0B111C",
        showlegend=False,
        font={
            "color": "#F8FAFC"
        },
        xaxis={
            "title": {
                "text": "Median Delay Hours"
            },
            "rangemode": "tozero",
            "gridcolor": "rgba(71, 85, 105, 0.50)",
            "tickfont": {
                "size": 11,
                "color": "#CBD5E1"
            },
            "showline": True,
            "linecolor": "#334155"
        },
        yaxis={
            "title": {
                "text": ""
            },
            "tickfont": {
                "size": 10,
                "color": "#CBD5E1"
            },
            "showgrid": False,
            "automargin": True
        }
    )

    return figure


def get_highest_median_group(
    valid_delay_data,
    group_column
):
    """
    Return the group with the highest median delay after applying
    the minimum-record threshold.
    """
    summary = prepare_group_delay_summary(
        valid_delay_data=valid_delay_data,
        group_column=group_column
    )

    if summary.empty:
        return {
            "group": "N/A",
            "median_hours": pd.NA,
            "p90_hours": pd.NA,
            "valid_records": 0
        }

    top_row = summary.iloc[0]

    return {
        "group": top_row[
            group_column
        ],
        "median_hours": top_row[
            "median_delay_hours"
        ],
        "p90_hours": top_row[
            "p90_delay_hours"
        ],
        "valid_records": int(
            top_row[
                "valid_records"
            ]
        )
    }


def show_delay_summary(data):
    """
    Display compact reporting-delay summary cards.
    """
    total_records = len(
        data
    )

    valid_delay_data = get_valid_delay_data(
        data
    )

    valid_count = len(
        valid_delay_data
    )

    valid_coverage = calculate_percentage(
        valid_count,
        total_records
    )

    statistics = calculate_delay_statistics(
        valid_delay_data
    )

    same_day_count = count_delay_bucket(
        data,
        "Same Day / Within 24 Hours"
    )

    over_seven_count = count_delay_bucket(
        data,
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

    bucket_data = prepare_delay_bucket_data(
        data
    )

    if bucket_data.empty:
        top_delay_bucket = "N/A"
        top_delay_bucket_count = 0
    else:
        top_bucket_row = bucket_data.loc[
            bucket_data[
                "incident_count"
            ].idxmax()
        ]

        top_delay_bucket = top_bucket_row[
            "delay_bucket"
        ]

        top_delay_bucket_count = int(
            top_bucket_row[
                "incident_count"
            ]
        )

    overview_items = [
        {
            "label": "Selected Incidents",
            "value": format_number(
                total_records
            ),
            "meta": "Current filtered view",
            "numeric": True
        },
        {
            "label": "Valid Delay Coverage",
            "value": format_percentage(
                valid_coverage
            ),
            "meta": f"{format_number(valid_count)} usable records",
            "numeric": True
        },
        {
            "label": "Median Delay",
            "value": format_delay(
                statistics[
                    "median_hours"
                ]
            ),
            "meta": "Typical reporting delay",
            "numeric": True
        },
        {
            "label": "P90 Delay",
            "value": format_delay(
                statistics[
                    "p90_hours"
                ]
            ),
            "meta": "90% reported within",
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
                top_delay_bucket_count
            )
        }
    ]

    show_compact_overview_strip(
        overview_items
    )

    if pd.isna(
        statistics[
            "median_hours"
        ]
    ):
        show_insight(
            "Valid reporting-delay statistics are unavailable for "
            "the current filtered selection."
        )
    else:
        show_insight(
            f"The median reporting delay is "
            f"{format_delay(statistics['median_hours'])}, while the "
            f"90th-percentile delay is "
            f"{format_delay(statistics['p90_hours'])}. "
            f"{format_percentage(same_day_percentage)} of valid records "
            f"were reported within 24 hours."
        )

    return {
        "valid_delay_data": valid_delay_data,
        "statistics": statistics,
        "valid_count": valid_count,
        "valid_coverage": valid_coverage,
        "same_day_count": same_day_count,
        "same_day_percentage": same_day_percentage,
        "over_seven_count": over_seven_count,
        "over_seven_percentage": over_seven_percentage,
        "top_delay_bucket": top_delay_bucket,
        "top_delay_bucket_count": top_delay_bucket_count
    }


def show_primary_delay_charts(
    data,
    summary
):
    """
    Display the ordered bucket distribution and median delay by
    crime group.
    """
    bucket_chart = create_ordered_delay_bucket_chart(
        data
    )

    crime_group_chart = create_group_median_delay_chart(
        valid_delay_data=summary[
            "valid_delay_data"
        ],
        group_column="crime_group",
        title="Median Delay by Crime Group"
    )

    top_crime_group = get_highest_median_group(
        valid_delay_data=summary[
            "valid_delay_data"
        ],
        group_column="crime_group"
    )

    chart_left, chart_right = st.columns(
        2,
        gap="small"
    )

    with chart_left:
        st.plotly_chart(
            bucket_chart,
            use_container_width=True,
            key="delay_ordered_bucket_chart",
            config=get_chart_config()
        )

    with chart_right:
        st.plotly_chart(
            crime_group_chart,
            use_container_width=True,
            key="delay_median_by_crime_group_chart",
            config=get_chart_config()
        )

    insight_left, insight_right = st.columns(
        2,
        gap="small"
    )

    with insight_left:
        show_insight(
            f"{summary['top_delay_bucket']} is the most common "
            f"reporting-delay bucket with "
            f"{format_number(summary['top_delay_bucket_count'])} records."
        )

    with insight_right:
        if pd.isna(
            top_crime_group[
                "median_hours"
            ]
        ):
            show_insight(
                f"No crime group meets the minimum "
                f"{MINIMUM_GROUP_RECORDS}-record threshold."
            )
        else:
            show_insight(
                f"{top_crime_group['group']} has the highest median "
                f"reporting delay among eligible crime groups at "
                f"{format_delay(top_crime_group['median_hours'])}. "
                f"This result is based on "
                f"{format_number(top_crime_group['valid_records'])} "
                f"valid records."
            )


def show_location_delay_chart(summary):
    """
    Display median reporting delay by location group.
    """
    location_chart = create_group_median_delay_chart(
        valid_delay_data=summary[
            "valid_delay_data"
        ],
        group_column="location_group",
        title="Median Delay by Location Group",
        max_categories=12
    )

    location_chart.update_layout(
        height=430
    )

    st.plotly_chart(
        location_chart,
        use_container_width=True,
        key="delay_median_by_location_group_chart",
        config=get_chart_config()
    )

    top_location_group = get_highest_median_group(
        valid_delay_data=summary[
            "valid_delay_data"
        ],
        group_column="location_group"
    )

    if pd.isna(
        top_location_group[
            "median_hours"
        ]
    ):
        show_insight(
            f"No location group meets the minimum "
            f"{MINIMUM_GROUP_RECORDS}-record threshold."
        )
    else:
        show_insight(
            f"{top_location_group['group']} has the highest median "
            f"reporting delay among eligible location groups at "
            f"{format_delay(top_location_group['median_hours'])}. "
            f"Its 90th-percentile delay is "
            f"{format_delay(top_location_group['p90_hours'])}."
        )


def show_high_delay_review(valid_delay_data):
    """
    Display a collapsed table containing the longest valid delays.
    """
    with st.expander(
        "High-Delay Record Review",
        expanded=False
    ):
        show_info_hint(
            "About this review panel",
            (
                "Use this table to inspect records with the longest "
                "valid reporting delays. Extreme values can strongly "
                "affect averages, which is why the dashboard uses the "
                "median as its primary delay measure."
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
            "delay_bucket",
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
        eyebrow="Timeliness Intelligence",
        title="Reporting Timeliness Profile",
        description=(
            "Measure how quickly incidents are reported using median, "
            "90th-percentile, and ordered delay-bucket analysis."
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
        summary
    )

    show_high_delay_review(
        summary[
            "valid_delay_data"
        ]
    )