"""
app.py

Purpose:
Build the Streamlit dashboard for the Terp Protect campus safety analytics project.

Current Scope:
- UMPD Daily Crime and Incident Logs: 2025
- UMPD Arrest Logs: 2025

Input Files:
- dashboard/powerbi/data/incident_detail.csv
- dashboard/powerbi/data/arrest_detail.csv
- dashboard/powerbi/data/incident_arrest_match.csv
- dashboard/powerbi/data/charge_category_summary.csv
- dashboard/powerbi/data/demographic_summary.csv

Current App Version:
Version 5 includes incident analytics, arrest analytics, incident-to-arrest matching,
data quality checks, improved dashboard styling, and dynamic insight captions.

Role in Pipeline:
This app belongs to the presentation layer. It uses dashboard-ready data generated from
the Terp Protect DBMS and SQL views to create an interactive local dashboard.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


DATA_DIR = Path("dashboard/powerbi/data")

INCIDENT_DETAIL_PATH = DATA_DIR / "incident_detail.csv"
ARREST_DETAIL_PATH = DATA_DIR / "arrest_detail.csv"
INCIDENT_ARREST_MATCH_PATH = DATA_DIR / "incident_arrest_match.csv"
CHARGE_CATEGORY_SUMMARY_PATH = DATA_DIR / "charge_category_summary.csv"
DEMOGRAPHIC_SUMMARY_PATH = DATA_DIR / "demographic_summary.csv"


st.set_page_config(
    page_title="Terp Protect Dashboard",
    page_icon="🐢",
    layout="wide"
)


def apply_custom_styles():
    """Apply custom dashboard styling."""
    st.markdown(
        """
        <style>
        .main {
            background-color: #fafafa;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        .dashboard-header {
            background: linear-gradient(90deg, #111111 0%, #b00020 100%);
            padding: 1.4rem 1.6rem;
            border-radius: 14px;
            margin-bottom: 1.4rem;
        }

        .dashboard-header h1 {
            color: white;
            font-size: 2rem;
            margin-bottom: 0.25rem;
        }

        .dashboard-header p {
            color: #f2f2f2;
            font-size: 1rem;
            margin-bottom: 0;
        }

        .section-note {
            background-color: #ffffff;
            border-left: 5px solid #b00020;
            padding: 0.9rem 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            color: #333333;
        }

        .insight-box {
            background-color: #fff8e6;
            border-left: 5px solid #f4c430;
            padding: 0.8rem 1rem;
            border-radius: 8px;
            margin-top: 0.4rem;
            margin-bottom: 1rem;
            color: #333333;
            font-size: 0.95rem;
        }

        div[data-testid="stMetric"] {
            background-color: #ffffff;
            padding: 1rem;
            border-radius: 12px;
            border: 1px solid #e6e6e6;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
        }

        div[data-testid="stMetricLabel"] {
            font-size: 0.9rem;
            color: #444444;
        }

        div[data-testid="stMetricValue"] {
            font-size: 1.4rem;
            color: #111111;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.4rem;
        }

        .stTabs [data-baseweb="tab"] {
            background-color: #ffffff;
            border-radius: 10px 10px 0 0;
            padding: 0.6rem 1rem;
            border: 1px solid #e6e6e6;
        }

        .stTabs [aria-selected="true"] {
            background-color: #b00020;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def show_dashboard_header():
    """Display the main dashboard header."""
    st.markdown(
        """
        <div class="dashboard-header">
            <h1>Terp Protect: Campus Safety Analytics</h1>
            <p>
                Interactive DBMS-powered dashboard for exploring UMPD incident records,
                arrest records, reporting delays, case outcomes, and charge patterns.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def show_section_note(text):
    """Display a short styled note under a section heading."""
    st.markdown(
        f"""
        <div class="section-note">
            {text}
        </div>
        """,
        unsafe_allow_html=True
    )


def show_insight(text):
    """Display a short analytical insight below a chart or section."""
    st.markdown(
        f"""
        <div class="insight-box">
            <strong>Insight:</strong> {text}
        </div>
        """,
        unsafe_allow_html=True
    )


@st.cache_data
def load_csv(path):
    """Load a CSV file with a friendly error if the file does not exist."""
    if not path.exists():
        st.error(f"Data file not found: {path}")
        st.stop()

    return pd.read_csv(path)


@st.cache_data
def load_dashboard_data():
    """Load all dashboard-ready datasets."""
    incident_data = load_csv(INCIDENT_DETAIL_PATH)
    arrest_data = load_csv(ARREST_DETAIL_PATH)
    match_data = load_csv(INCIDENT_ARREST_MATCH_PATH)
    charge_summary = load_csv(CHARGE_CATEGORY_SUMMARY_PATH)
    demographic_summary = load_csv(DEMOGRAPHIC_SUMMARY_PATH)

    incident_data["occurred_datetime"] = pd.to_datetime(
        incident_data["occurred_datetime"],
        errors="coerce"
    )

    incident_data["reported_datetime"] = pd.to_datetime(
        incident_data["reported_datetime"],
        errors="coerce"
    )

    arrest_data["arrested_datetime"] = pd.to_datetime(
        arrest_data["arrested_datetime"],
        errors="coerce"
    )

    match_data["occurred_datetime"] = pd.to_datetime(
        match_data["occurred_datetime"],
        errors="coerce"
    )

    match_data["reported_datetime"] = pd.to_datetime(
        match_data["reported_datetime"],
        errors="coerce"
    )

    match_data["arrested_datetime"] = pd.to_datetime(
        match_data["arrested_datetime"],
        errors="coerce"
    )

    return {
        "incident_data": incident_data,
        "arrest_data": arrest_data,
        "match_data": match_data,
        "charge_summary": charge_summary,
        "demographic_summary": demographic_summary
    }


def format_number(value):
    """Format large numbers with commas."""
    return f"{int(value):,}"


def format_percentage(value):
    """Format percentage values."""
    if pd.isna(value):
        return "0.0%"

    return f"{value:.1f}%"


def get_top_value(data, column):
    """Return the most frequent value and its count for a column."""
    if data.empty or column not in data.columns:
        return "N/A", 0

    counts = data[column].dropna().value_counts()

    if counts.empty:
        return "N/A", 0

    return counts.index[0], int(counts.iloc[0])


def get_month_order(data):
    """Return month names ordered by month number."""
    month_order = (
        data[["occurred_month", "occurred_month_name"]]
        .dropna()
        .drop_duplicates()
        .sort_values("occurred_month")
    )

    return month_order["occurred_month_name"].tolist()


def apply_incident_filters(data):
    """Create sidebar filters for incident data and return filtered data."""
    st.sidebar.header("Incident Filters")

    month_options = get_month_order(data)
    crime_group_options = sorted(data["crime_group"].dropna().unique().tolist())
    disposition_options = sorted(data["disposition_group"].dropna().unique().tolist())
    location_options = sorted(data["location_group"].dropna().unique().tolist())
    semester_options = sorted(data["occurred_semester_period"].dropna().unique().tolist())

    selected_months = st.sidebar.multiselect(
        "Month",
        options=month_options,
        default=month_options
    )

    selected_crime_groups = st.sidebar.multiselect(
        "Crime Group",
        options=crime_group_options,
        default=crime_group_options
    )

    selected_dispositions = st.sidebar.multiselect(
        "Disposition Group",
        options=disposition_options,
        default=disposition_options
    )

    selected_locations = st.sidebar.multiselect(
        "Location Group",
        options=location_options,
        default=location_options
    )

    selected_semesters = st.sidebar.multiselect(
        "Semester Period",
        options=semester_options,
        default=semester_options
    )

    filtered_data = data[
        data["occurred_month_name"].isin(selected_months)
        & data["crime_group"].isin(selected_crime_groups)
        & data["disposition_group"].isin(selected_dispositions)
        & data["location_group"].isin(selected_locations)
        & data["occurred_semester_period"].isin(selected_semesters)
    ]

    return filtered_data


def filter_related_arrest_data(arrest_data, match_data, filtered_incident_data):
    """Filter arrest and match datasets based on selected incident case numbers."""
    selected_case_numbers = filtered_incident_data["case_number"].dropna().unique().tolist()

    filtered_match_data = match_data[
        match_data["case_number"].isin(selected_case_numbers)
    ]

    matched_arrest_ids = (
        filtered_match_data["arrest_id"]
        .dropna()
        .unique()
        .tolist()
    )

    filtered_arrest_data = arrest_data[
        arrest_data["arrest_id"].isin(matched_arrest_ids)
    ]

    return filtered_arrest_data, filtered_match_data


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
        }
    )

    figure.update_layout(
        height=430,
        margin=dict(l=10, r=10, t=55, b=10)
    )

    return figure


def create_vertical_bar_chart(data, group_column, title, count_label="Incident Count"):
    """Create a vertical bar chart for grouped counts."""
    chart_data = create_count_dataframe(data, group_column)

    figure = px.bar(
        chart_data,
        x=group_column,
        y="incident_count",
        title=title,
        labels={
            group_column: "",
            "incident_count": count_label
        }
    )

    figure.update_layout(
        height=430,
        margin=dict(l=10, r=10, t=55, b=10)
    )

    return figure


def create_monthly_line_chart(data):
    """Create a monthly incident trend line chart."""
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
        }
    )

    figure.update_layout(
        height=430,
        margin=dict(l=10, r=10, t=55, b=10)
    )

    return figure


def create_arrest_monthly_chart(arrest_data):
    """Create a monthly arrest trend chart."""
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
        }
    )

    figure.update_layout(
        height=430,
        margin=dict(l=10, r=10, t=55, b=10)
    )

    return figure


def create_weekday_chart(data):
    """Create a weekday incident trend chart."""
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
        }
    )

    figure.update_layout(
        height=430,
        margin=dict(l=10, r=10, t=55, b=10)
    )

    return figure


def create_hourly_chart(data):
    """Create an hourly incident trend chart."""
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
        }
    )

    figure.update_layout(
        height=430,
        margin=dict(l=10, r=10, t=55, b=10)
    )

    return figure


def create_delay_bucket_chart(data):
    """Create a reporting delay bucket chart."""
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
        }
    )

    figure.update_layout(
        height=430,
        margin=dict(l=10, r=10, t=55, b=10)
    )

    return figure


def create_crime_disposition_heatmap(data):
    """Create a heatmap showing crime group by disposition group."""
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
        title="Crime Group by Disposition Group",
        labels={
            "disposition_group": "Disposition Group",
            "crime_group": "Crime Group",
            "incident_count": "Incident Count"
        }
    )

    figure.update_layout(
        height=520,
        margin=dict(l=10, r=10, t=55, b=10)
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
            "avg_report_delay_hours": "Average Reporting Delay Hours",
            group_column: ""
        }
    )

    figure.update_layout(
        height=430,
        margin=dict(l=10, r=10, t=55, b=10)
    )

    return figure


def show_executive_overview(data):
    """Display the Executive Overview tab."""
    st.subheader("Executive Overview")

    show_section_note(
        "This page summarizes overall incident volume, arrest-related outcomes, reporting delay, and the most common incident categories."
    )

    total_incidents = len(data)
    arrest_related_incidents = int(data["is_arrest_related"].sum())

    arrest_related_percentage = (
        arrest_related_incidents / total_incidents * 100
        if total_incidents > 0
        else 0
    )

    average_reporting_delay = data["report_delay_hours"].mean()

    most_common_crime_group, crime_count = get_top_value(data, "crime_group")
    most_common_disposition, disposition_count = get_top_value(data, "disposition_group")
    top_location_group, location_count = get_top_value(data, "location_group")

    card_1, card_2, card_3, card_4 = st.columns(4)

    card_1.metric("Total Incidents", format_number(total_incidents))
    card_2.metric("Arrest-Related Incidents", format_number(arrest_related_incidents))
    card_3.metric("Arrest-Related %", format_percentage(arrest_related_percentage))

    card_4.metric(
        "Avg Reporting Delay",
        f"{average_reporting_delay:.1f} hrs" if not pd.isna(average_reporting_delay) else "N/A"
    )

    card_5, card_6, card_7 = st.columns(3)

    card_5.metric("Most Common Crime Group", most_common_crime_group)
    card_6.metric("Most Common Disposition", most_common_disposition)
    card_7.metric("Top Location Group", top_location_group)

    show_insight(
        f"In the selected records, {most_common_crime_group} is the most common crime group "
        f"with {format_number(crime_count)} incidents. The most common disposition group is "
        f"{most_common_disposition}."
    )

    st.divider()

    left_column, right_column = st.columns(2)

    with left_column:
        st.plotly_chart(
            create_monthly_line_chart(data),
            use_container_width=True,
            key="executive_monthly_line_chart"
        )

        peak_month, peak_month_count = get_top_value(data, "occurred_month_name")
        show_insight(
            f"{peak_month} has the highest incident count in the selected filter range "
            f"with {format_number(peak_month_count)} incidents."
        )

    with right_column:
        st.plotly_chart(
            create_horizontal_bar_chart(data, "crime_group", "Incidents by Crime Group"),
            use_container_width=True,
            key="executive_crime_group_chart"
        )

        show_insight(
            f"{most_common_crime_group} appears most frequently, making it the strongest driver "
            f"of total incident volume in the current selection."
        )

    left_column, right_column = st.columns(2)

    with left_column:
        st.plotly_chart(
            create_horizontal_bar_chart(data, "disposition_group", "Incidents by Disposition Group"),
            use_container_width=True,
            key="executive_disposition_group_chart"
        )

        show_insight(
            f"{most_common_disposition} is the leading outcome category, appearing in "
            f"{format_number(disposition_count)} incident records."
        )

    with right_column:
        st.plotly_chart(
            create_horizontal_bar_chart(data, "location_group", "Incidents by Location Group"),
            use_container_width=True,
            key="executive_location_group_chart"
        )

        show_insight(
            f"{top_location_group} is the highest-volume location group in the selected data."
        )

    st.plotly_chart(
        create_delay_bucket_chart(data),
        use_container_width=True,
        key="executive_delay_bucket_chart"
    )

    top_delay_bucket, delay_bucket_count = get_top_value(data, "delay_bucket")
    show_insight(
        f"The most common reporting delay bucket is {top_delay_bucket}, with "
        f"{format_number(delay_bucket_count)} records."
    )


def show_incident_trends(data):
    """Display the Incident Trends tab."""
    st.subheader("Incident Trends")

    show_section_note(
        "This page highlights when incidents occur by month, weekday, hour of day, and academic period."
    )

    peak_month, peak_month_count = get_top_value(data, "occurred_month_name")
    peak_weekday, peak_weekday_count = get_top_value(data, "occurred_weekday")
    peak_hour, peak_hour_count = get_top_value(data, "occurred_hour")

    weekend_percentage = (
        data["occurred_is_weekend"].sum() / len(data) * 100
        if len(data) > 0
        else 0
    )

    card_1, card_2, card_3, card_4 = st.columns(4)

    card_1.metric("Peak Month", peak_month)
    card_2.metric("Peak Weekday", peak_weekday)
    card_3.metric("Peak Hour", peak_hour)
    card_4.metric("Weekend Incident %", format_percentage(weekend_percentage))

    show_insight(
        f"Incident activity is highest in {peak_month}, on {peak_weekday}s, "
        f"and around hour {peak_hour} in the selected filter range."
    )

    st.divider()

    left_column, right_column = st.columns(2)

    with left_column:
        st.plotly_chart(
            create_monthly_line_chart(data),
            use_container_width=True,
            key="trends_monthly_line_chart"
        )

        show_insight(
            f"{peak_month} is the peak month with {format_number(peak_month_count)} incidents."
        )

    with right_column:
        st.plotly_chart(
            create_weekday_chart(data),
            use_container_width=True,
            key="trends_weekday_chart"
        )

        show_insight(
            f"{peak_weekday} has the highest incident count with "
            f"{format_number(peak_weekday_count)} incidents."
        )

    left_column, right_column = st.columns(2)

    with left_column:
        st.plotly_chart(
            create_hourly_chart(data),
            use_container_width=True,
            key="trends_hourly_chart"
        )

        show_insight(
            f"Hour {peak_hour} has the highest incident count with "
            f"{format_number(peak_hour_count)} incidents."
        )

    with right_column:
        st.plotly_chart(
            create_vertical_bar_chart(data, "occurred_semester_period", "Incidents by Academic Period"),
            use_container_width=True,
            key="trends_academic_period_chart"
        )

        top_period, period_count = get_top_value(data, "occurred_semester_period")
        show_insight(
            f"{top_period} has the highest incident volume among academic periods, "
            f"with {format_number(period_count)} incidents."
        )


def show_incident_outcomes(data):
    """Display the Incident Outcomes tab."""
    st.subheader("Incident Outcomes")

    show_section_note(
        "This page compares case dispositions and shows how incident categories relate to outcome groups."
    )

    total_incidents = len(data)
    arrest_count = int(data["is_arrest_related"].sum())
    pending_count = int(data["is_pending"].sum())
    closed_count = int(data["is_closed"].sum())

    arrest_percentage = (
        arrest_count / total_incidents * 100
        if total_incidents > 0
        else 0
    )

    card_1, card_2, card_3, card_4 = st.columns(4)

    card_1.metric("Total Incidents", format_number(total_incidents))
    card_2.metric("Arrest-Related", format_number(arrest_count))
    card_3.metric("Pending / Active", format_number(pending_count))
    card_4.metric("Closed / Cleared", format_number(closed_count))

    show_insight(
        f"{format_percentage(arrest_percentage)} of selected incident records are marked as arrest-related "
        f"based on their disposition category."
    )

    st.divider()

    left_column, right_column = st.columns(2)

    with left_column:
        st.plotly_chart(
            create_horizontal_bar_chart(data, "disposition_group", "Incidents by Disposition Group"),
            use_container_width=True,
            key="outcomes_disposition_group_chart"
        )

        top_disposition, disposition_count = get_top_value(data, "disposition_group")
        show_insight(
            f"{top_disposition} is the most common disposition group, appearing in "
            f"{format_number(disposition_count)} records."
        )

    with right_column:
        st.plotly_chart(
            create_horizontal_bar_chart(data, "disposition", "Incidents by Detailed Disposition", max_categories=15),
            use_container_width=True,
            key="outcomes_detailed_disposition_chart"
        )

        top_detailed_disposition, detailed_count = get_top_value(data, "disposition")
        show_insight(
            f"The most common detailed disposition is {top_detailed_disposition}, "
            f"with {format_number(detailed_count)} records."
        )

    st.plotly_chart(
        create_crime_disposition_heatmap(data),
        use_container_width=True,
        key="outcomes_crime_disposition_heatmap"
    )

    show_insight(
        "The heatmap helps identify which crime groups are most often associated with each disposition outcome."
    )


def show_reporting_delay(data):
    """Display the Reporting Delay tab."""
    st.subheader("Reporting Delay Analysis")

    show_section_note(
        "This page measures the time between when an incident occurred and when it was reported."
    )

    valid_delay_data = data[data["has_valid_reporting_delay"] == 1]

    avg_delay_hours = valid_delay_data["report_delay_hours"].mean()
    avg_delay_days = valid_delay_data["report_delay_days"].mean()

    same_day_count = len(
        valid_delay_data[
            valid_delay_data["delay_bucket"] == "Same Day / Within 24 Hours"
        ]
    )

    over_7_days_count = len(
        valid_delay_data[
            valid_delay_data["delay_bucket"] == "Over 7 Days"
        ]
    )

    same_day_percentage = (
        same_day_count / len(valid_delay_data) * 100
        if len(valid_delay_data) > 0
        else 0
    )

    card_1, card_2, card_3, card_4 = st.columns(4)

    card_1.metric("Avg Delay Hours", f"{avg_delay_hours:.1f}" if not pd.isna(avg_delay_hours) else "N/A")
    card_2.metric("Avg Delay Days", f"{avg_delay_days:.1f}" if not pd.isna(avg_delay_days) else "N/A")
    card_3.metric("Same-Day Reporting %", format_percentage(same_day_percentage))
    card_4.metric("Over 7 Days Count", format_number(over_7_days_count))

    show_insight(
        f"The average reporting delay is {avg_delay_hours:.1f} hours. "
        f"{format_percentage(same_day_percentage)} of valid records were reported within the same day."
        if not pd.isna(avg_delay_hours)
        else "Reporting delay could not be calculated for the selected data."
    )

    st.divider()

    left_column, right_column = st.columns(2)

    with left_column:
        st.plotly_chart(
            create_delay_bucket_chart(data),
            use_container_width=True,
            key="delay_delay_bucket_chart"
        )

        top_delay_bucket, delay_bucket_count = get_top_value(data, "delay_bucket")
        show_insight(
            f"{top_delay_bucket} is the most common reporting delay bucket, with "
            f"{format_number(delay_bucket_count)} records."
        )

    with right_column:
        st.plotly_chart(
            create_reporting_delay_by_group_chart(
                data,
                "crime_group",
                "Average Reporting Delay by Crime Group"
            ),
            use_container_width=True,
            key="delay_by_crime_group_chart"
        )

        if not valid_delay_data.empty:
            delay_by_crime = (
                valid_delay_data
                .groupby("crime_group")["report_delay_hours"]
                .mean()
                .sort_values(ascending=False)
            )

            show_insight(
                f"{delay_by_crime.index[0]} has the highest average reporting delay among crime groups."
            )

    st.plotly_chart(
        create_reporting_delay_by_group_chart(
            data,
            "location_group",
            "Average Reporting Delay by Location Group"
        ),
        use_container_width=True,
        key="delay_by_location_group_chart"
    )

    if not valid_delay_data.empty:
        delay_by_location = (
            valid_delay_data
            .groupby("location_group")["report_delay_hours"]
            .mean()
            .sort_values(ascending=False)
        )

        show_insight(
            f"{delay_by_location.index[0]} has the highest average reporting delay among location groups."
        )

    with st.expander("Highest Reporting Delay Records"):
        delay_columns = [
            "incident_id",
            "case_number",
            "occurred_datetime",
            "reported_datetime",
            "crime_group",
            "disposition_group",
            "location_group",
            "report_delay_hours",
            "report_delay_days"
        ]

        st.dataframe(
            valid_delay_data[delay_columns]
            .sort_values("report_delay_hours", ascending=False)
            .head(50),
            use_container_width=True
        )


def show_location_analysis(data):
    """Display the Location Analysis tab."""
    st.subheader("Location Analysis")

    show_section_note(
        "This page identifies high-activity locations and shows how incident categories vary across location groups."
    )

    unique_locations = data["location_raw"].nunique()

    top_location, top_location_count = get_top_value(data, "location_raw")
    top_location_group, top_location_group_count = get_top_value(data, "location_group")

    card_1, card_2, card_3 = st.columns(3)

    card_1.metric("Unique Locations", format_number(unique_locations))
    card_2.metric("Top Location", top_location)
    card_3.metric("Top Location Group", top_location_group)

    show_insight(
        f"The selected data includes {format_number(unique_locations)} unique locations. "
        f"The highest-volume specific location is {top_location}."
    )

    st.divider()

    left_column, right_column = st.columns(2)

    with left_column:
        st.plotly_chart(
            create_horizontal_bar_chart(data, "location_raw", "Top Locations", max_categories=20),
            use_container_width=True,
            key="location_top_locations_chart"
        )

        show_insight(
            f"{top_location} appears most frequently with {format_number(top_location_count)} incidents."
        )

    with right_column:
        st.plotly_chart(
            create_horizontal_bar_chart(data, "location_group", "Incidents by Location Group"),
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


def show_arrest_analysis(arrest_data, match_data, charge_summary, demographic_summary):
    """Display the Arrest and Charge Analysis tab."""
    st.subheader("Arrest & Charge Analysis")

    show_section_note(
        "This page analyzes arrest records, charge categories, and incident-to-arrest matching using UMPD case numbers."
    )

    total_arrests = len(arrest_data)
    unique_arrest_cases = arrest_data["case_number"].nunique()
    matched_incidents = int(match_data["has_matching_arrest"].sum())
    total_incidents = len(match_data)

    match_percentage = (
        matched_incidents / total_incidents * 100
        if total_incidents > 0
        else 0
    )

    top_charge_category = (
        charge_summary.sort_values("arrest_count", ascending=False).iloc[0]["charge_category"]
        if not charge_summary.empty
        else "N/A"
    )

    card_1, card_2, card_3, card_4 = st.columns(4)

    card_1.metric("Total Arrest Records", format_number(total_arrests))
    card_2.metric("Unique Arrest Case Numbers", format_number(unique_arrest_cases))
    card_3.metric("Matched Incident Records", format_number(matched_incidents))
    card_4.metric("Incident Match %", format_percentage(match_percentage))

    card_5, card_6, card_7 = st.columns(3)

    card_5.metric("Top Charge Category", top_charge_category)
    card_6.metric("Charge Categories", format_number(charge_summary["charge_category"].nunique()))
    card_7.metric("Demographic Groups", format_number(len(demographic_summary)))

    show_insight(
        f"{format_percentage(match_percentage)} of selected incident records have a matching arrest record. "
        f"The leading charge category is {top_charge_category}."
    )

    st.caption(
        "Arrest records are matched to incident records using UMPD case number. "
        "Demographic summaries are descriptive only and should not be used for individual prediction or risk scoring."
    )

    st.divider()

    left_column, right_column = st.columns(2)

    with left_column:
        if arrest_data.empty:
            st.info("No matching arrest records are available for the selected filters.")
        else:
            st.plotly_chart(
                create_arrest_monthly_chart(arrest_data),
                use_container_width=True,
                key="arrest_monthly_chart"
            )

            top_arrest_month, arrest_month_count = get_top_value(arrest_data, "arrested_month_name")
            show_insight(
                f"{top_arrest_month} has the highest arrest count in the selected data, "
                f"with {format_number(arrest_month_count)} arrests."
            )

    with right_column:
        if arrest_data.empty:
            st.info("No charge category chart available for the selected filters.")
        else:
            st.plotly_chart(
                create_horizontal_bar_chart(
                    arrest_data,
                    "charge_category",
                    "Arrests by Charge Category",
                    count_label="Arrest Count"
                ),
                use_container_width=True,
                key="arrest_charge_category_chart"
            )

            top_charge, charge_count = get_top_value(arrest_data, "charge_category")
            show_insight(
                f"{top_charge} is the most common charge category among matching arrest records."
            )

    left_column, right_column = st.columns(2)

    with left_column:
        if not arrest_data.empty:
            st.plotly_chart(
                create_horizontal_bar_chart(
                    arrest_data,
                    "race",
                    "Arrests by Race",
                    count_label="Arrest Count"
                ),
                use_container_width=True,
                key="arrest_race_chart"
            )

            top_race, race_count = get_top_value(arrest_data, "race")
            show_insight(
                f"{top_race} is the most frequent race value in the selected arrest records. "
                "This is descriptive only and should be interpreted carefully."
            )
        else:
            st.info("No race summary available for the selected filters.")

    with right_column:
        if not arrest_data.empty:
            st.plotly_chart(
                create_horizontal_bar_chart(
                    arrest_data,
                    "sex",
                    "Arrests by Sex",
                    count_label="Arrest Count"
                ),
                use_container_width=True,
                key="arrest_sex_chart"
            )

            top_sex, sex_count = get_top_value(arrest_data, "sex")
            show_insight(
                f"{top_sex} is the most frequent sex value in the selected arrest records. "
                "This is descriptive only and should not be used for prediction."
            )
        else:
            st.info("No sex summary available for the selected filters.")

    left_column, right_column = st.columns(2)

    with left_column:
        match_summary = (
            match_data.groupby("has_matching_arrest")
            .size()
            .reset_index(name="incident_count")
        )

        match_summary["match_status"] = match_summary["has_matching_arrest"].map(
            {
                0: "No Matching Arrest",
                1: "Matching Arrest"
            }
        )

        figure = px.bar(
            match_summary,
            x="match_status",
            y="incident_count",
            title="Incident-to-Arrest Match Summary",
            labels={
                "match_status": "",
                "incident_count": "Incident Count"
            }
        )

        figure.update_layout(
            height=430,
            margin=dict(l=10, r=10, t=55, b=10)
        )

        st.plotly_chart(
            figure,
            use_container_width=True,
            key="incident_arrest_match_chart"
        )

        show_insight(
            f"{format_number(matched_incidents)} out of {format_number(total_incidents)} selected incident records "
            f"have a matching arrest record."
        )

    with right_column:
        matched_charge_data = (
            match_data[match_data["has_matching_arrest"] == 1]
            .groupby("charge_category")
            .size()
            .reset_index(name="matched_incident_count")
            .sort_values("matched_incident_count", ascending=True)
        )

        if matched_charge_data.empty:
            st.info("No matched incident-charge records are available for the selected filters.")
        else:
            figure = px.bar(
                matched_charge_data,
                x="matched_incident_count",
                y="charge_category",
                orientation="h",
                title="Matched Incidents by Charge Category",
                labels={
                    "matched_incident_count": "Matched Incident Count",
                    "charge_category": ""
                }
            )

            figure.update_layout(
                height=430,
                margin=dict(l=10, r=10, t=55, b=10)
            )

            st.plotly_chart(
                figure,
                use_container_width=True,
                key="matched_incident_charge_category_chart"
            )

            top_matched_charge = matched_charge_data.sort_values(
                "matched_incident_count",
                ascending=False
            ).iloc[0]

            show_insight(
                f"{top_matched_charge['charge_category']} is the leading charge category among matched incident records."
            )

    with st.expander("View Sample Arrest Records"):
        arrest_preview_columns = [
            "arrest_id",
            "arrest_number",
            "case_number",
            "arrested_datetime",
            "charge_category",
            "race",
            "sex",
            "age_group",
            "arrested_charge"
        ]

        st.dataframe(
            arrest_data[arrest_preview_columns].head(100),
            use_container_width=True
        )

    with st.expander("View Matched Incident-Arrest Records"):
        match_preview_columns = [
            "incident_id",
            "case_number",
            "occurred_datetime",
            "crime_group",
            "disposition_group",
            "arrest_id",
            "arrest_number",
            "arrested_datetime",
            "charge_category",
            "hours_from_incident_to_arrest"
        ]

        st.dataframe(
            match_data[
                match_data["has_matching_arrest"] == 1
            ][match_preview_columns].head(100),
            use_container_width=True
        )


def show_data_quality(incident_data, arrest_data):
    """Display the Data Quality tab."""
    st.subheader("Data Quality")

    show_section_note(
        "This page checks whether key incident and arrest fields are valid, complete, and ready for analysis."
    )

    total_incident_records = len(incident_data)
    total_arrest_records = len(arrest_data)

    valid_incident_case_numbers = int(incident_data["has_valid_case_number"].sum())
    valid_incident_dates = int(incident_data["has_valid_occurred_datetime"].sum())
    valid_arrest_case_numbers = int(arrest_data["has_valid_case_number"].sum()) if not arrest_data.empty else 0
    valid_arrest_dates = int(arrest_data["has_valid_arrested_datetime"].sum()) if not arrest_data.empty else 0

    incident_case_validity = (
        valid_incident_case_numbers / total_incident_records * 100
        if total_incident_records > 0
        else 0
    )

    arrest_case_validity = (
        valid_arrest_case_numbers / total_arrest_records * 100
        if total_arrest_records > 0
        else 0
    )

    card_1, card_2, card_3, card_4, card_5, card_6 = st.columns(6)

    card_1.metric("Incident Records", format_number(total_incident_records))
    card_2.metric("Arrest Records", format_number(total_arrest_records))
    card_3.metric("Valid Incident Cases", format_number(valid_incident_case_numbers))
    card_4.metric("Valid Incident Dates", format_number(valid_incident_dates))
    card_5.metric("Valid Arrest Cases", format_number(valid_arrest_case_numbers))
    card_6.metric("Valid Arrest Dates", format_number(valid_arrest_dates))

    show_insight(
        f"{format_percentage(incident_case_validity)} of selected incident records have valid case numbers. "
        f"{format_percentage(arrest_case_validity)} of selected arrest records have valid case numbers."
    )

    st.divider()

    quality_data = pd.DataFrame(
        {
            "Quality Check": [
                "Incident Valid Case Number",
                "Incident Valid Occurred Datetime",
                "Incident Valid Reported Datetime",
                "Incident Valid Reporting Delay",
                "Arrest Valid Case Number",
                "Arrest Valid Arrested Datetime",
                "Arrest Has Charge Text"
            ],
            "Valid Count": [
                valid_incident_case_numbers,
                int(incident_data["has_valid_occurred_datetime"].sum()),
                int(incident_data["has_valid_reported_datetime"].sum()),
                int(incident_data["has_valid_reporting_delay"].sum()),
                valid_arrest_case_numbers,
                valid_arrest_dates,
                int(arrest_data["has_charge_text"].sum()) if not arrest_data.empty else 0
            ],
            "Invalid Count": [
                total_incident_records - valid_incident_case_numbers,
                total_incident_records - int(incident_data["has_valid_occurred_datetime"].sum()),
                total_incident_records - int(incident_data["has_valid_reported_datetime"].sum()),
                total_incident_records - int(incident_data["has_valid_reporting_delay"].sum()),
                total_arrest_records - valid_arrest_case_numbers,
                total_arrest_records - valid_arrest_dates,
                total_arrest_records - int(arrest_data["has_charge_text"].sum()) if not arrest_data.empty else 0
            ]
        }
    )

    figure = px.bar(
        quality_data,
        x="Quality Check",
        y=["Valid Count", "Invalid Count"],
        title="Data Quality Summary",
        barmode="group",
        labels={
            "value": "Record Count",
            "variable": "Status"
        }
    )

    figure.update_layout(
        height=500,
        margin=dict(l=10, r=10, t=55, b=10)
    )

    st.plotly_chart(
        figure,
        use_container_width=True,
        key="quality_summary_chart"
    )

    show_insight(
        "Data quality checks confirm whether key identifiers, dates, reporting delays, and charge text are usable for analysis."
    )

    with st.expander("Incident Records Needing Review"):
        incident_review_columns = [
            "incident_id",
            "case_number",
            "occurred_datetime",
            "reported_datetime",
            "crime_group",
            "disposition_group",
            "location_group",
            "has_valid_case_number",
            "has_valid_occurred_datetime",
            "has_valid_reported_datetime",
            "has_valid_reporting_delay"
        ]

        incident_review_data = incident_data[
            (incident_data["has_valid_case_number"] == 0)
            | (incident_data["has_valid_occurred_datetime"] == 0)
            | (incident_data["has_valid_reported_datetime"] == 0)
            | (incident_data["has_valid_reporting_delay"] == 0)
        ]

        st.dataframe(
            incident_review_data[incident_review_columns],
            use_container_width=True
        )

    with st.expander("Arrest Records Needing Review"):
        arrest_review_columns = [
            "arrest_id",
            "arrest_number",
            "case_number",
            "arrested_datetime",
            "charge_category",
            "race",
            "sex",
            "age_group",
            "has_valid_arrest_number",
            "has_valid_case_number",
            "has_valid_arrested_datetime",
            "has_charge_text"
        ]

        if arrest_data.empty:
            st.info("No arrest records are available for the selected filters.")
        else:
            arrest_review_data = arrest_data[
                (arrest_data["has_valid_arrest_number"] == 0)
                | (arrest_data["has_valid_case_number"] == 0)
                | (arrest_data["has_valid_arrested_datetime"] == 0)
                | (arrest_data["has_charge_text"] == 0)
            ]

            st.dataframe(
                arrest_review_data[arrest_review_columns],
                use_container_width=True
            )


def show_sample_records(data):
    """Display sample incident records."""
    with st.expander("View Sample Incident Records"):
        preview_columns = [
            "incident_id",
            "case_number",
            "occurred_datetime",
            "crime_group",
            "disposition_group",
            "location_group",
            "report_delay_hours"
        ]

        st.dataframe(
            data[preview_columns].head(100),
            use_container_width=True
        )


def main():
    """Run the Streamlit dashboard."""
    apply_custom_styles()

    dashboard_data = load_dashboard_data()

    incident_data = dashboard_data["incident_data"]
    arrest_data = dashboard_data["arrest_data"]
    match_data = dashboard_data["match_data"]
    charge_summary = dashboard_data["charge_summary"]
    demographic_summary = dashboard_data["demographic_summary"]

    show_dashboard_header()

    filtered_incident_data = apply_incident_filters(incident_data)

    if filtered_incident_data.empty:
        st.warning("No incident records match the selected filters.")
        return

    filtered_arrest_data, filtered_match_data = filter_related_arrest_data(
        arrest_data,
        match_data,
        filtered_incident_data
    )

    tab_1, tab_2, tab_3, tab_4, tab_5, tab_6, tab_7 = st.tabs(
        [
            "Executive Overview",
            "Incident Trends",
            "Incident Outcomes",
            "Reporting Delay",
            "Location Analysis",
            "Arrest & Charge Analysis",
            "Data Quality"
        ]
    )

    with tab_1:
        show_executive_overview(filtered_incident_data)

    with tab_2:
        show_incident_trends(filtered_incident_data)

    with tab_3:
        show_incident_outcomes(filtered_incident_data)

    with tab_4:
        show_reporting_delay(filtered_incident_data)

    with tab_5:
        show_location_analysis(filtered_incident_data)

    with tab_6:
        show_arrest_analysis(
            filtered_arrest_data,
            filtered_match_data,
            charge_summary,
            demographic_summary
        )

    with tab_7:
        show_data_quality(
            filtered_incident_data,
            filtered_arrest_data
        )

    st.divider()

    show_sample_records(filtered_incident_data)


if __name__ == "__main__":
    main()
    