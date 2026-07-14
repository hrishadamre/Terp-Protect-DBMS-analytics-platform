"""
executive_overview.py

Purpose:
Display the executive-level Command Center for the Terp Protect
dashboard.

Responsibilities:
- Summarize the current filtered incident view
- Compare monthly incident activity across years
- Display the leading crime groups
- Present compact operational composition indicators
- Avoid repeating detailed charts available in dedicated tabs
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


MONTH_NUMBER_ORDER = list(
    range(
        1,
        13
    )
)


TOP_CRIME_GROUPS = 10

PRIMARY_CHART_HEIGHT = 440
COMPOSITION_CHART_HEIGHT = 330


YEAR_COLORS = [
    "#8ED8F3",
    "#E78A98",
    "#F2CC68",
    "#6AC7B6",
    "#B6A6E9",
    "#F2B880"
]


OUTCOME_COLORS = {
    "Closed / Cleared": "#6AC7B6",
    "Pending / Active": "#F2CC68",
    "Arrest-Related": "#E78A98",
    "Other": "#AAB7C8"
}


DELAY_COLORS = {
    "Same Day / Within 24 Hours": "#6AC7B6",
    "1-3 Days": "#F2CC68",
    "4-7 Days": "#E9A85D",
    "Over 7 Days": "#D95F65",
    "Unknown": "#AAB7C8"
}


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


def distinct_incident_count(data):
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


def safe_binary_sum(
    data,
    column
):
    """
    Safely sum a binary indicator column.
    """
    if (
        data is None
        or data.empty
        or column not in data.columns
    ):
        return 0

    values = pd.to_numeric(
        data[column],
        errors="coerce"
    ).fillna(0)

    return int(
        values.sum()
    )


def get_valid_delay_count(data):
    """
    Return the number of records with a valid non-negative delay.
    """
    if (
        data is None
        or data.empty
        or "report_delay_hours" not in data.columns
    ):
        return 0

    delay_values = pd.to_numeric(
        data["report_delay_hours"],
        errors="coerce"
    )

    valid_mask = (
        delay_values.notna()
        & (
            delay_values >= 0
        )
    )

    if "has_valid_reporting_delay" in data.columns:
        valid_flag = pd.to_numeric(
            data["has_valid_reporting_delay"],
            errors="coerce"
        ).fillna(0)

        valid_mask = (
            valid_mask
            & (
                valid_flag == 1
            )
        )

    return int(
        valid_mask.sum()
    )


def calculate_median_delay_hours(data):
    """
    Calculate the median valid reporting delay.
    """
    if (
        data is None
        or data.empty
        or "report_delay_hours" not in data.columns
    ):
        return pd.NA

    delay_values = pd.to_numeric(
        data["report_delay_hours"],
        errors="coerce"
    )

    delay_values = delay_values[
        delay_values.notna()
        & (
            delay_values >= 0
        )
    ]

    if delay_values.empty:
        return pd.NA

    return float(
        delay_values.median()
    )


def format_delay(hours):
    """
    Format a delay value as hours or days.
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


def calculate_weekend_percentage(data):
    """
    Calculate weekend incident share.
    """
    if data is None or data.empty:
        return 0.0

    if "occurred_is_weekend" in data.columns:
        weekend_values = pd.to_numeric(
            data["occurred_is_weekend"],
            errors="coerce"
        ).fillna(0)

        return float(
            weekend_values.mean()
            * 100
        )

    if "occurred_weekday" in data.columns:
        weekend_count = data[
            "occurred_weekday"
        ].isin(
            [
                "Saturday",
                "Sunday"
            ]
        ).sum()

        return calculate_percentage(
            weekend_count,
            len(data)
        )

    return 0.0


def get_month_column(data):
    """
    Return the best available month-number column.
    """
    preferred_columns = [
        "occurred_month",
        "month",
        "month_number"
    ]

    for column in preferred_columns:
        if column in data.columns:
            return column

    return None


def get_year_column(data):
    """
    Return the best available year column.
    """
    preferred_columns = [
        "occurred_year",
        "source_year",
        "year"
    ]

    for column in preferred_columns:
        if column in data.columns:
            return column

    return None


def prepare_monthly_year_data(data):
    """
    Prepare monthly incident counts by year.
    """
    if data is None or data.empty:
        return pd.DataFrame()

    year_column = get_year_column(
        data
    )

    month_column = get_month_column(
        data
    )

    if year_column is None:
        return pd.DataFrame()

    working_data = data.copy()

    working_data["_year"] = pd.to_numeric(
        working_data[year_column],
        errors="coerce"
    )

    if month_column is not None:
        working_data["_month_number"] = pd.to_numeric(
            working_data[month_column],
            errors="coerce"
        )

    elif "occurred_month_name" in working_data.columns:
        month_mapping = {
            month_name: month_number
            for month_number, month_name in enumerate(
                MONTH_ORDER,
                start=1
            )
        }

        working_data["_month_number"] = (
            working_data["occurred_month_name"]
            .map(
                month_mapping
            )
        )

    elif "occurred_datetime" in working_data.columns:
        occurred_datetime = pd.to_datetime(
            working_data["occurred_datetime"],
            errors="coerce"
        )

        working_data["_month_number"] = (
            occurred_datetime.dt.month
        )

    else:
        return pd.DataFrame()

    working_data = working_data.dropna(
        subset=[
            "_year",
            "_month_number"
        ]
    )

    working_data = working_data[
        working_data["_month_number"].between(
            1,
            12
        )
    ]

    if working_data.empty:
        return pd.DataFrame()

    working_data["_year"] = (
        working_data["_year"]
        .astype(int)
    )

    working_data["_month_number"] = (
        working_data["_month_number"]
        .astype(int)
    )

    if "incident_id" in working_data.columns:
        monthly_summary = (
            working_data
            .groupby(
                [
                    "_year",
                    "_month_number"
                ]
            )["incident_id"]
            .nunique()
            .reset_index(
                name="incident_count"
            )
        )

    else:
        monthly_summary = (
            working_data
            .groupby(
                [
                    "_year",
                    "_month_number"
                ]
            )
            .size()
            .reset_index(
                name="incident_count"
            )
        )

    complete_index = pd.MultiIndex.from_product(
        [
            sorted(
                monthly_summary["_year"]
                .unique()
            ),
            MONTH_NUMBER_ORDER
        ],
        names=[
            "_year",
            "_month_number"
        ]
    )

    monthly_summary = (
        monthly_summary
        .set_index(
            [
                "_year",
                "_month_number"
            ]
        )
        .reindex(
            complete_index,
            fill_value=0
        )
        .reset_index()
    )

    monthly_summary["month_name"] = (
        monthly_summary["_month_number"]
        .map(
            {
                month_number: month_name
                for month_number, month_name in enumerate(
                    MONTH_ORDER,
                    start=1
                )
            }
        )
    )

    return monthly_summary


def create_monthly_year_chart(data):
    """
    Create a monthly incident trend with one line per year.
    """
    monthly_data = prepare_monthly_year_data(
        data
    )

    figure = go.Figure()

    if monthly_data.empty:
        figure.add_annotation(
            text="Monthly year-comparison data is unavailable.",
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
            title="Monthly Incident Trend by Year",
            height=PRIMARY_CHART_HEIGHT,
            paper_bgcolor="#0B111C",
            plot_bgcolor="#0B111C"
        )

        return figure

    available_years = sorted(
        monthly_data["_year"]
        .unique()
    )

    for index, year in enumerate(
        available_years
    ):
        year_data = monthly_data[
            monthly_data["_year"]
            == year
        ].sort_values(
            "_month_number"
        )

        figure.add_trace(
            go.Scatter(
                x=year_data[
                    "month_name"
                ],
                y=year_data[
                    "incident_count"
                ],
                mode="lines+markers",
                name=str(
                    year
                ),
                line={
                    "width": 2.6,
                    "color": YEAR_COLORS[
                        index
                        % len(
                            YEAR_COLORS
                        )
                    ]
                },
                marker={
                    "size": 7
                },
                hovertemplate=(
                    f"<b>{year}</b><br>"
                    "Month: %{x}<br>"
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
                "size": 17,
                "color": "#F8FAFC"
            }
        },
        height=PRIMARY_CHART_HEIGHT,
        margin={
            "l": 62,
            "r": 25,
            "t": 78,
            "b": 65
        },
        paper_bgcolor="#0B111C",
        plot_bgcolor="#0B111C",
        font={
            "color": "#F8FAFC"
        },
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
            "font": {
                "size": 11,
                "color": "#E2E8F0"
            }
        },
        xaxis={
            "title": {
                "text": "Month"
            },
            "categoryorder": "array",
            "categoryarray": MONTH_ORDER,
            "tickfont": {
                "size": 10,
                "color": "#CBD5E1"
            },
            "tickangle": -35,
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
        },
        hovermode="x unified"
    )

    return figure


def prepare_crime_group_data(data):
    """
    Prepare top crime-group counts.
    """
    if (
        data is None
        or data.empty
        or "crime_group" not in data.columns
    ):
        return pd.DataFrame()

    working_data = data[
        [
            "crime_group"
        ]
    ].copy()

    working_data["crime_group"] = (
        working_data["crime_group"]
        .apply(
            clean_category_value
        )
    )

    if "incident_id" in data.columns:
        working_data["incident_id"] = data[
            "incident_id"
        ]

        summary = (
            working_data
            .groupby(
                "crime_group"
            )["incident_id"]
            .nunique()
            .reset_index(
                name="incident_count"
            )
        )

    else:
        summary = (
            working_data
            .groupby(
                "crime_group"
            )
            .size()
            .reset_index(
                name="incident_count"
            )
        )

    total_incidents = summary[
        "incident_count"
    ].sum()

    summary["percentage"] = (
        summary["incident_count"]
        / total_incidents
        * 100
        if total_incidents > 0
        else 0.0
    )

    return (
        summary
        .sort_values(
            [
                "incident_count",
                "crime_group"
            ],
            ascending=[
                False,
                True
            ]
        )
        .head(
            TOP_CRIME_GROUPS
        )
    )


def create_top_crime_group_chart(data):
    """
    Create a horizontal bar chart for leading crime groups.
    """
    crime_data = prepare_crime_group_data(
        data
    )

    figure = go.Figure()

    if crime_data.empty:
        figure.add_annotation(
            text="Crime-group data is unavailable.",
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
            title="Top Crime Groups",
            height=PRIMARY_CHART_HEIGHT,
            paper_bgcolor="#0B111C",
            plot_bgcolor="#0B111C"
        )

        return figure

    chart_data = crime_data.sort_values(
        "incident_count",
        ascending=True
    )

    figure.add_trace(
        go.Bar(
            x=chart_data[
                "incident_count"
            ],
            y=chart_data[
                "crime_group"
            ],
            orientation="h",
            marker={
                "color": "#BEEBFA",
                "line": {
                    "color": "#8ED8F3",
                    "width": 1
                }
            },
            customdata=chart_data[
                [
                    "percentage"
                ]
            ],
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Incidents: %{x:,}<br>"
                "Share: %{customdata[0]:.1f}%"
                "<extra></extra>"
            )
        )
    )

    figure.update_layout(
        title={
            "text": "Top Crime Groups",
            "x": 0,
            "xanchor": "left",
            "font": {
                "size": 17,
                "color": "#F8FAFC"
            }
        },
        height=PRIMARY_CHART_HEIGHT,
        margin={
            "l": 170,
            "r": 25,
            "t": 78,
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


def normalize_outcome_label(value):
    """
    Convert a source outcome label into a compact operational category.
    """
    normalized_value = clean_category_value(
        value
    )

    lower_value = normalized_value.lower()

    if any(
        keyword in lower_value
        for keyword in [
            "closed",
            "cleared"
        ]
    ):
        return "Closed / Cleared"

    if any(
        keyword in lower_value
        for keyword in [
            "pending",
            "active"
        ]
    ):
        return "Pending / Active"

    if "arrest" in lower_value:
        return "Arrest-Related"

    return "Other"


def prepare_outcome_composition(data):
    """
    Prepare major outcome composition.
    """
    if data is None or data.empty:
        return pd.DataFrame()

    if "disposition_group" in data.columns:
        outcome_values = (
            data["disposition_group"]
            .apply(
                normalize_outcome_label
            )
        )

    else:
        outcome_values = pd.Series(
            "Other",
            index=data.index
        )

        closed_mask = pd.Series(
            False,
            index=data.index
        )

        pending_mask = pd.Series(
            False,
            index=data.index
        )

        arrest_mask = pd.Series(
            False,
            index=data.index
        )

        if "is_closed" in data.columns:
            closed_mask = (
                pd.to_numeric(
                    data["is_closed"],
                    errors="coerce"
                ).fillna(0)
                == 1
            )

        if "is_pending" in data.columns:
            pending_mask = (
                pd.to_numeric(
                    data["is_pending"],
                    errors="coerce"
                ).fillna(0)
                == 1
            )

        if "is_arrest_related" in data.columns:
            arrest_mask = (
                pd.to_numeric(
                    data["is_arrest_related"],
                    errors="coerce"
                ).fillna(0)
                == 1
            )

        outcome_values.loc[
            closed_mask
        ] = "Closed / Cleared"

        outcome_values.loc[
            pending_mask
        ] = "Pending / Active"

        outcome_values.loc[
            arrest_mask
        ] = "Arrest-Related"

    counts = (
        outcome_values
        .value_counts()
        .reindex(
            [
                "Closed / Cleared",
                "Pending / Active",
                "Arrest-Related",
                "Other"
            ],
            fill_value=0
        )
    )

    total = int(
        counts.sum()
    )

    summary = counts.rename(
        "count"
    ).reset_index()

    summary.columns = [
        "category",
        "count"
    ]

    summary["percentage"] = (
        summary["count"]
        / total
        * 100
        if total > 0
        else 0.0
    )

    return summary


def prepare_delay_composition(data):
    """
    Prepare reporting-delay bucket composition.
    """
    delay_order = [
        "Same Day / Within 24 Hours",
        "1-3 Days",
        "4-7 Days",
        "Over 7 Days",
        "Unknown"
    ]

    if (
        data is None
        or data.empty
        or "delay_bucket" not in data.columns
    ):
        counts = pd.Series(
            [0] * len(
                delay_order
            ),
            index=delay_order
        )

    else:
        delay_values = (
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

        counts = (
            delay_values
            .value_counts()
            .reindex(
                delay_order,
                fill_value=0
            )
        )

    total = int(
        counts.sum()
    )

    summary = counts.rename(
        "count"
    ).reset_index()

    summary.columns = [
        "category",
        "count"
    ]

    summary["percentage"] = (
        summary["count"]
        / total
        * 100
        if total > 0
        else 0.0
    )

    return summary


def prepare_weekpart_composition(data):
    """
    Prepare weekday-versus-weekend composition.
    """
    total = len(
        data
    )

    weekend_percentage = calculate_weekend_percentage(
        data
    )

    weekend_count = round(
        total
        * weekend_percentage
        / 100
    )

    weekday_count = max(
        total - weekend_count,
        0
    )

    return pd.DataFrame(
        {
            "category": [
                "Weekday",
                "Weekend"
            ],
            "count": [
                weekday_count,
                weekend_count
            ],
            "percentage": [
                calculate_percentage(
                    weekday_count,
                    total
                ),
                calculate_percentage(
                    weekend_count,
                    total
                )
            ]
        }
    )


def add_composition_row(
    figure,
    row_label,
    composition_data,
    color_mapping
):
    """
    Add one 100% stacked horizontal composition row.
    """
    for _, row in composition_data.iterrows():
        figure.add_trace(
            go.Bar(
                y=[
                    row_label
                ],
                x=[
                    row[
                        "percentage"
                    ]
                ],
                name=row[
                    "category"
                ],
                orientation="h",
                marker={
                    "color": color_mapping.get(
                        row[
                            "category"
                        ],
                        "#AAB7C8"
                    )
                },
                customdata=[
                    row[
                        "count"
                    ]
                ],
                hovertemplate=(
                    f"<b>{row_label}</b><br>"
                    f"{row['category']}<br>"
                    "Share: %{x:.1f}%<br>"
                    "Incidents: %{customdata:,}"
                    "<extra></extra>"
                ),
                showlegend=False
            )
        )


def create_operational_composition_chart(data):
    """
    Create a compact operational composition chart.

    Rows:
    - Case outcomes
    - Reporting timeliness
    - Weekday versus weekend activity
    """
    outcome_data = prepare_outcome_composition(
        data
    )

    delay_data = prepare_delay_composition(
        data
    )

    weekpart_data = prepare_weekpart_composition(
        data
    )

    figure = go.Figure()

    add_composition_row(
        figure=figure,
        row_label="Case Outcomes",
        composition_data=outcome_data,
        color_mapping=OUTCOME_COLORS
    )

    add_composition_row(
        figure=figure,
        row_label="Reporting Timeliness",
        composition_data=delay_data,
        color_mapping=DELAY_COLORS
    )

    add_composition_row(
        figure=figure,
        row_label="Incident Timing",
        composition_data=weekpart_data,
        color_mapping={
            "Weekday": "#8ED8F3",
            "Weekend": "#B6A6E9"
        }
    )

    figure.update_layout(
        title={
            "text": "Operational Composition",
            "x": 0,
            "xanchor": "left",
            "font": {
                "size": 17,
                "color": "#F8FAFC"
            }
        },
        barmode="stack",
        height=COMPOSITION_CHART_HEIGHT,
        margin={
            "l": 150,
            "r": 30,
            "t": 70,
            "b": 55
        },
        paper_bgcolor="#0B111C",
        plot_bgcolor="#0B111C",
        font={
            "color": "#F8FAFC"
        },
        xaxis={
            "title": {
                "text": "Share of Selected Incidents"
            },
            "range": [
                0,
                100
            ],
            "ticksuffix": "%",
            "gridcolor": "rgba(71, 85, 105, 0.50)",
            "showline": True,
            "linecolor": "#334155",
            "tickfont": {
                "size": 11,
                "color": "#CBD5E1"
            }
        },
        yaxis={
            "title": {
                "text": ""
            },
            "categoryorder": "array",
            "categoryarray": [
                "Case Outcomes",
                "Reporting Timeliness",
                "Incident Timing"
            ],
            "autorange": "reversed",
            "showgrid": False,
            "tickfont": {
                "size": 11,
                "color": "#CBD5E1"
            }
        }
    )

    return figure


def get_peak_month_year(data):
    """
    Return the highest-volume month and year combination.
    """
    monthly_data = prepare_monthly_year_data(
        data
    )

    if monthly_data.empty:
        return {
            "year": "N/A",
            "month": "N/A",
            "count": 0
        }

    top_row = monthly_data.sort_values(
        "incident_count",
        ascending=False
    ).iloc[0]

    return {
        "year": int(
            top_row[
                "_year"
            ]
        ),
        "month": top_row[
            "month_name"
        ],
        "count": int(
            top_row[
                "incident_count"
            ]
        )
    }


def get_same_day_percentage(data):
    """
    Return the percentage of incidents in the same-day delay bucket.
    """
    delay_data = prepare_delay_composition(
        data
    )

    matching_rows = delay_data[
        delay_data["category"]
        == "Same Day / Within 24 Hours"
    ]

    if matching_rows.empty:
        return 0.0

    return float(
        matching_rows.iloc[0][
            "percentage"
        ]
    )


def get_closed_percentage(data):
    """
    Return the closed or cleared incident share.
    """
    outcome_data = prepare_outcome_composition(
        data
    )

    matching_rows = outcome_data[
        outcome_data["category"]
        == "Closed / Cleared"
    ]

    if matching_rows.empty:
        return 0.0

    return float(
        matching_rows.iloc[0][
            "percentage"
        ]
    )


def show_command_summary(data):
    """
    Display the compact executive KPI strip.
    """
    selected_incidents = distinct_incident_count(
        data
    )

    top_crime_group, top_crime_count = get_top_value(
        data,
        "crime_group"
    )

    top_location_group, top_location_count = get_top_value(
        data,
        "location_group"
    )

    top_outcome_group, top_outcome_count = get_top_value(
        data,
        "disposition_group"
    )

    median_delay = calculate_median_delay_hours(
        data
    )

    valid_delay_count = get_valid_delay_count(
        data
    )

    valid_delay_percentage = calculate_percentage(
        valid_delay_count,
        len(data)
    )

    same_day_percentage = get_same_day_percentage(
        data
    )

    closed_percentage = get_closed_percentage(
        data
    )

    weekend_percentage = calculate_weekend_percentage(
        data
    )

    overview_items = [
        {
            "label": "Selected Incidents",
            "value": format_number(
                selected_incidents
            ),
            "meta": "Distinct filtered incidents",
            "numeric": True
        },
        {
            "label": "Top Crime Group",
            "value": top_crime_group,
            "meta": "Leading incident category",
            "badge": format_number(
                top_crime_count
            )
        },
        {
            "label": "Top Location Group",
            "value": top_location_group,
            "meta": "Leading location type",
            "badge": format_number(
                top_location_count
            )
        },
        {
            "label": "Top Outcome",
            "value": top_outcome_group,
            "meta": "Leading disposition group",
            "badge": format_number(
                top_outcome_count
            )
        },
        {
            "label": "Closed / Cleared",
            "value": format_percentage(
                closed_percentage
            ),
            "meta": "Selected incident share",
            "numeric": True
        },
        {
            "label": "Same-Day Reporting",
            "value": format_percentage(
                same_day_percentage
            ),
            "meta": "Within 24 hours",
            "numeric": True
        },
        {
            "label": "Median Delay",
            "value": format_delay(
                median_delay
            ),
            "meta": (
                f"{format_percentage(valid_delay_percentage)} "
                "valid coverage"
            ),
            "numeric": True
        },
        {
            "label": "Weekend Share",
            "value": format_percentage(
                weekend_percentage
            ),
            "meta": "Saturday and Sunday",
            "numeric": True
        }
    ]

    show_compact_overview_strip(
        overview_items
    )

    peak_period = get_peak_month_year(
        data
    )

    show_insight(
        f"{top_crime_group} is the leading crime group with "
        f"{format_number(top_crime_count)} incidents. "
        f"The highest monthly point is {peak_period['month']} "
        f"{peak_period['year']} with "
        f"{format_number(peak_period['count'])} incidents, while "
        f"{format_percentage(same_day_percentage)} of selected records "
        f"were reported within 24 hours."
    )

    show_info_hint(
        "Command Center scope",
        (
            "This page provides an executive summary. Use the dedicated "
            "tabs for detailed time, location, outcome, delay, arrest, "
            "and data-quality analysis."
        )
    )

    return {
        "selected_incidents": selected_incidents,
        "top_crime_group": top_crime_group,
        "top_crime_count": top_crime_count,
        "top_location_group": top_location_group,
        "top_location_count": top_location_count,
        "top_outcome_group": top_outcome_group,
        "top_outcome_count": top_outcome_count,
        "median_delay": median_delay,
        "same_day_percentage": same_day_percentage,
        "closed_percentage": closed_percentage,
        "weekend_percentage": weekend_percentage,
        "peak_period": peak_period
    }


def show_primary_charts(
    data,
    summary
):
    """
    Display the two primary Command Center charts.
    """
    monthly_chart = create_monthly_year_chart(
        data
    )

    crime_chart = create_top_crime_group_chart(
        data
    )

    chart_left, chart_right = st.columns(
        [
            1.15,
            0.85
        ],
        gap="small"
    )

    with chart_left:
        st.plotly_chart(
            monthly_chart,
            use_container_width=True,
            key="command_monthly_year_chart",
            config=get_chart_config()
        )

    with chart_right:
        st.plotly_chart(
            crime_chart,
            use_container_width=True,
            key="command_top_crime_groups_chart",
            config=get_chart_config()
        )

    insight_left, insight_right = st.columns(
        [
            1.15,
            0.85
        ],
        gap="small"
    )

    with insight_left:
        peak_period = summary[
            "peak_period"
        ]

        show_insight(
            f"{peak_period['month']} {peak_period['year']} is the "
            f"highest-volume month-year combination with "
            f"{format_number(peak_period['count'])} incidents."
        )

    with insight_right:
        show_insight(
            f"{summary['top_crime_group']} is the leading crime group "
            f"with {format_number(summary['top_crime_count'])} incidents."
        )


def show_operational_composition(
    data,
    summary
):
    """
    Display the compact operational composition strip.
    """
    composition_chart = create_operational_composition_chart(
        data
    )

    st.plotly_chart(
        composition_chart,
        use_container_width=True,
        key="command_operational_composition_chart",
        config=get_chart_config()
    )

    show_insight(
        f"{format_percentage(summary['closed_percentage'])} of selected "
        f"incidents are closed or cleared, "
        f"{format_percentage(summary['same_day_percentage'])} were "
        f"reported within 24 hours, and "
        f"{format_percentage(summary['weekend_percentage'])} occurred "
        f"on weekends."
    )


def show_executive_overview(data):
    """
    Display the complete Command Center.
    """
    show_section_banner(
        eyebrow="Executive Intelligence",
        title="Terp Protect Command Center",
        description=(
            "Monitor incident volume, seasonal trends, leading crime "
            "categories, and core operational composition for the "
            "current filtered view."
        )
    )

    summary = show_command_summary(
        data
    )

    st.divider()

    show_primary_charts(
        data,
        summary
    )

    show_operational_composition(
        data,
        summary
    )