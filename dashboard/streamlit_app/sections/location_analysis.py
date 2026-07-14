"""
location_analysis.py

Purpose:
Display the campus hotspot profile for the Terp Protect dashboard.

Responsibilities:
- Summarize specific locations and location groups
- Display a map when validated coordinates are available
- Show the highest-volume specific locations
- Compare incident volume across location groups
- Show normalized crime composition within major location groups
"""

import textwrap

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.charts import (
    create_location_map,
    get_chart_config
)
from components.layout import (
    show_compact_overview_strip,
    show_insight,
    show_section_banner
)
from components.metrics import (
    format_number,
    get_top_value
)


TOP_SPECIFIC_LOCATIONS = 12
TOP_LOCATION_GROUPS = 8
TOP_CRIME_GROUPS = 10

PAIR_CHART_HEIGHT = 450
HEATMAP_HEIGHT = 500
MAP_HEIGHT = 560


def get_unique_location_count(data):
    """
    Return the number of distinct non-null specific locations.
    """
    if (
        data is None
        or data.empty
        or "location_raw" not in data.columns
    ):
        return 0

    return int(
        data["location_raw"]
        .dropna()
        .nunique()
    )


def clean_location_value(value):
    """
    Return a cleaned location label.
    """
    if pd.isna(value):
        return "Unknown"

    cleaned_value = str(value).strip()

    if not cleaned_value:
        return "Unknown"

    return cleaned_value


def shorten_label(
    value,
    maximum_length=42
):
    """
    Shorten long labels for chart display.

    The full label remains available in hover information.
    """
    cleaned_value = clean_location_value(value)

    if len(cleaned_value) <= maximum_length:
        return cleaned_value

    return (
        cleaned_value[: maximum_length - 3]
        + "..."
    )


def wrap_label(
    value,
    width=26
):
    """
    Wrap a label for chart display.
    """
    cleaned_value = clean_location_value(value)

    return "<br>".join(
        textwrap.wrap(
            cleaned_value,
            width=width
        )
    )


def prepare_specific_location_data(
    data,
    maximum_locations=TOP_SPECIFIC_LOCATIONS
):
    """
    Prepare the highest-volume specific locations.
    """
    if (
        data is None
        or data.empty
        or "location_raw" not in data.columns
    ):
        return pd.DataFrame()

    location_data = data[
        ["location_raw"]
    ].copy()

    location_data["location_raw"] = (
        location_data["location_raw"]
        .apply(clean_location_value)
    )

    location_summary = (
        location_data
        .groupby("location_raw")
        .size()
        .reset_index(name="incident_count")
        .sort_values(
            [
                "incident_count",
                "location_raw"
            ],
            ascending=[
                False,
                True
            ]
        )
        .head(maximum_locations)
    )

    location_summary["display_location"] = (
        location_summary["location_raw"]
        .apply(shorten_label)
    )

    return location_summary


def create_specific_location_chart(data):
    """
    Create a readable horizontal bar chart for top locations.
    """
    location_summary = prepare_specific_location_data(data)

    figure = go.Figure()

    if location_summary.empty:
        figure.add_annotation(
            text="Specific location data is unavailable.",
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
            title="Top Specific Locations",
            height=PAIR_CHART_HEIGHT,
            paper_bgcolor="#0B111C",
            plot_bgcolor="#0B111C"
        )

        return figure

    chart_data = location_summary.sort_values(
        "incident_count",
        ascending=True
    )

    figure.add_trace(
        go.Bar(
            x=chart_data["incident_count"],
            y=chart_data["display_location"],
            orientation="h",
            marker={
                "color": "#BEEBFA",
                "line": {
                    "color": "#8ED8F3",
                    "width": 1
                }
            },
            customdata=chart_data[
                ["location_raw"]
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
            "text": "Top Specific Locations",
            "x": 0,
            "xanchor": "left",
            "font": {
                "size": 17,
                "color": "#F8FAFC"
            }
        },
        height=PAIR_CHART_HEIGHT,
        margin={
            "l": 180,
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
            "tickfont": {
                "size": 10,
                "color": "#CBD5E1"
            },
            "automargin": True,
            "showgrid": False
        }
    )

    return figure


def prepare_location_group_data(data):
    """
    Prepare incident counts by location group.
    """
    if (
        data is None
        or data.empty
        or "location_group" not in data.columns
    ):
        return pd.DataFrame()

    location_group_data = data[
        ["location_group"]
    ].copy()

    location_group_data["location_group"] = (
        location_group_data["location_group"]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
        .replace(
            {
                "": "Unknown"
            }
        )
    )

    return (
        location_group_data
        .groupby("location_group")
        .size()
        .reset_index(name="incident_count")
        .sort_values(
            "incident_count",
            ascending=False
        )
    )


def create_location_group_chart(data):
    """
    Create a horizontal bar chart for location-group volume.
    """
    location_group_summary = prepare_location_group_data(data)

    figure = go.Figure()

    if location_group_summary.empty:
        figure.add_annotation(
            text="Location-group data is unavailable.",
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
            title="Incident Volume by Location Group",
            height=PAIR_CHART_HEIGHT,
            paper_bgcolor="#0B111C",
            plot_bgcolor="#0B111C"
        )

        return figure

    chart_data = (
        location_group_summary
        .head(TOP_LOCATION_GROUPS)
        .sort_values(
            "incident_count",
            ascending=True
        )
    )

    figure.add_trace(
        go.Bar(
            x=chart_data["incident_count"],
            y=chart_data["location_group"],
            orientation="h",
            marker={
                "color": "#BEEBFA",
                "line": {
                    "color": "#8ED8F3",
                    "width": 1
                }
            },
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Incidents: %{x:,}"
                "<extra></extra>"
            )
        )
    )

    figure.update_layout(
        title={
            "text": "Incident Volume by Location Group",
            "x": 0,
            "xanchor": "left",
            "font": {
                "size": 17,
                "color": "#F8FAFC"
            }
        },
        height=PAIR_CHART_HEIGHT,
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
            "tickfont": {
                "size": 10,
                "color": "#CBD5E1"
            },
            "automargin": True,
            "showgrid": False
        }
    )

    return figure


def prepare_location_crime_composition(data):
    """
    Prepare normalized crime composition by location group.

    Each row sums to 100%, allowing location groups with different
    total incident volumes to be compared fairly.
    """
    required_columns = {
        "location_group",
        "crime_group"
    }

    if (
        data is None
        or data.empty
        or not required_columns.issubset(data.columns)
    ):
        return {
            "percentage_data": pd.DataFrame(),
            "count_data": pd.DataFrame()
        }

    working_data = data[
        [
            "location_group",
            "crime_group"
        ]
    ].copy()

    for column in required_columns:
        working_data[column] = (
            working_data[column]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
            .replace(
                {
                    "": "Unknown"
                }
            )
        )

    top_location_groups = (
        working_data["location_group"]
        .value_counts()
        .head(TOP_LOCATION_GROUPS)
        .index
        .tolist()
    )

    top_crime_groups = (
        working_data["crime_group"]
        .value_counts()
        .head(TOP_CRIME_GROUPS)
        .index
        .tolist()
    )

    filtered_data = working_data[
        working_data["location_group"].isin(
            top_location_groups
        )
        & working_data["crime_group"].isin(
            top_crime_groups
        )
    ].copy()

    if filtered_data.empty:
        return {
            "percentage_data": pd.DataFrame(),
            "count_data": pd.DataFrame()
        }

    count_data = pd.crosstab(
        filtered_data["location_group"],
        filtered_data["crime_group"]
    )

    count_data = count_data.reindex(
        index=top_location_groups,
        columns=top_crime_groups,
        fill_value=0
    )

    row_totals = count_data.sum(
        axis=1
    ).replace(
        0,
        pd.NA
    )

    percentage_data = (
        count_data
        .div(
            row_totals,
            axis=0
        )
        .fillna(0)
        * 100
    )

    return {
        "percentage_data": percentage_data,
        "count_data": count_data
    }


def create_location_crime_composition_heatmap(data):
    """
    Create a normalized location-by-crime heatmap.
    """
    heatmap_data = prepare_location_crime_composition(data)

    percentage_data = heatmap_data["percentage_data"]
    count_data = heatmap_data["count_data"]

    figure = go.Figure()

    if percentage_data.empty:
        figure.add_annotation(
            text="Location and crime composition data is unavailable.",
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
            title="Crime Composition by Location Group",
            height=HEATMAP_HEIGHT,
            paper_bgcolor="#0B111C",
            plot_bgcolor="#0B111C"
        )

        return figure

    wrapped_crime_labels = [
        wrap_label(
            crime_group,
            width=18
        )
        for crime_group in percentage_data.columns
    ]

    figure.add_trace(
        go.Heatmap(
            z=percentage_data.values,
            x=wrapped_crime_labels,
            y=percentage_data.index.tolist(),
            customdata=count_data.values,
            colorscale=[
                [0.00, "#F3F8FC"],
                [0.20, "#D9ECF7"],
                [0.40, "#B7DBEF"],
                [0.60, "#8FC7E2"],
                [0.80, "#447FA8"],
                [1.00, "#263B67"]
            ],
            colorbar={
                "title": {
                    "text": "Share",
                    "font": {
                        "color": "#F8FAFC"
                    }
                },
                "ticksuffix": "%",
                "tickfont": {
                    "color": "#CBD5E1"
                },
                "outlinecolor": "#475569",
                "outlinewidth": 1
            },
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Crime group: %{x}<br>"
                "Share within location group: %{z:.1f}%<br>"
                "Incidents: %{customdata:,}"
                "<extra></extra>"
            )
        )
    )

    figure.update_layout(
        title={
            "text": "Crime Composition by Location Group",
            "x": 0,
            "xanchor": "left",
            "font": {
                "size": 17,
                "color": "#F8FAFC"
            }
        },
        height=HEATMAP_HEIGHT,
        margin={
            "l": 150,
            "r": 85,
            "t": 70,
            "b": 120
        },
        paper_bgcolor="#0B111C",
        plot_bgcolor="#0B111C",
        font={
            "color": "#F8FAFC"
        },
        xaxis={
            "title": {
                "text": "Crime Group"
            },
            "tickfont": {
                "size": 9,
                "color": "#CBD5E1"
            },
            "tickangle": -35,
            "showgrid": False
        },
        yaxis={
            "title": {
                "text": "Location Group"
            },
            "tickfont": {
                "size": 10,
                "color": "#CBD5E1"
            },
            "showgrid": False,
            "autorange": "reversed"
        }
    )

    return figure


def show_location_summary(data):
    """
    Display compact location summary cards.
    """
    unique_locations = get_unique_location_count(data)

    top_location, top_location_count = get_top_value(
        data,
        "location_raw"
    )

    top_location_group, top_location_group_count = get_top_value(
        data,
        "location_group"
    )

    top_crime_group, top_crime_group_count = get_top_value(
        data,
        "crime_group"
    )

    overview_items = [
        {
            "label": "Selected Incidents",
            "value": format_number(len(data)),
            "meta": "Current filtered view",
            "numeric": True
        },
        {
            "label": "Unique Locations",
            "value": format_number(unique_locations),
            "meta": "Distinct location values",
            "numeric": True
        },
        {
            "label": "Top Location",
            "value": shorten_label(
                top_location,
                maximum_length=30
            ),
            "meta": "Highest specific location",
            "badge": format_number(top_location_count)
        },
        {
            "label": "Top Location Group",
            "value": top_location_group,
            "meta": "Leading location type",
            "badge": format_number(top_location_group_count)
        },
        {
            "label": "Top Crime Group",
            "value": top_crime_group,
            "meta": "Leading incident category",
            "badge": format_number(top_crime_group_count)
        }
    ]

    show_compact_overview_strip(overview_items)

    show_insight(
        f"The selected view contains "
        f"{format_number(unique_locations)} unique location values. "
        f"{top_location} has the highest specific-location volume, "
        f"while {top_location_group} is the leading location group."
    )

    return {
        "unique_locations": unique_locations,
        "top_location": top_location,
        "top_location_count": top_location_count,
        "top_location_group": top_location_group,
        "top_location_group_count": top_location_group_count,
        "top_crime_group": top_crime_group,
        "top_crime_group_count": top_crime_group_count
    }


def show_map_section(data):
    """
    Display a location map when valid coordinates are available.
    """
    map_figure = create_location_map(data)

    if map_figure is None:
        st.info(
            "The map is currently unavailable because validated latitude "
            "and longitude fields are not present in the dashboard dataset. "
            "The ranked location and composition views below remain available."
        )

        return

    map_figure.update_layout(
        height=MAP_HEIGHT
    )

    st.plotly_chart(
        map_figure,
        use_container_width=True,
        key="location_campus_hotspot_map",
        config=get_chart_config()
    )

    show_insight(
        "The map displays incident concentration using validated "
        "location coordinates. Higher-intensity markers represent "
        "locations with more selected incidents."
    )


def show_location_comparison_charts(
    data,
    summary
):
    """
    Display top specific locations and location groups.
    """
    specific_location_chart = create_specific_location_chart(data)
    location_group_chart = create_location_group_chart(data)

    chart_left, chart_right = st.columns(
        2,
        gap="small"
    )

    with chart_left:
        st.plotly_chart(
            specific_location_chart,
            use_container_width=True,
            key="location_top_specific_locations_chart",
            config=get_chart_config()
        )

    with chart_right:
        st.plotly_chart(
            location_group_chart,
            use_container_width=True,
            key="location_group_volume_chart",
            config=get_chart_config()
        )

    insight_left, insight_right = st.columns(
        2,
        gap="small"
    )

    with insight_left:
        show_insight(
            f"{summary['top_location']} is the highest-volume "
            f"specific location with "
            f"{format_number(summary['top_location_count'])} incidents."
        )

    with insight_right:
        show_insight(
            f"{summary['top_location_group']} is the leading "
            f"location group with "
            f"{format_number(summary['top_location_group_count'])} "
            f"incidents."
        )


def show_location_crime_heatmap(
    data,
    summary
):
    """
    Display normalized crime composition by location group.
    """
    heatmap = create_location_crime_composition_heatmap(data)

    st.plotly_chart(
        heatmap,
        use_container_width=True,
        key="location_crime_composition_heatmap",
        config=get_chart_config()
    )

    show_insight(
        f"The heatmap compares crime composition within each major "
        f"location group rather than only raw volume. "
        f"{summary['top_crime_group']} remains the leading overall "
        f"crime group with "
        f"{format_number(summary['top_crime_group_count'])} incidents."
    )


def show_location_analysis(data):
    """
    Display the complete location hotspot section.
    """
    show_section_banner(
        eyebrow="Spatial Intelligence",
        title="Campus Hotspot Profile",
        description=(
            "Identify high-activity locations, compare campus location "
            "types, and examine crime composition across major location groups."
        )
    )

    summary = show_location_summary(data)

    st.divider()

    show_map_section(data)

    show_location_comparison_charts(
        data,
        summary
    )

    show_location_crime_heatmap(
        data,
        summary
    )