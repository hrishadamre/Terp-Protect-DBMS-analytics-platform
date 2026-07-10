"""
location_analysis.py

Purpose:
Display the campus hotspot profile section for the Terp Protect Streamlit dashboard.

This section identifies high-activity locations, summarizes location groups,
shows location-crime patterns, and optionally displays a map if latitude and
longitude columns are available in the dataset.
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
    show_insight,
    show_section_note
)

from components.metrics import (
    format_number,
    get_top_value
)


def show_location_analysis(data):
    """Display the campus hotspot profile section."""
    st.subheader("Campus Hotspot Profile")

    show_section_note(
        "Identify high-activity locations, compare campus location groups, and review where specific incident categories are concentrated."
    )

    unique_locations = data["location_raw"].nunique()

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

    card_1, card_2, card_3, card_4 = st.columns(4)

    card_1.metric(
        "Unique Locations",
        format_number(unique_locations)
    )

    card_2.metric(
        "Top Location",
        top_location
    )

    card_3.metric(
        "Top Location Group",
        top_location_group
    )

    card_4.metric(
        "Top Crime Group",
        top_crime_group
    )

    show_insight(
        f"The selected data includes {format_number(unique_locations)} unique locations. "
        f"{top_location} has the highest location-level incident count."
    )

    st.divider()

    map_figure = create_location_map(data)

    if map_figure is not None:
        st.plotly_chart(
            map_figure,
            use_container_width=True,
            key="location_campus_hotspot_map",
            config=get_chart_config()
        )

        show_insight(
            "The map highlights incident concentration by location using available latitude and longitude fields."
        )
    else:
        st.info(
            "A real campus map can be displayed after latitude and longitude fields are added to the location dataset. "
            "For now, the section uses ranked location and heatmap views."
        )

    left_column, right_column = st.columns(2)

    with left_column:
        st.plotly_chart(
            create_ranked_lollipop_chart(
                data=data,
                group_column="location_raw",
                title="Top Specific Locations",
                max_categories=20,
                count_label="Incident Count",
                chart_type="incident_soft"
            ),
            use_container_width=True,
            key="location_top_specific_locations_chart",
            config=get_chart_config()
        )

        show_insight(
            f"{top_location} is the highest specific location with {format_number(top_location_count)} incidents."
        )

    with right_column:
        st.plotly_chart(
            create_horizontal_bar_chart(
                data=data,
                group_column="location_group",
                title="Incident Volume by Location Group",
                count_label="Incident Count",
                chart_type="incident_soft"
            ),
            use_container_width=True,
            key="location_group_volume_chart",
            config=get_chart_config()
        )

        show_insight(
            f"{top_location_group} is the leading location group with {format_number(top_location_group_count)} incidents."
        )

    st.plotly_chart(
        create_location_crime_heatmap(data),
        use_container_width=True,
        key="location_crime_group_heatmap",
        config=get_chart_config()
    )

    show_insight(
        f"The heatmap helps identify which crime groups are concentrated across location groups. "
        f"{top_crime_group} is the leading crime group with {format_number(top_crime_group_count)} incidents."
    )