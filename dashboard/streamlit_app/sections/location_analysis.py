"""
location_analysis.py

Purpose:
Display the campus hotspot profile section for the Terp Protect dashboard.

Responsibilities:
- Summarize location activity
- Display a campus map when coordinates are available
- Compare specific locations and location groups
- Show location-to-crime concentration patterns
"""

import streamlit as st

from components.charts import (
    create_horizontal_bar_chart,
    create_location_crime_heatmap,
    create_location_map,
    create_ranked_lollipop_chart,
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


PRIMARY_CHART_HEIGHT = 470
HEATMAP_HEIGHT = 540


def standardize_chart_height(
    figure,
    height=PRIMARY_CHART_HEIGHT
):
    """
    Apply consistent dimensions to paired charts.
    """
    figure.update_layout(
        height=height,
        margin={
            "l": 58,
            "r": 24,
            "t": 68,
            "b": 52
        }
    )

    return figure


def get_unique_location_count(data):
    """
    Safely count unique specific locations.
    """
    if (
        data.empty
        or "location_raw" not in data.columns
    ):
        return 0

    return data["location_raw"].nunique(
        dropna=True
    )


def show_location_summary(data):
    """
    Display compact location summary cards.
    """
    unique_locations = get_unique_location_count(
        data
    )

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
            "value": format_number(
                len(data)
            ),
            "meta": "Current filtered view",
            "numeric": True
        },
        {
            "label": "Unique Locations",
            "value": format_number(
                unique_locations
            ),
            "meta": "Distinct location values",
            "numeric": True
        },
        {
            "label": "Top Location",
            "value": top_location,
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
        f"{format_number(unique_locations)} unique locations. "
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
    Display the campus map when valid coordinates are available.
    """
    map_figure = create_location_map(
        data
    )

    if map_figure is None:
        st.info(
            "The map is currently unavailable because latitude and "
            "longitude are not present in the dashboard dataset. "
            "Ranked location and heatmap views are shown below."
        )

        return

    map_figure.update_layout(
        height=520
    )

    st.plotly_chart(
        map_figure,
        use_container_width=True,
        key="location_campus_hotspot_map",
        config=get_chart_config()
    )

    show_insight(
        "The map displays incident concentration using the available "
        "location coordinates. Larger or higher-intensity markers "
        "represent locations with more selected incidents."
    )


def show_location_comparison_charts(
    data,
    summary
):
    """
    Display ranked location charts in an aligned row.
    """
    specific_location_chart = standardize_chart_height(
        create_ranked_lollipop_chart(
            data=data,
            group_column="location_raw",
            title="Top Specific Locations",
            max_categories=18,
            count_label="Incident Count",
            chart_type="incident_soft"
        )
    )

    location_group_chart = standardize_chart_height(
        create_horizontal_bar_chart(
            data=data,
            group_column="location_group",
            title="Incident Volume by Location Group",
            count_label="Incident Count",
            chart_type="incident_soft"
        )
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


def show_location_heatmap(
    data,
    summary
):
    """
    Display the location-group and crime-group heatmap.
    """
    heatmap = create_location_crime_heatmap(
        data
    )

    heatmap.update_layout(
        height=HEATMAP_HEIGHT
    )

    st.plotly_chart(
        heatmap,
        use_container_width=True,
        key="location_crime_group_heatmap",
        config=get_chart_config()
    )

    show_insight(
        f"The heatmap highlights where incident categories are "
        f"concentrated across location groups. "
        f"{summary['top_crime_group']} is the leading crime group "
        f"with {format_number(summary['top_crime_group_count'])} "
        f"selected incidents."
    )


def show_location_analysis(data):
    """
    Display the complete location hotspot section.
    """
    show_section_banner(
        eyebrow="",
        title="Campus Hotspot Profile",
        description=(
            "Locate high-activity areas, compare campus location types, "
            "and identify where incident categories are concentrated."
        )
    )

    summary = show_location_summary(
        data
    )

    st.divider()

    show_map_section(
        data
    )

    show_location_comparison_charts(
        data,
        summary
    )

    show_location_heatmap(
        data,
        summary
    )