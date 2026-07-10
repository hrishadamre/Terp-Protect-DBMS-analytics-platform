"""
charts.py

Purpose:
Reusable Plotly chart functions for the Terp Protect Streamlit dashboard.

Design rules:
- Use one consistent dark chart surface.
- Use soft chart colors instead of vivid primary colors.
- Use blue for general incident volume.
- Use muted red for arrest/enforcement-related views.
- Use amber/orange/red scale for delay and risk-style views.
- Use green/teal for valid, stable, or quality-positive views.
- Use area/wave-style charts where trend readability matters.
- Keep charts readable, calm, and easy to skim.
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from components.theme import (
    get_chart_color,
    get_chart_template,
    get_heatmap_scale,
    get_risk_scale,
    get_soft_categorical_palette,
    get_status_color,
    get_theme
)


def apply_chart_theme(figure, height=430, show_legend=False):
    """Apply the centralized dashboard theme to a Plotly figure."""
    chart_template = get_chart_template()
    theme = get_theme()

    figure.update_layout(
        height=height,
        paper_bgcolor=chart_template["paper_bgcolor"],
        plot_bgcolor=chart_template["plot_bgcolor"],
        font=chart_template["font"],
        title=chart_template["title"],
        legend=chart_template["legend"],
        margin=chart_template["margin"],
        showlegend=show_legend,
        hoverlabel={
            "bgcolor": theme["background"]["card_alt"],
            "font": {
                "color": theme["text"]["dark"]
            },
            "bordercolor": theme["border"]["light"]
        },
        modebar={
            "bgcolor": "rgba(0,0,0,0)",
            "color": "rgba(203, 213, 225, 0.55)",
            "activecolor": theme["chart"]["primary"]
        },
        dragmode=False
    )

    figure.update_xaxes(
        gridcolor=theme["chart"]["grid"],
        zerolinecolor=theme["chart"]["grid"],
        linecolor=theme["chart"]["axis"],
        tickfont={
            "color": theme["chart"]["muted_text"],
            "size": 11
        },
        title={
            "font": {
                "color": theme["chart"]["text"],
                "size": 12
            }
        },
        automargin=True
    )

    figure.update_yaxes(
        gridcolor=theme["chart"]["grid"],
        zerolinecolor=theme["chart"]["grid"],
        linecolor=theme["chart"]["axis"],
        tickfont={
            "color": theme["chart"]["muted_text"],
            "size": 11
        },
        title={
            "font": {
                "color": theme["chart"]["text"],
                "size": 12
            }
        },
        automargin=True
    )

    return figure


def get_chart_config():
    """
    Return a reusable Plotly config.

    Sections can pass this into st.plotly_chart if needed.
    """
    return {
        "displaylogo": False,
        "modeBarButtonsToRemove": [
            "lasso2d",
            "select2d",
            "autoScale2d"
        ]
    }


def create_count_dataframe(data, group_column, count_column_name="record_count"):
    """Create a grouped count dataframe."""
    if data.empty or group_column not in data.columns:
        return pd.DataFrame(columns=[group_column, count_column_name])

    return (
        data.groupby(group_column)
        .size()
        .reset_index(name=count_column_name)
        .sort_values(count_column_name, ascending=False)
    )


def create_horizontal_bar_chart(
    data,
    group_column,
    title,
    max_categories=None,
    count_label="Incident Count",
    chart_type="incident"
):
    """Create a calm horizontal bar chart for grouped counts."""
    chart_data = create_count_dataframe(data, group_column, "record_count")

    if max_categories is not None:
        chart_data = chart_data.head(max_categories)

    chart_data = chart_data.sort_values("record_count", ascending=True)

    bar_color = get_chart_color(chart_type)

    figure = go.Figure(
        data=[
            go.Bar(
                x=chart_data["record_count"],
                y=chart_data[group_column],
                orientation="h",
                marker={
                    "color": bar_color,
                    "line": {
                        "width": 0
                    }
                },
                opacity=0.92,
                hovertemplate="<b>%{y}</b><br>" + count_label + ": %{x}<extra></extra>"
            )
        ]
    )

    figure.update_layout(
        title=title,
        xaxis_title=count_label,
        yaxis_title=""
    )

    return apply_chart_theme(figure)


def create_vertical_bar_chart(
    data,
    group_column,
    title,
    count_label="Incident Count",
    chart_type="incident"
):
    """Create a calm vertical bar chart for grouped counts."""
    chart_data = create_count_dataframe(data, group_column, "record_count")
    bar_color = get_chart_color(chart_type)

    figure = go.Figure(
        data=[
            go.Bar(
                x=chart_data[group_column],
                y=chart_data["record_count"],
                marker={
                    "color": bar_color,
                    "line": {
                        "width": 0
                    }
                },
                opacity=0.92,
                hovertemplate="<b>%{x}</b><br>" + count_label + ": %{y}<extra></extra>"
            )
        ]
    )

    figure.update_layout(
        title=title,
        xaxis_title="",
        yaxis_title=count_label
    )

    return apply_chart_theme(figure)


def create_status_bar_chart(
    data,
    group_column,
    title,
    max_categories=None,
    count_label="Incident Count"
):
    """
    Create a horizontal bar chart where bar colors are based on semantic status.

    Useful for outcomes, quality checks, or disposition-like fields.
    """
    chart_data = create_count_dataframe(data, group_column, "record_count")

    if max_categories is not None:
        chart_data = chart_data.head(max_categories)

    chart_data = chart_data.sort_values("record_count", ascending=True)
    colors = [get_status_color(value) for value in chart_data[group_column]]

    figure = go.Figure(
        data=[
            go.Bar(
                x=chart_data["record_count"],
                y=chart_data[group_column],
                orientation="h",
                marker={
                    "color": colors,
                    "line": {
                        "width": 0
                    }
                },
                opacity=0.9,
                hovertemplate="<b>%{y}</b><br>" + count_label + ": %{x}<extra></extra>"
            )
        ]
    )

    figure.update_layout(
        title=title,
        xaxis_title=count_label,
        yaxis_title=""
    )

    return apply_chart_theme(figure)


def create_area_line_chart(
    chart_data,
    x_column,
    y_column,
    title,
    x_label,
    y_label,
    line_color=None,
    fill_color=None,
    hover_label="Records"
):
    """Create a smooth area/wave-style line chart."""
    theme = get_theme()

    if line_color is None:
        line_color = theme["chart"]["area_line"]

    if fill_color is None:
        fill_color = theme["chart"]["area_fill"]

    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=chart_data[x_column],
            y=chart_data[y_column],
            mode="lines+markers",
            line={
                "shape": "spline",
                "smoothing": 0.85,
                "width": 3,
                "color": line_color
            },
            marker={
                "size": 7,
                "color": line_color,
                "line": {
                    "width": 2,
                    "color": theme["chart"]["paper"]
                }
            },
            fill="tozeroy",
            fillcolor=fill_color,
            hovertemplate="<b>%{x}</b><br>" + hover_label + ": %{y}<extra></extra>"
        )
    )

    figure.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label
    )

    return apply_chart_theme(figure)


def create_monthly_line_chart(data):
    """Create a monthly incident trend area chart."""
    theme = get_theme()

    chart_data = (
        data.groupby(["occurred_month", "occurred_month_name"])
        .size()
        .reset_index(name="incident_count")
        .sort_values("occurred_month")
    )

    return create_area_line_chart(
        chart_data=chart_data,
        x_column="occurred_month_name",
        y_column="incident_count",
        title="Monthly Incident Trend",
        x_label="Month",
        y_label="Incident Count",
        line_color=theme["chart"]["incident"],
        fill_color="rgba(142, 216, 243, 0.20)",
        hover_label="Incidents"
    )


def create_arrest_monthly_chart(arrest_data):
    """Create a monthly arrest trend area chart."""
    theme = get_theme()

    chart_data = (
        arrest_data.groupby(["arrested_month", "arrested_month_name"])
        .size()
        .reset_index(name="arrest_count")
        .sort_values("arrested_month")
    )

    return create_area_line_chart(
        chart_data=chart_data,
        x_column="arrested_month_name",
        y_column="arrest_count",
        title="Monthly Arrest Trend",
        x_label="Month",
        y_label="Arrest Count",
        line_color=theme["chart"]["arrest"],
        fill_color="rgba(231, 138, 152, 0.20)",
        hover_label="Arrests"
    )


def create_weekday_chart(data):
    """Create a weekday incident trend chart."""
    theme = get_theme()

    weekday_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]

    chart_data = (
        data.groupby("occurred_weekday")
        .size()
        .reset_index(name="incident_count")
    )

    chart_data["occurred_weekday"] = pd.Categorical(
        chart_data["occurred_weekday"],
        categories=weekday_order,
        ordered=True
    )

    chart_data = chart_data.sort_values("occurred_weekday")

    figure = go.Figure(
        data=[
            go.Bar(
                x=chart_data["occurred_weekday"],
                y=chart_data["incident_count"],
                marker={
                    "color": theme["chart"]["incident"],
                    "line": {
                        "width": 0
                    }
                },
                opacity=0.9,
                hovertemplate="<b>%{x}</b><br>Incidents: %{y}<extra></extra>"
            )
        ]
    )

    figure.update_layout(
        title="Incident Volume by Weekday",
        xaxis_title="Weekday",
        yaxis_title="Incident Count"
    )

    return apply_chart_theme(figure)


def create_hourly_chart(data):
    """Create an hourly incident trend area chart."""
    theme = get_theme()

    chart_data = (
        data.groupby("occurred_hour")
        .size()
        .reset_index(name="incident_count")
        .sort_values("occurred_hour")
    )

    return create_area_line_chart(
        chart_data=chart_data,
        x_column="occurred_hour",
        y_column="incident_count",
        title="Incident Volume by Hour",
        x_label="Hour of Day",
        y_label="Incident Count",
        line_color=theme["chart"]["incident"],
        fill_color="rgba(142, 216, 243, 0.18)",
        hover_label="Incidents"
    )


def create_delay_bucket_chart(data):
    """Create a reporting delay distribution chart with soft risk colors."""
    theme = get_theme()

    delay_order = [
        "Same Day / Within 24 Hours",
        "1-3 Days",
        "4-7 Days",
        "Over 7 Days",
        "Unknown"
    ]

    chart_data = (
        data.groupby("delay_bucket")
        .size()
        .reset_index(name="incident_count")
    )

    chart_data["delay_bucket"] = pd.Categorical(
        chart_data["delay_bucket"],
        categories=delay_order,
        ordered=True
    )

    chart_data = chart_data.sort_values("delay_bucket")

    color_map = {
        "Same Day / Within 24 Hours": theme["semantic"]["stable"],
        "1-3 Days": theme["semantic"]["attention"],
        "4-7 Days": theme["semantic"]["warning"],
        "Over 7 Days": theme["semantic"]["critical"],
        "Unknown": theme["semantic"]["neutral"]
    }

    colors = [
        color_map.get(delay_bucket, theme["semantic"]["neutral"])
        for delay_bucket in chart_data["delay_bucket"]
    ]

    figure = go.Figure()

    figure.add_trace(
        go.Bar(
            x=chart_data["delay_bucket"],
            y=chart_data["incident_count"],
            marker={
                "color": colors,
                "line": {
                    "width": 0
                }
            },
            opacity=0.9,
            hovertemplate="<b>%{x}</b><br>Incidents: %{y}<extra></extra>"
        )
    )

    figure.add_trace(
        go.Scatter(
            x=chart_data["delay_bucket"],
            y=chart_data["incident_count"],
            mode="lines+markers",
            line={
                "shape": "spline",
                "smoothing": 0.7,
                "width": 2,
                "color": "rgba(255,255,255,0.52)"
            },
            marker={
                "size": 6,
                "color": "rgba(255,255,255,0.74)"
            },
            hoverinfo="skip"
        )
    )

    figure.update_layout(
        title="Reporting Delay Distribution",
        xaxis_title="Reporting Delay",
        yaxis_title="Incident Count"
    )

    return apply_chart_theme(figure, show_legend=False)


def create_crime_disposition_heatmap(data):
    """Create a heatmap showing crime group by outcome group."""
    theme = get_theme()

    chart_data = (
        data.groupby(["crime_group", "disposition_group"])
        .size()
        .reset_index(name="incident_count")
    )

    figure = px.density_heatmap(
        chart_data,
        x="disposition_group",
        y="crime_group",
        z="incident_count",
        title="Crime Group by Case Outcome",
        labels={
            "disposition_group": "Outcome Group",
            "crime_group": "Crime Group",
            "incident_count": "Incident Count"
        },
        color_continuous_scale=get_heatmap_scale()
    )

    figure.update_traces(
        hovertemplate="<b>%{y}</b><br>Outcome: %{x}<br>Incidents: %{z}<extra></extra>"
    )

    figure = apply_chart_theme(figure, height=520)

    figure.update_layout(
        coloraxis_colorbar={
            "title": {
                "text": "Incidents",
                "font": {
                    "color": theme["chart"]["text"]
                }
            },
            "tickfont": {
                "color": theme["chart"]["text"]
            }
        }
    )

    return figure


def create_reporting_delay_by_group_chart(data, group_column, title, max_categories=15):
    """Create a bar chart for average reporting delay by group."""
    chart_data = (
        data[data["has_valid_reporting_delay"] == 1]
        .groupby(group_column)["report_delay_hours"]
        .mean()
        .reset_index(name="avg_report_delay_hours")
        .sort_values("avg_report_delay_hours", ascending=False)
        .head(max_categories)
    )

    chart_data = chart_data.sort_values("avg_report_delay_hours", ascending=True)

    figure = px.bar(
        chart_data,
        x="avg_report_delay_hours",
        y=group_column,
        orientation="h",
        title=title,
        labels={
            "avg_report_delay_hours": "Average Delay Hours",
            group_column: ""
        },
        color="avg_report_delay_hours",
        color_continuous_scale=get_risk_scale()
    )

    figure.update_traces(
        marker_line_width=0,
        opacity=0.9,
        hovertemplate="<b>%{y}</b><br>Avg Delay Hours: %{x:.1f}<extra></extra>"
    )

    figure = apply_chart_theme(figure)

    figure.update_layout(
        coloraxis_showscale=False
    )

    return figure


def create_quality_bar_chart(quality_data):
    """Create a grouped bar chart for valid vs invalid quality checks."""
    theme = get_theme()

    figure = px.bar(
        quality_data,
        x="Quality Check",
        y=["Valid Count", "Invalid Count"],
        title="Pipeline Data Quality Checks",
        barmode="group",
        labels={
            "value": "Record Count",
            "variable": "Status"
        },
        color_discrete_map={
            "Valid Count": theme["chart"]["quality_valid"],
            "Invalid Count": theme["chart"]["quality_invalid"]
        }
    )

    figure.update_traces(
        marker_line_width=0,
        opacity=0.9,
        hovertemplate="<b>%{x}</b><br>%{fullData.name}: %{y}<extra></extra>"
    )

    return apply_chart_theme(figure, height=500, show_legend=True)


def create_match_summary_chart(match_summary):
    """Create incident-to-arrest match summary chart."""
    theme = get_theme()

    figure = px.bar(
        match_summary,
        x="match_status",
        y="incident_count",
        title="Incident-to-Arrest Match Coverage",
        labels={
            "match_status": "",
            "incident_count": "Incident Count"
        },
        color="match_status",
        color_discrete_map={
            "Matching Arrest": theme["chart"]["arrest"],
            "No Matching Arrest": theme["chart"]["neutral"]
        }
    )

    figure.update_traces(
        marker_line_width=0,
        opacity=0.9,
        hovertemplate="<b>%{x}</b><br>Incidents: %{y}<extra></extra>"
    )

    return apply_chart_theme(figure, height=430, show_legend=False)


def create_location_crime_heatmap(data):
    """Create a location group by crime group heatmap."""
    theme = get_theme()

    chart_data = (
        data.groupby(["location_group", "crime_group"])
        .size()
        .reset_index(name="incident_count")
    )

    figure = px.density_heatmap(
        chart_data,
        x="crime_group",
        y="location_group",
        z="incident_count",
        title="Location Group by Crime Group",
        labels={
            "crime_group": "Crime Group",
            "location_group": "Location Group",
            "incident_count": "Incident Count"
        },
        color_continuous_scale=get_heatmap_scale()
    )

    figure.update_traces(
        hovertemplate="<b>%{y}</b><br>Crime Group: %{x}<br>Incidents: %{z}<extra></extra>"
    )

    figure = apply_chart_theme(figure, height=540)

    figure.update_layout(
        coloraxis_colorbar={
            "title": {
                "text": "Incidents",
                "font": {
                    "color": theme["chart"]["text"]
                }
            },
            "tickfont": {
                "color": theme["chart"]["text"]
            }
        }
    )

    return figure


def create_location_map(data):
    """
    Create a map if latitude and longitude columns are available.

    Expected coordinate column options:
    - latitude / longitude
    - lat / lon
    - location_latitude / location_longitude

    If coordinates are not available, this returns None.
    """
    coordinate_options = [
        ("latitude", "longitude"),
        ("lat", "lon"),
        ("location_latitude", "location_longitude")
    ]

    latitude_column = None
    longitude_column = None

    for latitude_candidate, longitude_candidate in coordinate_options:
        if latitude_candidate in data.columns and longitude_candidate in data.columns:
            latitude_column = latitude_candidate
            longitude_column = longitude_candidate
            break

    if latitude_column is None or longitude_column is None:
        return None

    map_data = (
        data.dropna(subset=[latitude_column, longitude_column])
        .groupby([latitude_column, longitude_column, "location_raw", "location_group"])
        .size()
        .reset_index(name="incident_count")
    )

    if map_data.empty:
        return None

    figure = px.scatter_mapbox(
        map_data,
        lat=latitude_column,
        lon=longitude_column,
        size="incident_count",
        color="incident_count",
        hover_name="location_raw",
        hover_data={
            "location_group": True,
            "incident_count": True,
            latitude_column: False,
            longitude_column: False
        },
        color_continuous_scale=get_risk_scale(),
        size_max=28,
        zoom=13,
        title="Campus Incident Hotspot Map"
    )

    figure.update_layout(
        mapbox_style="carto-darkmatter",
        mapbox_center={
            "lat": float(map_data[latitude_column].mean()),
            "lon": float(map_data[longitude_column].mean())
        }
    )

    figure = apply_chart_theme(figure, height=560)

    figure.update_layout(
        margin={
            "l": 0,
            "r": 0,
            "t": 54,
            "b": 0
        },
        coloraxis_showscale=False
    )

    return figure


def create_soft_donut_chart(data, label_column, value_column, title):
    """Create a soft donut chart for compact composition views."""
    theme = get_theme()

    figure = px.pie(
        data,
        names=label_column,
        values=value_column,
        hole=0.58,
        title=title,
        color_discrete_sequence=get_soft_categorical_palette()
    )

    figure.update_traces(
        textposition="inside",
        textinfo="percent",
        marker={
            "line": {
                "color": theme["chart"]["paper"],
                "width": 2
            }
        },
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>"
    )

    return apply_chart_theme(figure, height=430, show_legend=True)


def create_ranked_lollipop_chart(
    data,
    group_column,
    title,
    max_categories=15,
    count_label="Incident Count",
    chart_type="incident"
):
    """Create a cleaner ranked lollipop chart for top categories."""
    theme = get_theme()

    chart_data = create_count_dataframe(data, group_column, "record_count").head(max_categories)
    chart_data = chart_data.sort_values("record_count", ascending=True)

    color = get_chart_color(chart_type)

    figure = go.Figure()

    for _, row in chart_data.iterrows():
        figure.add_trace(
            go.Scatter(
                x=[0, row["record_count"]],
                y=[row[group_column], row[group_column]],
                mode="lines",
                line={
                    "color": "rgba(203, 213, 225, 0.28)",
                    "width": 2
                },
                hoverinfo="skip",
                showlegend=False
            )
        )

    figure.add_trace(
        go.Scatter(
            x=chart_data["record_count"],
            y=chart_data[group_column],
            mode="markers",
            marker={
                "size": 13,
                "color": color,
                "line": {
                    "width": 2,
                    "color": theme["chart"]["paper"]
                }
            },
            hovertemplate="<b>%{y}</b><br>" + count_label + ": %{x}<extra></extra>",
            showlegend=False
        )
    )

    figure.update_layout(
        title=title,
        xaxis_title=count_label,
        yaxis_title=""
    )

    return apply_chart_theme(figure)