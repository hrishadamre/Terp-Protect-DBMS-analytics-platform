"""
arrest_analysis.py

Purpose:
Display the arrest linkage profile section for the Terp Protect dashboard.

Responsibilities:
- Summarize arrest records and incident-to-arrest matching
- Compare arrest activity and charge categories
- Present descriptive public-record metadata responsibly
- Hide age analysis when meaningful age data is unavailable
"""

import pandas as pd
import streamlit as st

from components.charts import (
    create_arrest_monthly_chart,
    create_horizontal_bar_chart,
    create_match_summary_chart,
    create_soft_donut_chart,
    get_chart_config
)
from components.layout import (
    show_compact_overview_strip,
    show_compact_record_note,
    show_info_hint,
    show_insight,
    show_section_banner
)
from components.metrics import (
    format_number,
    format_percentage,
    get_top_value
)


PRIMARY_CHART_HEIGHT = 455


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
            "b": 50
        }
    )

    return figure


def get_safe_top_charge_category(charge_summary):
    """
    Return the leading charge category.
    """
    required_columns = {
        "charge_category",
        "arrest_count"
    }

    if (
        charge_summary is None
        or charge_summary.empty
        or not required_columns.issubset(
            charge_summary.columns
        )
    ):
        return "N/A", 0

    top_row = (
        charge_summary
        .sort_values(
            "arrest_count",
            ascending=False
        )
        .iloc[0]
    )

    return (
        top_row["charge_category"],
        int(top_row["arrest_count"])
    )


def get_safe_unique_count(
    data,
    column
):
    """
    Return a safe unique count.
    """
    if (
        data.empty
        or column not in data.columns
    ):
        return 0

    return data[column].nunique(
        dropna=True
    )


def get_matched_incident_count(match_data):
    """
    Safely count incidents with matching arrest records.
    """
    if match_data.empty:
        return 0

    if "has_matching_arrest" in match_data.columns:
        values = pd.to_numeric(
            match_data["has_matching_arrest"],
            errors="coerce"
        ).fillna(0)

        return int(
            values.sum()
        )

    if "arrest_id" in match_data.columns:
        return int(
            match_data["arrest_id"]
            .notna()
            .sum()
        )

    return 0


def has_meaningful_age_data(arrest_data):
    """
    Determine whether age-group data contains meaningful values.

    Unknown, missing, blank, and unavailable values are excluded.
    """
    if (
        arrest_data.empty
        or "age_group" not in arrest_data.columns
    ):
        return False

    normalized_values = (
        arrest_data["age_group"]
        .dropna()
        .astype(str)
        .str.strip()
        .str.lower()
    )

    excluded_values = {
        "",
        "unknown",
        "n/a",
        "na",
        "none",
        "not available",
        "missing"
    }

    meaningful_values = normalized_values[
        ~normalized_values.isin(
            excluded_values
        )
    ]

    return not meaningful_values.empty


def show_arrest_summary(
    arrest_data,
    match_data,
    charge_summary
):
    """
    Display compact arrest and linkage summary cards.
    """
    total_arrests = len(
        arrest_data
    )

    unique_arrest_cases = get_safe_unique_count(
        arrest_data,
        "case_number"
    )

    matched_incidents = get_matched_incident_count(
        match_data
    )

    total_incidents = len(
        match_data
    )

    match_percentage = (
        matched_incidents
        / total_incidents
        * 100
        if total_incidents > 0
        else 0.0
    )

    (
        top_charge_category,
        top_charge_count
    ) = get_safe_top_charge_category(
        charge_summary
    )

    charge_category_count = get_safe_unique_count(
        arrest_data,
        "charge_category"
    )

    overview_items = [
        {
            "label": "Arrest Records",
            "value": format_number(
                total_arrests
            ),
            "meta": "Linked filtered records",
            "numeric": True
        },
        {
            "label": "Unique Arrest Cases",
            "value": format_number(
                unique_arrest_cases
            ),
            "meta": "Distinct case numbers",
            "numeric": True
        },
        {
            "label": "Matched Incidents",
            "value": format_number(
                matched_incidents
            ),
            "meta": "Incident-arrest matches",
            "numeric": True
        },
        {
            "label": "Match Coverage",
            "value": format_percentage(
                match_percentage
            ),
            "meta": "Selected incident share",
            "numeric": True
        },
        {
            "label": "Top Charge Category",
            "value": top_charge_category,
            "meta": "Leading charge group",
            "badge": format_number(
                top_charge_count
            )
        },
        {
            "label": "Charge Categories",
            "value": format_number(
                charge_category_count
            ),
            "meta": "Distinct categories",
            "numeric": True
        }
    ]

    show_compact_overview_strip(
        overview_items
    )

    show_insight(
        f"{format_percentage(match_percentage)} of selected incident "
        f"records have a matching arrest record. "
        f"{top_charge_category} is the leading charge category."
    )

    show_info_hint(
        "Responsible use note",
        (
            "Demographic fields are descriptive public-record values. "
            "Do not use them for individual prediction, profiling, "
            "enforcement scoring, or causal conclusions."
        )
    )

    return {
        "matched_incidents": matched_incidents,
        "total_incidents": total_incidents,
        "match_percentage": match_percentage
    }


def show_arrest_activity_charts(arrest_data):
    """
    Display arrest trend and charge-category charts.
    """
    if arrest_data.empty:
        st.info(
            "No matching arrest records are available for the "
            "selected incident filters."
        )

        return

    monthly_chart = standardize_chart_height(
        create_arrest_monthly_chart(
            arrest_data
        )
    )

    charge_chart = standardize_chart_height(
        create_horizontal_bar_chart(
            data=arrest_data,
            group_column="charge_category",
            title="Arrest Volume by Charge Category",
            count_label="Arrest Count",
            chart_type="arrest_soft"
        )
    )

    top_arrest_month, arrest_month_count = get_top_value(
        arrest_data,
        "arrested_month_name"
    )

    top_charge, charge_count = get_top_value(
        arrest_data,
        "charge_category"
    )

    chart_left, chart_right = st.columns(
        2,
        gap="small"
    )

    with chart_left:
        st.plotly_chart(
            monthly_chart,
            use_container_width=True,
            key="arrest_monthly_chart",
            config=get_chart_config()
        )

    with chart_right:
        st.plotly_chart(
            charge_chart,
            use_container_width=True,
            key="arrest_charge_category_chart",
            config=get_chart_config()
        )

    insight_left, insight_right = st.columns(
        2,
        gap="small"
    )

    with insight_left:
        show_insight(
            f"{top_arrest_month} has the highest selected arrest "
            f"volume with "
            f"{format_number(arrest_month_count)} arrests."
        )

    with insight_right:
        show_insight(
            f"{top_charge} is the most common charge category with "
            f"{format_number(charge_count)} arrests."
        )


def create_match_summary_data(match_data):
    """
    Prepare incident-to-arrest match summary data.
    """
    if match_data.empty:
        return pd.DataFrame()

    if "has_matching_arrest" in match_data.columns:
        summary = (
            match_data
            .groupby(
                "has_matching_arrest"
            )
            .size()
            .reset_index(
                name="incident_count"
            )
        )

        summary["match_status"] = (
            summary["has_matching_arrest"]
            .map(
                {
                    0: "No Matching Arrest",
                    1: "Matching Arrest"
                }
            )
        )

        return summary

    if "arrest_id" in match_data.columns:
        prepared_data = match_data.copy()

        prepared_data["match_status"] = (
            prepared_data["arrest_id"]
            .notna()
            .map(
                {
                    True: "Matching Arrest",
                    False: "No Matching Arrest"
                }
            )
        )

        return (
            prepared_data
            .groupby(
                "match_status"
            )
            .size()
            .reset_index(
                name="incident_count"
            )
        )

    return pd.DataFrame()


def show_match_charts(
    match_data,
    summary
):
    """
    Display match coverage and matched charge composition.
    """
    match_summary = create_match_summary_data(
        match_data
    )

    if match_summary.empty:
        st.info(
            "No incident-to-arrest matching information is available."
        )

        return

    match_chart = standardize_chart_height(
        create_match_summary_chart(
            match_summary
        )
    )

    matched_charge_data = pd.DataFrame()

    if (
        "charge_category" in match_data.columns
        and "has_matching_arrest" in match_data.columns
    ):
        matched_charge_data = (
            match_data[
                pd.to_numeric(
                    match_data["has_matching_arrest"],
                    errors="coerce"
                ).fillna(0) == 1
            ]
            .groupby(
                "charge_category"
            )
            .size()
            .reset_index(
                name="matched_incident_count"
            )
            .sort_values(
                "matched_incident_count",
                ascending=False
            )
        )

    chart_left, chart_right = st.columns(
        2,
        gap="small"
    )

    with chart_left:
        st.plotly_chart(
            match_chart,
            use_container_width=True,
            key="incident_arrest_match_chart",
            config=get_chart_config()
        )

    with chart_right:
        if matched_charge_data.empty:
            st.info(
                "No matched charge-category composition is available "
                "for the selected records."
            )
        else:
            matched_donut = standardize_chart_height(
                create_soft_donut_chart(
                    data=matched_charge_data,
                    label_column="charge_category",
                    value_column="matched_incident_count",
                    title="Matched Incident Share by Charge Category"
                )
            )

            st.plotly_chart(
                matched_donut,
                use_container_width=True,
                key="matched_incident_charge_category_donut_chart",
                config=get_chart_config()
            )

    insight_left, insight_right = st.columns(
        2,
        gap="small"
    )

    with insight_left:
        show_insight(
            f"{format_number(summary['matched_incidents'])} of "
            f"{format_number(summary['total_incidents'])} selected "
            f"incident records have a matching arrest."
        )

    with insight_right:
        if not matched_charge_data.empty:
            top_matched_charge = matched_charge_data.iloc[0]

            show_insight(
                f"{top_matched_charge['charge_category']} is the "
                f"leading charge category among matched incidents."
            )


def show_demographic_metadata(arrest_data):
    """
    Display descriptive public-record metadata.
    """
    st.markdown(
        "### Descriptive Arrest Metadata"
    )

    show_info_hint(
        "How to read this section",
        (
            "These charts summarize values already present in public "
            "arrest records. They are included for transparency and "
            "data understanding, not prediction or profiling."
        )
    )

    if arrest_data.empty:
        st.info(
            "No descriptive arrest metadata is available for the "
            "selected filters."
        )

        return

    chart_left, chart_right = st.columns(
        2,
        gap="small"
    )

    race_available = (
        "race" in arrest_data.columns
        and arrest_data["race"].notna().any()
    )

    sex_available = (
        "sex" in arrest_data.columns
        and arrest_data["sex"].notna().any()
    )

    with chart_left:
        if not race_available:
            st.info(
                "No race-field summary is available."
            )
        else:
            race_chart = standardize_chart_height(
                create_horizontal_bar_chart(
                    data=arrest_data,
                    group_column="race",
                    title="Arrest Records by Race Field",
                    count_label="Arrest Count",
                    chart_type="neutral"
                )
            )

            st.plotly_chart(
                race_chart,
                use_container_width=True,
                key="arrest_race_chart",
                config=get_chart_config()
            )

    with chart_right:
        if not sex_available:
            st.info(
                "No sex-field summary is available."
            )
        else:
            sex_chart = standardize_chart_height(
                create_horizontal_bar_chart(
                    data=arrest_data,
                    group_column="sex",
                    title="Arrest Records by Sex Field",
                    count_label="Arrest Count",
                    chart_type="neutral"
                )
            )

            st.plotly_chart(
                sex_chart,
                use_container_width=True,
                key="arrest_sex_chart",
                config=get_chart_config()
            )

    insight_left, insight_right = st.columns(
        2,
        gap="small"
    )

    with insight_left:
        if race_available:
            top_race, race_count = get_top_value(
                arrest_data,
                "race"
            )

            show_insight(
                f"{top_race} is the most frequent race-field value, "
                f"appearing in {format_number(race_count)} records."
            )

    with insight_right:
        if sex_available:
            top_sex, sex_count = get_top_value(
                arrest_data,
                "sex"
            )

            show_insight(
                f"{top_sex} is the most frequent sex-field value, "
                f"appearing in {format_number(sex_count)} records."
            )

    if has_meaningful_age_data(
        arrest_data
    ):
        meaningful_age_data = arrest_data.copy()

        meaningful_age_data["age_group"] = (
            meaningful_age_data["age_group"]
            .astype(str)
            .str.strip()
        )

        excluded_values = {
            "",
            "unknown",
            "n/a",
            "na",
            "none",
            "not available",
            "missing"
        }

        meaningful_age_data = meaningful_age_data[
            ~meaningful_age_data["age_group"]
            .str.lower()
            .isin(
                excluded_values
            )
        ]

        age_group_summary = (
            meaningful_age_data
            .groupby(
                "age_group"
            )
            .size()
            .reset_index(
                name="arrest_count"
            )
            .sort_values(
                "arrest_count",
                ascending=False
            )
        )

        age_chart = create_soft_donut_chart(
            data=age_group_summary,
            label_column="age_group",
            value_column="arrest_count",
            title="Arrest Records by Age Group"
        )

        st.plotly_chart(
            age_chart,
            use_container_width=True,
            key="arrest_age_group_donut_chart",
            config=get_chart_config()
        )

        top_age_group = age_group_summary.iloc[0]

        show_insight(
            f"{top_age_group['age_group']} is the most frequent "
            f"available age group."
        )
    else:
        st.info(
            "Age analysis is hidden because the current arrest source "
            "does not contain meaningful age values."
        )


def show_arrest_record_review(
    arrest_data,
    match_data,
    matched_incidents
):
    """
    Display collapsed arrest and matched-case record samples.
    """
    with st.expander(
        "Arrest and Matched Case Review",
        expanded=False
    ):
        show_info_hint(
            "About this review panel",
            (
                "Use these samples to validate arrest records and "
                "incident-to-arrest links. Detailed records are hidden "
                "by default to keep the analytical views focused."
            )
        )

        arrest_tab, match_tab = st.tabs(
            [
                (
                    "Arrest records "
                    f"({format_number(len(arrest_data))})"
                ),
                (
                    "Matched cases "
                    f"({format_number(matched_incidents)})"
                )
            ]
        )

        with arrest_tab:
            if arrest_data.empty:
                st.info(
                    "No arrest records are available."
                )
            else:
                show_compact_record_note(
                    "Showing the first 25 arrest records from the "
                    "current filtered view."
                )

                arrest_columns = [
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

                visible_columns = [
                    column
                    for column in arrest_columns
                    if column in arrest_data.columns
                ]

                st.dataframe(
                    arrest_data[
                        visible_columns
                    ].head(25),
                    use_container_width=True,
                    hide_index=True
                )

        with match_tab:
            if match_data.empty:
                st.info(
                    "No matched records are available."
                )

                return

            if "has_matching_arrest" in match_data.columns:
                matched_records = match_data[
                    pd.to_numeric(
                        match_data["has_matching_arrest"],
                        errors="coerce"
                    ).fillna(0) == 1
                ]
            elif "arrest_id" in match_data.columns:
                matched_records = match_data[
                    match_data["arrest_id"].notna()
                ]
            else:
                matched_records = match_data.iloc[0:0]

            if matched_records.empty:
                st.info(
                    "No matched incident-arrest records are available."
                )
            else:
                show_compact_record_note(
                    "Showing the first 25 matched incident-arrest "
                    "records from the current filtered view."
                )

                match_columns = [
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

                visible_columns = [
                    column
                    for column in match_columns
                    if column in matched_records.columns
                ]

                st.dataframe(
                    matched_records[
                        visible_columns
                    ].head(25),
                    use_container_width=True,
                    hide_index=True
                )


def show_arrest_analysis(
    arrest_data,
    match_data,
    charge_summary,
    demographic_summary
):
    """
    Display the complete arrest-linkage section.
    """
    show_section_banner(
        eyebrow="",
        title="Arrest Linkage Profile",
        description=(
            "Review arrest activity, charge categories, and case-number "
            "links between incidents and public arrest records."
        )
    )

    summary = show_arrest_summary(
        arrest_data,
        match_data,
        charge_summary
    )

    st.divider()

    show_arrest_activity_charts(
        arrest_data
    )

    show_match_charts(
        match_data,
        summary
    )

    st.divider()

    show_demographic_metadata(
        arrest_data
    )

    show_arrest_record_review(
        arrest_data,
        match_data,
        summary["matched_incidents"]
    )