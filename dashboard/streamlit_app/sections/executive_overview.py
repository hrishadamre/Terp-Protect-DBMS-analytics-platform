"""
executive_overview.py

Command Center section for the Terp Protect dashboard.

Responsibilities:
- Calculate high-level incident statistics
- Display one compact horizontal overview strip
- Compare monthly incident trends across selected years
- Display aligned overview charts and analytical insights
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.charts import (
    create_delay_bucket_chart,
    create_horizontal_bar_chart,
    create_status_bar_chart,
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


MONTH_ORDER = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
]


YEAR_COLORS = [
    {
        "line": "#7DD3FC",
        "fill": "rgba(125, 211, 252, 0.18)"
    },
    {
        "line": "#F9A8D4",
        "fill": "rgba(249, 168, 212, 0.16)"
    },
    {
        "line": "#FCD34D",
        "fill": "rgba(252, 211, 77, 0.15)"
    },
    {
        "line": "#86EFAC",
        "fill": "rgba(134, 239, 172, 0.15)"
    },
    {
        "line": "#C4B5FD",
        "fill": "rgba(196, 181, 253, 0.16)"
    }
]


PRIMARY_CHART_HEIGHT = 485


def calculate_arrest_metrics(data):
    """
    Calculate arrest-related incident count and share.
    """
    total_incidents = len(data)

    if "is_arrest_related" not in data.columns:
        return 0, 0.0

    arrest_related_values = pd.to_numeric(
        data["is_arrest_related"],
        errors="coerce"
    ).fillna(0)

    arrest_related_count = int(
        arrest_related_values.sum()
    )

    arrest_share = (
        arrest_related_count
        / total_incidents
        * 100
        if total_incidents > 0
        else 0.0
    )

    return (
        arrest_related_count,
        arrest_share
    )


def calculate_average_delay(data):
    """
    Calculate average reporting delay in hours.
    """
    if "report_delay_hours" not in data.columns:
        return pd.NA

    delay_values = pd.to_numeric(
        data["report_delay_hours"],
        errors="coerce"
    )

    return delay_values.mean()


def format_average_delay(hours):
    """
    Format average reporting delay compactly.
    """
    if pd.isna(hours):
        return "N/A"

    if hours < 48:
        return f"{hours:.1f} hrs"

    return f"{hours / 24:.1f} days"


def get_chart_year_column(data):
    """
    Return the year column used for chart comparison.
    """
    if "source_year" in data.columns:
        return "source_year"

    if "occurred_year" in data.columns:
        return "occurred_year"

    return None


def prepare_monthly_year_comparison(data):
    """
    Aggregate incident counts by year and month.

    Missing month-year combinations are filled with zero.
    """
    year_column = get_chart_year_column(
        data
    )

    required_columns = {
        "occurred_month",
        "occurred_month_name"
    }

    if (
        year_column is None
        or not required_columns.issubset(data.columns)
    ):
        return pd.DataFrame()

    chart_data = data[
        [
            year_column,
            "occurred_month",
            "occurred_month_name"
        ]
    ].copy()

    chart_data[year_column] = pd.to_numeric(
        chart_data[year_column],
        errors="coerce"
    )

    chart_data["occurred_month"] = pd.to_numeric(
        chart_data["occurred_month"],
        errors="coerce"
    )

    chart_data = chart_data.dropna(
        subset=[
            year_column,
            "occurred_month"
        ]
    )

    if chart_data.empty:
        return pd.DataFrame()

    chart_data[year_column] = (
        chart_data[year_column]
        .astype(int)
    )

    chart_data["occurred_month"] = (
        chart_data["occurred_month"]
        .astype(int)
    )

    selected_years = sorted(
        chart_data[year_column]
        .drop_duplicates()
        .tolist(),
        reverse=True
    )

    complete_index = pd.MultiIndex.from_product(
        [
            selected_years,
            range(1, 13)
        ],
        names=[
            year_column,
            "occurred_month"
        ]
    )

    monthly_counts = (
        chart_data
        .groupby(
            [
                year_column,
                "occurred_month"
            ]
        )
        .size()
        .reindex(
            complete_index,
            fill_value=0
        )
        .rename("incident_count")
        .reset_index()
    )

    month_lookup = {
        month_number: month_name
        for month_number, month_name in enumerate(
            MONTH_ORDER,
            start=1
        )
    }

    monthly_counts["month_name"] = (
        monthly_counts["occurred_month"]
        .map(month_lookup)
    )

    return monthly_counts


def create_yearly_monthly_wave_chart(data):
    """
    Create a separate translucent monthly wave for each selected year.
    """
    monthly_counts = prepare_monthly_year_comparison(
        data
    )

    figure = go.Figure()

    if monthly_counts.empty:
        figure.add_annotation(
            text="Monthly year-comparison data is unavailable.",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font={
                "size": 15,
                "color": "#CBD5E1"
            }
        )

        figure.update_layout(
            title="Monthly Incident Trend by Year",
            height=PRIMARY_CHART_HEIGHT,
            paper_bgcolor="#0B111C",
            plot_bgcolor="#0B111C"
        )

        return figure

    year_column = get_chart_year_column(
        data
    )

    selected_years = sorted(
        monthly_counts[year_column]
        .drop_duplicates()
        .tolist(),
        reverse=True
    )

    for index, year in enumerate(
        selected_years
    ):
        year_data = monthly_counts[
            monthly_counts[year_column] == year
        ].sort_values(
            "occurred_month"
        )

        color = YEAR_COLORS[
            index % len(YEAR_COLORS)
        ]

        figure.add_trace(
            go.Scatter(
                x=year_data["month_name"],
                y=year_data["incident_count"],
                name=str(year),
                mode="lines+markers",
                line={
                    "color": color["line"],
                    "width": 3,
                    "shape": "spline",
                    "smoothing": 0.75
                },
                marker={
                    "size": 8,
                    "color": color["line"],
                    "line": {
                        "color": "#0B111C",
                        "width": 2
                    }
                },
                fill="tozeroy",
                fillcolor=color["fill"],
                hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "%{x}<br>"
                    "Incidents: %{y:,}"
                    "<extra></extra>"
                )
            )
        )

    figure.update_layout(
        title={
            "text": "Monthly Incident Trend by Year",
            "x": 0,
            "xanchor": "left",
            "font": {
                "size": 19,
                "color": "#F8FAFC"
            }
        },
        height=PRIMARY_CHART_HEIGHT,
        margin={
            "l": 55,
            "r": 25,
            "t": 80,
            "b": 70
        },
        paper_bgcolor="#0B111C",
        plot_bgcolor="#0B111C",
        hovermode="x unified",
        legend={
            "title": {
                "text": "Year",
                "font": {
                    "color": "#CBD5E1",
                    "size": 12
                }
            },
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.03,
            "xanchor": "right",
            "x": 1,
            "font": {
                "color": "#E2E8F0",
                "size": 12
            },
            "bgcolor": "rgba(11, 17, 28, 0.65)",
            "bordercolor": "rgba(148, 163, 184, 0.25)",
            "borderwidth": 1
        },
        xaxis={
            "title": {
                "text": "Month",
                "font": {
                    "color": "#F8FAFC",
                    "size": 14
                }
            },
            "categoryorder": "array",
            "categoryarray": MONTH_ORDER,
            "tickangle": -32,
            "tickfont": {
                "color": "#CBD5E1",
                "size": 11
            },
            "showgrid": False,
            "showline": True,
            "linecolor": "#334155",
            "fixedrange": False
        },
        yaxis={
            "title": {
                "text": "Incident Count",
                "font": {
                    "color": "#F8FAFC",
                    "size": 14
                }
            },
            "rangemode": "tozero",
            "tickfont": {
                "color": "#CBD5E1",
                "size": 11
            },
            "gridcolor": "rgba(71, 85, 105, 0.55)",
            "zerolinecolor": "rgba(71, 85, 105, 0.8)",
            "showline": True,
            "linecolor": "#334155",
            "fixedrange": False
        },
        font={
            "family": "Arial, sans-serif",
            "color": "#F8FAFC"
        }
    )

    return figure


def standardize_chart_height(
    figure,
    height=PRIMARY_CHART_HEIGHT
):
    """
    Force a Plotly chart to use the same height and outer margins
    as the adjacent chart.

    This keeps the insight bars aligned horizontally.
    """
    figure.update_layout(
        height=height,
        margin={
            "l": 55,
            "r": 25,
            "t": 80,
            "b": 70
        }
    )

    return figure


def get_yearly_peak_summary(data):
    """
    Return the highest-volume month for each selected year.
    """
    monthly_counts = prepare_monthly_year_comparison(
        data
    )

    if monthly_counts.empty:
        return (
            "Monthly year-comparison data "
            "is unavailable"
        )

    year_column = get_chart_year_column(
        data
    )

    summaries = []

    selected_years = sorted(
        monthly_counts[year_column]
        .drop_duplicates()
        .tolist(),
        reverse=True
    )

    for year in selected_years:
        year_data = monthly_counts[
            monthly_counts[year_column] == year
        ]

        peak_row = year_data.loc[
            year_data["incident_count"].idxmax()
        ]

        summaries.append(
            f"{year}: {peak_row['month_name']} "
            f"({format_number(peak_row['incident_count'])})"
        )

    return "; ".join(
        summaries
    )


def show_operational_summary(data):
    """
    Display the compact operational summary.
    """
    total_incidents = len(data)

    (
        arrest_related_count,
        arrest_share
    ) = calculate_arrest_metrics(
        data
    )

    average_delay = calculate_average_delay(
        data
    )

    (
        top_crime_group,
        crime_count
    ) = get_top_value(
        data,
        "crime_group"
    )

    (
        top_outcome,
        outcome_count
    ) = get_top_value(
        data,
        "disposition_group"
    )

    (
        top_location_group,
        location_count
    ) = get_top_value(
        data,
        "location_group"
    )

    overview_items = [
        {
            "label": "Incidents",
            "value": format_number(
                total_incidents
            ),
            "meta": "Filtered records",
            "numeric": True
        },
        {
            "label": "Arrest-Related",
            "value": format_number(
                arrest_related_count
            ),
            "meta": "Arrest-linked incidents",
            "numeric": True
        },
        {
            "label": "Arrest Share",
            "value": format_percentage(
                arrest_share
            ),
            "meta": "Selected incident share",
            "numeric": True
        },
        {
            "label": "Average Delay",
            "value": format_average_delay(
                average_delay
            ),
            "meta": "Reporting time",
            "numeric": True
        },
        {
            "label": "Top Crime Group",
            "value": top_crime_group,
            "meta": "Leading category",
            "badge": format_number(
                crime_count
            )
        },
        {
            "label": "Top Outcome",
            "value": top_outcome,
            "meta": "Leading outcome",
            "badge": format_number(
                outcome_count
            )
        },
        {
            "label": "Top Location Group",
            "value": top_location_group,
            "meta": "Leading location",
            "badge": format_number(
                location_count
            )
        }
    ]

    show_compact_overview_strip(
        overview_items
    )

    show_insight(
        f"{top_crime_group} is the most frequent crime group "
        f"with {format_number(crime_count)} incidents. "
        f"{top_outcome} is the leading outcome, while "
        f"{top_location_group} is the leading location group."
    )

    return {
        "top_crime_group": top_crime_group,
        "crime_count": crime_count,
        "top_outcome": top_outcome,
        "outcome_count": outcome_count,
        "top_location_group": top_location_group,
        "location_count": location_count
    }


def show_primary_charts(
    data,
    summary_values
):
    """
    Display the primary Command Center charts.

    Charts are rendered in one row and their insight bars are rendered
    in a separate matching row. This guarantees horizontal alignment.
    """
    monthly_chart = create_yearly_monthly_wave_chart(
        data
    )

    crime_chart = create_horizontal_bar_chart(
        data=data,
        group_column="crime_group",
        title="Incident Volume by Crime Group",
        count_label="Incident Count",
        chart_type="incident_soft"
    )

    monthly_chart = standardize_chart_height(
        monthly_chart
    )

    crime_chart = standardize_chart_height(
        crime_chart
    )

    chart_left, chart_right = st.columns(
        2,
        gap="small"
    )

    with chart_left:
        st.plotly_chart(
            monthly_chart,
            use_container_width=True,
            key="command_yearly_monthly_wave_chart",
            config=get_chart_config()
        )

    with chart_right:
        st.plotly_chart(
            crime_chart,
            use_container_width=True,
            key="command_crime_group_chart",
            config=get_chart_config()
        )

    insight_left, insight_right = st.columns(
        2,
        gap="small"
    )

    with insight_left:
        show_insight(
            "Peak month by selected year — "
            f"{get_yearly_peak_summary(data)}."
        )

    with insight_right:
        show_insight(
            f"{summary_values['top_crime_group']} contributes "
            "the largest share of selected incident volume."
        )

    outcome_chart = create_status_bar_chart(
        data=data,
        group_column="disposition_group",
        title="Case Outcomes by Volume",
        count_label="Incident Count"
    )

    location_chart = create_horizontal_bar_chart(
        data=data,
        group_column="location_group",
        title="Incident Volume by Location Group",
        count_label="Incident Count",
        chart_type="incident_soft"
    )

    outcome_chart = standardize_chart_height(
        outcome_chart
    )

    location_chart = standardize_chart_height(
        location_chart
    )

    chart_left, chart_right = st.columns(
        2,
        gap="small"
    )

    with chart_left:
        st.plotly_chart(
            outcome_chart,
            use_container_width=True,
            key="command_outcome_group_chart",
            config=get_chart_config()
        )

    with chart_right:
        st.plotly_chart(
            location_chart,
            use_container_width=True,
            key="command_location_group_chart",
            config=get_chart_config()
        )

    insight_left, insight_right = st.columns(
        2,
        gap="small"
    )

    with insight_left:
        show_insight(
            f"{summary_values['top_outcome']} is the leading "
            "outcome category, appearing in "
            f"{format_number(summary_values['outcome_count'])} "
            "selected records."
        )

    with insight_right:
        show_insight(
            f"{summary_values['top_location_group']} is the "
            "highest-volume location group with "
            f"{format_number(summary_values['location_count'])} "
            "incidents."
        )


def show_delay_chart(data):
    """
    Display the reporting-delay distribution chart.
    """
    st.plotly_chart(
        create_delay_bucket_chart(
            data
        ),
        use_container_width=True,
        key="command_delay_bucket_chart",
        config=get_chart_config()
    )

    (
        top_delay_bucket,
        delay_bucket_count
    ) = get_top_value(
        data,
        "delay_bucket"
    )

    show_insight(
        f"The most common reporting delay bucket is "
        f"{top_delay_bucket}, with "
        f"{format_number(delay_bucket_count)} records."
    )


def show_executive_overview(data):
    """
    Display the complete Command Center section.
    """
    show_section_banner(
        eyebrow="",
        title="Operational Snapshot",
        description=(
            "Monitor incident volume, arrest involvement, case outcomes, "
            "reporting delay, and leading categories for the current "
            "filtered selection."
        )
    )

    summary_values = show_operational_summary(
        data
    )

    st.divider()

    show_primary_charts(
        data,
        summary_values
    )

    show_delay_chart(
        data
    )