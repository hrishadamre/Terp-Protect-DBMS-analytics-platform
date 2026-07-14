"""
incident_trends.py

Purpose:
Display the temporal activity profile for the Terp Protect dashboard.

Responsibilities:
- Summarize peak months, weekdays, hours, and academic periods
- Display monthly incident trends
- Show combined weekday-by-hour activity patterns
- Normalize academic-period comparisons by duration
- Keep the section compact and operationally useful
"""

import calendar

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.charts import (
    create_monthly_line_chart,
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


WEEKDAY_ORDER = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]


ACADEMIC_PERIOD_ORDER = [
    "Fall Semester",
    "Spring Semester",
    "Summer Break",
    "Winter Break"
]


MONTHLY_CHART_HEIGHT = 420
HEATMAP_HEIGHT = 500
ACADEMIC_PERIOD_CHART_HEIGHT = 390


def format_hour(hour):
    """
    Convert a numeric hour into a readable 12-hour label.
    """
    numeric_hour = pd.to_numeric(
        hour,
        errors="coerce"
    )

    if pd.isna(numeric_hour):
        return str(hour)

    numeric_hour = int(
        numeric_hour
    ) % 24

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
        data is None
        or data.empty
        or "occurred_is_weekend" not in data.columns
    ):
        return 0.0

    weekend_values = pd.to_numeric(
        data["occurred_is_weekend"],
        errors="coerce"
    ).fillna(0)

    return float(
        weekend_values.mean()
        * 100
    )


def prepare_time_data(data):
    """
    Return a cleaned dataframe containing valid weekday and hour values.
    """
    required_columns = {
        "occurred_weekday",
        "occurred_hour"
    }

    if (
        data is None
        or data.empty
        or not required_columns.issubset(
            data.columns
        )
    ):
        return pd.DataFrame()

    time_data = data[
        [
            "occurred_weekday",
            "occurred_hour"
        ]
    ].copy()

    time_data["occurred_weekday"] = (
        time_data["occurred_weekday"]
        .astype(str)
        .str.strip()
    )

    time_data["occurred_hour"] = pd.to_numeric(
        time_data["occurred_hour"],
        errors="coerce"
    )

    time_data = time_data.dropna(
        subset=[
            "occurred_weekday",
            "occurred_hour"
        ]
    )

    time_data = time_data[
        time_data["occurred_weekday"].isin(
            WEEKDAY_ORDER
        )
    ]

    time_data = time_data[
        time_data["occurred_hour"].between(
            0,
            23
        )
    ]

    time_data["occurred_hour"] = (
        time_data["occurred_hour"]
        .astype(int)
    )

    return time_data


def create_weekday_hour_heatmap(data):
    """
    Create a weekday-by-hour heatmap.

    Rows represent weekdays.
    Columns represent hours of day.
    Cell color represents incident count.
    """
    time_data = prepare_time_data(
        data
    )

    complete_index = pd.MultiIndex.from_product(
        [
            WEEKDAY_ORDER,
            range(24)
        ],
        names=[
            "occurred_weekday",
            "occurred_hour"
        ]
    )

    if time_data.empty:
        heatmap_data = pd.DataFrame(
            0,
            index=WEEKDAY_ORDER,
            columns=range(24)
        )
    else:
        heatmap_data = (
            time_data
            .groupby(
                [
                    "occurred_weekday",
                    "occurred_hour"
                ]
            )
            .size()
            .reindex(
                complete_index,
                fill_value=0
            )
            .rename(
                "incident_count"
            )
            .reset_index()
            .pivot(
                index="occurred_weekday",
                columns="occurred_hour",
                values="incident_count"
            )
            .reindex(
                WEEKDAY_ORDER
            )
        )

    hour_labels = [
        format_hour(hour)
        for hour in range(24)
    ]

    figure = go.Figure(
        data=go.Heatmap(
            z=heatmap_data.values,
            x=hour_labels,
            y=WEEKDAY_ORDER,
            colorscale=[
                [0.00, "#101827"],
                [0.15, "#1E3A4A"],
                [0.35, "#2F6F8A"],
                [0.55, "#59A9C8"],
                [0.75, "#8ED8F3"],
                [1.00, "#DDF3FB"]
            ],
            colorbar={
                "title": {
                    "text": "Incidents",
                    "font": {
                        "color": "#F8FAFC"
                    }
                },
                "tickfont": {
                    "color": "#CBD5E1"
                }
            },
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Hour: %{x}<br>"
                "Incidents: %{z:,}"
                "<extra></extra>"
            )
        )
    )

    figure.update_layout(
        title={
            "text": "Incident Activity by Weekday and Hour",
            "x": 0,
            "xanchor": "left",
            "font": {
                "size": 17,
                "color": "#F8FAFC"
            }
        },
        height=HEATMAP_HEIGHT,
        margin={
            "l": 95,
            "r": 70,
            "t": 70,
            "b": 75
        },
        paper_bgcolor="#0B111C",
        plot_bgcolor="#0B111C",
        font={
            "color": "#F8FAFC"
        },
        xaxis={
            "title": {
                "text": "Hour of Day"
            },
            "tickmode": "array",
            "tickvals": hour_labels,
            "ticktext": [
                label
                if hour % 3 == 0
                else ""
                for hour, label in enumerate(
                    hour_labels
                )
            ],
            "tickfont": {
                "size": 11,
                "color": "#CBD5E1"
            },
            "showgrid": False,
            "side": "bottom"
        },
        yaxis={
            "title": {
                "text": "Weekday"
            },
            "tickfont": {
                "size": 11,
                "color": "#CBD5E1"
            },
            "showgrid": False,
            "autorange": "reversed"
        }
    )

    return figure


def get_date_column(data):
    """
    Return the best available incident date column.
    """
    preferred_columns = [
        "occurred_date",
        "occurred_datetime",
        "full_date"
    ]

    for column in preferred_columns:
        if column in data.columns:
            return column

    return None


def prepare_academic_period_rates(data):
    """
    Calculate incident counts and incidents per week by academic period.

    The calculation uses the actual date span represented in each
    selected academic period rather than comparing only raw totals.
    """
    required_column = "occurred_semester_period"

    if (
        data is None
        or data.empty
        or required_column not in data.columns
    ):
        return pd.DataFrame()

    date_column = get_date_column(
        data
    )

    working_data = data.copy()

    working_data[required_column] = (
        working_data[required_column]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
    )

    if date_column is None:
        summary = (
            working_data
            .groupby(
                required_column
            )
            .size()
            .reset_index(
                name="incident_count"
            )
        )

        summary["active_days"] = pd.NA
        summary["active_weeks"] = pd.NA
        summary["incidents_per_week"] = pd.NA

        return summary

    working_data["_analysis_date"] = pd.to_datetime(
        working_data[date_column],
        errors="coerce"
    ).dt.normalize()

    working_data = working_data.dropna(
        subset=[
            "_analysis_date"
        ]
    )

    if working_data.empty:
        return pd.DataFrame()

    period_counts = (
        working_data
        .groupby(
            required_column
        )
        .size()
        .rename(
            "incident_count"
        )
    )

    period_days = (
        working_data
        .groupby(
            required_column
        )["_analysis_date"]
        .nunique()
        .rename(
            "active_days"
        )
    )

    summary = pd.concat(
        [
            period_counts,
            period_days
        ],
        axis=1
    ).reset_index()

    summary["active_weeks"] = (
        summary["active_days"]
        / 7
    )

    summary["incidents_per_week"] = (
        summary["incident_count"]
        / summary["active_weeks"]
    )

    summary["period_order"] = summary[
        required_column
    ].map(
        {
            period: index
            for index, period in enumerate(
                ACADEMIC_PERIOD_ORDER
            )
        }
    ).fillna(
        len(
            ACADEMIC_PERIOD_ORDER
        )
    )

    summary = summary.sort_values(
        [
            "period_order",
            required_column
        ]
    )

    return summary


def create_academic_period_rate_chart(data):
    """
    Create an academic-period chart using incidents per active week.

    Raw incident counts and active-day counts remain visible in hover.
    """
    summary = prepare_academic_period_rates(
        data
    )

    figure = go.Figure()

    if summary.empty:
        figure.add_annotation(
            text="Academic-period data is unavailable.",
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
            title="Incident Rate by Academic Period",
            height=ACADEMIC_PERIOD_CHART_HEIGHT,
            paper_bgcolor="#0B111C",
            plot_bgcolor="#0B111C"
        )

        return figure

    usable_rate_data = summary[
        summary["incidents_per_week"].notna()
    ].copy()

    if usable_rate_data.empty:
        figure.add_annotation(
            text=(
                "A normalized rate requires a valid incident date column."
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
            title="Incident Rate by Academic Period",
            height=ACADEMIC_PERIOD_CHART_HEIGHT,
            paper_bgcolor="#0B111C",
            plot_bgcolor="#0B111C"
        )

        return figure

    figure.add_trace(
        go.Bar(
            x=usable_rate_data[
                "occurred_semester_period"
            ],
            y=usable_rate_data[
                "incidents_per_week"
            ],
            marker={
                "color": "#BEEBFA",
                "line": {
                    "color": "#8ED8F3",
                    "width": 1
                }
            },
            customdata=usable_rate_data[
                [
                    "incident_count",
                    "active_days",
                    "active_weeks"
                ]
            ],
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Incidents per active week: %{y:.1f}<br>"
                "Raw incidents: %{customdata[0]:,}<br>"
                "Active dates represented: %{customdata[1]:,}<br>"
                "Equivalent active weeks: %{customdata[2]:.1f}"
                "<extra></extra>"
            )
        )
    )

    figure.update_layout(
        title={
            "text": "Incident Rate by Academic Period",
            "x": 0,
            "xanchor": "left",
            "font": {
                "size": 17,
                "color": "#F8FAFC"
            }
        },
        height=ACADEMIC_PERIOD_CHART_HEIGHT,
        margin={
            "l": 65,
            "r": 24,
            "t": 68,
            "b": 65
        },
        paper_bgcolor="#0B111C",
        plot_bgcolor="#0B111C",
        showlegend=False,
        font={
            "color": "#F8FAFC"
        },
        xaxis={
            "title": {
                "text": "Academic Period"
            },
            "categoryorder": "array",
            "categoryarray": ACADEMIC_PERIOD_ORDER,
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
                "text": "Incidents per Active Week"
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


def get_peak_weekday_hour(data):
    """
    Return the busiest weekday-hour combination.
    """
    time_data = prepare_time_data(
        data
    )

    if time_data.empty:
        return {
            "weekday": "N/A",
            "hour": "N/A",
            "count": 0
        }

    grouped_data = (
        time_data
        .groupby(
            [
                "occurred_weekday",
                "occurred_hour"
            ]
        )
        .size()
        .reset_index(
            name="incident_count"
        )
        .sort_values(
            "incident_count",
            ascending=False
        )
    )

    top_row = grouped_data.iloc[0]

    return {
        "weekday": top_row[
            "occurred_weekday"
        ],
        "hour": int(
            top_row[
                "occurred_hour"
            ]
        ),
        "count": int(
            top_row[
                "incident_count"
            ]
        )
    }


def get_top_academic_period_rate(data):
    """
    Return the academic period with the highest incident rate.
    """
    summary = prepare_academic_period_rates(
        data
    )

    valid_summary = summary[
        summary["incidents_per_week"].notna()
    ].copy()

    if valid_summary.empty:
        return {
            "period": "N/A",
            "rate": pd.NA,
            "incident_count": 0
        }

    top_row = valid_summary.sort_values(
        "incidents_per_week",
        ascending=False
    ).iloc[0]

    return {
        "period": top_row[
            "occurred_semester_period"
        ],
        "rate": float(
            top_row[
                "incidents_per_week"
            ]
        ),
        "incident_count": int(
            top_row[
                "incident_count"
            ]
        )
    }


def show_temporal_summary(data):
    """
    Display the compact temporal KPI strip.
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

    weekend_percentage = calculate_weekend_percentage(
        data
    )

    top_period_rate = get_top_academic_period_rate(
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
            "value": format_hour(
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
            "label": "Highest Period Rate",
            "value": top_period_rate[
                "period"
            ],
            "meta": (
                f"{top_period_rate['rate']:.1f} incidents/week"
                if pd.notna(
                    top_period_rate[
                        "rate"
                    ]
                )
                else "Rate unavailable"
            ),
            "badge": format_number(
                top_period_rate[
                    "incident_count"
                ]
            )
        }
    ]

    show_compact_overview_strip(
        overview_items
    )

    peak_combination = get_peak_weekday_hour(
        data
    )

    if peak_combination["weekday"] == "N/A":
        show_insight(
            f"Activity peaks in {peak_month}, with "
            f"{peak_weekday} as the highest-volume weekday."
        )
    else:
        show_insight(
            f"Activity peaks in {peak_month}. The busiest weekday-hour "
            f"combination is {peak_combination['weekday']} at "
            f"{format_hour(peak_combination['hour'])}, with "
            f"{format_number(peak_combination['count'])} incidents."
        )

    return {
        "peak_month": peak_month,
        "peak_month_count": peak_month_count,
        "peak_weekday": peak_weekday,
        "peak_weekday_count": peak_weekday_count,
        "peak_hour": peak_hour,
        "peak_hour_count": peak_hour_count,
        "top_period_rate": top_period_rate,
        "peak_combination": peak_combination
    }


def show_monthly_chart(
    data,
    summary
):
    """
    Display the monthly trend chart.
    """
    monthly_chart = create_monthly_line_chart(
        data
    )

    monthly_chart.update_layout(
        height=MONTHLY_CHART_HEIGHT,
        margin={
            "l": 58,
            "r": 24,
            "t": 68,
            "b": 58
        }
    )

    st.plotly_chart(
        monthly_chart,
        use_container_width=True,
        key="time_monthly_line_chart",
        config=get_chart_config()
    )

    show_insight(
        f"{summary['peak_month']} has the highest monthly incident "
        f"volume with "
        f"{format_number(summary['peak_month_count'])} incidents."
    )


def show_weekday_hour_heatmap(
    data,
    summary
):
    """
    Display the combined weekday-hour heatmap.
    """
    heatmap = create_weekday_hour_heatmap(
        data
    )

    st.plotly_chart(
        heatmap,
        use_container_width=True,
        key="time_weekday_hour_heatmap",
        config=get_chart_config()
    )

    peak_combination = summary[
        "peak_combination"
    ]

    if peak_combination["weekday"] == "N/A":
        show_insight(
            "Weekday and hourly activity data is unavailable for the "
            "current filtered selection."
        )
    else:
        show_insight(
            f"The busiest weekday-hour combination is "
            f"{peak_combination['weekday']} at "
            f"{format_hour(peak_combination['hour'])}, with "
            f"{format_number(peak_combination['count'])} incidents."
        )


def show_academic_period_chart(
    data,
    summary
):
    """
    Display normalized academic-period incident rates.
    """
    academic_chart = create_academic_period_rate_chart(
        data
    )

    st.plotly_chart(
        academic_chart,
        use_container_width=True,
        key="time_academic_period_rate_chart",
        config=get_chart_config()
    )

    top_period_rate = summary[
        "top_period_rate"
    ]

    if pd.isna(
        top_period_rate[
            "rate"
        ]
    ):
        show_insight(
            "Academic-period rates could not be calculated because "
            "a valid incident date field was unavailable."
        )
    else:
        show_insight(
            f"{top_period_rate['period']} has the highest normalized "
            f"incident rate at "
            f"{top_period_rate['rate']:.1f} incidents per active week. "
            f"The period contains "
            f"{format_number(top_period_rate['incident_count'])} "
            f"selected incidents."
        )


def show_incident_trends(data):
    """
    Display the complete temporal activity section.
    """
    show_section_banner(
        eyebrow="Time Intelligence",
        title="Temporal Activity Profile",
        description=(
            "Identify seasonal patterns, weekday-hour hotspots, and "
            "normalized incident rates across academic periods."
        )
    )

    summary = show_temporal_summary(
        data
    )

    st.divider()

    chart_left, chart_right = st.columns(
        [
            0.9,
            1.1
        ],
        gap="small"
    )

    with chart_left:
        show_monthly_chart(
            data,
            summary
        )

    with chart_right:
        show_academic_period_chart(
            data,
            summary
        )

    show_weekday_hour_heatmap(
        data,
        summary
    )