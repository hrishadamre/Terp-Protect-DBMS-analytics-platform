"""
incident_outcomes.py

Purpose:
Display the case resolution profile section for the Terp Protect dashboard.

Responsibilities:
- Summarize arrest-related, pending, and closed outcomes
- Compare major and detailed dispositions
- Show crime-group and outcome relationships
"""

import pandas as pd
import streamlit as st

from components.charts import (
    create_crime_disposition_heatmap,
    create_horizontal_bar_chart,
    create_soft_donut_chart,
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


PRIMARY_CHART_HEIGHT = 455
HEATMAP_HEIGHT = 520


def standardize_chart_height(
    figure,
    height=PRIMARY_CHART_HEIGHT
):
    """
    Apply consistent height and margins to paired charts.
    """
    figure.update_layout(
        height=height,
        margin={
            "l": 58,
            "r": 22,
            "t": 68,
            "b": 48
        }
    )

    return figure


def safe_binary_sum(
    data,
    column
):
    """
    Safely sum a binary indicator column.
    """
    if (
        data.empty
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


def calculate_share(
    count,
    total
):
    """
    Calculate a safe percentage.
    """
    if total == 0:
        return 0.0

    return count / total * 100


def show_outcome_summary(data):
    """
    Display compact case-resolution summary cards.
    """
    total_incidents = len(data)

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

    arrest_percentage = calculate_share(
        arrest_count,
        total_incidents
    )

    pending_percentage = calculate_share(
        pending_count,
        total_incidents
    )

    closed_percentage = calculate_share(
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
            "label": "Arrest-Related",
            "value": format_percentage(
                arrest_percentage
            ),
            "meta": f"{format_number(arrest_count)} records",
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
            "label": "Closed / Cleared",
            "value": format_percentage(
                closed_percentage
            ),
            "meta": f"{format_number(closed_count)} records",
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
            "value": top_detailed_disposition,
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

    return {
        "top_disposition": top_disposition,
        "disposition_count": disposition_count,
        "top_detailed_disposition": top_detailed_disposition,
        "detailed_count": detailed_count
    }


def show_major_outcome_charts(
    data,
    summary
):
    """
    Display major outcome volume and composition.
    """
    outcome_summary = (
        data.groupby(
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

    outcome_bar_chart = standardize_chart_height(
        create_status_bar_chart(
            data=data,
            group_column="disposition_group",
            title="Case Outcome Volume",
            count_label="Incident Count"
        )
    )

    outcome_donut_chart = standardize_chart_height(
        create_soft_donut_chart(
            data=outcome_summary,
            label_column="disposition_group",
            value_column="incident_count",
            title="Outcome Share"
        )
    )

    chart_left, chart_right = st.columns(
        2,
        gap="small"
    )

    with chart_left:
        st.plotly_chart(
            outcome_bar_chart,
            use_container_width=True,
            key="outcomes_disposition_group_chart",
            config=get_chart_config()
        )

    with chart_right:
        st.plotly_chart(
            outcome_donut_chart,
            use_container_width=True,
            key="outcomes_share_donut_chart",
            config=get_chart_config()
        )

    insight_left, insight_right = st.columns(
        2,
        gap="small"
    )

    with insight_left:
        show_insight(
            f"{summary['top_disposition']} is the leading major "
            f"outcome with "
            f"{format_number(summary['disposition_count'])} records."
        )

    with insight_right:
        show_insight(
            "The composition view shows the relative share of each "
            "major outcome group within the current filtered selection."
        )


def show_detailed_outcome_charts(
    data,
    summary
):
    """
    Display detailed dispositions and crime-group context.
    """
    detailed_chart = standardize_chart_height(
        create_horizontal_bar_chart(
            data=data,
            group_column="disposition",
            title="Detailed Disposition Volume",
            max_categories=15,
            count_label="Incident Count",
            chart_type="neutral"
        )
    )

    crime_group_chart = standardize_chart_height(
        create_horizontal_bar_chart(
            data=data,
            group_column="crime_group",
            title="Incident Volume by Crime Group",
            max_categories=15,
            count_label="Incident Count",
            chart_type="incident_soft"
        )
    )

    top_crime_group, crime_group_count = get_top_value(
        data,
        "crime_group"
    )

    chart_left, chart_right = st.columns(
        2,
        gap="small"
    )

    with chart_left:
        st.plotly_chart(
            detailed_chart,
            use_container_width=True,
            key="outcomes_detailed_disposition_chart",
            config=get_chart_config()
        )

    with chart_right:
        st.plotly_chart(
            crime_group_chart,
            use_container_width=True,
            key="outcomes_crime_group_chart",
            config=get_chart_config()
        )

    insight_left, insight_right = st.columns(
        2,
        gap="small"
    )

    with insight_left:
        show_insight(
            f"{summary['top_detailed_disposition']} is the most "
            f"common detailed disposition with "
            f"{format_number(summary['detailed_count'])} records."
        )

    with insight_right:
        show_insight(
            f"{top_crime_group} is the highest-volume crime group "
            f"in this outcome view with "
            f"{format_number(crime_group_count)} incidents."
        )


def show_outcome_heatmap(data):
    """
    Display crime-group and outcome relationships.
    """
    heatmap = create_crime_disposition_heatmap(
        data
    )

    heatmap.update_layout(
        height=HEATMAP_HEIGHT
    )

    st.plotly_chart(
        heatmap,
        use_container_width=True,
        key="outcomes_crime_disposition_heatmap",
        config=get_chart_config()
    )

    show_insight(
        "The heatmap shows which crime groups contribute most strongly "
        "to each outcome category and where outcome patterns differ."
    )


def show_incident_outcomes(data):
    """
    Display the complete case-resolution section.
    """
    show_section_banner(
        eyebrow="",
        title="Case Resolution Profile",
        description=(
            "Compare arrest-related, pending, active, closed, cleared, "
            "and detailed disposition outcomes in the selected records."
        )
    )

    summary = show_outcome_summary(
        data
    )

    st.divider()

    show_major_outcome_charts(
        data,
        summary
    )

    show_detailed_outcome_charts(
        data,
        summary
    )

    show_outcome_heatmap(
        data
    )