"""
location_analysis.py

Purpose:
Display the Location Analysis tab for the Terp Protect Streamlit dashboard.

This page identifies high-activity locations, summarizes location groups,
and shows how incident categories vary across location groups.
"""

import plotly.express as px
import streamlit as st

from components.charts import (
    create_horizontal_bar_chart
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
    """Display the Location Analysis tab."""
    st.subheader("Location Analysis")

    show_section_note(
        "This page identifies high-activity locations and shows how incident categories vary across location groups."
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

    card_1, card_2, card_3 = st.columns(3)

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

    show_insight(
        f"The selected data includes {format_number(unique_locations)} unique locations. "
        f"The highest-volume specific location is {top_location}."
    )

    st.divider()

    left_column, right_column = st.columns(2)

    with left_column:
        st.plotly_chart(
            create_horizontal_bar_chart(
                data,
                "location_raw",
                "Top Locations",
                max_categories=20
            ),
            use_container_width=True,
            key="location_top_locations_chart"
        )

        show_insight(
            f"{top_location} appears most frequently with "
            f"{format_number(top_location_count)} incidents."
        )

    with right_column:
        st.plotly_chart(
            create_horizontal_bar_chart(
                data,
                "location_group",
                "Incidents by Location Group"
            ),
            use_container_width=True,
            key="location_group_chart"
        )

        show_insight(
            f"{top_location_group} is the leading location group with "
            f"{format_number(top_location_group_count)} incidents."
        )

    matrix_data = (
        data.groupby(["location_group", "crime_group"])
        .size()
        .reset_index(name="incident_count")
    )

    figure = px.density_heatmap(
        matrix_data,
        x="crime_group",
        y="location_group",
        z="incident_count",
        title="Location Group by Crime Group",
        labels={
            "crime_group": "Crime Group",
            "location_group": "Location Group",
            "incident_count": "Incident Count"
        }
    )

    figure.update_layout(
        height=520,
        margin=dict(l=10, r=10, t=55, b=10)
    )

    st.plotly_chart(
        figure,
        use_container_width=True,
        key="location_crime_group_heatmap"
    )

    show_insight(
        "The location-crime heatmap helps identify which incident categories are concentrated in specific location groups."
    )