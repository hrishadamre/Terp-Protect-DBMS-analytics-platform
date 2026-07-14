"""
executive_overview.py

Purpose:
Display the executive-level Command Center for the Terp Protect
dashboard.

Responsibilities:
- Summarize the current filtered incident view
- Compare monthly incident volume across source years
- Display the leading crime groups
- Present compact operational composition indicators
- Avoid repeating detailed charts available in dedicated tabs
- Avoid treating missing month-year data as zero incidents
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


MONTH_NUMBER_TO_NAME = {
    month_number: month_name
    for month_number, month_name in enumerate(
        MONTH_ORDER,
        start=1
    )
}


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
    "Reported Within 24 Hours": "#6AC7B6",
    "1-3 Days": "#F2CC68",
    "4-7 Days": "#E9A85D",
    "Over 7 Days": "#D95F65",
    "Unknown": "#AAB7C8"
}


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
    Return a cleaned categorical value.
    """
    if pd.isna(value):
        return "Unknown"

    cleaned_value = str(
        value
    ).strip()

    if not cleaned_value:
        return "Unknown"

    return cleaned_value


def get_source_year_column(data):
    """
    Return the year column used for the Command Center comparison.

    source_year is intentionally preferred because it represents the
    published UMPD log year and matches the dashboard's global Year filter.

    occurred_year is only used as a fallback when source_year is absent.
    """
    if "source_year" in data.columns:
        return "source_year"

    if "occurred_year" in data.columns:
        return "occurred_year"

    if "year" in data.columns:
        return "year"

    return None


def get_month_number(data):
    """
    Return a numeric occurrence-month series.
    """
    if "occurred_month" in data.columns:
        return pd.to_numeric(
            data["occurred_month"],
            errors="coerce"
        )

    if "occurred_month_name" in data.columns:
        month_lookup = {
            month_name: month_number
            for month_number, month_name in enumerate(
                MONTH_ORDER,
                start=1
            )
        }

        return (
            data["occurred_month_name"]
            .map(
                month_lookup
            )
        )

    if "occurred_datetime" in data.columns:
        occurred_datetime = pd.to_datetime(
            data["occurred_datetime"],
            errors="coerce"
        )

        return occurred_datetime.dt.month

    return pd.Series(
        pd.NA,
        index=data.index,
        dtype="Float64"
    )


def prepare_monthly_source_year_data(data):
    """
    Prepare monthly incident counts by source year.

    Important:
    - source_year is used whenever available
    - only observed month-year combinations are counted
    - missing combinations are represented as gaps, not zero incidents
    - distinct incident IDs are counted when available
    """
    if data is None or data.empty:
        return pd.DataFrame()

    year_column = get_source_year_column(
        data
    )

    if year_column is None:
        return pd.DataFrame()

    working_data = data.copy()

    working_data["_source_year"] = pd.to_numeric(
        working_data[year_column],
        errors="coerce"
    )

    working_data["_month_number"] = get_month_number(
        working_data
    )

    working_data = working_data.dropna(
        subset=[
            "_source_year",
            "_month_number"
        ]
    )

    working_data = working_data[
        working_data["_month_number"].between(
            1,
            12
        )
    ].copy()

    if working_data.empty:
        return pd.DataFrame()

    working_data["_source_year"] = (
        working_data["_source_year"]
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
                    "_source_year",
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
                    "_source_year",
                    "_month_number"
                ]
            )
            .size()
            .reset_index(
                name="incident_count"
            )
        )

    monthly_summary["month_name"] = (
        monthly_summary["_month_number"]
        .map(
            MONTH_NUMBER_TO_NAME
        )
    )

    return monthly_summary.sort_values(
        [
            "_source_year",
            "_month_number"
        ]
    )


def prepare_source_year_plot_data(
    monthly_data,
    source_year
):
    """
    Prepare one complete 12-month plotting frame for a source year.

    Missing months are assigned None so Plotly displays a gap instead
    of an artificial zero value.
    """
    full_month_frame = pd.DataFrame(
        {
            "_month_number": range(
                1,
                13
            ),
            "month_name": MONTH_ORDER
        }
    )

    year_data = monthly_data[
        monthly_data["_source_year"]
        == source_year
    ][
        [
            "_month_number",
            "incident_count"
        ]
    ].copy()

    plot_data = full_month_frame.merge(
        year_data,
        on="_month_number",
        how="left"
    )

    plot_data["incident_count"] = (
        plot_data["incident_count"]
        .where(
            plot_data["incident_count"].notna(),
            None
        )
    )

    return plot_data


def create_monthly_source_year_chart(data):
    """
    Create the monthly incident comparison by source year.
    """
    monthly_data = prepare_monthly_source_year_data(
        data
    )

    figure = go.Figure()

    if monthly_data.empty:
        figure.add_annotation(
            text="Monthly source-year data is unavailable.",
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
            title="Monthly Incident Volume by Source Year",
            height=PRIMARY_CHART_HEIGHT,
            paper_bgcolor="#0B111C",
            plot_bgcolor="#0B111C"
        )

        return figure

    available_years = sorted(
        monthly_data["_source_year"]
        .drop_duplicates()
        .tolist()
    )

    for index, source_year in enumerate(
        available_years
    ):
        year_data = prepare_source_year_plot_data(
            monthly_data=monthly_data,
            source_year=source_year
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
                    source_year
                ),
                connectgaps=False,
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
                    f"<b>Source year {source_year}</b><br>"
                    "Month: %{x}<br>"
                    "Incidents: %{y:,}"
                    "<extra></extra>"
                )
            )
        )

    figure.update_layout(
        title={
            "text": "Monthly Incident Volume by Source Year",
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
            "title": {
                "text": "Source Year",
                "font": {
                    "size": 11,
                    "color": "#CBD5E1"
                }
            },
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
                "text": "Occurrence Month"
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
    Prepare the leading crime-group counts.
    """
    if (
        data is None
        or data.empty
        or "crime_group" not in data.columns
    ):
        return pd.DataFrame()

    selected_columns = [
        "crime_group"
    ]

    if "incident_id" in data.columns:
        selected_columns.append(
            "incident_id"
        )

    working_data = data[
        selected_columns
    ].copy()

    working_data["crime_group"] = (
        working_data["crime_group"]
        .apply(
            clean_category_value
        )
    )

    if "incident_id" in working_data.columns:
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

    summary["percentage"] = summary[
        "incident_count"
    ].apply(
        lambda count: safe_percentage(
            count,
            total_incidents
        )
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
                "Share of selected incidents: %{customdata[0]:.1f}%"
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
    Convert a source outcome value into a compact operational category.
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
    Prepare major case-outcome composition.
    """
    outcome_order = [
        "Closed / Cleared",
        "Pending / Active",
        "Arrest-Related",
        "Other"
    ]

    if data is None or data.empty:
        return pd.DataFrame(
            {
                "category": outcome_order,
                "count": [
                    0,
                    0,
                    0,
                    0
                ],
                "percentage": [
                    0.0,
                    0.0,
                    0.0,
                    0.0
                ]
            }
        )

    if "disposition_group" in data.columns:
        working_data = data.copy()

        working_data["_outcome_category"] = (
            working_data["disposition_group"]
            .apply(
                normalize_outcome_label
            )
        )

        if "incident_id" in working_data.columns:
            counts = (
                working_data
                .groupby(
                    "_outcome_category"
                )["incident_id"]
                .nunique()
                .reindex(
                    outcome_order,
                    fill_value=0
                )
            )

        else:
            counts = (
                working_data[
                    "_outcome_category"
                ]
                .value_counts()
                .reindex(
                    outcome_order,
                    fill_value=0
                )
            )

    else:
        counts = pd.Series(
            [
                0,
                0,
                0,
                distinct_incident_count(
                    data
                )
            ],
            index=outcome_order
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

    summary["percentage"] = summary[
        "count"
    ].apply(
        lambda count: safe_percentage(
            count,
            total
        )
    )

    return summary


def normalize_delay_bucket(value):
    """
    Standardize delay-bucket wording for the Command Center.
    """
    cleaned_value = clean_category_value(
        value
    )

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


def prepare_delay_composition(data):
    """
    Prepare reporting-delay composition.
    """
    delay_order = [
        "Reported Within 24 Hours",
        "1-3 Days",
        "4-7 Days",
        "Over 7 Days",
        "Unknown"
    ]

    if data is None or data.empty:
        counts = pd.Series(
            [
                0,
                0,
                0,
                0,
                0
            ],
            index=delay_order
        )

    elif "delay_bucket" in data.columns:
        delay_values = (
            data["delay_bucket"]
            .apply(
                normalize_delay_bucket
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

    elif "report_delay_hours" in data.columns:
        delay_hours = pd.to_numeric(
            data["report_delay_hours"],
            errors="coerce"
        )

        delay_values = pd.Series(
            "Unknown",
            index=data.index,
            dtype="object"
        )

        delay_values.loc[
            delay_hours.notna()
            & (
                delay_hours >= 0
            )
            & (
                delay_hours <= 24
            )
        ] = "Reported Within 24 Hours"

        delay_values.loc[
            (
                delay_hours > 24
            )
            & (
                delay_hours <= 72
            )
        ] = "1-3 Days"

        delay_values.loc[
            (
                delay_hours > 72
            )
            & (
                delay_hours <= 168
            )
        ] = "4-7 Days"

        delay_values.loc[
            delay_hours > 168
        ] = "Over 7 Days"

        counts = (
            delay_values
            .value_counts()
            .reindex(
                delay_order,
                fill_value=0
            )
        )

    else:
        counts = pd.Series(
            [
                0,
                0,
                0,
                0,
                distinct_incident_count(
                    data
                )
            ],
            index=delay_order
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

    summary["percentage"] = summary[
        "count"
    ].apply(
        lambda count: safe_percentage(
            count,
            total
        )
    )

    return summary


def prepare_weekpart_composition(data):
    """
    Prepare weekday-versus-weekend composition.
    """
    total_incidents = distinct_incident_count(
        data
    )

    if total_incidents <= 0:
        return pd.DataFrame(
            {
                "category": [
                    "Weekday",
                    "Weekend"
                ],
                "count": [
                    0,
                    0
                ],
                "percentage": [
                    0.0,
                    0.0
                ]
            }
        )

    if "occurred_is_weekend" in data.columns:
        weekend_flag = pd.to_numeric(
            data["occurred_is_weekend"],
            errors="coerce"
        ).fillna(0)

        weekend_data = data[
            weekend_flag == 1
        ]

    elif "occurred_weekday" in data.columns:
        weekend_data = data[
            data["occurred_weekday"].isin(
                [
                    "Saturday",
                    "Sunday"
                ]
            )
        ]

    else:
        weekend_data = data.iloc[
            0:0
        ]

    weekend_count = distinct_incident_count(
        weekend_data
    )

    weekday_count = max(
        total_incidents - weekend_count,
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
                safe_percentage(
                    weekday_count,
                    total_incidents
                ),
                safe_percentage(
                    weekend_count,
                    total_incidents
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
            "linecolor": "#334155"
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
            "showgrid": False
        }
    )

    return figure


def get_peak_source_year_month(data):
    """
    Return the highest observed source-year and month combination.
    """
    monthly_data = prepare_monthly_source_year_data(
        data
    )

    if monthly_data.empty:
        return {
            "source_year": "N/A",
            "month": "N/A",
            "count": 0
        }

    top_row = monthly_data.sort_values(
        "incident_count",
        ascending=False
    ).iloc[
        0
    ]

    return {
        "source_year": int(
            top_row[
                "_source_year"
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


def get_composition_percentage(
    composition_data,
    category
):
    """
    Return one percentage from a composition dataframe.
    """
    matching_rows = composition_data[
        composition_data["category"]
        == category
    ]

    if matching_rows.empty:
        return 0.0

    return float(
        matching_rows.iloc[
            0
        ][
            "percentage"
        ]
    )


def calculate_valid_delay_statistics(data):
    """
    Calculate median delay and valid-delay coverage.
    """
    if (
        data is None
        or data.empty
        or "report_delay_hours" not in data.columns
    ):
        return {
            "median_delay": pd.NA,
            "valid_count": 0,
            "valid_coverage": 0.0
        }

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

    valid_values = delay_values[
        valid_mask
    ]

    if valid_values.empty:
        median_delay = pd.NA

    else:
        median_delay = float(
            valid_values.median()
        )

    valid_count = int(
        valid_mask.sum()
    )

    return {
        "median_delay": median_delay,
        "valid_count": valid_count,
        "valid_coverage": safe_percentage(
            valid_count,
            len(
                data
            )
        )
    }


def format_delay(hours):
    """
    Format a reporting delay as hours or days.
    """
    numeric_hours = pd.to_numeric(
        hours,
        errors="coerce"
    )

    if pd.isna(
        numeric_hours
    ):
        return "N/A"

    numeric_hours = float(
        numeric_hours
    )

    if numeric_hours < 48:
        return f"{numeric_hours:.1f} hrs"

    return f"{numeric_hours / 24:.1f} days"


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

    delay_statistics = calculate_valid_delay_statistics(
        data
    )

    outcome_composition = prepare_outcome_composition(
        data
    )

    delay_composition = prepare_delay_composition(
        data
    )

    weekpart_composition = prepare_weekpart_composition(
        data
    )

    closed_percentage = get_composition_percentage(
        outcome_composition,
        "Closed / Cleared"
    )

    within_24_hour_percentage = get_composition_percentage(
        delay_composition,
        "Reported Within 24 Hours"
    )

    weekend_percentage = get_composition_percentage(
        weekpart_composition,
        "Weekend"
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
            "numeric": True,
            "metric_key": "closed_share"
        },
        {
            "label": "Reported Within 24 Hours",
            "value": format_percentage(
                within_24_hour_percentage
            ),
            "meta": "Elapsed reporting time",
            "numeric": True,
            "metric_key": "same_day_share"
        },
        {
            "label": "Median Delay",
            "value": format_delay(
                delay_statistics[
                    "median_delay"
                ]
            ),
            "meta": (
                f"{format_percentage(delay_statistics['valid_coverage'])} "
                "valid coverage"
            ),
            "numeric": True,
            "metric_key": "median_delay"
        },
        {
            "label": "Weekend Share",
            "value": format_percentage(
                weekend_percentage
            ),
            "meta": "Saturday and Sunday",
            "numeric": True,
            "metric_key": "weekend_share"
        }
    ]

    show_compact_overview_strip(
        overview_items
    )

    peak_period = get_peak_source_year_month(
        data
    )

    show_insight(
        f"{top_crime_group} is the leading crime group with "
        f"{format_number(top_crime_count)} incidents. "
        f"The highest observed source-year month is "
        f"{peak_period['month']} {peak_period['source_year']} with "
        f"{format_number(peak_period['count'])} incidents, while "
        f"{format_percentage(within_24_hour_percentage)} of selected "
        f"records were reported within 24 hours."
    )

    show_info_hint(
        "Command Center scope",
        (
            "The year comparison uses source_year, which represents the "
            "UMPD log year and matches the dashboard Year filter. Occurrence "
            "dates are still used for the month within each source year."
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
        "median_delay": delay_statistics[
            "median_delay"
        ],
        "within_24_hour_percentage": within_24_hour_percentage,
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
    monthly_chart = create_monthly_source_year_chart(
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
            key="command_monthly_source_year_chart",
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
            f"{peak_period['month']} {peak_period['source_year']} is the "
            f"highest observed source-year month with "
            f"{format_number(peak_period['count'])} incidents."
        )

        show_info_hint(
            "Missing-month treatment",
            (
                "A missing month-year combination is displayed as a gap, "
                "not as zero. Zero is only appropriate when the dataset "
                "explicitly confirms that no incidents occurred."
            )
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
    Display the compact operational composition chart.
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
        f"{format_percentage(summary['within_24_hour_percentage'])} were "
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
            "Monitor incident volume, source-year patterns, leading crime "
            "categories, and core operational composition for the current "
            "filtered view."
        )
    )

    summary = show_command_summary(
        data
    )

    # st.divider()

    show_primary_charts(
        data,
        summary
    )

    show_operational_composition(
        data,
        summary
    )