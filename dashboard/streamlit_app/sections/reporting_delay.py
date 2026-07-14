"""
reporting_delay.py

Purpose:
Analyze how long incidents take to be reported after occurrence.

Responsibilities:
- Validate reporting-delay values
- Summarize median and P90 reporting delay
- Show ordered elapsed-time delay buckets
- Compare median delay across crime and location groups
- Use consistent valid-record denominators
- Keep high-delay record review collapsed
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
    "Reported Within 24 Hours",
    "1-3 Days",
    "4-7 Days",
    "Over 7 Days",
    "Unknown"
]


DELAY_BUCKET_COLORS = {
    "Reported Within 24 Hours": "#6AC7B6",
    "1-3 Days": "#F2CC68",
    "4-7 Days": "#E9A85D",
    "Over 7 Days": "#D95F65",
    "Unknown": "#AAB7C8"
}


MINIMUM_GROUP_RECORDS = 20
TOP_GROUPS = 12

BUCKET_CHART_HEIGHT = 430
GROUP_CHART_HEIGHT = 470


def safe_percentage(
    numerator,
    denominator
):
    """
    Calculate a percentage safely.
    """
    numeric_numerator = pd.to_numeric(
        numerator,
        errors="coerce"
    )

    numeric_denominator = pd.to_numeric(
        denominator,
        errors="coerce"
    )

    if (
        pd.isna(numeric_numerator)
        or pd.isna(numeric_denominator)
        or numeric_denominator <= 0
    ):
        return 0.0

    return float(
        numeric_numerator
        / numeric_denominator
        * 100
    )


def distinct_incident_count(data):
    """
    Return the number of distinct incidents.
    """
    if data is None or data.empty:
        return 0

    if "incident_id" in data.columns:
        return int(
            data["incident_id"]
            .dropna()
            .nunique()
        )

    return len(
        data
    )


def format_delay_duration(value):
    """
    Format a reporting delay consistently.

    Delays below 48 hours are displayed in hours.
    Delays of 48 hours or more are displayed in days.
    """
    numeric_value = pd.to_numeric(
        value,
        errors="coerce"
    )

    if pd.isna(
        numeric_value
    ):
        return "N/A"

    numeric_value = float(
        numeric_value
    )

    if numeric_value < 48:
        return f"{numeric_value:.1f} hrs"

    return f"{numeric_value / 24:.1f} days"


def normalize_delay_bucket(value):
    """
    Standardize delay bucket labels.

    The first bucket is based on elapsed time, not calendar date.
    """
    if pd.isna(value):
        return "Unknown"

    cleaned_value = str(
        value
    ).strip()

    lower_value = cleaned_value.lower()

    if (
        "same day" in lower_value
        or "within 24" in lower_value
    ):
        return "Reported Within 24 Hours"

    if (
        "1-3" in lower_value
        or "1 - 3" in lower_value
    ):
        return "1-3 Days"

    if (
        "4-7" in lower_value
        or "4 - 7" in lower_value
    ):
        return "4-7 Days"

    if (
        "over 7" in lower_value
        or "more than 7" in lower_value
    ):
        return "Over 7 Days"

    return "Unknown"


def get_valid_delay_data(data):
    """
    Return records containing valid, non-negative reporting delays.
    """
    if (
        data is None
        or data.empty
        or "report_delay_hours" not in data.columns
    ):
        return pd.DataFrame()

    valid_data = data.copy()

    valid_data["report_delay_hours"] = pd.to_numeric(
        valid_data["report_delay_hours"],
        errors="coerce"
    )

    valid_mask = (
        valid_data["report_delay_hours"].notna()
        & (
            valid_data["report_delay_hours"] >= 0
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

    valid_data = valid_data[
        valid_mask
    ].copy()

    if (
        not valid_data.empty
        and "incident_id" in valid_data.columns
    ):
        valid_data = valid_data.drop_duplicates(
            subset=[
                "incident_id"
            ]
        )

    return valid_data


def calculate_delay_statistics(data):
    """
    Calculate reporting-delay statistics from valid incident records.
    """
    total_records = distinct_incident_count(
        data
    )

    valid_data = get_valid_delay_data(
        data
    )

    valid_count = distinct_incident_count(
        valid_data
    )

    invalid_count = max(
        total_records - valid_count,
        0
    )

    valid_coverage = safe_percentage(
        valid_count,
        total_records
    )

    if valid_data.empty:
        return {
            "total_records": total_records,
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "valid_coverage": valid_coverage,
            "median_delay": pd.NA,
            "p90_delay": pd.NA,
            "within_24_count": 0,
            "within_24_share": 0.0,
            "over_seven_day_count": 0,
            "over_seven_day_share": 0.0
        }

    delay_values = valid_data[
        "report_delay_hours"
    ]

    median_delay = float(
        delay_values.median()
    )

    p90_delay = float(
        delay_values.quantile(
            0.90
        )
    )

    within_24_count = int(
        (
            delay_values <= 24
        ).sum()
    )

    over_seven_day_count = int(
        (
            delay_values > 168
        ).sum()
    )

    within_24_share = safe_percentage(
        within_24_count,
        valid_count
    )

    over_seven_day_share = safe_percentage(
        over_seven_day_count,
        valid_count
    )

    return {
        "total_records": total_records,
        "valid_count": valid_count,
        "invalid_count": invalid_count,
        "valid_coverage": valid_coverage,
        "median_delay": median_delay,
        "p90_delay": p90_delay,
        "within_24_count": within_24_count,
        "within_24_share": within_24_share,
        "over_seven_day_count": over_seven_day_count,
        "over_seven_day_share": over_seven_day_share
    }


def prepare_delay_bucket_data(data):
    """
    Prepare ordered reporting-delay bucket counts.

    The first bucket means elapsed reporting time of 24 hours or less.
    """
    if data is None or data.empty:
        return pd.DataFrame(
            {
                "delay_bucket": DELAY_BUCKET_ORDER,
                "incident_count": [
                    0
                ] * len(
                    DELAY_BUCKET_ORDER
                ),
                "percentage": [
                    0.0
                ] * len(
                    DELAY_BUCKET_ORDER
                )
            }
        )

    working_data = data.copy()

    if (
        "incident_id" in working_data.columns
    ):
        working_data = working_data.drop_duplicates(
            subset=[
                "incident_id"
            ]
        )

    if "delay_bucket" in working_data.columns:
        bucket_values = (
            working_data["delay_bucket"]
            .apply(
                normalize_delay_bucket
            )
        )

    elif "report_delay_hours" in working_data.columns:
        delay_values = pd.to_numeric(
            working_data["report_delay_hours"],
            errors="coerce"
        )

        bucket_values = pd.Series(
            "Unknown",
            index=working_data.index,
            dtype="object"
        )

        bucket_values.loc[
            delay_values.notna()
            & (
                delay_values >= 0
            )
            & (
                delay_values <= 24
            )
        ] = "Reported Within 24 Hours"

        bucket_values.loc[
            (
                delay_values > 24
            )
            & (
                delay_values <= 72
            )
        ] = "1-3 Days"

        bucket_values.loc[
            (
                delay_values > 72
            )
            & (
                delay_values <= 168
            )
        ] = "4-7 Days"

        bucket_values.loc[
            delay_values > 168
        ] = "Over 7 Days"

    else:
        bucket_values = pd.Series(
            "Unknown",
            index=working_data.index,
            dtype="object"
        )

    bucket_counts = (
        bucket_values
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

    bucket_data["percentage"] = bucket_data[
        "incident_count"
    ].apply(
        lambda count: safe_percentage(
            count,
            total_records
        )
    )

    return bucket_data


def create_delay_bucket_chart(data):
    """
    Create the ordered elapsed reporting-delay distribution.
    """
    bucket_data = prepare_delay_bucket_data(
        data
    )

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
                "color": [
                    DELAY_BUCKET_COLORS.get(
                        bucket,
                        "#AAB7C8"
                    )
                    for bucket in bucket_data[
                        "delay_bucket"
                    ]
                ]
            },
            customdata=bucket_data[
                [
                    "percentage"
                ]
            ],
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Distinct incidents: %{y:,}<br>"
                "Share of selected incidents: %{customdata[0]:.1f}%"
                "<extra></extra>"
            )
        )
    )

    figure.update_layout(
        title={
            "text": "Elapsed Reporting Delay Distribution",
            "x": 0,
            "xanchor": "left",
            "font": {
                "size": 17,
                "color": "#F8FAFC"
            }
        },
        height=BUCKET_CHART_HEIGHT,
        margin={
            "l": 60,
            "r": 25,
            "t": 70,
            "b": 95
        },
        paper_bgcolor="#0B111C",
        plot_bgcolor="#0B111C",
        showlegend=False,
        font={
            "color": "#F8FAFC"
        },
        xaxis={
            "title": {
                "text": "Elapsed Time from Occurrence to Report"
            },
            "categoryorder": "array",
            "categoryarray": DELAY_BUCKET_ORDER,
            "tickangle": -25,
            "tickfont": {
                "size": 10,
                "color": "#CBD5E1"
            },
            "showgrid": False,
            "showline": True,
            "linecolor": "#334155"
        },
        yaxis={
            "title": {
                "text": "Distinct Incident Count"
            },
            "rangemode": "tozero",
            "gridcolor": "rgba(71, 85, 105, 0.50)",
            "tickfont": {
                "size": 11,
                "color": "#CBD5E1"
            },
            "showline": True,
            "linecolor": "#334155"
        }
    )

    return figure


def prepare_group_delay_data(
    data,
    group_column,
    maximum_groups=TOP_GROUPS,
    minimum_records=MINIMUM_GROUP_RECORDS
):
    """
    Prepare median and P90 delay by category.

    Groups below the minimum valid-record threshold are excluded.
    """
    valid_data = get_valid_delay_data(
        data
    )

    if (
        valid_data.empty
        or group_column not in valid_data.columns
    ):
        return pd.DataFrame()

    selected_columns = [
        group_column,
        "report_delay_hours"
    ]

    if "incident_id" in valid_data.columns:
        selected_columns.append(
            "incident_id"
        )

    working_data = valid_data[
        selected_columns
    ].copy()

    working_data[group_column] = (
        working_data[group_column]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
        .replace(
            {
                "": "Unknown"
            }
        )
    )

    if "incident_id" in working_data.columns:
        working_data = working_data.drop_duplicates(
            subset=[
                "incident_id",
                group_column
            ]
        )

    group_summary = (
        working_data
        .groupby(
            group_column
        )["report_delay_hours"]
        .agg(
            record_count="count",
            median_delay_hours="median",
            p90_delay_hours=lambda values: values.quantile(
                0.90
            )
        )
        .reset_index()
    )

    group_summary = group_summary[
        group_summary[
            "record_count"
        ] >= minimum_records
    ].copy()

    return (
        group_summary
        .sort_values(
            [
                "median_delay_hours",
                "record_count"
            ],
            ascending=[
                False,
                False
            ]
        )
        .head(
            maximum_groups
        )
    )


def get_delay_color(
    delay_hours,
    maximum_delay
):
    """
    Assign a simple risk-oriented color based on relative median delay.
    """
    if maximum_delay <= 0:
        return "#6AC7B6"

    ratio = float(
        delay_hours
        / maximum_delay
    )

    if ratio >= 0.75:
        return "#D95F65"

    if ratio >= 0.40:
        return "#F2CC68"

    return "#6AC7B6"


def create_group_delay_chart(
    data,
    group_column,
    title
):
    """
    Create a median reporting-delay comparison chart.
    """
    group_data = prepare_group_delay_data(
        data=data,
        group_column=group_column
    )

    figure = go.Figure()

    if group_data.empty:
        figure.add_annotation(
            text=(
                "No groups meet the minimum valid-record threshold."
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
            title=title,
            height=GROUP_CHART_HEIGHT,
            paper_bgcolor="#0B111C",
            plot_bgcolor="#0B111C"
        )

        return figure

    chart_data = group_data.sort_values(
        "median_delay_hours",
        ascending=True
    )

    maximum_delay = float(
        chart_data[
            "median_delay_hours"
        ].max()
    )

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
                "color": [
                    get_delay_color(
                        delay_hours=delay,
                        maximum_delay=maximum_delay
                    )
                    for delay in chart_data[
                        "median_delay_hours"
                    ]
                ]
            },
            customdata=chart_data[
                [
                    "record_count",
                    "p90_delay_hours"
                ]
            ],
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Median delay: %{x:.1f} hours<br>"
                "P90 delay: %{customdata[1]:.1f} hours<br>"
                "Valid distinct incidents: %{customdata[0]:,}"
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
            "l": 190,
            "r": 25,
            "t": 70,
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
                "text": "Median Reporting Delay (Hours)"
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
            "automargin": True,
            "showgrid": False,
            "tickfont": {
                "size": 10,
                "color": "#CBD5E1"
            }
        }
    )

    return figure


def get_highest_median_group(
    data,
    group_column
):
    """
    Return the group with the highest eligible median delay.
    """
    group_data = prepare_group_delay_data(
        data=data,
        group_column=group_column
    )

    if group_data.empty:
        return {
            "group": "N/A",
            "median_delay": pd.NA,
            "p90_delay": pd.NA,
            "record_count": 0
        }

    top_row = group_data.sort_values(
        "median_delay_hours",
        ascending=False
    ).iloc[
        0
    ]

    return {
        "group": top_row[
            group_column
        ],
        "median_delay": float(
            top_row[
                "median_delay_hours"
            ]
        ),
        "p90_delay": float(
            top_row[
                "p90_delay_hours"
            ]
        ),
        "record_count": int(
            top_row[
                "record_count"
            ]
        )
    }


def get_largest_delay_bucket(data):
    """
    Return the largest delay bucket and its count.
    """
    bucket_data = prepare_delay_bucket_data(
        data
    )

    if bucket_data.empty:
        return "N/A", 0

    top_row = bucket_data.sort_values(
        "incident_count",
        ascending=False
    ).iloc[
        0
    ]

    return (
        top_row[
            "delay_bucket"
        ],
        int(
            top_row[
                "incident_count"
            ]
        )
    )


def show_delay_summary(data):
    """
    Display reporting-delay overview cards.
    """
    statistics = calculate_delay_statistics(
        data
    )

    (
        top_delay_bucket,
        top_delay_bucket_count
    ) = get_largest_delay_bucket(
        data
    )

    overview_items = [
        {
            "label": "Selected Incidents",
            "value": format_number(
                statistics[
                    "total_records"
                ]
            ),
            "meta": "Distinct filtered incidents",
            "numeric": True,
            "metric_key": "selected_incidents"
        },
        {
            "label": "Valid Delay Coverage",
            "value": format_percentage(
                statistics[
                    "valid_coverage"
                ]
            ),
            "meta": (
                f"{format_number(statistics['valid_count'])} "
                "usable incidents"
            ),
            "numeric": True,
            "metric_key": "valid_delay_coverage"
        },
        {
            "label": "Median Delay",
            "value": format_delay_duration(
                statistics[
                    "median_delay"
                ]
            ),
            "meta": "Middle valid delay",
            "numeric": True,
            "metric_key": "median_delay"
        },
        {
            "label": "P90 Delay",
            "value": format_delay_duration(
                statistics[
                    "p90_delay"
                ]
            ),
            "meta": "90% reported within",
            "numeric": True,
            "metric_key": "p90_delay"
        },
        {
            "label": "Reported Within 24 Hours",
            "value": format_percentage(
                statistics[
                    "within_24_share"
                ]
            ),
            "meta": (
                f"{format_number(statistics['within_24_count'])} "
                "valid incidents"
            ),
            "numeric": True,
            "metric_key": "same_day_share"
        },
        {
            "label": "Reported After 7 Days",
            "value": format_percentage(
                statistics[
                    "over_seven_day_share"
                ]
            ),
            "meta": (
                f"{format_number(statistics['over_seven_day_count'])} "
                "valid incidents"
            ),
            "numeric": True,
            "metric_key": "over_seven_day_share"
        },
        {
            "label": "Largest Delay Bucket",
            "value": top_delay_bucket,
            "meta": "Most common elapsed range",
            "badge": format_number(
                top_delay_bucket_count
            ),
            # "help": (
            #     "The elapsed reporting-delay bucket containing the "
            #     "largest number of distinct selected incidents."
            # )
        }
    ]

    show_compact_overview_strip(
        overview_items
    )

    show_insight(
        f"The median valid reporting delay is "
        f"{format_delay_duration(statistics['median_delay'])}, while "
        f"90% of valid incidents were reported within "
        f"{format_delay_duration(statistics['p90_delay'])}. "
        f"{format_percentage(statistics['within_24_share'])} of valid "
        f"incidents were reported within 24 elapsed hours."
    )

    show_info_hint(
        "Delay denominator",
        (
            "Median, P90, within-24-hour share, and after-seven-day share "
            "use only distinct incidents with valid non-negative reporting "
            "delays. Valid delay coverage compares those usable incidents "
            "with all distinct selected incidents."
        )
    )

    # show_info_hint(
    #     "Within 24 hours definition",
    #     (
    #         "Reported Within 24 Hours is based on elapsed time between "
    #         "occurrence and report. It does not require the report to occur "
    #         "on the same calendar date."
    #     )
    # )

    return statistics


def show_delay_distribution(
    data,
    statistics
):
    """
    Display the ordered delay-bucket chart.
    """
    figure = create_delay_bucket_chart(
        data
    )

    st.plotly_chart(
        figure,
        use_container_width=True,
        key="reporting_delay_bucket_chart",
        config=get_chart_config()
    )

    show_insight(
        f"{format_number(statistics['within_24_count'])} valid incidents "
        f"were reported within 24 elapsed hours, while "
        f"{format_number(statistics['over_seven_day_count'])} were "
        f"reported after more than seven days."
    )


def show_group_delay_charts(data):
    """
    Display median reporting delay by crime and location group.
    """
    crime_chart = create_group_delay_chart(
        data=data,
        group_column="crime_group",
        title="Median Reporting Delay by Crime Group"
    )

    location_chart = create_group_delay_chart(
        data=data,
        group_column="location_group",
        title="Median Reporting Delay by Location Group"
    )

    crime_summary = get_highest_median_group(
        data=data,
        group_column="crime_group"
    )

    location_summary = get_highest_median_group(
        data=data,
        group_column="location_group"
    )

    chart_left, chart_right = st.columns(
        2,
        gap="small"
    )

    with chart_left:
        st.plotly_chart(
            crime_chart,
            use_container_width=True,
            key="reporting_delay_crime_group_chart",
            config=get_chart_config()
        )

    with chart_right:
        st.plotly_chart(
            location_chart,
            use_container_width=True,
            key="reporting_delay_location_group_chart",
            config=get_chart_config()
        )

    insight_left, insight_right = st.columns(
        2,
        gap="small"
    )

    with insight_left:
        if crime_summary[
            "group"
        ] == "N/A":
            show_insight(
                "No crime groups meet the minimum valid-delay "
                "record threshold."
            )

        else:
            show_insight(
                f"{crime_summary['group']} has the highest displayed "
                f"median crime-group delay at "
                f"{format_delay_duration(crime_summary['median_delay'])}, "
                f"based on "
                f"{format_number(crime_summary['record_count'])} valid "
                f"distinct incidents."
            )

    with insight_right:
        if location_summary[
            "group"
        ] == "N/A":
            show_insight(
                "No location groups meet the minimum valid-delay "
                "record threshold."
            )

        else:
            show_insight(
                f"{location_summary['group']} has the highest displayed "
                f"median location-group delay at "
                f"{format_delay_duration(location_summary['median_delay'])}, "
                f"based on "
                f"{format_number(location_summary['record_count'])} valid "
                f"distinct incidents."
            )

    show_info_hint(
        "Group comparison threshold",
        (
            f"Only groups with at least {MINIMUM_GROUP_RECORDS} valid "
            "distinct reporting-delay records are displayed. This reduces "
            "unstable comparisons based on very small samples."
        )
    )

    # show_info_hint(
    #     "Chart units",
    #     (
    #         "Group comparison axes use hours for a consistent numeric scale. "
    #         "Insight text converts larger values into days for readability."
    #     )
    # )


def get_high_delay_records(data):
    """
    Return records with valid reporting delays above seven days.
    """
    valid_data = get_valid_delay_data(
        data
    )

    if valid_data.empty:
        return pd.DataFrame()

    return (
        valid_data[
            valid_data[
                "report_delay_hours"
            ] > 168
        ]
        .sort_values(
            "report_delay_hours",
            ascending=False
        )
        .copy()
    )


def show_high_delay_review(data):
    """
    Display high-delay records in a collapsed review panel.
    """
    high_delay_data = get_high_delay_records(
        data
    )

    with st.expander(
        (
            "High-Delay Record Review "
            f"({format_number(len(high_delay_data))})"
        ),
        expanded=False
    ):
        show_info_hint(
            "Review scope",
            (
                "This table contains distinct incidents with valid elapsed "
                "reporting delays greater than seven days. It is intended "
                "for validation and investigation."
            )
        )

        if high_delay_data.empty:
            st.success(
                "No valid reporting-delay records exceed seven days "
                "in the current filtered view."
            )

            return

        show_compact_record_note(
            "Showing the first 25 incidents with the longest valid "
            "reporting delays."
        )

        review_columns = [
            "incident_id",
            "case_number",
            "occurred_datetime",
            "reported_datetime",
            "crime_group",
            "location_group",
            "disposition_group",
            "report_delay_hours",
            "delay_bucket"
        ]

        visible_columns = [
            column
            for column in review_columns
            if column in high_delay_data.columns
        ]

        st.dataframe(
            high_delay_data[
                visible_columns
            ].head(
                25
            ),
            use_container_width=True,
            hide_index=True
        )


def show_reporting_delay(data):
    """
    Display the complete reporting-delay section.
    """
    show_section_banner(
        eyebrow="Operational Timeliness",
        title="Reporting Timeliness Profile",
        description=(
            "Measure elapsed reporting time using median, P90, ordered "
            "delay buckets, and reliable group-level comparisons."
        )
    )

    statistics = show_delay_summary(
        data
    )

    # st.divider()

    show_delay_distribution(
        data,
        statistics
    )

    show_group_delay_charts(
        data
    )

    show_high_delay_review(
        data
    )