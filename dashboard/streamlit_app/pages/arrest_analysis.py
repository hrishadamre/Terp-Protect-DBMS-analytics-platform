"""
arrest_analysis.py

Purpose:
Display the Arrest & Charge Analysis tab for the Terp Protect Streamlit dashboard.

This page analyzes arrest records, charge categories, incident-to-arrest matching,
and descriptive demographic summaries using UMPD public arrest data.
"""

import plotly.express as px
import streamlit as st

from components.charts import (
    create_arrest_monthly_chart,
    create_horizontal_bar_chart
)

from components.layout import (
    show_insight,
    show_section_note
)

from components.metrics import (
    format_number,
    format_percentage,
    get_top_value
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

            top_arrest_month, arrest_month_count = get_top_value(
                arrest_data,
                "arrested_month_name"
            )

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

            top_charge, charge_count = get_top_value(
                arrest_data,
                "charge_category"
            )

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