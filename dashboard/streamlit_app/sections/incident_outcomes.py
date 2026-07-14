"""
incident_outcomes.py

Purpose:
Display the case resolution profile for the Terp Protect dashboard.

Responsibilities:
- Summarize major and detailed case outcomes
- Display closed, pending, arrest-related, and other dispositions
- Compare normalized outcome composition across high-volume crime groups
- Apply minimum sample thresholds to normalized comparisons
- Clearly distinguish outcome classification from arrest-record matching
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


MAJOR_OUTCOME_CHART_HEIGHT = 430
DETAILED_OUTCOME_CHART_HEIGHT = 470
OUTCOME_COMPOSITION_CHART_HEIGHT = 540

TOP_DETAILED_DISPOSITIONS = 15
TOP_CRIME_GROUPS = 10
MINIMUM_CRIME_GROUP_RECORDS = 20


OUTCOME_ORDER = [
    "Closed / Cleared",
    "Pending / Active",
    "Arrest-Related",
    "Unfounded",
    "Summons / Warrant Issued",
    "Other",
    "Unknown"
]


OUTCOME_COLORS = {
    "Closed / Cleared": "#6AC7B6",
    "Pending / Active": "#F2CC68",
    "Arrest-Related": "#E78A98",
    "Unfounded": "#8ED8F3",
    "Summons / Warrant Issued": "#B6A6E9",
    "Other": "#AAB7C8",
    "Unknown": "#64748B"
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


def shorten_label(
    value,
    maximum_length=40
):
    """
    Shorten a long label for display.
    """
    cleaned_value = clean_category_value(
        value
    )

    if len(cleaned_value) <= maximum_length:
        return cleaned_value

    return (
        cleaned_value[
            : maximum_length - 3
        ]
        + "..."
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


def get_detail_disposition_column(data):
    """
    Return the first available detailed disposition column.
    """
    candidate_columns = [
        "disposition",
        "disposition_detail",
        "disposition_clean",
        "case_disposition"
    ]

    for column in candidate_columns:
        if column in data.columns:
            return column

    return None


def normalize_outcome_label(value):
    """
    Normalize source disposition values into major operational groups.

    CBE is not expanded into a specific meaning because the source
    abbreviation should be confirmed using official documentation.
    """
    cleaned_value = clean_category_value(
        value
    )

    lower_value = cleaned_value.lower()

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
            "active",
            "investigation"
        ]
    ):
        return "Pending / Active"

    if "arrest" in lower_value:
        return "Arrest-Related"

    if "unfounded" in lower_value:
        return "Unfounded"

    if any(
        keyword in lower_value
        for keyword in [
            "summons",
            "warrant"
        ]
    ):
        return "Summons / Warrant Issued"

    if lower_value == "unknown":
        return "Unknown"

    return "Other"


def prepare_major_outcome_data(data):
    """
    Prepare distinct incident counts by major outcome group.
    """
    if data is None or data.empty:
        return pd.DataFrame()

    working_data = data.copy()

    if "disposition_group" in working_data.columns:
        working_data["_outcome_group"] = (
            working_data["disposition_group"]
            .apply(
                normalize_outcome_label
            )
        )

    else:
        working_data["_outcome_group"] = "Other"

        if "is_closed" in working_data.columns:
            closed_mask = (
                pd.to_numeric(
                    working_data["is_closed"],
                    errors="coerce"
                ).fillna(0)
                == 1
            )

            working_data.loc[
                closed_mask,
                "_outcome_group"
            ] = "Closed / Cleared"

        if "is_pending" in working_data.columns:
            pending_mask = (
                pd.to_numeric(
                    working_data["is_pending"],
                    errors="coerce"
                ).fillna(0)
                == 1
            )

            working_data.loc[
                pending_mask,
                "_outcome_group"
            ] = "Pending / Active"

        if "is_arrest_related" in working_data.columns:
            arrest_mask = (
                pd.to_numeric(
                    working_data["is_arrest_related"],
                    errors="coerce"
                ).fillna(0)
                == 1
            )

            working_data.loc[
                arrest_mask,
                "_outcome_group"
            ] = "Arrest-Related"

    if "incident_id" in working_data.columns:
        summary = (
            working_data
            .groupby(
                "_outcome_group"
            )["incident_id"]
            .nunique()
            .reindex(
                OUTCOME_ORDER,
                fill_value=0
            )
            .rename(
                "incident_count"
            )
            .reset_index()
        )

    else:
        summary = (
            working_data["_outcome_group"]
            .value_counts()
            .reindex(
                OUTCOME_ORDER,
                fill_value=0
            )
            .rename(
                "incident_count"
            )
            .reset_index()
        )

    summary.columns = [
        "disposition_group",
        "incident_count"
    ]

    summary = summary[
        summary["incident_count"] > 0
    ].copy()

    total_incidents = int(
        summary["incident_count"]
        .sum()
    )

    summary["percentage"] = summary[
        "incident_count"
    ].apply(
        lambda count: safe_percentage(
            count,
            total_incidents
        )
    )

    return summary.sort_values(
        [
            "incident_count",
            "disposition_group"
        ],
        ascending=[
            False,
            True
        ]
    )


def get_outcome_color(outcome):
    """
    Return the semantic color assigned to an outcome group.
    """
    return OUTCOME_COLORS.get(
        outcome,
        "#AAB7C8"
    )


def create_major_outcome_chart(data):
    """
    Create the major case outcome volume chart.
    """
    outcome_summary = prepare_major_outcome_data(
        data
    )

    figure = go.Figure()

    if outcome_summary.empty:
        figure.add_annotation(
            text="Major outcome data is unavailable.",
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
            title="Major Case Outcome Volume",
            height=MAJOR_OUTCOME_CHART_HEIGHT,
            paper_bgcolor="#0B111C",
            plot_bgcolor="#0B111C"
        )

        return figure

    chart_data = outcome_summary.sort_values(
        "incident_count",
        ascending=True
    )

    figure.add_trace(
        go.Bar(
            x=chart_data[
                "incident_count"
            ],
            y=chart_data[
                "disposition_group"
            ],
            orientation="h",
            marker={
                "color": [
                    get_outcome_color(
                        outcome
                    )
                    for outcome in chart_data[
                        "disposition_group"
                    ]
                ]
            },
            customdata=chart_data[
                [
                    "percentage"
                ]
            ],
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Distinct incidents: %{x:,}<br>"
                "Share of selected incidents: %{customdata[0]:.1f}%"
                "<extra></extra>"
            )
        )
    )

    figure.update_layout(
        title={
            "text": "Major Case Outcome Volume",
            "x": 0,
            "xanchor": "left",
            "font": {
                "size": 17,
                "color": "#F8FAFC"
            }
        },
        height=MAJOR_OUTCOME_CHART_HEIGHT,
        margin={
            "l": 170,
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
                "text": "Distinct Incident Count"
            },
            "rangemode": "tozero",
            "gridcolor": "rgba(71, 85, 105, 0.50)",
            "showline": True,
            "linecolor": "#334155"
        },
        yaxis={
            "title": {
                "text": ""
            },
            "showgrid": False,
            "automargin": True
        }
    )

    return figure


def prepare_detailed_disposition_data(
    data,
    maximum_categories=TOP_DETAILED_DISPOSITIONS
):
    """
    Prepare distinct incident counts by detailed disposition.
    """
    if data is None or data.empty:
        return pd.DataFrame()

    disposition_column = get_detail_disposition_column(
        data
    )

    if disposition_column is None:
        return pd.DataFrame()

    selected_columns = [
        disposition_column
    ]

    if "incident_id" in data.columns:
        selected_columns.append(
            "incident_id"
        )

    working_data = data[
        selected_columns
    ].copy()

    working_data[disposition_column] = (
        working_data[disposition_column]
        .apply(
            clean_category_value
        )
    )

    if "incident_id" in working_data.columns:
        summary = (
            working_data
            .groupby(
                disposition_column
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
                disposition_column
            )
            .size()
            .reset_index(
                name="incident_count"
            )
        )

    summary = (
        summary
        .sort_values(
            [
                "incident_count",
                disposition_column
            ],
            ascending=[
                False,
                True
            ]
        )
        .head(
            maximum_categories
        )
        .rename(
            columns={
                disposition_column: "disposition"
            }
        )
    )

    summary["display_disposition"] = (
        summary["disposition"]
        .apply(
            shorten_label
        )
    )

    return summary


def create_detailed_disposition_chart(data):
    """
    Create the detailed disposition volume chart.
    """
    disposition_summary = prepare_detailed_disposition_data(
        data
    )

    figure = go.Figure()

    if disposition_summary.empty:
        figure.add_annotation(
            text="Detailed disposition data is unavailable.",
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
            title="Detailed Disposition Volume",
            height=DETAILED_OUTCOME_CHART_HEIGHT,
            paper_bgcolor="#0B111C",
            plot_bgcolor="#0B111C"
        )

        return figure

    chart_data = disposition_summary.sort_values(
        "incident_count",
        ascending=True
    )

    figure.add_trace(
        go.Bar(
            x=chart_data[
                "incident_count"
            ],
            y=chart_data[
                "display_disposition"
            ],
            orientation="h",
            marker={
                "color": "#C5D3E3",
                "line": {
                    "color": "#AAB7C8",
                    "width": 1
                }
            },
            customdata=chart_data[
                [
                    "disposition"
                ]
            ],
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Distinct incidents: %{x:,}"
                "<extra></extra>"
            )
        )
    )

    figure.update_layout(
        title={
            "text": "Detailed Disposition Volume",
            "x": 0,
            "xanchor": "left",
            "font": {
                "size": 17,
                "color": "#F8FAFC"
            }
        },
        height=DETAILED_OUTCOME_CHART_HEIGHT,
        margin={
            "l": 205,
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
                "text": "Distinct Incident Count"
            },
            "rangemode": "tozero",
            "gridcolor": "rgba(71, 85, 105, 0.50)",
            "showline": True,
            "linecolor": "#334155"
        },
        yaxis={
            "title": {
                "text": ""
            },
            "showgrid": False,
            "automargin": True
        }
    )

    return figure


def prepare_crime_outcome_composition(data):
    """
    Prepare normalized outcome composition by crime group.

    Rules:
    - only crime groups with at least the minimum incident count are used
    - only the highest-volume eligible groups are displayed
    - each row uses all incidents in that crime group as the denominator
    """
    required_columns = {
        "crime_group",
        "disposition_group"
    }

    if (
        data is None
        or data.empty
        or not required_columns.issubset(
            data.columns
        )
    ):
        return {
            "count_data": pd.DataFrame(),
            "percentage_data": pd.DataFrame(),
            "crime_totals": pd.Series(
                dtype=int
            )
        }

    selected_columns = [
        "crime_group",
        "disposition_group"
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

    working_data["outcome_group"] = (
        working_data["disposition_group"]
        .apply(
            normalize_outcome_label
        )
    )

    if "incident_id" in working_data.columns:
        crime_totals_all = (
            working_data
            .groupby(
                "crime_group"
            )["incident_id"]
            .nunique()
            .sort_values(
                ascending=False
            )
        )

    else:
        crime_totals_all = (
            working_data[
                "crime_group"
            ]
            .value_counts()
        )

    eligible_crime_groups = (
        crime_totals_all[
            crime_totals_all
            >= MINIMUM_CRIME_GROUP_RECORDS
        ]
        .head(
            TOP_CRIME_GROUPS
        )
        .index
        .tolist()
    )

    if not eligible_crime_groups:
        return {
            "count_data": pd.DataFrame(),
            "percentage_data": pd.DataFrame(),
            "crime_totals": pd.Series(
                dtype=int
            )
        }

    eligible_data = working_data[
        working_data["crime_group"].isin(
            eligible_crime_groups
        )
    ].copy()

    if "incident_id" in eligible_data.columns:
        grouped_counts = (
            eligible_data
            .groupby(
                [
                    "crime_group",
                    "outcome_group"
                ]
            )["incident_id"]
            .nunique()
            .reset_index(
                name="incident_count"
            )
        )

    else:
        grouped_counts = (
            eligible_data
            .groupby(
                [
                    "crime_group",
                    "outcome_group"
                ]
            )
            .size()
            .reset_index(
                name="incident_count"
            )
        )

    count_data = (
        grouped_counts
        .pivot(
            index="crime_group",
            columns="outcome_group",
            values="incident_count"
        )
        .fillna(0)
        .reindex(
            index=eligible_crime_groups,
            columns=[
                outcome
                for outcome in OUTCOME_ORDER
                if outcome in grouped_counts[
                    "outcome_group"
                ].unique()
            ],
            fill_value=0
        )
        .astype(int)
    )

    crime_totals = count_data.sum(
        axis=1
    )

    percentage_data = (
        count_data
        .div(
            crime_totals.replace(
                0,
                pd.NA
            ),
            axis=0
        )
        .fillna(0)
        * 100
    )

    crime_order = (
        crime_totals
        .sort_values(
            ascending=True
        )
        .index
        .tolist()
    )

    count_data = count_data.reindex(
        crime_order
    )

    percentage_data = percentage_data.reindex(
        crime_order
    )

    crime_totals = crime_totals.reindex(
        crime_order
    )

    return {
        "count_data": count_data,
        "percentage_data": percentage_data,
        "crime_totals": crime_totals
    }


def create_crime_outcome_composition_chart(data):
    """
    Create a 100% stacked outcome composition chart.
    """
    composition = prepare_crime_outcome_composition(
        data
    )

    count_data = composition[
        "count_data"
    ]

    percentage_data = composition[
        "percentage_data"
    ]

    crime_totals = composition[
        "crime_totals"
    ]

    figure = go.Figure()

    if percentage_data.empty:
        figure.add_annotation(
            text=(
                "No crime groups meet the minimum incident threshold "
                "for outcome composition analysis."
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
            title="Outcome Composition by Crime Group",
            height=OUTCOME_COMPOSITION_CHART_HEIGHT,
            paper_bgcolor="#0B111C",
            plot_bgcolor="#0B111C"
        )

        return figure

    display_labels = {
        crime_group: (
            f"{crime_group} "
            f"(n={format_number(crime_totals.loc[crime_group])})"
        )
        for crime_group in percentage_data.index
    }

    for outcome in percentage_data.columns:
        figure.add_trace(
            go.Bar(
                y=[
                    display_labels[
                        crime_group
                    ]
                    for crime_group in percentage_data.index
                ],
                x=percentage_data[
                    outcome
                ],
                name=outcome,
                orientation="h",
                marker={
                    "color": get_outcome_color(
                        outcome
                    )
                },
                customdata=[
                    [
                        int(
                            count_data.loc[
                                crime_group,
                                outcome
                            ]
                        ),
                        int(
                            crime_totals.loc[
                                crime_group
                            ]
                        ),
                        crime_group
                    ]
                    for crime_group in percentage_data.index
                ],
                hovertemplate=(
                    "<b>%{customdata[2]}</b><br>"
                    f"Outcome: {outcome}<br>"
                    "Share within crime group: %{x:.1f}%<br>"
                    "Distinct incidents: %{customdata[0]:,}<br>"
                    "Crime-group total: %{customdata[1]:,}"
                    "<extra></extra>"
                )
            )
        )

    figure.update_layout(
        title={
            "text": "Outcome Composition by Crime Group",
            "x": 0,
            "xanchor": "left",
            "font": {
                "size": 17,
                "color": "#F8FAFC"
            }
        },
        barmode="stack",
        height=OUTCOME_COMPOSITION_CHART_HEIGHT,
        margin={
            "l": 220,
            "r": 30,
            "t": 90,
            "b": 60
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
                "size": 10,
                "color": "#E2E8F0"
            }
        },
        xaxis={
            "title": {
                "text": "Share of Crime-Group Incidents"
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
            "showgrid": False,
            "automargin": True
        }
    )

    return figure


def get_major_outcome_count(
    outcome_data,
    outcome
):
    """
    Return one major outcome count.
    """
    matching_rows = outcome_data[
        outcome_data["disposition_group"]
        == outcome
    ]

    if matching_rows.empty:
        return 0

    return int(
        matching_rows.iloc[
            0
        ][
            "incident_count"
        ]
    )


def show_outcome_summary(data):
    """
    Display compact case outcome summary metrics.
    """
    total_incidents = distinct_incident_count(
        data
    )

    outcome_data = prepare_major_outcome_data(
        data
    )

    closed_count = get_major_outcome_count(
        outcome_data,
        "Closed / Cleared"
    )

    pending_count = get_major_outcome_count(
        outcome_data,
        "Pending / Active"
    )

    arrest_count = get_major_outcome_count(
        outcome_data,
        "Arrest-Related"
    )

    closed_percentage = safe_percentage(
        closed_count,
        total_incidents
    )

    pending_percentage = safe_percentage(
        pending_count,
        total_incidents
    )

    arrest_percentage = safe_percentage(
        arrest_count,
        total_incidents
    )

    top_outcome_group = "N/A"
    top_outcome_count = 0

    if not outcome_data.empty:
        top_row = outcome_data.sort_values(
            "incident_count",
            ascending=False
        ).iloc[
            0
        ]

        top_outcome_group = top_row[
            "disposition_group"
        ]

        top_outcome_count = int(
            top_row[
                "incident_count"
            ]
        )

    detail_column = get_detail_disposition_column(
        data
    )

    if detail_column:
        (
            top_detailed_disposition,
            detailed_count
        ) = get_top_value(
            data,
            detail_column
        )

    else:
        top_detailed_disposition = "N/A"
        detailed_count = 0

    overview_items = [
        {
            "label": "Selected Incidents",
            "value": format_number(
                total_incidents
            ),
            "meta": "Distinct filtered incidents",
            "numeric": True,
            "metric_key": "selected_incidents"
        },
        {
            "label": "Closed / Cleared",
            "value": format_percentage(
                closed_percentage
            ),
            "meta": (
                f"{format_number(closed_count)} incidents"
            ),
            "numeric": True,
            "metric_key": "closed_share"
        },
        {
            "label": "Pending / Active",
            "value": format_percentage(
                pending_percentage
            ),
            "meta": (
                f"{format_number(pending_count)} incidents"
            ),
            "numeric": True,
            "metric_key": "pending_share"
        },
        {
            "label": "Arrest-Related Outcome",
            "value": format_percentage(
                arrest_percentage
            ),
            "meta": (
                f"{format_number(arrest_count)} incidents"
            ),
            "numeric": True,
            "metric_key": "arrest_related_share"
        },
        {
            "label": "Top Outcome Group",
            "value": top_outcome_group,
            "meta": "Leading major outcome",
            "badge": format_number(
                top_outcome_count
            )
        },
        {
            "label": "Top Disposition",
            "value": shorten_label(
                top_detailed_disposition,
                maximum_length=30
            ),
            "meta": "Source disposition value",
            "badge": format_number(
                detailed_count
            ),
        }
    ]

    show_compact_overview_strip(
        overview_items
    )

    show_insight(
        f"{format_percentage(closed_percentage)} of selected incidents "
        f"are closed or cleared, "
        f"{format_percentage(pending_percentage)} are pending or active, "
        f"and {format_percentage(arrest_percentage)} have an "
        f"arrest-related outcome classification."
    )

    show_info_hint(
        "Methodology",
        (
        "Outcome percentages use distinct selected incidents. "
        "Arrest-related outcome comes from the incident disposition field, "
        "while arrest match coverage is calculated by linking incident and "
        "arrest records. Source abbreviations such as CBE are retained "
        "without interpretation unless officially confirmed."
        )
    )

    return {
        "total_incidents": total_incidents,
        "top_outcome_group": top_outcome_group,
        "top_outcome_count": top_outcome_count,
        "top_detailed_disposition": top_detailed_disposition,
        "detailed_count": detailed_count,
        "closed_count": closed_count,
        "pending_count": pending_count,
        "arrest_count": arrest_count,
        "closed_percentage": closed_percentage,
        "pending_percentage": pending_percentage,
        "arrest_percentage": arrest_percentage
    }


def show_outcome_volume_charts(
    data,
    summary
):
    """
    Display major and detailed disposition charts.
    """
    major_chart = create_major_outcome_chart(
        data
    )

    detailed_chart = create_detailed_disposition_chart(
        data
    )

    chart_left, chart_right = st.columns(
        2,
        gap="small"
    )

    with chart_left:
        st.plotly_chart(
            major_chart,
            use_container_width=True,
            key="outcomes_major_outcome_chart",
            config=get_chart_config()
        )

    with chart_right:
        st.plotly_chart(
            detailed_chart,
            use_container_width=True,
            key="outcomes_detailed_disposition_chart",
            config=get_chart_config()
        )

    insight_left, insight_right = st.columns(
        2,
        gap="small"
    )

    with insight_left:
        show_insight(
            f"{summary['top_outcome_group']} is the leading major outcome "
            f"with {format_number(summary['top_outcome_count'])} distinct "
            f"incidents."
        )

    with insight_right:
        show_insight(
            f"{summary['top_detailed_disposition']} is the most common "
            f"detailed source disposition with "
            f"{format_number(summary['detailed_count'])} records."
        )


def get_strongest_outcome_concentration(data):
    """
    Return the highest eligible crime-group outcome concentration.
    """
    composition = prepare_crime_outcome_composition(
        data
    )

    percentage_data = composition[
        "percentage_data"
    ]

    count_data = composition[
        "count_data"
    ]

    crime_totals = composition[
        "crime_totals"
    ]

    if percentage_data.empty:
        return {
            "crime_group": "N/A",
            "outcome": "N/A",
            "percentage": 0.0,
            "count": 0,
            "crime_total": 0
        }

    stacked_data = (
        percentage_data
        .stack()
        .reset_index()
    )

    stacked_data.columns = [
        "crime_group",
        "outcome",
        "percentage"
    ]

    strongest_row = stacked_data.sort_values(
        [
            "percentage",
            "crime_group"
        ],
        ascending=[
            False,
            True
        ]
    ).iloc[
        0
    ]

    crime_group = strongest_row[
        "crime_group"
    ]

    outcome = strongest_row[
        "outcome"
    ]

    return {
        "crime_group": crime_group,
        "outcome": outcome,
        "percentage": float(
            strongest_row[
                "percentage"
            ]
        ),
        "count": int(
            count_data.loc[
                crime_group,
                outcome
            ]
        ),
        "crime_total": int(
            crime_totals.loc[
                crime_group
            ]
        )
    }


def show_outcome_composition_chart(data):
    """
    Display normalized outcome composition across eligible crime groups.
    """
    show_info_hint(
        "Normalized composition",
        (
            "Each crime-group bar totals 100% of all distinct incidents in "
            "that crime group. Every segment shows the share assigned to the "
            "corresponding outcome category."
        )
    )

    # show_info_hint(
    #     "Minimum sample threshold",
    #     (
    #         f"Only crime groups with at least "
    #         f"{MINIMUM_CRIME_GROUP_RECORDS} distinct selected incidents are "
    #         "displayed. The group total is shown beside each chart label."
    #     )
    # )

    composition_chart = create_crime_outcome_composition_chart(
        data
    )

    st.plotly_chart(
        composition_chart,
        use_container_width=True,
        key="outcomes_crime_group_composition_chart",
        config=get_chart_config()
    )

    strongest = get_strongest_outcome_concentration(
        data
    )

    if strongest[
        "crime_group"
    ] == "N/A":
        show_insight(
            "No crime groups meet the minimum sample threshold for "
            "outcome-composition analysis."
        )

        return

    show_insight(
        f"{strongest['crime_group']} has the highest displayed outcome "
        f"concentration: {format_percentage(strongest['percentage'])} "
        f"are classified as {strongest['outcome']}, based on "
        f"{format_number(strongest['count'])} of "
        f"{format_number(strongest['crime_total'])} distinct incidents."
    )


def show_incident_outcomes(data):
    """
    Display the complete case outcome section.
    """
    show_section_banner(
        eyebrow="Resolution Intelligence",
        title="Case Resolution Profile",
        description=(
            "Compare major and detailed dispositions, then examine outcome "
            "composition across sufficiently large crime groups."
        )
    )

    summary = show_outcome_summary(
        data
    )

    # st.divider()

    show_outcome_volume_charts(
        data,
        summary
    )

    show_outcome_composition_chart(
        data
    )