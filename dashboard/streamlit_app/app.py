"""
app.py

Purpose:
Build the Streamlit dashboard for the Terp Protect campus safety analytics project.

Current Scope:
- Source: UMPD Daily Crime and Incident Logs
- Year: 2025
- Input File: dashboard/powerbi/data/incident_detail.csv

Current App Version:
Version 2 includes multiple dashboard tabs:
1. Executive Overview
2. Incident Trends
3. Incident Outcomes
4. Reporting Delay
5. Location Analysis
6. Data Quality

Role in Pipeline:
This app belongs to the presentation layer. It uses dashboard-ready data generated from
the Terp Protect DBMS and SQL views to create an interactive local dashboard.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


DATA_PATH = Path("dashboard/powerbi/data/incident_detail.csv")


st.set_page_config(
    page_title="Terp Protect Dashboard",
    page_icon="🐢",
    layout="wide"
)


@st.cache_data
def load_data():
    """Load dashboard-ready incident detail data."""
    if not DATA_PATH.exists():
        st.error(f"Data file not found: {DATA_PATH}")
        st.stop()

    data = pd.read_csv(DATA_PATH)

    data["occurred_datetime"] = pd.to_datetime(
        data["occurred_datetime"],
        errors="coerce"
    )

    data["reported_datetime"] = pd.to_datetime(
        data["reported_datetime"],
        errors="coerce"
    )

    return data


def format_number(value):
    """Format large numbers with commas."""
    return f"{int(value):,}"


def format_percentage(value):
    """Format percentage values."""
    if pd.isna(value):
        return "0.0%"

    return f"{value:.1f}%"


def get_month_order(data):
    """Return month names ordered by month number."""
    month_order = (
        data[["occurred_month", "occurred_month_name"]]
        .dropna()
        .drop_duplicates()
        .sort_values("occurred_month")
    )

    return month_order["occurred_month_name"].tolist()


def apply_filters(data):
    """Create sidebar filters and return filtered data."""
    st.sidebar.header("Filters")

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


def create_count_dataframe(data, group_column, count_column_name="incident_count"):
    """Create a grouped count dataframe."""
    return (
        data.groupby(group_column)
        .size()
        .reset_index(name=count_column_name)
        .sort_values(count_column_name, ascending=False)
    )


def create_horizontal_bar_chart(data, group_column, title, max_categories=None):
    """Create a horizontal bar chart for grouped incident counts."""
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
            "incident_count": "Incident Count",
            group_column: ""
        }
    )

    figure.update_layout(
        height=430,
        margin=dict(l=10, r=10, t=55, b=10)
    )

    return figure


def create_vertical_bar_chart(data, group_column, title):
    """Create a vertical bar chart for grouped incident counts."""
    chart_data = create_count_dataframe(data, group_column)

    figure = px.bar(
        chart_data,
        x=group_column,
        y="incident_count",
        title=title,
        labels={
            group_column: "",
            "incident_count": "Incident Count"
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

    total_incidents = len(data)
    arrest_related_incidents = int(data["is_arrest_related"].sum())

    arrest_related_percentage = (
        arrest_related_incidents / total_incidents * 100
        if total_incidents > 0
        else 0
    )

    average_reporting_delay = data["report_delay_hours"].mean()

    most_common_crime_group = (
        data["crime_group"].mode().iloc[0]
        if not data.empty
        else "N/A"
    )

    most_common_disposition = (
        data["disposition_group"].mode().iloc[0]
        if not data.empty
        else "N/A"
    )

    top_location_group = (
        data["location_group"].mode().iloc[0]
        if not data.empty
        else "N/A"
    )

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

    st.divider()

    left_column, right_column = st.columns(2)

    with left_column:
        st.plotly_chart(
            create_monthly_line_chart(data),
            use_container_width=True,
            key="executive_monthly_line_chart"
        )

    with right_column:
        st.plotly_chart(
            create_horizontal_bar_chart(data, "crime_group", "Incidents by Crime Group"),
            use_container_width=True,
            key="executive_crime_group_chart"
        )

    left_column, right_column = st.columns(2)

    with left_column:
        st.plotly_chart(
            create_horizontal_bar_chart(data, "disposition_group", "Incidents by Disposition Group"),
            use_container_width=True,
            key="executive_disposition_group_chart"
        )

    with right_column:
        st.plotly_chart(
            create_horizontal_bar_chart(data, "location_group", "Incidents by Location Group"),
            use_container_width=True,
            key="executive_location_group_chart"
        )

    st.plotly_chart(
        create_delay_bucket_chart(data),
        use_container_width=True,
        key="executive_delay_bucket_chart"
    )


def show_incident_trends(data):
    """Display the Incident Trends tab."""
    st.subheader("Incident Trends")

    peak_month = (
        create_count_dataframe(data, "occurred_month_name").iloc[0]["occurred_month_name"]
        if not data.empty
        else "N/A"
    )

    peak_weekday = (
        create_count_dataframe(data, "occurred_weekday").iloc[0]["occurred_weekday"]
        if not data.empty
        else "N/A"
    )

    peak_hour = (
        create_count_dataframe(data, "occurred_hour").iloc[0]["occurred_hour"]
        if not data.empty
        else "N/A"
    )

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

    st.divider()

    left_column, right_column = st.columns(2)

    with left_column:
        st.plotly_chart(
            create_monthly_line_chart(data),
            use_container_width=True,
            key="trends_monthly_line_chart"
        )

    with right_column:
        st.plotly_chart(
            create_weekday_chart(data),
            use_container_width=True,
            key="trends_weekday_chart"
        )

    left_column, right_column = st.columns(2)

    with left_column:
        st.plotly_chart(
            create_hourly_chart(data),
            use_container_width=True,
            key="trends_hourly_chart"
        )

    with right_column:
        st.plotly_chart(
            create_vertical_bar_chart(data, "occurred_semester_period", "Incidents by Academic Period"),
            use_container_width=True,
            key="trends_academic_period_chart"
        )


def show_incident_outcomes(data):
    """Display the Incident Outcomes tab."""
    st.subheader("Incident Outcomes")

    total_incidents = len(data)
    arrest_count = int(data["is_arrest_related"].sum())
    pending_count = int(data["is_pending"].sum())
    closed_count = int(data["is_closed"].sum())

    card_1, card_2, card_3, card_4 = st.columns(4)

    card_1.metric("Total Incidents", format_number(total_incidents))
    card_2.metric("Arrest-Related", format_number(arrest_count))
    card_3.metric("Pending / Active", format_number(pending_count))
    card_4.metric("Closed / Cleared", format_number(closed_count))

    st.divider()

    left_column, right_column = st.columns(2)

    with left_column:
        st.plotly_chart(
            create_horizontal_bar_chart(data, "disposition_group", "Incidents by Disposition Group"),
            use_container_width=True,
            key="outcomes_disposition_group_chart"
        )

    with right_column:
        st.plotly_chart(
            create_horizontal_bar_chart(data, "disposition", "Incidents by Detailed Disposition", max_categories=15),
            use_container_width=True,
            key="outcomes_detailed_disposition_chart"
        )

    st.plotly_chart(
        create_crime_disposition_heatmap(data),
        use_container_width=True,
        key="outcomes_crime_disposition_heatmap"
    )


def show_reporting_delay(data):
    """Display the Reporting Delay tab."""
    st.subheader("Reporting Delay Analysis")

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

    st.divider()

    left_column, right_column = st.columns(2)

    with left_column:
        st.plotly_chart(
            create_delay_bucket_chart(data),
            use_container_width=True,
            key="delay_delay_bucket_chart"
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

    st.plotly_chart(
        create_reporting_delay_by_group_chart(
            data,
            "location_group",
            "Average Reporting Delay by Location Group"
        ),
        use_container_width=True,
        key="delay_by_location_group_chart"
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

    unique_locations = data["location_raw"].nunique()

    top_location = (
        create_count_dataframe(data, "location_raw").iloc[0]["location_raw"]
        if not data.empty
        else "N/A"
    )

    top_location_group = (
        create_count_dataframe(data, "location_group").iloc[0]["location_group"]
        if not data.empty
        else "N/A"
    )

    card_1, card_2, card_3 = st.columns(3)

    card_1.metric("Unique Locations", format_number(unique_locations))
    card_2.metric("Top Location", top_location)
    card_3.metric("Top Location Group", top_location_group)

    st.divider()

    left_column, right_column = st.columns(2)

    with left_column:
        st.plotly_chart(
            create_horizontal_bar_chart(data, "location_raw", "Top Locations", max_categories=20),
            use_container_width=True,
            key="location_top_locations_chart"
        )

    with right_column:
        st.plotly_chart(
            create_horizontal_bar_chart(data, "location_group", "Incidents by Location Group"),
            use_container_width=True,
            key="location_group_chart"
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


def show_data_quality(data):
    """Display the Data Quality tab."""
    st.subheader("Data Quality")

    total_records = len(data)
    valid_case_numbers = int(data["has_valid_case_number"].sum())
    valid_occurred_dates = int(data["has_valid_occurred_datetime"].sum())
    valid_reported_dates = int(data["has_valid_reported_datetime"].sum())
    valid_reporting_delays = int(data["has_valid_reporting_delay"].sum())

    card_1, card_2, card_3, card_4, card_5 = st.columns(5)

    card_1.metric("Total Records", format_number(total_records))
    card_2.metric("Valid Case Numbers", format_number(valid_case_numbers))
    card_3.metric("Valid Occurred Dates", format_number(valid_occurred_dates))
    card_4.metric("Valid Reported Dates", format_number(valid_reported_dates))
    card_5.metric("Valid Reporting Delays", format_number(valid_reporting_delays))

    st.divider()

    quality_data = pd.DataFrame(
        {
            "Quality Check": [
                "Valid Case Number",
                "Valid Occurred Datetime",
                "Valid Reported Datetime",
                "Valid Reporting Delay"
            ],
            "Valid Count": [
                valid_case_numbers,
                valid_occurred_dates,
                valid_reported_dates,
                valid_reporting_delays
            ],
            "Invalid Count": [
                total_records - valid_case_numbers,
                total_records - valid_occurred_dates,
                total_records - valid_reported_dates,
                total_records - valid_reporting_delays
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
        height=430,
        margin=dict(l=10, r=10, t=55, b=10)
    )

    st.plotly_chart(
        figure,
        use_container_width=True,
        key="quality_summary_chart"
    )

    with st.expander("Records Needing Review"):
        review_columns = [
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

        review_data = data[
            (data["has_valid_case_number"] == 0)
            | (data["has_valid_occurred_datetime"] == 0)
            | (data["has_valid_reported_datetime"] == 0)
            | (data["has_valid_reporting_delay"] == 0)
        ]

        st.dataframe(
            review_data[review_columns],
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
    data = load_data()

    st.title("Terp Protect: Campus Safety Incident Analytics")

    st.caption(
        "Interactive dashboard built from cleaned and modeled UMPD Daily Crime and Incident Log records."
    )

    filtered_data = apply_filters(data)

    if filtered_data.empty:
        st.warning("No records match the selected filters.")
        return

    tab_1, tab_2, tab_3, tab_4, tab_5, tab_6 = st.tabs(
        [
            "Executive Overview",
            "Incident Trends",
            "Incident Outcomes",
            "Reporting Delay",
            "Location Analysis",
            "Data Quality"
        ]
    )

    with tab_1:
        show_executive_overview(filtered_data)

    with tab_2:
        show_incident_trends(filtered_data)

    with tab_3:
        show_incident_outcomes(filtered_data)

    with tab_4:
        show_reporting_delay(filtered_data)

    with tab_5:
        show_location_analysis(filtered_data)

    with tab_6:
        show_data_quality(filtered_data)

    st.divider()

    show_sample_records(filtered_data)


if __name__ == "__main__":
    main()