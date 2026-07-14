"""
incident_trends.py

Purpose:
Display the temporal activity profile for the Terp Protect dashboard.

Responsibilities:
- Summarize peak months, weekdays, hours, and academic periods
- Display seasonal incident patterns by calendar month
- Show weekday-by-hour incident activity
- Compare academic periods using calendar-time exposure
- Standardize inconsistent academic-period labels
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.charts import get_chart_config
from components.layout import (
    show_compact_overview_strip,
    show_info_hint,
    show_insight,
    show_section_banner
)
from components.metrics import (
    format_number,
    format_percentage
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


MONTH_NUMBER_TO_NAME = {
    month_number: month_name
    for month_number, month_name in enumerate(
        MONTH_ORDER,
        start=1
    )
}


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
ACADEMIC_PERIOD_CHART_HEIGHT = 400


ACADEMIC_PERIOD_ALIASES = {
    "fall": "Fall Semester",
    "fall semester": "Fall Semester",
    "autumn": "Fall Semester",
    "autumn semester": "Fall Semester",

    "spring": "Spring Semester",
    "spring semester": "Spring Semester",

    "summer": "Summer Break",
    "summer break": "Summer Break",
    "summer semester": "Summer Break",
    "summer session": "Summer Break",

    "winter": "Winter Break",
    "winter break": "Winter Break",
    "winter session": "Winter Break",

    "unknown": "Unknown",
    "": "Unknown"
}


def format_hour(hour):
    """
    Convert a numeric hour into a readable 12-hour label.
    """
    numeric_hour = pd.to_numeric(
        hour,
        errors="coerce"
    )

    if pd.isna(numeric_hour):
        return str(
            hour
        )

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


def safe_distinct_incident_count(data):
    """
    Return the number of distinct selected incidents.
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


def count_incidents(data):
    """
    Count incidents using distinct incident IDs when available.
    """
    return safe_distinct_incident_count(
        data
    )


def clean_category_value(value):
    """
    Return a cleaned category value.
    """
    if pd.isna(value):
        return "Unknown"

    cleaned_value = str(
        value
    ).strip()

    if not cleaned_value:
        return "Unknown"

    return cleaned_value


def normalize_academic_period(value):
    """
    Standardize source academic-period labels.
    """
    cleaned_value = clean_category_value(
        value
    )

    normalized_key = cleaned_value.lower()

    return ACADEMIC_PERIOD_ALIASES.get(
        normalized_key,
        cleaned_value
    )


def academic_period_from_month(month):
    """
    Assign an academic period using the incident occurrence month.

    January:
        Winter Break

    February through May:
        Spring Semester

    June through August:
        Summer Break

    September through December:
        Fall Semester
    """
    numeric_month = pd.to_numeric(
        month,
        errors="coerce"
    )

    if pd.isna(numeric_month):
        return "Unknown"

    numeric_month = int(
        numeric_month
    )

    if numeric_month == 1:
        return "Winter Break"

    if numeric_month in [
        2,
        3,
        4,
        5
    ]:
        return "Spring Semester"

    if numeric_month in [
        6,
        7,
        8
    ]:
        return "Summer Break"

    if numeric_month in [
        9,
        10,
        11,
        12
    ]:
        return "Fall Semester"

    return "Unknown"


def get_date_column(data):
    """
    Return the best available incident occurrence date column.
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


def prepare_occurrence_dates(data):
    """
    Return a copy of the data with normalized occurrence dates.
    """
    if data is None or data.empty:
        return pd.DataFrame()

    date_column = get_date_column(
        data
    )

    if date_column is None:
        return pd.DataFrame()

    working_data = data.copy()

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

    working_data["_occurred_year"] = (
        working_data["_analysis_date"]
        .dt.year
        .astype(int)
    )

    working_data["_occurred_month"] = (
        working_data["_analysis_date"]
        .dt.month
        .astype(int)
    )

    working_data["_academic_period"] = (
        working_data["_occurred_month"]
        .apply(
            academic_period_from_month
        )
    )

    return working_data


def calculate_weekend_percentage(data):
    """
    Calculate the percentage of incidents occurring on weekends.
    """
    total_incidents = count_incidents(
        data
    )

    if total_incidents <= 0:
        return 0.0

    if "occurred_is_weekend" in data.columns:
        working_data = data.copy()

        weekend_values = pd.to_numeric(
            working_data["occurred_is_weekend"],
            errors="coerce"
        ).fillna(0)

        if "incident_id" in working_data.columns:
            weekend_data = working_data[
                weekend_values == 1
            ]

            weekend_count = (
                weekend_data["incident_id"]
                .dropna()
                .nunique()
            )

        else:
            weekend_count = int(
                (
                    weekend_values == 1
                ).sum()
            )

        return float(
            weekend_count
            / total_incidents
            * 100
        )

    if "occurred_weekday" in data.columns:
        weekend_data = data[
            data["occurred_weekday"].isin(
                [
                    "Saturday",
                    "Sunday"
                ]
            )
        ]

        weekend_count = count_incidents(
            weekend_data
        )

        return float(
            weekend_count
            / total_incidents
            * 100
        )

    return 0.0


def prepare_monthly_seasonality_data(data):
    """
    Prepare incident volume by calendar month.

    This combines the same calendar month across all selected years.
    """
    if data is None or data.empty:
        return pd.DataFrame()

    working_data = data.copy()

    if "occurred_month_name" in working_data.columns:
        working_data["_month_name"] = (
            working_data["occurred_month_name"]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
        )

    else:
        dated_data = prepare_occurrence_dates(
            working_data
        )

        if dated_data.empty:
            return pd.DataFrame()

        working_data = dated_data

        working_data["_month_name"] = (
            working_data["_occurred_month"]
            .map(
                MONTH_NUMBER_TO_NAME
            )
        )

    working_data = working_data[
        working_data["_month_name"].isin(
            MONTH_ORDER
        )
    ].copy()

    if working_data.empty:
        return pd.DataFrame()

    if "incident_id" in working_data.columns:
        summary = (
            working_data
            .groupby(
                "_month_name"
            )["incident_id"]
            .nunique()
            .reindex(
                MONTH_ORDER,
                fill_value=0
            )
            .rename(
                "incident_count"
            )
            .reset_index()
        )

    else:
        summary = (
            working_data
            .groupby(
                "_month_name"
            )
            .size()
            .reindex(
                MONTH_ORDER,
                fill_value=0
            )
            .rename(
                "incident_count"
            )
            .reset_index()
        )

    summary = summary.rename(
        columns={
            "_month_name": "month_name"
        }
    )

    return summary


def create_monthly_seasonality_chart(data):
    """
    Create the seasonal incident pattern by calendar month.
    """
    monthly_data = prepare_monthly_seasonality_data(
        data
    )

    figure = go.Figure()

    if monthly_data.empty:
        figure.add_annotation(
            text="Monthly incident data is unavailable.",
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
            title="Seasonal Incident Pattern by Calendar Month",
            height=MONTHLY_CHART_HEIGHT,
            paper_bgcolor="#0B111C",
            plot_bgcolor="#0B111C"
        )

        return figure

    figure.add_trace(
        go.Scatter(
            x=monthly_data[
                "month_name"
            ],
            y=monthly_data[
                "incident_count"
            ],
            mode="lines+markers",
            line={
                "color": "#8ED8F3",
                "width": 2.5,
                "shape": "spline"
            },
            marker={
                "size": 7,
                "color": "#BEEBFA",
                "line": {
                    "color": "#4EA8C8",
                    "width": 1
                }
            },
            fill="tozeroy",
            fillcolor="rgba(142, 216, 243, 0.18)",
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Selected incidents: %{y:,}<br>"
                "The same month is combined across selected years."
                "<extra></extra>"
            )
        )
    )

    figure.update_layout(
        title={
            "text": "Seasonal Incident Pattern by Calendar Month",
            "x": 0,
            "xanchor": "left",
            "font": {
                "size": 17,
                "color": "#F8FAFC"
            }
        },
        height=MONTHLY_CHART_HEIGHT,
        margin={
            "l": 58,
            "r": 24,
            "t": 68,
            "b": 70
        },
        paper_bgcolor="#0B111C",
        plot_bgcolor="#0B111C",
        showlegend=False,
        font={
            "color": "#F8FAFC"
        },
        xaxis={
            "title": {
                "text": "Calendar Month"
            },
            "categoryorder": "array",
            "categoryarray": MONTH_ORDER,
            "tickangle": -35,
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


def prepare_time_data(data):
    """
    Return valid weekday and hour values for the heatmap.
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

    selected_columns = [
        "occurred_weekday",
        "occurred_hour"
    ]

    if "incident_id" in data.columns:
        selected_columns.append(
            "incident_id"
        )

    time_data = data[
        selected_columns
    ].copy()

    time_data["occurred_weekday"] = (
        time_data["occurred_weekday"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    time_data["occurred_hour"] = pd.to_numeric(
        time_data["occurred_hour"],
        errors="coerce"
    )

    time_data = time_data.dropna(
        subset=[
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


def prepare_weekday_hour_counts(data):
    """
    Prepare weekday-hour incident counts.
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
        return pd.DataFrame(
            0,
            index=WEEKDAY_ORDER,
            columns=range(24)
        )

    if "incident_id" in time_data.columns:
        grouped_data = (
            time_data
            .groupby(
                [
                    "occurred_weekday",
                    "occurred_hour"
                ]
            )["incident_id"]
            .nunique()
        )

    else:
        grouped_data = (
            time_data
            .groupby(
                [
                    "occurred_weekday",
                    "occurred_hour"
                ]
            )
            .size()
        )

    heatmap_data = (
        grouped_data
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

    return heatmap_data


def create_weekday_hour_heatmap(data):
    """
    Create a weekday-by-hour heatmap.

    Light shades represent lower incident counts.
    Dark shades represent higher incident counts.
    """
    heatmap_data = prepare_weekday_hour_counts(
        data
    )

    hour_labels = [
        format_hour(
            hour
        )
        for hour in range(
            24
        )
    ]

    figure = go.Figure(
        data=go.Heatmap(
            z=heatmap_data.values,
            x=hour_labels,
            y=WEEKDAY_ORDER,
            colorscale=[
                [
                    0.00,
                    "#E5F6FE"
                ],
                [
                    0.15,
                    "#C8ECFA"
                ],
                [
                    0.35,
                    "#8ED8F3"
                ],
                [
                    0.55,
                    "#4EA8C8"
                ],
                [
                    0.75,
                    "#2F6F8A"
                ],
                [
                    1.00,
                    "#101827"
                ]
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
                },
                "outlinecolor": "#475569",
                "outlinewidth": 1
            },
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Hour: %{x}<br>"
                "Selected incidents: %{z:,}"
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


def academic_period_boundaries(
    year,
    academic_period
):
    """
    Return calendar boundaries for one academic period and year.
    """
    year = int(
        year
    )

    if academic_period == "Winter Break":
        return (
            pd.Timestamp(
                year=year,
                month=1,
                day=1
            ),
            pd.Timestamp(
                year=year,
                month=1,
                day=31
            )
        )

    if academic_period == "Spring Semester":
        return (
            pd.Timestamp(
                year=year,
                month=2,
                day=1
            ),
            pd.Timestamp(
                year=year,
                month=5,
                day=31
            )
        )

    if academic_period == "Summer Break":
        return (
            pd.Timestamp(
                year=year,
                month=6,
                day=1
            ),
            pd.Timestamp(
                year=year,
                month=8,
                day=31
            )
        )

    if academic_period == "Fall Semester":
        return (
            pd.Timestamp(
                year=year,
                month=9,
                day=1
            ),
            pd.Timestamp(
                year=year,
                month=12,
                day=31
            )
        )

    return (
        pd.NaT,
        pd.NaT
    )


def calculate_period_exposure_days(
    dated_data,
    year,
    academic_period
):
    """
    Calculate calendar exposure days for one year-period combination.
    """
    if dated_data.empty:
        return 0

    period_start, period_end = academic_period_boundaries(
        year,
        academic_period
    )

    if pd.isna(period_start) or pd.isna(period_end):
        return 0

    selected_start = dated_data[
        "_analysis_date"
    ].min()

    selected_end = dated_data[
        "_analysis_date"
    ].max()

    exposure_start = max(
        period_start,
        selected_start
    )

    exposure_end = min(
        period_end,
        selected_end
    )

    if exposure_end < exposure_start:
        return 0

    return int(
        (
            exposure_end
            - exposure_start
        ).days
        + 1
    )


def prepare_academic_period_rates(data):
    """
    Calculate incidents per calendar week by academic period.
    """
    dated_data = prepare_occurrence_dates(
        data
    )

    if dated_data.empty:
        return pd.DataFrame()

    group_columns = [
        "_occurred_year",
        "_academic_period"
    ]

    if "incident_id" in dated_data.columns:
        yearly_period_counts = (
            dated_data
            .groupby(
                group_columns
            )["incident_id"]
            .nunique()
            .reset_index(
                name="incident_count"
            )
        )

    else:
        yearly_period_counts = (
            dated_data
            .groupby(
                group_columns
            )
            .size()
            .reset_index(
                name="incident_count"
            )
        )

    yearly_period_counts["calendar_days"] = (
        yearly_period_counts.apply(
            lambda row: calculate_period_exposure_days(
                dated_data=dated_data,
                year=row[
                    "_occurred_year"
                ],
                academic_period=row[
                    "_academic_period"
                ]
            ),
            axis=1
        )
    )

    yearly_period_counts = yearly_period_counts[
        yearly_period_counts[
            "_academic_period"
        ].isin(
            ACADEMIC_PERIOD_ORDER
        )
    ].copy()

    yearly_period_counts = yearly_period_counts[
        yearly_period_counts[
            "calendar_days"
        ] > 0
    ].copy()

    if yearly_period_counts.empty:
        return pd.DataFrame()

    summary = (
        yearly_period_counts
        .groupby(
            "_academic_period",
            as_index=False
        )
        .agg(
            incident_count=(
                "incident_count",
                "sum"
            ),
            calendar_days=(
                "calendar_days",
                "sum"
            ),
            represented_years=(
                "_occurred_year",
                "nunique"
            )
        )
    )

    summary["calendar_weeks"] = (
        summary["calendar_days"]
        / 7
    )

    summary["incidents_per_week"] = (
        summary["incident_count"]
        / summary["calendar_weeks"]
    )

    summary = summary.rename(
        columns={
            "_academic_period": "academic_period"
        }
    )

    complete_periods = pd.DataFrame(
        {
            "academic_period": ACADEMIC_PERIOD_ORDER
        }
    )

    summary = complete_periods.merge(
        summary,
        on="academic_period",
        how="left"
    )

    numeric_columns = [
        "incident_count",
        "calendar_days",
        "represented_years",
        "calendar_weeks",
        "incidents_per_week"
    ]

    for column in numeric_columns:
        summary[column] = pd.to_numeric(
            summary[column],
            errors="coerce"
        )

    summary["period_order"] = (
        summary["academic_period"]
        .map(
            {
                period: index
                for index, period in enumerate(
                    ACADEMIC_PERIOD_ORDER
                )
            }
        )
    )

    return summary.sort_values(
        "period_order"
    )


def create_academic_period_rate_chart(data):
    """
    Create an academic-period incident-rate chart.
    """
    summary = prepare_academic_period_rates(
        data
    )

    figure = go.Figure()

    usable_data = summary[
        summary["incidents_per_week"].notna()
    ].copy()

    if usable_data.empty:
        figure.add_annotation(
            text="Academic-period rate data is unavailable.",
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
            x=usable_data[
                "academic_period"
            ],
            y=usable_data[
                "incidents_per_week"
            ],
            marker={
                "color": "#BEEBFA",
                "line": {
                    "color": "#8ED8F3",
                    "width": 1
                }
            },
            customdata=usable_data[
                [
                    "incident_count",
                    "calendar_days",
                    "calendar_weeks",
                    "represented_years"
                ]
            ],
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Incidents per calendar week: %{y:.1f}<br>"
                "Selected incidents: %{customdata[0]:,}<br>"
                "Calendar days represented: %{customdata[1]:,.0f}<br>"
                "Calendar weeks represented: %{customdata[2]:.1f}<br>"
                "Occurrence years represented: %{customdata[3]:,.0f}"
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
            "b": 70
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
                "size": 10,
                "color": "#CBD5E1"
            },
            "showgrid": False,
            "showline": True,
            "linecolor": "#334155"
        },
        yaxis={
            "title": {
                "text": "Incidents per Calendar Week"
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


def get_peak_month(data):
    """
    Return the highest-volume calendar month.
    """
    monthly_data = prepare_monthly_seasonality_data(
        data
    )

    if monthly_data.empty:
        return {
            "month": "N/A",
            "count": 0
        }

    top_row = monthly_data.sort_values(
        "incident_count",
        ascending=False
    ).iloc[0]

    return {
        "month": top_row[
            "month_name"
        ],
        "count": int(
            top_row[
                "incident_count"
            ]
        )
    }


def get_peak_weekday(data):
    """
    Return the highest-volume weekday.
    """
    if (
        data is None
        or data.empty
        or "occurred_weekday" not in data.columns
    ):
        return {
            "weekday": "N/A",
            "count": 0
        }

    working_data = data[
        data["occurred_weekday"].isin(
            WEEKDAY_ORDER
        )
    ].copy()

    if working_data.empty:
        return {
            "weekday": "N/A",
            "count": 0
        }

    if "incident_id" in working_data.columns:
        summary = (
            working_data
            .groupby(
                "occurred_weekday"
            )["incident_id"]
            .nunique()
            .sort_values(
                ascending=False
            )
        )

    else:
        summary = (
            working_data[
                "occurred_weekday"
            ]
            .value_counts()
        )

    return {
        "weekday": summary.index[0],
        "count": int(
            summary.iloc[0]
        )
    }


def get_peak_hour(data):
    """
    Return the highest-volume occurrence hour.
    """
    if (
        data is None
        or data.empty
        or "occurred_hour" not in data.columns
    ):
        return {
            "hour": "N/A",
            "count": 0
        }

    working_data = data.copy()

    working_data["_hour"] = pd.to_numeric(
        working_data["occurred_hour"],
        errors="coerce"
    )

    working_data = working_data[
        working_data["_hour"].between(
            0,
            23
        )
    ].copy()

    if working_data.empty:
        return {
            "hour": "N/A",
            "count": 0
        }

    working_data["_hour"] = (
        working_data["_hour"]
        .astype(int)
    )

    if "incident_id" in working_data.columns:
        summary = (
            working_data
            .groupby(
                "_hour"
            )["incident_id"]
            .nunique()
            .sort_values(
                ascending=False
            )
        )

    else:
        summary = (
            working_data[
                "_hour"
            ]
            .value_counts()
        )

    return {
        "hour": int(
            summary.index[0]
        ),
        "count": int(
            summary.iloc[0]
        )
    }


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

    if "incident_id" in time_data.columns:
        grouped_data = (
            time_data
            .groupby(
                [
                    "occurred_weekday",
                    "occurred_hour"
                ]
            )["incident_id"]
            .nunique()
            .reset_index(
                name="incident_count"
            )
        )

    else:
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
        )

    grouped_data = grouped_data.sort_values(
        "incident_count",
        ascending=False
    )

    top_row = grouped_data.iloc[
        0
    ]

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
    Return the academic period with the highest calendar-week rate.
    """
    summary = prepare_academic_period_rates(
        data
    )

    if summary.empty:
        return {
            "period": "N/A",
            "rate": pd.NA,
            "incident_count": 0,
            "calendar_weeks": pd.NA
        }

    valid_summary = summary[
        summary["incidents_per_week"].notna()
    ].copy()

    if valid_summary.empty:
        return {
            "period": "N/A",
            "rate": pd.NA,
            "incident_count": 0,
            "calendar_weeks": pd.NA
        }

    top_row = valid_summary.sort_values(
        "incidents_per_week",
        ascending=False
    ).iloc[
        0
    ]

    return {
        "period": top_row[
            "academic_period"
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
        ),
        "calendar_weeks": float(
            top_row[
                "calendar_weeks"
            ]
        )
    }


def show_temporal_summary(data):
    """
    Display the temporal KPI strip.
    """
    selected_incidents = count_incidents(
        data
    )

    peak_month = get_peak_month(
        data
    )

    peak_weekday = get_peak_weekday(
        data
    )

    peak_hour = get_peak_hour(
        data
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
                selected_incidents
            ),
            "meta": "Distinct filtered incidents",
            "numeric": True,
            "metric_key": "selected_incidents"
        },
        {
            "label": "Peak Month",
            "value": peak_month[
                "month"
            ],
            "meta": "Highest seasonal volume",
            "badge": format_number(
                peak_month[
                    "count"
                ]
            ),
            "help": (
                "The calendar month with the largest incident count "
                "after the same month is combined across selected years."
            )
        },
        {
            "label": "Peak Weekday",
            "value": peak_weekday[
                "weekday"
            ],
            "meta": "Highest weekday volume",
            "badge": format_number(
                peak_weekday[
                    "count"
                ]
            )
        },
        {
            "label": "Peak Hour",
            "value": format_hour(
                peak_hour[
                    "hour"
                ]
            ),
            "meta": "Highest hourly volume",
            "badge": format_number(
                peak_hour[
                    "count"
                ]
            )
        },
        {
            "label": "Weekend Share",
            "value": format_percentage(
                weekend_percentage
            ),
            "meta": "Saturday and Sunday",
            "numeric": True,
            "metric_key": "weekend_share"
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
            ),
            "metric_key": "academic_period_rate"
        }
    ]

    show_compact_overview_strip(
        overview_items
    )

    peak_combination = get_peak_weekday_hour(
        data
    )

    if peak_combination[
        "weekday"
    ] == "N/A":
        show_insight(
            f"Activity is highest in "
            f"{peak_month['month']}, with "
            f"{peak_weekday['weekday']} as the highest-volume weekday."
        )

    else:
        show_insight(
            f"Seasonal activity is highest in "
            f"{peak_month['month']}. The busiest weekday-hour "
            f"combination is {peak_combination['weekday']} at "
            f"{format_hour(peak_combination['hour'])}, with "
            f"{format_number(peak_combination['count'])} incidents."
        )

    return {
        "selected_incidents": selected_incidents,
        "peak_month": peak_month,
        "peak_weekday": peak_weekday,
        "peak_hour": peak_hour,
        "weekend_percentage": weekend_percentage,
        "top_period_rate": top_period_rate,
        "peak_combination": peak_combination
    }


def show_monthly_chart(
    data,
    summary
):
    """
    Display the seasonal monthly chart.
    """
    monthly_chart = create_monthly_seasonality_chart(
        data
    )

    st.plotly_chart(
        monthly_chart,
        use_container_width=True,
        key="time_monthly_seasonality_chart",
        config=get_chart_config()
    )

    show_insight(
        f"{summary['peak_month']['month']} has the highest combined "
        f"calendar-month volume with "
        f"{format_number(summary['peak_month']['count'])} selected "
        f"incidents."
    )

    show_info_hint(
        "Monthly chart definition",
        (
            "This is a seasonal comparison. January values from all "
            "selected years are combined, February values are combined, "
            "and so on. It is not a chronological month-by-month timeline."
        )
    )


def show_academic_period_chart(
    data,
    summary
):
    """
    Display calendar-normalized academic-period rates.
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
            "a valid occurrence date was unavailable."
        )

    else:
        show_insight(
            f"{top_period_rate['period']} has the highest normalized "
            f"incident rate at "
            f"{top_period_rate['rate']:.1f} incidents per calendar week. "
            f"The period contains "
            f"{format_number(top_period_rate['incident_count'])} "
            f"selected incidents."
        )

    show_info_hint(
        "Academic-period denominator",
        (
            "The rate uses all calendar days represented in each academic "
            "period, including days with zero incidents. Summer, Summer "
            "Semester, Summer Session, and Summer Break are treated as "
            "one Summer Break category."
        )
    )


def show_weekday_hour_heatmap(
    data,
    summary
):
    """
    Display the weekday-hour heatmap.
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

    if peak_combination[
        "weekday"
    ] == "N/A":
        show_insight(
            "Weekday and hourly activity data is unavailable for the "
            "current filtered selection."
        )

    else:
        show_insight(
            f"The busiest weekday-hour combination is "
            f"{peak_combination['weekday']} at "
            f"{format_hour(peak_combination['hour'])}, with "
            f"{format_number(peak_combination['count'])} selected incidents."
        )

    show_info_hint(
        "Heatmap denominator",
        (
            "Each cell shows the raw count of distinct selected incidents "
            "for that weekday and hour. Light cells indicate lower incident "
            "volume, while darker cells indicate higher incident volume."
        )
    )


def show_incident_trends(data):
    """
    Display the complete temporal activity section.
    """
    show_section_banner(
        eyebrow="Time Intelligence",
        title="Temporal Activity Profile",
        description=(
            "Identify seasonal patterns, weekday-hour activity, and "
            "calendar-normalized incident rates across academic periods."
        )
    )

    summary = show_temporal_summary(
        data
    )

    # st.divider()

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