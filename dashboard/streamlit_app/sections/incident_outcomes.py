"""
incident_outcomes.py

Purpose:
Display the case resolution profile for the Terp Protect dashboard.

Responsibilities:
- Summarize arrest-related, pending, and closed outcomes
- Display major case-outcome volume
- Display detailed disposition volume
- Compare normalized outcome composition across major crime groups
- Avoid repeating general crime-group volume charts
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

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
OUTCOME_COMPOSITION_CHART_HEIGHT = 530

TOP_DETAILED_DISPOSITIONS = 15
TOP_CRIME_GROUPS = 10


OUTCOME_ORDER = [
    "Closed / Cleared",
    "Pending / Active",
    "Arrest-Related",
    "Other"
]


OUTCOME_COLORS = {
    "Closed / Cleared": "#6AC7B6",
    "Pending / Active": "#F2CC68",
    "Arrest-Related": "#E78A98",
    "Other": "#AAB7C8"
}


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
    Shorten long chart labels while preserving full values in hover.
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


def prepare_major_outcome_data(data):
    """
    Prepare incident counts by major disposition group.
    """
    if (
        data is None
        or data.empty
        or "disposition_group" not in data.columns
    ):
        return pd.DataFrame()

    outcome_data = data[
        [
            "disposition_group"
        ]
    ].copy()

    outcome_data["disposition_group"] = (
        outcome_data["disposition_group"]
        .apply(
            clean_category_value
        )
    )

    outcome_summary = (
        outcome_data
        .groupby(
            "disposition_group"
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

    total_incidents = outcome_summary[
        "incident_count"
    ].sum()

    outcome_summary["percentage"] = (
        outcome_summary["incident_count"]
        / total_incidents
        * 100
        if total_incidents > 0
        else 0.0
    )

    return outcome_summary


def get_outcome_color(outcome):
    """
    Return a semantic color based on the outcome label.
    """
    normalized_outcome = str(
        outcome
    ).strip().lower()

    if any(
        keyword in normalized_outcome
        for keyword in [
            "closed",
            "cleared"
        ]
    ):
        return "#6AC7B6"

    if any(
        keyword in normalized_outcome
        for keyword in [
            "pending",
            "active"
        ]
    ):
        return "#F2CC68"

    if "arrest" in normalized_outcome:
        return "#E78A98"

    return "#AAB7C8"


def create_major_outcome_chart(data):
    """
    Create the major case-outcome volume chart.
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

    colors = [
        get_outcome_color(
            outcome
        )
        for outcome in chart_data[
            "disposition_group"
        ]
    ]

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
                "color": colors,
                "line": {
                    "color": "rgba(255, 255, 255, 0.10)",
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
                "text": "Incident Count"
            },
            "rangemode": "tozero",
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
            "showgrid": False,
            "automargin": True,
            "tickfont": {
                "size": 10,
                "color": "#CBD5E1"
            }
        }
    )

    return figure


def prepare_detailed_disposition_data(
    data,
    maximum_categories=TOP_DETAILED_DISPOSITIONS
):
    """
    Prepare the highest-volume detailed dispositions.
    """
    if (
        data is None
        or data.empty
        or "disposition" not in data.columns
    ):
        return pd.DataFrame()

    disposition_data = data[
        [
            "disposition"
        ]
    ].copy()

    disposition_data["disposition"] = (
        disposition_data["disposition"]
        .apply(
            clean_category_value
        )
    )

    disposition_summary = (
        disposition_data
        .groupby(
            "disposition"
        )
        .size()
        .reset_index(
            name="incident_count"
        )
        .sort_values(
            [
                "incident_count",
                "disposition"
            ],
            ascending=[
                False,
                True
            ]
        )
        .head(
            maximum_categories
        )
    )

    disposition_summary["display_disposition"] = (
        disposition_summary["disposition"]
        .apply(
            shorten_label
        )
    )

    return disposition_summary


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
                "Incidents: %{x:,}"
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
                "text": "Incident Count"
            },
            "rangemode": "tozero",
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
            "showgrid": False,
            "automargin": True,
            "tickfont": {
                "size": 10,
                "color": "#CBD5E1"
            }
        }
    )

    return figure


def prepare_crime_outcome_composition(data):
    """
    Prepare a normalized crime-group outcome composition table.

    Each crime-group row sums to 100%, making outcome patterns
    comparable even when crime groups have different total volumes.
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
            "crime_totals": pd.Series(dtype=int)
        }

    working_data = data[
        [
            "crime_group",
            "disposition_group"
        ]
    ].copy()

    working_data["crime_group"] = (
        working_data["crime_group"]
        .apply(
            clean_category_value
        )
    )

    working_data["disposition_group"] = (
        working_data["disposition_group"]
        .apply(
            clean_category_value
        )
    )

    top_crime_groups = (
        working_data[
            "crime_group"
        ]
        .value_counts()
        .head(
            TOP_CRIME_GROUPS
        )
        .index
        .tolist()
    )

    filtered_data = working_data[
        working_data["crime_group"].isin(
            top_crime_groups
        )
    ].copy()

    if filtered_data.empty:
        return {
            "count_data": pd.DataFrame(),
            "percentage_data": pd.DataFrame(),
            "crime_totals": pd.Series(dtype=int)
        }

    count_data = pd.crosstab(
        filtered_data[
            "crime_group"
        ],
        filtered_data[
            "disposition_group"
        ]
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


def get_ordered_outcome_columns(available_columns):
    """
    Arrange outcome columns in a meaningful semantic order.

    Any source-specific categories not recognized are appended after
    the main semantic categories.
    """
    ordered_columns = []

    semantic_matches = {
        "Closed / Cleared": [],
        "Pending / Active": [],
        "Arrest-Related": [],
        "Other": []
    }

    for column in available_columns:
        normalized_column = str(
            column
        ).strip().lower()

        if any(
            keyword in normalized_column
            for keyword in [
                "closed",
                "cleared"
            ]
        ):
            semantic_matches[
                "Closed / Cleared"
            ].append(
                column
            )

        elif any(
            keyword in normalized_column
            for keyword in [
                "pending",
                "active"
            ]
        ):
            semantic_matches[
                "Pending / Active"
            ].append(
                column
            )

        elif "arrest" in normalized_column:
            semantic_matches[
                "Arrest-Related"
            ].append(
                column
            )

        else:
            semantic_matches[
                "Other"
            ].append(
                column
            )

    for semantic_group in OUTCOME_ORDER:
        ordered_columns.extend(
            semantic_matches[
                semantic_group
            ]
        )

    return ordered_columns


def create_crime_outcome_composition_chart(data):
    """
    Create a 100% stacked horizontal bar chart showing outcome
    composition for major crime groups.
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
            text="Crime-group outcome composition is unavailable.",
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

    ordered_outcomes = get_ordered_outcome_columns(
        percentage_data.columns.tolist()
    )

    fallback_colors = [
        "#6AC7B6",
        "#F2CC68",
        "#E78A98",
        "#AAB7C8",
        "#8ED8F3",
        "#B6A6E9",
        "#F2B880",
        "#C5D3E3"
    ]

    for index, outcome in enumerate(
        ordered_outcomes
    ):
        outcome_color = get_outcome_color(
            outcome
        )

        if outcome_color == "#AAB7C8":
            outcome_color = fallback_colors[
                index % len(
                    fallback_colors
                )
            ]

        figure.add_trace(
            go.Bar(
                y=percentage_data.index.tolist(),
                x=percentage_data[
                    outcome
                ],
                name=outcome,
                orientation="h",
                marker={
                    "color": outcome_color
                },
                customdata=[
                    [
                        count_data.loc[
                            crime_group,
                            outcome
                        ],
                        crime_totals.loc[
                            crime_group
                        ]
                    ]
                    for crime_group in percentage_data.index
                ],
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    f"Outcome: {outcome}<br>"
                    "Share: %{x:.1f}%<br>"
                    "Incidents: %{customdata[0]:,}<br>"
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
            "l": 175,
            "r": 30,
            "t": 85,
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
            },
            "bgcolor": "rgba(11, 17, 28, 0.65)",
            "bordercolor": "rgba(148, 163, 184, 0.22)",
            "borderwidth": 1
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
            "showgrid": False,
            "automargin": True,
            "tickfont": {
                "size": 10,
                "color": "#CBD5E1"
            }
        }
    )

    return figure


def get_dominant_outcome_by_crime_group(data):
    """
    Return the crime group with the highest share for each major
    outcome category when available.
    """
    composition = prepare_crime_outcome_composition(
        data
    )

    percentage_data = composition[
        "percentage_data"
    ]

    if percentage_data.empty:
        return []

    findings = []

    for outcome in get_ordered_outcome_columns(
        percentage_data.columns.tolist()
    ):
        outcome_values = percentage_data[
            outcome
        ]

        if outcome_values.empty:
            continue

        top_crime_group = outcome_values.idxmax()

        findings.append(
            {
                "outcome": outcome,
                "crime_group": top_crime_group,
                "percentage": float(
                    outcome_values.loc[
                        top_crime_group
                    ]
                )
            }
        )

    return findings


def show_outcome_summary(data):
    """
    Display compact case-resolution summary cards.
    """
    total_incidents = len(
        data
    )

    arrest_count = safe_binary_sum(
        data,
        "is_arrest_related"
    )

    pending_count = safe_binary_sum(
        data,
        "is_pending"
    )

    closed_count = safe_binary_sum(
        data,
        "is_closed"
    )

    arrest_percentage = calculate_percentage(
        arrest_count,
        total_incidents
    )

    pending_percentage = calculate_percentage(
        pending_count,
        total_incidents
    )

    closed_percentage = calculate_percentage(
        closed_count,
        total_incidents
    )

    top_disposition, disposition_count = get_top_value(
        data,
        "disposition_group"
    )

    top_detailed_disposition, detailed_count = get_top_value(
        data,
        "disposition"
    )

    overview_items = [
        {
            "label": "Selected Incidents",
            "value": format_number(
                total_incidents
            ),
            "meta": "Current filtered view",
            "numeric": True
        },
        {
            "label": "Closed / Cleared",
            "value": format_percentage(
                closed_percentage
            ),
            "meta": f"{format_number(closed_count)} records",
            "numeric": True
        },
        {
            "label": "Pending / Active",
            "value": format_percentage(
                pending_percentage
            ),
            "meta": f"{format_number(pending_count)} records",
            "numeric": True
        },
        {
            "label": "Arrest-Related",
            "value": format_percentage(
                arrest_percentage
            ),
            "meta": f"{format_number(arrest_count)} records",
            "numeric": True
        },
        {
            "label": "Top Outcome Group",
            "value": top_disposition,
            "meta": "Leading major outcome",
            "badge": format_number(
                disposition_count
            )
        },
        {
            "label": "Top Disposition",
            "value": shorten_label(
                top_detailed_disposition,
                maximum_length=30
            ),
            "meta": "Leading detailed value",
            "badge": format_number(
                detailed_count
            )
        }
    ]

    show_compact_overview_strip(
        overview_items
    )

    show_insight(
        f"{format_percentage(closed_percentage)} of selected incidents "
        f"are closed or cleared, "
        f"{format_percentage(pending_percentage)} are pending or active, "
        f"and {format_percentage(arrest_percentage)} are arrest-related."
    )

    show_info_hint(
        "Disposition terminology",
        (
            "Detailed dispositions may contain source-specific codes "
            "or abbreviations. Interpret them using the official UMPD "
            "source definitions or project data dictionary."
        )
    )

    return {
        "top_disposition": top_disposition,
        "disposition_count": disposition_count,
        "top_detailed_disposition": top_detailed_disposition,
        "detailed_count": detailed_count,
        "arrest_count": arrest_count,
        "pending_count": pending_count,
        "closed_count": closed_count,
        "arrest_percentage": arrest_percentage,
        "pending_percentage": pending_percentage,
        "closed_percentage": closed_percentage
    }


def show_outcome_volume_charts(
    data,
    summary
):
    """
    Display major and detailed outcome volume charts.
    """
    major_outcome_chart = create_major_outcome_chart(
        data
    )

    detailed_outcome_chart = create_detailed_disposition_chart(
        data
    )

    chart_left, chart_right = st.columns(
        2,
        gap="small"
    )

    with chart_left:
        st.plotly_chart(
            major_outcome_chart,
            use_container_width=True,
            key="outcomes_major_outcome_chart",
            config={
                "displaylogo": False,
                "responsive": True
            }
        )

    with chart_right:
        st.plotly_chart(
            detailed_outcome_chart,
            use_container_width=True,
            key="outcomes_detailed_disposition_chart",
            config={
                "displaylogo": False,
                "responsive": True
            }
        )

    insight_left, insight_right = st.columns(
        2,
        gap="small"
    )

    with insight_left:
        show_insight(
            f"{summary['top_disposition']} is the leading major "
            f"outcome category with "
            f"{format_number(summary['disposition_count'])} records."
        )

    with insight_right:
        show_insight(
            f"{summary['top_detailed_disposition']} is the most "
            f"common detailed disposition with "
            f"{format_number(summary['detailed_count'])} records."
        )


def show_outcome_composition_chart(data):
    """
    Display normalized outcome composition across crime groups.
    """
    composition_chart = create_crime_outcome_composition_chart(
        data
    )

    st.plotly_chart(
        composition_chart,
        use_container_width=True,
        key="outcomes_crime_group_composition_chart",
        config={
            "displaylogo": False,
            "responsive": True
        }
    )

    findings = get_dominant_outcome_by_crime_group(
        data
    )

    if not findings:
        show_insight(
            "Crime-group outcome composition is unavailable for the "
            "current filtered selection."
        )

        return

    leading_finding = max(
        findings,
        key=lambda item: item[
            "percentage"
        ]
    )

    show_insight(
        f"{leading_finding['crime_group']} has the strongest observed "
        f"concentration in the "
        f"{leading_finding['outcome']} outcome category, where it "
        f"represents {leading_finding['percentage']:.1f}% of that "
        f"crime group's selected incidents."
    )


def show_incident_outcomes(data):
    """
    Display the complete case-resolution section.
    """
    show_section_banner(
        eyebrow="Resolution Intelligence",
        title="Case Resolution Profile",
        description=(
            "Compare major and detailed dispositions, then examine how "
            "outcome composition differs across high-volume crime groups."
        )
    )

    summary = show_outcome_summary(
        data
    )

    st.divider()

    show_outcome_volume_charts(
        data,
        summary
    )

    show_outcome_composition_chart(
        data
    )