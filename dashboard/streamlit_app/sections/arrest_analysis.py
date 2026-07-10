"""
arrest_analysis.py

Purpose:
Display the arrest linkage profile section for the Terp Protect Streamlit dashboard.

This section analyzes arrest records, charge categories, incident-to-arrest matching,
and descriptive demographic summaries using UMPD public arrest data.
"""

import plotly.express as px
import streamlit as st

from components.charts import (
    apply_chart_theme,
    create_arrest_monthly_chart,
    create_horizontal_bar_chart,
    create_match_summary_chart,
    create_soft_donut_chart,
    get_chart_config
)

from components.layout import (
    show_compact_record_note,
    show_info_hint,
    show_insight,
    show_section_note
)

from components.metrics import (
    format_number,
    format_percentage,
    get_top_value
)

from components.theme import get_theme


def get_safe_top_charge_category(charge_summary):
    """Return the leading charge category from charge summary data."""
    if charge_summary.empty or "charge_category" not in charge_summary.columns:
        return "N/A"

    if "arrest_count" not in charge_summary.columns:
        return "N/A"

    return (
        charge_summary
        .sort_values("arrest_count", ascending=False)
        .iloc[0]["charge_category"]
    )


def get_safe_unique_count(data, column):
    """Return unique count for a column if it exists."""
    if data.empty or column not in data.columns:
        return 0

    return data[column].nunique()


def show_arrest_analysis(arrest_data, match_data, charge_summary, demographic_summary):
    """Display the arrest linkage profile section."""
    st.subheader("Arrest Linkage Profile")

    show_section_note(
        "Analyze arrest records, charge categories, and incident-to-arrest matching using UMPD case numbers. Demographic summaries are descriptive public-record fields only."
    )

    total_arrests = len(arrest_data)
    unique_arrest_cases = get_safe_unique_count(arrest_data, "case_number")

    matched_incidents = (
        int(match_data["has_matching_arrest"].sum())
        if "has_matching_arrest" in match_data.columns
        else 0
    )

    total_incidents = len(match_data)

    match_percentage = (
        matched_incidents / total_incidents * 100
        if total_incidents > 0
        else 0
    )

    top_charge_category = get_safe_top_charge_category(charge_summary)

    charge_category_count = (
        charge_summary["charge_category"].nunique()
        if not charge_summary.empty and "charge_category" in charge_summary.columns
        else 0
    )

    demographic_group_count = len(demographic_summary) if demographic_summary is not None else 0

    card_1, card_2, card_3, card_4 = st.columns(4)

    card_1.metric(
        "Arrest Records",
        format_number(total_arrests)
    )

    card_2.metric(
        "Unique Arrest Cases",
        format_number(unique_arrest_cases)
    )

    card_3.metric(
        "Matched Incidents",
        format_number(matched_incidents)
    )

    card_4.metric(
        "Match Coverage",
        format_percentage(match_percentage)
    )

    card_5, card_6, card_7 = st.columns(3)

    card_5.metric(
        "Top Charge Category",
        top_charge_category
    )

    card_6.metric(
        "Charge Categories",
        format_number(charge_category_count)
    )

    card_7.metric(
        "Demographic Groups",
        format_number(demographic_group_count)
    )

    show_insight(
        f"{format_percentage(match_percentage)} of selected incident records have a matching arrest record. "
        f"The leading charge category is {top_charge_category}."
    )

    show_info_hint(
        "Responsible use note",
        "Demographic summaries are descriptive only. They should not be used for individual prediction, enforcement risk scoring, profiling, or causal claims."
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
                key="arrest_monthly_chart",
                config=get_chart_config()
            )

            top_arrest_month, arrest_month_count = get_top_value(
                arrest_data,
                "arrested_month_name"
            )

            show_insight(
                f"{top_arrest_month} has the highest selected arrest count with "
                f"{format_number(arrest_month_count)} arrests."
            )

    with right_column:
        if arrest_data.empty:
            st.info("No charge category chart is available for the selected filters.")
        else:
            st.plotly_chart(
                create_horizontal_bar_chart(
                    data=arrest_data,
                    group_column="charge_category",
                    title="Arrest Volume by Charge Category",
                    count_label="Arrest Count",
                    chart_type="arrest_soft"
                ),
                use_container_width=True,
                key="arrest_charge_category_chart",
                config=get_chart_config()
            )

            top_charge, charge_count = get_top_value(
                arrest_data,
                "charge_category"
            )

            show_insight(
                f"{top_charge} is the most common charge category among selected arrest records, "
                f"with {format_number(charge_count)} arrests."
            )

    left_column, right_column = st.columns(2)

    with left_column:
        if match_data.empty or "has_matching_arrest" not in match_data.columns:
            st.info("No incident-to-arrest match records are available.")
        else:
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

            st.plotly_chart(
                create_match_summary_chart(match_summary),
                use_container_width=True,
                key="incident_arrest_match_chart",
                config=get_chart_config()
            )

            show_insight(
                f"{format_number(matched_incidents)} out of {format_number(total_incidents)} selected incident records "
                f"have a matching arrest record."
            )

    with right_column:
        if match_data.empty or "has_matching_arrest" not in match_data.columns:
            st.info("No matched incident-charge records are available.")
        else:
            matched_charge_data = (
                match_data[match_data["has_matching_arrest"] == 1]
                .groupby("charge_category")
                .size()
                .reset_index(name="matched_incident_count")
                .sort_values("matched_incident_count", ascending=False)
            )

            if matched_charge_data.empty:
                st.info("No matched incident-charge records are available for the selected filters.")
            else:
                st.plotly_chart(
                    create_soft_donut_chart(
                        data=matched_charge_data,
                        label_column="charge_category",
                        value_column="matched_incident_count",
                        title="Matched Incident Share by Charge Category"
                    ),
                    use_container_width=True,
                    key="matched_incident_charge_category_donut_chart",
                    config=get_chart_config()
                )

                top_matched_charge = matched_charge_data.iloc[0]

                show_insight(
                    f"{top_matched_charge['charge_category']} is the leading charge category among matched incident records."
                )

    st.divider()

    st.markdown("### Descriptive Arrest Metadata")

    show_info_hint(
        "How to read this section",
        "These charts summarize fields present in public arrest records. They are included for transparency and data understanding, not for prediction or profiling."
    )

    left_column, right_column = st.columns(2)

    with left_column:
        if arrest_data.empty or "race" not in arrest_data.columns:
            st.info("No race field summary is available for the selected filters.")
        else:
            st.plotly_chart(
                create_horizontal_bar_chart(
                    data=arrest_data,
                    group_column="race",
                    title="Arrest Records by Race Field",
                    count_label="Arrest Count",
                    chart_type="neutral"
                ),
                use_container_width=True,
                key="arrest_race_chart",
                config=get_chart_config()
            )

            top_race, race_count = get_top_value(arrest_data, "race")

            show_insight(
                f"{top_race} is the most frequent race value in the selected arrest records, "
                f"appearing in {format_number(race_count)} records."
            )

    with right_column:
        if arrest_data.empty or "sex" not in arrest_data.columns:
            st.info("No sex field summary is available for the selected filters.")
        else:
            st.plotly_chart(
                create_horizontal_bar_chart(
                    data=arrest_data,
                    group_column="sex",
                    title="Arrest Records by Sex Field",
                    count_label="Arrest Count",
                    chart_type="neutral"
                ),
                use_container_width=True,
                key="arrest_sex_chart",
                config=get_chart_config()
            )

            top_sex, sex_count = get_top_value(arrest_data, "sex")

            show_insight(
                f"{top_sex} is the most frequent sex value in the selected arrest records, "
                f"appearing in {format_number(sex_count)} records."
            )

    if not arrest_data.empty and "age_group" in arrest_data.columns:
        age_group_summary = (
            arrest_data.groupby("age_group")
            .size()
            .reset_index(name="arrest_count")
            .sort_values("arrest_count", ascending=False)
        )

        st.plotly_chart(
            create_soft_donut_chart(
                data=age_group_summary,
                label_column="age_group",
                value_column="arrest_count",
                title="Arrest Records by Age Group"
            ),
            use_container_width=True,
            key="arrest_age_group_donut_chart",
            config=get_chart_config()
        )

        top_age_group = age_group_summary.iloc[0]

        show_insight(
            f"{top_age_group['age_group']} is the most frequent age group in the selected arrest records."
        )

    with st.expander("Arrest and Matched Case Review", expanded=False):
        show_info_hint(
            "About this review panel",
            "Detailed records are hidden by default to reduce clutter. Use this panel only when validating specific arrest or matched-case examples."
        )

        record_tab_1, record_tab_2 = st.tabs(
            [
                f"Arrest records ({format_number(len(arrest_data))})",
                f"Matched cases ({format_number(matched_incidents)})"
            ]
        )

        with record_tab_1:
            if arrest_data.empty:
                st.info("No arrest records are available for the selected filters.")
            else:
                show_compact_record_note(
                    "Showing the first 25 arrest records from the current filtered view."
                )

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

                available_columns = [
                    column for column in arrest_preview_columns
                    if column in arrest_data.columns
                ]

                st.dataframe(
                    arrest_data[available_columns].head(25),
                    use_container_width=True,
                    hide_index=True
                )

        with record_tab_2:
            if match_data.empty or "has_matching_arrest" not in match_data.columns:
                st.info("No matched incident-arrest records are available.")
            else:
                matched_records = match_data[match_data["has_matching_arrest"] == 1]

                if matched_records.empty:
                    st.info("No matched incident-arrest records are available for the selected filters.")
                else:
                    show_compact_record_note(
                        "Showing the first 25 matched incident-arrest records from the current filtered view."
                    )

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

                    available_columns = [
                        column for column in match_preview_columns
                        if column in matched_records.columns
                    ]

                    st.dataframe(
                        matched_records[available_columns].head(25),
                        use_container_width=True,
                        hide_index=True
                    )