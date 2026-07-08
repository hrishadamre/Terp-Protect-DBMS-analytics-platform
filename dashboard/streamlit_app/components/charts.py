"""
charts.py

Purpose:
Store reusable Plotly chart functions for the Terp Protect Streamlit dashboard.

This file keeps chart-building logic separate from dashboard page logic.
All charts use the centralized dashboard theme.
"""

import pandas as pd
import plotly.express as px

from components.theme import get_chart_template, get_theme


def apply_chart_theme(figure, height=430):
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
        hoverlabel={
            "bgcolor": theme["background"]["card"],
            "font": {
                "color": theme["text"]["dark"]
            },
            "bordercolor": theme["border"]["light"]
        }
    )

    figure.update_xaxes(
        gridcolor=theme["chart"]["grid"],
        zerolinecolor=theme["chart"]["grid"],
        linecolor=theme["chart"]["grid"],
        tickfont={
            "color": theme["chart"]["text"]
        },
        title={
            "font": {
                "color": theme["chart"]["text"]
            }
        }
    )

    figure.update_yaxes(
        gridcolor=theme["chart"]["grid"],
        zerolinecolor=theme["chart"]["grid"],
        linecolor=theme["chart"]["grid"],
        tickfont={
            "color": theme["chart"]["text"]
        },
        title={
            "font": {
                "color": theme["chart"]["text"]
            }
        }
    )

    return figure


def create_count_dataframe(data, group_column, count_column_name="incident_count"):
    """Create a grouped count dataframe."""
    return (
        data.groupby(group_column)
        .size()
        .reset_index(name=count_column_name)
        .sort_values(count_column_name, ascending=False)
    )


def create_horizontal_bar_chart(data, group_column, title, max_categories=None, count_label="Incident Count"):
    """Create a horizontal bar chart for grouped counts."""
    theme = get_theme()
    chart_data = create_count_dataframe(data, group_column)

    if max_categories is not None:
        chart_data = chart_data.head(max_categories)

    chart_data = chart_data.sort_values("incident_count", ascending=True)

    figure = px.bar(
        chart_data,
        x="incident_count",
        y=group_column,
        orientation="h",
        title=title,
        labels={
            "incident_count": count_label,
            group_column: ""
        },
        color_discrete_sequence=[theme["chart"]["primary"]]
    )

    figure.update_traces(
        marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>" + count_label + ": %{x}<extra></extra>"
    )

    return apply_chart_theme(figure)


def create_vertical_bar_chart(data, group_column, title, count_label="Incident Count"):
    """Create a vertical bar chart for grouped counts."""
    theme = get_theme()
    chart_data = create_count_dataframe(data, group_column)

    figure = px.bar(
        chart_data,
        x=group_column,
        y="incident_count",
        title=title,
        labels={
            group_column: "",
            "incident_count": count_label
        },
        color_discrete_sequence=[theme["chart"]["primary"]]
    )

    figure.update_traces(
        marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>" + count_label + ": %{y}<extra></extra>"
    )

    return apply_chart_theme(figure)


def create_monthly_line_chart(data):
    """Create a monthly incident trend line chart."""
    theme = get_theme()

    chart_data = (
        data.groupby(["occurred_month", "occurred_month_name"])
        .size()
        .reset_index(name="incident_count")
        .sort_values("occurred_month")
    )

    figure = px.line(
        chart_data,
        x="occurred_month_name",
        y="incident_count",
        markers=True,
        title="Incidents by Month",
        labels={
            "occurred_month_name": "Month",
            "incident_count": "Incident Count"
        },
        color_discrete_sequence=[theme["chart"]["primary"]]
    )

    figure.update_traces(
        line={
            "width": 3
        },
        marker={
            "size": 7,
            "line": {
                "width": 1,
                "color": theme["chart"]["paper"]
            }
        },
        hovertemplate="<b>%{x}</b><br>Incidents: %{y}<extra></extra>"
    )

    return apply_chart_theme(figure)


def create_arrest_monthly_chart(arrest_data):
    """Create a monthly arrest trend chart."""
    theme = get_theme()

    chart_data = (
        arrest_data.groupby(["arrested_month", "arrested_month_name"])
        .size()
        .reset_index(name="arrest_count")
        .sort_values("arrested_month")
    )

    figure = px.line(
        chart_data,
        x="arrested_month_name",
        y="arrest_count",
        markers=True,
        title="Arrests by Month",
        labels={
            "arrested_month_name": "Month",
            "arrest_count": "Arrest Count"
        },
        color_discrete_sequence=[theme["chart"]["secondary"]]
    )

    figure.update_traces(
        line={
            "width": 3
        },
        marker={
            "size": 7,
            "line": {
                "width": 1,
                "color": theme["chart"]["paper"]
            }
        },
        hovertemplate="<b>%{x}</b><br>Arrests: %{y}<extra></extra>"
    )

    return apply_chart_theme(figure)


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

    figure = px.bar(
        chart_data,
        x="occurred_weekday",
        y="incident_count",
        title="Incidents by Weekday",
        labels={
            "occurred_weekday": "Weekday",
            "incident_count": "Incident Count"
        },
        color_discrete_sequence=[theme["chart"]["primary"]]
    )

    figure.update_traces(
        marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>Incidents: %{y}<extra></extra>"
    )

    return apply_chart_theme(figure)


def create_hourly_chart(data):
    """Create an hourly incident trend chart."""
    theme = get_theme()

    chart_data = (
        data.groupby("occurred_hour")
        .size()
        .reset_index(name="incident_count")
        .sort_values("occurred_hour")
    )

    figure = px.bar(
        chart_data,
        x="occurred_hour",
        y="incident_count",
        title="Incidents by Hour of Day",
        labels={
            "occurred_hour": "Hour of Day",
            "incident_count": "Incident Count"
        },
        color_discrete_sequence=[theme["chart"]["primary"]]
    )

    figure.update_traces(
        marker_line_width=0,
        hovertemplate="<b>Hour %{x}</b><br>Incidents: %{y}<extra></extra>"
    )

    return apply_chart_theme(figure)


def create_delay_bucket_chart(data):
    """Create a reporting delay bucket chart."""
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

    figure = px.bar(
        chart_data,
        x="delay_bucket",
        y="incident_count",
        title="Reporting Delay Distribution",
        labels={
            "delay_bucket": "Reporting Delay",
            "incident_count": "Incident Count"
        },
        color_discrete_sequence=[theme["chart"]["accent"]]
    )

    figure.update_traces(
        marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>Incidents: %{y}<extra></extra>"
    )

    return apply_chart_theme(figure)


def create_crime_disposition_heatmap(data):
    """Create a heatmap showing crime group by disposition group."""
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
        title="Crime Group by Outcome Group",
        labels={
            "disposition_group": "Outcome Group",
            "crime_group": "Crime Group",
            "incident_count": "Incident Count"
        },
        color_continuous_scale="Blues"
    )

    figure.update_traces(
        hovertemplate="<b>%{y}</b><br>Outcome: %{x}<br>Incidents: %{z}<extra></extra>"
    )

    figure = apply_chart_theme(figure, height=520)

    figure.update_layout(
        coloraxis_colorbar={
            "title": "Incidents",
            "tickfont": {
                "color": theme["chart"]["text"]
            },
            "title": {
                "font": {
                    "color": theme["chart"]["text"]
                }
            }
        }
    )

    return figure


def create_reporting_delay_by_group_chart(data, group_column, title, max_categories=15):
    """Create a bar chart for average reporting delay by group."""
    theme = get_theme()

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
            "avg_report_delay_hours": "Average Reporting Delay Hours",
            group_column: ""
        },
        color_discrete_sequence=[theme["chart"]["accent"]]
    )

    figure.update_traces(
        marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>Avg Delay Hours: %{x:.1f}<extra></extra>"
    )

    return apply_chart_theme(figure)