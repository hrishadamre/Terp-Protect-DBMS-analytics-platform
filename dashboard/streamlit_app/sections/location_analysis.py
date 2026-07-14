"""
location_analysis.py

Purpose:
Display location-based incident patterns for the Terp Protect dashboard.

Responsibilities:
- Summarize distinct locations and location groups
- Display a map when validated coordinates are available
- Rank high-volume specific locations
- Compare incident volume across location groups
- Show complete crime composition within major location groups
- Apply minimum sample thresholds to normalized comparisons
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
    show_info_hint,
    show_insight,
    show_section_banner
)
from components.metrics import (
    format_number,
    format_percentage,
    get_top_value
)


TOP_SPECIFIC_LOCATIONS = 12
TOP_LOCATION_GROUPS = 8

TOP_DISPLAYED_CRIME_GROUPS = 9
OTHER_CRIME_GROUP_LABEL = "Other Crime Groups"

MINIMUM_LOCATION_GROUP_RECORDS = 20

PAIR_CHART_HEIGHT = 450
HEATMAP_HEIGHT = 520
MAP_HEIGHT = 560


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


def shorten_label(
    value,
    maximum_length=42
):
    """
    Shorten a long label for chart display.

    The complete value remains available in hover information.
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


def wrap_label(
    value,
    width=22
):
    """
    Wrap a chart label across multiple lines.
    """
    cleaned_value = clean_category_value(
        value
    )

    return "<br>".join(
        textwrap.wrap(
            cleaned_value,
            width=width
        )
    )


def distinct_incident_count(data):
    """
    Return the number of distinct incidents.

    incident_id is used when available. Otherwise, dataframe rows
    are counted.
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


def group_incident_counts(
    data,
    group_column
):
    """
    Count distinct incidents by one categorical field.
    """
    if (
        data is None
        or data.empty
        or group_column not in data.columns
    ):
        return pd.DataFrame(
            columns=[
                group_column,
                "incident_count"
            ]
        )

    selected_columns = [
        group_column
    ]

    if "incident_id" in data.columns:
        selected_columns.append(
            "incident_id"
        )

    working_data = data[
        selected_columns
    ].copy()

    working_data[group_column] = (
        working_data[group_column]
        .apply(
            clean_category_value
        )
    )

    if "incident_id" in working_data.columns:
        summary = (
            working_data
            .groupby(
                group_column
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
                group_column
            )
            .size()
            .reset_index(
                name="incident_count"
            )
        )

    return summary.sort_values(
        [
            "incident_count",
            group_column
        ],
        ascending=[
            False,
            True
        ]
    )


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

    cleaned_locations = (
        data["location_raw"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    cleaned_locations = cleaned_locations[
        cleaned_locations != ""
    ]

    return int(
        cleaned_locations.nunique()
    )


def prepare_specific_location_data(
    data,
    maximum_locations=TOP_SPECIFIC_LOCATIONS
):
    """
    Prepare the highest-volume specific locations.
    """
    location_summary = group_incident_counts(
        data=data,
        group_column="location_raw"
    )

    if location_summary.empty:
        return location_summary

    location_summary = location_summary.head(
        maximum_locations
    ).copy()

    location_summary["display_location"] = (
        location_summary["location_raw"]
        .apply(
            shorten_label
        )
    )

    return location_summary


def create_specific_location_chart(data):
    """
    Create a horizontal bar chart for top specific locations.
    """
    location_summary = prepare_specific_location_data(
        data
    )

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

    total_incidents = distinct_incident_count(
        data
    )

    chart_data["percentage"] = (
        chart_data["incident_count"]
        / total_incidents
        * 100
        if total_incidents > 0
        else 0.0
    )

    figure.add_trace(
        go.Bar(
            x=chart_data[
                "incident_count"
            ],
            y=chart_data[
                "display_location"
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
                    "location_raw",
                    "percentage"
                ]
            ],
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Distinct incidents: %{x:,}<br>"
                "Share of selected incidents: %{customdata[1]:.1f}%"
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
                "text": "Distinct Incident Count"
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
    Prepare distinct incident counts by location group.
    """
    return group_incident_counts(
        data=data,
        group_column="location_group"
    )


def create_location_group_chart(data):
    """
    Create a horizontal bar chart for major location groups.
    """
    location_group_summary = prepare_location_group_data(
        data
    )

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
        .head(
            TOP_LOCATION_GROUPS
        )
        .sort_values(
            "incident_count",
            ascending=True
        )
        .copy()
    )

    total_incidents = distinct_incident_count(
        data
    )

    chart_data["percentage"] = (
        chart_data["incident_count"]
        / total_incidents
        * 100
        if total_incidents > 0
        else 0.0
    )

    figure.add_trace(
        go.Bar(
            x=chart_data[
                "incident_count"
            ],
            y=chart_data[
                "location_group"
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
                "Distinct incidents: %{x:,}<br>"
                "Share of selected incidents: %{customdata[0]:.1f}%"
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
                "text": "Distinct Incident Count"
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
    Prepare complete crime composition within major location groups.

    Analytical rules:
    - only location groups with at least the minimum record count are used
    - the largest location groups are displayed
    - the largest crime groups receive their own columns
    - all remaining crime groups are combined as Other Crime Groups
    - every location-group row uses all incidents in that location group
      as its denominator
    """
    required_columns = {
        "location_group",
        "crime_group"
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
            "location_totals": pd.Series(
                dtype=int
            ),
            "eligible_location_groups": []
        }

    selected_columns = [
        "location_group",
        "crime_group"
    ]

    if "incident_id" in data.columns:
        selected_columns.append(
            "incident_id"
        )

    working_data = data[
        selected_columns
    ].copy()

    working_data["location_group"] = (
        working_data["location_group"]
        .apply(
            clean_category_value
        )
    )

    working_data["crime_group"] = (
        working_data["crime_group"]
        .apply(
            clean_category_value
        )
    )

    if "incident_id" in working_data.columns:
        location_totals_all = (
            working_data
            .groupby(
                "location_group"
            )["incident_id"]
            .nunique()
            .sort_values(
                ascending=False
            )
        )

    else:
        location_totals_all = (
            working_data[
                "location_group"
            ]
            .value_counts()
        )

    eligible_location_groups = (
        location_totals_all[
            location_totals_all
            >= MINIMUM_LOCATION_GROUP_RECORDS
        ]
        .head(
            TOP_LOCATION_GROUPS
        )
        .index
        .tolist()
    )

    if not eligible_location_groups:
        return {
            "count_data": pd.DataFrame(),
            "percentage_data": pd.DataFrame(),
            "location_totals": pd.Series(
                dtype=int
            ),
            "eligible_location_groups": []
        }

    eligible_data = working_data[
        working_data["location_group"].isin(
            eligible_location_groups
        )
    ].copy()

    if "incident_id" in eligible_data.columns:
        crime_totals = (
            eligible_data
            .groupby(
                "crime_group"
            )["incident_id"]
            .nunique()
            .sort_values(
                ascending=False
            )
        )

    else:
        crime_totals = (
            eligible_data[
                "crime_group"
            ]
            .value_counts()
        )

    top_crime_groups = (
        crime_totals
        .head(
            TOP_DISPLAYED_CRIME_GROUPS
        )
        .index
        .tolist()
    )

    eligible_data["_display_crime_group"] = (
        eligible_data["crime_group"]
        .where(
            eligible_data["crime_group"].isin(
                top_crime_groups
            ),
            OTHER_CRIME_GROUP_LABEL
        )
    )

    if "incident_id" in eligible_data.columns:
        grouped_counts = (
            eligible_data
            .groupby(
                [
                    "location_group",
                    "_display_crime_group"
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
                    "location_group",
                    "_display_crime_group"
                ]
            )
            .size()
            .reset_index(
                name="incident_count"
            )
        )

    displayed_crime_order = top_crime_groups.copy()

    if (
        eligible_data["_display_crime_group"]
        == OTHER_CRIME_GROUP_LABEL
    ).any():
        displayed_crime_order.append(
            OTHER_CRIME_GROUP_LABEL
        )

    count_data = (
        grouped_counts
        .pivot(
            index="location_group",
            columns="_display_crime_group",
            values="incident_count"
        )
        .fillna(0)
        .reindex(
            index=eligible_location_groups,
            columns=displayed_crime_order,
            fill_value=0
        )
        .astype(int)
    )

    location_totals = count_data.sum(
        axis=1
    )

    percentage_data = (
        count_data
        .div(
            location_totals.replace(
                0,
                pd.NA
            ),
            axis=0
        )
        .fillna(0)
        * 100
    )

    return {
        "count_data": count_data,
        "percentage_data": percentage_data,
        "location_totals": location_totals,
        "eligible_location_groups": eligible_location_groups
    }


def create_location_crime_composition_heatmap(data):
    """
    Create a complete normalized crime-composition heatmap.

    Light cells indicate smaller shares.
    Dark cells indicate larger shares.
    """
    composition = prepare_location_crime_composition(
        data
    )

    count_data = composition[
        "count_data"
    ]

    percentage_data = composition[
        "percentage_data"
    ]

    location_totals = composition[
        "location_totals"
    ]

    figure = go.Figure()

    if percentage_data.empty:
        figure.add_annotation(
            text=(
                "No location groups meet the minimum record threshold "
                "for composition analysis."
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
            title="Complete Crime Composition by Location Group",
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

    custom_data = []

    for location_group in percentage_data.index:
        row_custom_data = []

        for crime_group in percentage_data.columns:
            row_custom_data.append(
                [
                    int(
                        count_data.loc[
                            location_group,
                            crime_group
                        ]
                    ),
                    int(
                        location_totals.loc[
                            location_group
                        ]
                    ),
                    crime_group
                ]
            )

        custom_data.append(
            row_custom_data
        )

    figure.add_trace(
        go.Heatmap(
            z=percentage_data.values,
            x=wrapped_crime_labels,
            y=percentage_data.index.tolist(),
            customdata=custom_data,
            zmin=0,
            zmax=max(
                float(
                    percentage_data.max().max()
                ),
                1
            ),
            colorscale=[
                [
                    0.00,
                    "#F3F8FC"
                ],
                [
                    0.20,
                    "#D9ECF7"
                ],
                [
                    0.40,
                    "#B7DBEF"
                ],
                [
                    0.60,
                    "#68AFCF"
                ],
                [
                    0.80,
                    "#447FA8"
                ],
                [
                    1.00,
                    "#172554"
                ]
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
                "Crime group: %{customdata[2]}<br>"
                "Share within location group: %{z:.1f}%<br>"
                "Distinct incidents: %{customdata[0]:,}<br>"
                "Location-group total: %{customdata[1]:,}"
                "<extra></extra>"
            )
        )
    )

    figure.update_layout(
        title={
            "text": "Complete Crime Composition by Location Group",
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
            "b": 125
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


def get_top_location_value(data):
    """
    Return the highest-volume specific location using distinct incidents.
    """
    location_data = prepare_specific_location_data(
        data,
        maximum_locations=1
    )

    if location_data.empty:
        return "N/A", 0

    row = location_data.iloc[
        0
    ]

    return (
        row[
            "location_raw"
        ],
        int(
            row[
                "incident_count"
            ]
        )
    )


def get_top_location_group_value(data):
    """
    Return the highest-volume location group using distinct incidents.
    """
    group_data = prepare_location_group_data(
        data
    )

    if group_data.empty:
        return "N/A", 0

    row = group_data.iloc[
        0
    ]

    return (
        row[
            "location_group"
        ],
        int(
            row[
                "incident_count"
            ]
        )
    )


def show_location_summary(data):
    """
    Display compact location summary metrics.
    """
    selected_incidents = distinct_incident_count(
        data
    )

    unique_locations = get_unique_location_count(
        data
    )

    (
        top_location,
        top_location_count
    ) = get_top_location_value(
        data
    )

    (
        top_location_group,
        top_location_group_count
    ) = get_top_location_group_value(
        data
    )

    (
        top_crime_group,
        top_crime_group_count
    ) = get_top_value(
        data,
        "crime_group"
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
            "label": "Unique Locations",
            "value": format_number(
                unique_locations
            ),
            "meta": "Distinct source locations",
            "numeric": True,
            "help": (
                "The number of distinct non-empty source location values "
                "in the selected incident view. Similar location names may "
                "still require future standardization."
            )
        },
        {
            "label": "Top Location",
            "value": shorten_label(
                top_location,
                maximum_length=30
            ),
            "meta": "Highest specific location",
            "badge": format_number(
                top_location_count
            )
        },
        {
            "label": "Top Location Group",
            "value": top_location_group,
            "meta": "Leading location type",
            "badge": format_number(
                top_location_group_count
            )
        },
        {
            "label": "Top Crime Group",
            "value": top_crime_group,
            "meta": "Leading incident category",
            "badge": format_number(
                top_crime_group_count
            )
        }
    ]

    show_compact_overview_strip(
        overview_items
    )

    show_insight(
        f"The selected view contains "
        f"{format_number(unique_locations)} distinct source location "
        f"values. {top_location} has the highest specific-location "
        f"volume, while {top_location_group} is the leading location group."
    )

    show_info_hint(
        "Location-name limitation",
        (
            "Specific locations are based on cleaned source text. Similar "
            "names, abbreviations, intersections, and block-level references "
            "may still describe the same physical area and should be reviewed "
            "before formal geographic reporting."
        )
    )

    return {
        "selected_incidents": selected_incidents,
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
    Display a location map when validated coordinates are available.
    """
    map_figure = create_location_map(
        data
    )

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
        "coordinates. Coordinate-based analysis should only be used after "
        "location values have been reviewed and confirmed."
    )


def show_location_comparison_charts(
    data,
    summary
):
    """
    Display ranked specific locations and location groups.
    """
    specific_location_chart = create_specific_location_chart(
        data
    )

    location_group_chart = create_location_group_chart(
        data
    )

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
            f"{summary['top_location']} is the highest-volume specific "
            f"location with "
            f"{format_number(summary['top_location_count'])} distinct "
            f"incidents."
        )

    with insight_right:
        show_insight(
            f"{summary['top_location_group']} is the leading location "
            f"group with "
            f"{format_number(summary['top_location_group_count'])} "
            f"distinct incidents."
        )


def get_strongest_location_crime_concentration(data):
    """
    Return the highest percentage cell in the eligible composition table.
    """
    composition = prepare_location_crime_composition(
        data
    )

    percentage_data = composition[
        "percentage_data"
    ]

    count_data = composition[
        "count_data"
    ]

    location_totals = composition[
        "location_totals"
    ]

    if percentage_data.empty:
        return {
            "location_group": "N/A",
            "crime_group": "N/A",
            "percentage": 0.0,
            "count": 0,
            "location_total": 0
        }

    stacked_data = (
        percentage_data
        .stack()
        .reset_index()
    )

    stacked_data.columns = [
        "location_group",
        "crime_group",
        "percentage"
    ]

    strongest_row = stacked_data.sort_values(
        [
            "percentage",
            "location_group"
        ],
        ascending=[
            False,
            True
        ]
    ).iloc[
        0
    ]

    location_group = strongest_row[
        "location_group"
    ]

    crime_group = strongest_row[
        "crime_group"
    ]

    return {
        "location_group": location_group,
        "crime_group": crime_group,
        "percentage": float(
            strongest_row[
                "percentage"
            ]
        ),
        "count": int(
            count_data.loc[
                location_group,
                crime_group
            ]
        ),
        "location_total": int(
            location_totals.loc[
                location_group
            ]
        )
    }


def show_location_crime_heatmap(data):
    """
    Display complete normalized crime composition by location group.
    """
    show_info_hint(
        "Composition denominator",
        (
            "Each row totals 100% of all distinct incidents in that location "
            "group. The largest crime groups receive individual columns, and "
            "all remaining categories are combined into Other Crime Groups."
        )
    )

    # show_info_hint(
    #     "Minimum sample threshold",
    #     (
    #         f"Only location groups with at least "
    #         f"{MINIMUM_LOCATION_GROUP_RECORDS} distinct selected incidents "
    #         "are included. This prevents very small groups from appearing "
    #         "important because of unstable 100% percentages."
    #     )
    # )

    heatmap = create_location_crime_composition_heatmap(
        data
    )

    st.plotly_chart(
        heatmap,
        use_container_width=True,
        key="location_complete_crime_composition_heatmap",
        config=get_chart_config()
    )

    strongest_result = get_strongest_location_crime_concentration(
        data
    )

    if strongest_result[
        "location_group"
    ] == "N/A":
        show_insight(
            "No location groups meet the minimum sample threshold for "
            "crime-composition analysis."
        )

        return

    show_insight(
        f"{strongest_result['crime_group']} represents the largest "
        f"displayed share within {strongest_result['location_group']} at "
        f"{format_percentage(strongest_result['percentage'])}, based on "
        f"{format_number(strongest_result['count'])} of "
        f"{format_number(strongest_result['location_total'])} distinct "
        f"incidents."
    )


def show_location_analysis(data):
    """
    Display the complete location hotspot section.
    """
    show_section_banner(
        eyebrow="Spatial Intelligence",
        title="Campus Hotspot Profile",
        description=(
            "Identify high-activity locations, compare location types, "
            "and examine complete crime composition across major "
            "location groups."
        )
    )

    summary = show_location_summary(
        data
    )

    # st.divider()

    show_map_section(
        data
    )

    show_location_comparison_charts(
        data,
        summary
    )

    show_location_crime_heatmap(
        data
    )