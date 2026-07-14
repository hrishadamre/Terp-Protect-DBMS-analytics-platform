"""
arrest_analysis.py

Purpose:
Display arrest activity, charge categories, and validated
incident-to-arrest linkages for the Terp Protect dashboard.

Responsibilities:
- Calculate incident-to-arrest matching at the distinct incident grain
- Summarize distinct arrest records and arrest cases
- Display monthly arrest activity
- Compare overall and matched charge-category volume
- Display compact incident-to-arrest match coverage
- Keep demographic fields in a collapsed descriptive section
- Provide collapsed arrest and match-record review tables
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.charts import (
    create_arrest_monthly_chart,
    create_horizontal_bar_chart,
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


PRIMARY_CHART_HEIGHT = 430
COMPARISON_CHART_HEIGHT = 450
DEMOGRAPHIC_CHART_HEIGHT = 370
MATCH_COVERAGE_HEIGHT = 220

TOP_CHARGE_CATEGORIES = 10


def distinct_count(
    data,
    column
):
    """
    Return the number of distinct non-null values in a column.
    """
    if (
        data is None
        or data.empty
        or column not in data.columns
    ):
        return 0

    return int(
        data[column]
        .dropna()
        .nunique()
    )


def calculate_percentage(
    count,
    total
):
    """
    Calculate a safe percentage.
    """
    if total <= 0:
        return 0.0

    return (
        count
        / total
        * 100
    )


def standardize_chart_height(
    figure,
    height=PRIMARY_CHART_HEIGHT
):
    """
    Apply consistent height and margins to an existing figure.
    """
    figure.update_layout(
        height=height,
        margin={
            "l": 60,
            "r": 24,
            "t": 68,
            "b": 55
        }
    )

    return figure


def clean_category_value(value):
    """
    Return a cleaned categorical value.
    """
    if pd.isna(value):
        return "Unknown"

    cleaned_value = str(
        value
    ).strip()

    if not cleaned_value:
        return "Unknown"

    return cleaned_value


def get_selected_incident_count(incident_data):
    """
    Return the selected incident count at the distinct incident grain.
    """
    if incident_data is None or incident_data.empty:
        return 0

    if "incident_id" in incident_data.columns:
        return distinct_count(
            incident_data,
            "incident_id"
        )

    if "case_number" in incident_data.columns:
        return distinct_count(
            incident_data,
            "case_number"
        )

    return len(
        incident_data
    )


def get_distinct_arrest_count(arrest_data):
    """
    Return the number of distinct arrest records.
    """
    if arrest_data is None or arrest_data.empty:
        return 0

    if "arrest_id" in arrest_data.columns:
        return distinct_count(
            arrest_data,
            "arrest_id"
        )

    if "arrest_number" in arrest_data.columns:
        return distinct_count(
            arrest_data,
            "arrest_number"
        )

    return len(
        arrest_data
    )


def get_unique_arrest_case_count(arrest_data):
    """
    Return the number of distinct arrest case numbers.
    """
    return distinct_count(
        arrest_data,
        "case_number"
    )


def get_matched_rows(match_data):
    """
    Return rows containing a valid incident-to-arrest match.
    """
    if match_data is None or match_data.empty:
        return pd.DataFrame()

    if "has_matching_arrest" in match_data.columns:
        match_flag = pd.to_numeric(
            match_data["has_matching_arrest"],
            errors="coerce"
        ).fillna(0)

        return match_data[
            match_flag == 1
        ].copy()

    if "arrest_id" in match_data.columns:
        return match_data[
            match_data["arrest_id"].notna()
        ].copy()

    if "arrest_number" in match_data.columns:
        return match_data[
            match_data["arrest_number"].notna()
        ].copy()

    return match_data.iloc[0:0].copy()


def get_matched_incident_count(match_data):
    """
    Return the number of distinct incidents with at least one
    matching arrest.
    """
    matched_rows = get_matched_rows(
        match_data
    )

    if matched_rows.empty:
        return 0

    if "incident_id" in matched_rows.columns:
        return distinct_count(
            matched_rows,
            "incident_id"
        )

    if "case_number" in matched_rows.columns:
        return distinct_count(
            matched_rows,
            "case_number"
        )

    return len(
        matched_rows
    )


def calculate_match_coverage(
    matched_incidents,
    selected_incidents
):
    """
    Calculate the percentage of selected incidents with an arrest match.
    """
    return calculate_percentage(
        matched_incidents,
        selected_incidents
    )


def get_top_charge_category(arrest_data):
    """
    Return the most common charge category.
    """
    if (
        arrest_data is None
        or arrest_data.empty
        or "charge_category" not in arrest_data.columns
    ):
        return "N/A", 0

    return get_top_value(
        arrest_data,
        "charge_category"
    )


def get_charge_category_count(arrest_data):
    """
    Return the number of distinct charge categories.
    """
    return distinct_count(
        arrest_data,
        "charge_category"
    )


def show_arrest_summary(
    incident_data,
    arrest_data,
    match_data
):
    """
    Display compact arrest-linkage summary metrics.
    """
    selected_incidents = get_selected_incident_count(
        incident_data
    )

    arrest_records = get_distinct_arrest_count(
        arrest_data
    )

    unique_arrest_cases = get_unique_arrest_case_count(
        arrest_data
    )

    matched_incidents = get_matched_incident_count(
        match_data
    )

    match_coverage = calculate_match_coverage(
        matched_incidents,
        selected_incidents
    )

    (
        top_charge_category,
        top_charge_count
    ) = get_top_charge_category(
        arrest_data
    )

    charge_category_count = get_charge_category_count(
        arrest_data
    )

    overview_items = [
        {
            "label": "Selected Incidents",
            "value": format_number(
                selected_incidents
            ),
            "meta": "Distinct filtered incidents",
            "numeric": True
        },
        {
            "label": "Arrest Records",
            "value": format_number(
                arrest_records
            ),
            "meta": "Distinct arrest records",
            "numeric": True
        },
        {
            "label": "Unique Arrest Cases",
            "value": format_number(
                unique_arrest_cases
            ),
            "meta": "Distinct arrest case numbers",
            "numeric": True
        },
        {
            "label": "Matched Incidents",
            "value": format_number(
                matched_incidents
            ),
            "meta": "Distinct incidents with arrest",
            "numeric": True
        },
        {
            "label": "Match Coverage",
            "value": format_percentage(
                match_coverage
            ),
            "meta": "Matched ÷ selected incidents",
            "numeric": True
        },
        {
            "label": "Top Charge Category",
            "value": top_charge_category,
            "meta": "Leading arrest category",
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
        f"{format_number(matched_incidents)} of "
        f"{format_number(selected_incidents)} distinct selected incidents "
        f"have at least one matching arrest record, producing "
        f"{format_percentage(match_coverage)} match coverage."
    )

    show_info_hint(
        "Metric definition",
        (
            "Match coverage equals distinct selected incidents with at "
            "least one linked arrest divided by all distinct selected "
            "incidents. Multiple arrest rows linked to one incident do "
            "not increase the matched-incident count."
        )
    )

    return {
        "selected_incidents": selected_incidents,
        "arrest_records": arrest_records,
        "unique_arrest_cases": unique_arrest_cases,
        "matched_incidents": matched_incidents,
        "match_coverage": match_coverage,
        "top_charge_category": top_charge_category,
        "top_charge_count": top_charge_count
    }


def show_arrest_activity_charts(arrest_data):
    """
    Display monthly arrest activity and overall charge-category volume.
    """
    if arrest_data is None or arrest_data.empty:
        st.info(
            "No arrest records are available for the selected incidents."
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
            max_categories=TOP_CHARGE_CATEGORIES,
            count_label="Arrest Count",
            chart_type="arrest_soft"
        )
    )

    (
        top_arrest_month,
        arrest_month_count
    ) = get_top_value(
        arrest_data,
        "arrested_month_name"
    )

    (
        top_charge,
        charge_count
    ) = get_top_value(
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
            f"volume with {format_number(arrest_month_count)} records."
        )

    with insight_right:
        show_insight(
            f"{top_charge} is the leading charge category with "
            f"{format_number(charge_count)} arrest records."
        )


def create_match_coverage_chart(
    matched_incidents,
    selected_incidents
):
    """
    Create a compact 100% stacked match-coverage chart.
    """
    unmatched_incidents = max(
        selected_incidents - matched_incidents,
        0
    )

    match_percentage = calculate_match_coverage(
        matched_incidents,
        selected_incidents
    )

    unmatched_percentage = max(
        100 - match_percentage,
        0
    )

    figure = go.Figure()

    figure.add_trace(
        go.Bar(
            y=["Selected incidents"],
            x=[match_percentage],
            name="Matching Arrest",
            orientation="h",
            marker={
                "color": "#E78A98"
            },
            customdata=[
                matched_incidents
            ],
            hovertemplate=(
                "<b>Matching Arrest</b><br>"
                "Share: %{x:.1f}%<br>"
                "Distinct incidents: %{customdata:,}"
                "<extra></extra>"
            )
        )
    )

    figure.add_trace(
        go.Bar(
            y=["Selected incidents"],
            x=[unmatched_percentage],
            name="No Matching Arrest",
            orientation="h",
            marker={
                "color": "#AAB7C8"
            },
            customdata=[
                unmatched_incidents
            ],
            hovertemplate=(
                "<b>No Matching Arrest</b><br>"
                "Share: %{x:.1f}%<br>"
                "Distinct incidents: %{customdata:,}"
                "<extra></extra>"
            )
        )
    )

    figure.update_layout(
        title={
            "text": "Incident-to-Arrest Match Coverage",
            "x": 0,
            "xanchor": "left",
            "font": {
                "size": 17,
                "color": "#F8FAFC"
            }
        },
        barmode="stack",
        height=MATCH_COVERAGE_HEIGHT,
        margin={
            "l": 20,
            "r": 20,
            "t": 70,
            "b": 40
        },
        paper_bgcolor="#0B111C",
        plot_bgcolor="#0B111C",
        font={
            "color": "#F8FAFC"
        },
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
            "font": {
                "size": 11,
                "color": "#E2E8F0"
            }
        },
        xaxis={
            "title": {
                "text": "Share of Selected Incidents"
            },
            "range": [
                0,
                100
            ],
            "ticksuffix": "%",
            "gridcolor": "rgba(71, 85, 105, 0.45)",
            "showline": True,
            "linecolor": "#334155"
        },
        yaxis={
            "showticklabels": False,
            "showgrid": False
        }
    )

    return figure


def show_match_coverage(summary):
    """
    Display compact incident-to-arrest match coverage.
    """
    figure = create_match_coverage_chart(
        matched_incidents=summary[
            "matched_incidents"
        ],
        selected_incidents=summary[
            "selected_incidents"
        ]
    )

    st.plotly_chart(
        figure,
        use_container_width=True,
        key="incident_arrest_match_coverage_chart",
        config=get_chart_config()
    )

    unmatched_incidents = max(
        summary["selected_incidents"]
        - summary["matched_incidents"],
        0
    )

    show_insight(
        f"{format_number(summary['matched_incidents'])} distinct incidents "
        f"have at least one matching arrest record, while "
        f"{format_number(unmatched_incidents)} do not."
    )


def prepare_arrest_charge_data(arrest_data):
    """
    Prepare charge-category counts for all selected arrest records.
    """
    if (
        arrest_data is None
        or arrest_data.empty
        or "charge_category" not in arrest_data.columns
    ):
        return pd.DataFrame(
            columns=[
                "charge_category",
                "all_arrest_count"
            ]
        )

    working_data = arrest_data[
        [
            "charge_category"
        ]
    ].copy()

    working_data["charge_category"] = (
        working_data["charge_category"]
        .apply(
            clean_category_value
        )
    )

    return (
        working_data
        .groupby(
            "charge_category"
        )
        .size()
        .reset_index(
            name="all_arrest_count"
        )
    )


def prepare_matched_charge_data(match_data):
    """
    Prepare charge-category counts from matched incident-arrest rows.

    Distinct arrest identifiers are used where available to avoid
    counting the same arrest repeatedly.
    """
    matched_rows = get_matched_rows(
        match_data
    )

    if (
        matched_rows.empty
        or "charge_category" not in matched_rows.columns
    ):
        return pd.DataFrame(
            columns=[
                "charge_category",
                "matched_arrest_count"
            ]
        )

    matched_rows = matched_rows.copy()

    matched_rows["charge_category"] = (
        matched_rows["charge_category"]
        .apply(
            clean_category_value
        )
    )

    if "arrest_id" in matched_rows.columns:
        matched_summary = (
            matched_rows
            .dropna(
                subset=[
                    "arrest_id"
                ]
            )
            .drop_duplicates(
                subset=[
                    "arrest_id",
                    "charge_category"
                ]
            )
            .groupby(
                "charge_category"
            )
            .size()
            .reset_index(
                name="matched_arrest_count"
            )
        )

    elif "arrest_number" in matched_rows.columns:
        matched_summary = (
            matched_rows
            .dropna(
                subset=[
                    "arrest_number"
                ]
            )
            .drop_duplicates(
                subset=[
                    "arrest_number",
                    "charge_category"
                ]
            )
            .groupby(
                "charge_category"
            )
            .size()
            .reset_index(
                name="matched_arrest_count"
            )
        )

    else:
        matched_summary = (
            matched_rows
            .groupby(
                "charge_category"
            )
            .size()
            .reset_index(
                name="matched_arrest_count"
            )
        )

    return matched_summary


def prepare_charge_comparison_data(
    arrest_data,
    match_data
):
    """
    Merge overall and matched charge-category counts.
    """
    all_charge_data = prepare_arrest_charge_data(
        arrest_data
    )

    matched_charge_data = prepare_matched_charge_data(
        match_data
    )

    comparison_data = all_charge_data.merge(
        matched_charge_data,
        on="charge_category",
        how="outer"
    )

    if comparison_data.empty:
        return comparison_data

    comparison_data[
        "all_arrest_count"
    ] = pd.to_numeric(
        comparison_data[
            "all_arrest_count"
        ],
        errors="coerce"
    ).fillna(0).astype(int)

    comparison_data[
        "matched_arrest_count"
    ] = pd.to_numeric(
        comparison_data[
            "matched_arrest_count"
        ],
        errors="coerce"
    ).fillna(0).astype(int)

    comparison_data[
        "matched_share"
    ] = comparison_data.apply(
        lambda row: calculate_percentage(
            row[
                "matched_arrest_count"
            ],
            row[
                "all_arrest_count"
            ]
        ),
        axis=1
    )

    comparison_data = comparison_data.sort_values(
        [
            "all_arrest_count",
            "matched_arrest_count"
        ],
        ascending=[
            False,
            False
        ]
    ).head(
        TOP_CHARGE_CATEGORIES
    )

    return comparison_data


def create_charge_comparison_chart(
    arrest_data,
    match_data
):
    """
    Create a grouped horizontal bar chart comparing all selected
    arrest records with arrest records present in the match view.
    """
    comparison_data = prepare_charge_comparison_data(
        arrest_data,
        match_data
    )

    figure = go.Figure()

    if comparison_data.empty:
        figure.add_annotation(
            text="Charge comparison data is unavailable.",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font={
                "size": 14,
                "color": "#CBD5E1"
            }
        )

        figure.update_layout(
            title="All Arrests vs Matched Arrests by Charge Category",
            height=COMPARISON_CHART_HEIGHT,
            paper_bgcolor="#0B111C",
            plot_bgcolor="#0B111C"
        )

        return figure

    chart_data = comparison_data.sort_values(
        "all_arrest_count",
        ascending=True
    )

    figure.add_trace(
        go.Bar(
            x=chart_data[
                "all_arrest_count"
            ],
            y=chart_data[
                "charge_category"
            ],
            name="All Selected Arrests",
            orientation="h",
            marker={
                "color": "#AAB7C8"
            },
            customdata=chart_data[
                [
                    "matched_share"
                ]
            ],
            hovertemplate=(
                "<b>%{y}</b><br>"
                "All selected arrests: %{x:,}<br>"
                "Matched share: %{customdata[0]:.1f}%"
                "<extra></extra>"
            )
        )
    )

    figure.add_trace(
        go.Bar(
            x=chart_data[
                "matched_arrest_count"
            ],
            y=chart_data[
                "charge_category"
            ],
            name="Matched Arrests",
            orientation="h",
            marker={
                "color": "#E78A98"
            },
            customdata=chart_data[
                [
                    "all_arrest_count",
                    "matched_share"
                ]
            ],
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Matched arrests: %{x:,}<br>"
                "All selected arrests: %{customdata[0]:,}<br>"
                "Matched share: %{customdata[1]:.1f}%"
                "<extra></extra>"
            )
        )
    )

    figure.update_layout(
        title={
            "text": "All Arrests vs Matched Arrests by Charge Category",
            "x": 0,
            "xanchor": "left",
            "font": {
                "size": 17,
                "color": "#F8FAFC"
            }
        },
        barmode="group",
        height=COMPARISON_CHART_HEIGHT,
        margin={
            "l": 175,
            "r": 30,
            "t": 80,
            "b": 55
        },
        paper_bgcolor="#0B111C",
        plot_bgcolor="#0B111C",
        font={
            "color": "#F8FAFC"
        },
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
            "font": {
                "size": 11,
                "color": "#E2E8F0"
            }
        },
        xaxis={
            "title": {
                "text": "Distinct Arrest Count"
            },
            "rangemode": "tozero",
            "gridcolor": "rgba(71, 85, 105, 0.50)",
            "showline": True,
            "linecolor": "#334155",
            "tickfont": {
                "size": 11,
                "color": "#CBD5E1"
            }
        },
        yaxis={
            "title": {
                "text": ""
            },
            "showgrid": False,
            "automargin": True,
            "tickfont": {
                "size": 10,
                "color": "#CBD5E1"
            }
        }
    )

    return figure


def get_highest_matched_share_category(
    arrest_data,
    match_data
):
    """
    Return the charge category with the highest matched share among
    the displayed major categories.
    """
    comparison_data = prepare_charge_comparison_data(
        arrest_data,
        match_data
    )

    comparison_data = comparison_data[
        comparison_data[
            "all_arrest_count"
        ] > 0
    ].copy()

    if comparison_data.empty:
        return {
            "charge_category": "N/A",
            "matched_share": 0.0,
            "matched_arrest_count": 0,
            "all_arrest_count": 0
        }

    top_row = comparison_data.sort_values(
        [
            "matched_share",
            "all_arrest_count"
        ],
        ascending=[
            False,
            False
        ]
    ).iloc[0]

    return {
        "charge_category": top_row[
            "charge_category"
        ],
        "matched_share": float(
            top_row[
                "matched_share"
            ]
        ),
        "matched_arrest_count": int(
            top_row[
                "matched_arrest_count"
            ]
        ),
        "all_arrest_count": int(
            top_row[
                "all_arrest_count"
            ]
        )
    }


def show_charge_comparison(
    arrest_data,
    match_data
):
    """
    Display all-versus-matched charge-category comparison.
    """
    comparison_chart = create_charge_comparison_chart(
        arrest_data,
        match_data
    )

    st.plotly_chart(
        comparison_chart,
        use_container_width=True,
        key="arrest_charge_comparison_chart",
        config=get_chart_config()
    )

    leading_category = get_highest_matched_share_category(
        arrest_data,
        match_data
    )

    if leading_category[
        "charge_category"
    ] == "N/A":
        show_insight(
            "A matched charge-category comparison is unavailable for "
            "the current filtered selection."
        )

        return

    show_insight(
        f"{leading_category['charge_category']} has the highest matched "
        f"share among the displayed charge categories at "
        f"{format_percentage(leading_category['matched_share'])}, with "
        f"{format_number(leading_category['matched_arrest_count'])} of "
        f"{format_number(leading_category['all_arrest_count'])} selected "
        f"arrest records represented in the match view."
    )


def has_meaningful_age_data(arrest_data):
    """
    Determine whether age-group data contains meaningful values.
    """
    if (
        arrest_data is None
        or arrest_data.empty
        or "age_group" not in arrest_data.columns
    ):
        return False

    age_values = (
        arrest_data["age_group"]
        .dropna()
        .astype(str)
        .str.strip()
        .str.lower()
    )

    invalid_values = {
        "",
        "unknown",
        "n/a",
        "na",
        "none",
        "not available",
        "missing"
    }

    meaningful_values = age_values[
        ~age_values.isin(
            invalid_values
        )
    ]

    return not meaningful_values.empty


def show_demographic_metadata(arrest_data):
    """
    Display demographic metadata in a collapsed section.
    """
    with st.expander(
        "Descriptive Arrest Metadata",
        expanded=False
    ):
        show_info_hint(
            "Responsible use note",
            (
                "These charts summarize descriptive fields from public "
                "arrest records. They should not be used for individual "
                "prediction, profiling, risk scoring, or causal conclusions."
            )
        )

        if arrest_data is None or arrest_data.empty:
            st.info(
                "No descriptive arrest metadata is available."
            )

            return

        race_available = (
            "race" in arrest_data.columns
            and arrest_data["race"].notna().any()
        )

        sex_available = (
            "sex" in arrest_data.columns
            and arrest_data["sex"].notna().any()
        )

        chart_left, chart_right = st.columns(
            2,
            gap="small"
        )

        with chart_left:
            if race_available:
                race_chart = standardize_chart_height(
                    create_horizontal_bar_chart(
                        data=arrest_data,
                        group_column="race",
                        title="Arrest Records by Race Field",
                        max_categories=10,
                        count_label="Arrest Count",
                        chart_type="neutral"
                    ),
                    height=DEMOGRAPHIC_CHART_HEIGHT
                )

                st.plotly_chart(
                    race_chart,
                    use_container_width=True,
                    key="arrest_race_chart",
                    config=get_chart_config()
                )
            else:
                st.info(
                    "No race-field summary is available."
                )

        with chart_right:
            if sex_available:
                sex_chart = standardize_chart_height(
                    create_horizontal_bar_chart(
                        data=arrest_data,
                        group_column="sex",
                        title="Arrest Records by Sex Field",
                        max_categories=10,
                        count_label="Arrest Count",
                        chart_type="neutral"
                    ),
                    height=DEMOGRAPHIC_CHART_HEIGHT
                )

                st.plotly_chart(
                    sex_chart,
                    use_container_width=True,
                    key="arrest_sex_chart",
                    config=get_chart_config()
                )
            else:
                st.info(
                    "No sex-field summary is available."
                )

        if has_meaningful_age_data(
            arrest_data
        ):
            st.info(
                "Meaningful age values are available, but age analysis "
                "remains hidden to keep this section compact."
            )
        else:
            st.info(
                "Age analysis is hidden because meaningful age values "
                "are not available in the current arrest data."
            )


def show_arrest_record_review(
    arrest_data,
    match_data
):
    """
    Display collapsed arrest and matched-record samples.
    """
    matched_rows = get_matched_rows(
        match_data
    )

    with st.expander(
        "Arrest and Matched Case Review",
        expanded=False
    ):
        show_info_hint(
            "About this review panel",
            (
                "Use these tables to validate arrest records and "
                "incident-to-arrest links. Table rows do not determine "
                "the distinct summary counts shown above."
            )
        )

        arrest_tab, match_tab = st.tabs(
            [
                (
                    "Arrest records "
                    f"({format_number(get_distinct_arrest_count(arrest_data))})"
                ),
                (
                    "Matched incidents "
                    f"({format_number(get_matched_incident_count(match_data))})"
                )
            ]
        )

        with arrest_tab:
            if arrest_data is None or arrest_data.empty:
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
                    "arrested_charge",
                    "race",
                    "sex",
                    "age_group"
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
            if matched_rows.empty:
                st.info(
                    "No matched incident-arrest records are available."
                )
            else:
                show_compact_record_note(
                    "Showing the first 25 matched rows. One incident may "
                    "appear multiple times when linked to multiple arrests."
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
                    if column in matched_rows.columns
                ]

                st.dataframe(
                    matched_rows[
                        visible_columns
                    ].head(25),
                    use_container_width=True,
                    hide_index=True
                )


def show_arrest_analysis(
    incident_data,
    arrest_data,
    match_data,
    charge_summary=None,
    demographic_summary=None
):
    """
    Display the complete arrest-linkage section.

    charge_summary and demographic_summary remain accepted to preserve
    compatibility with the existing application interface.
    """
    show_section_banner(
        eyebrow="Enforcement Linkage",
        title="Arrests and Charges Profile",
        description=(
            "Review monthly arrest activity, charge-category volume, "
            "and validated links between selected incidents and arrests."
        )
    )

    summary = show_arrest_summary(
        incident_data=incident_data,
        arrest_data=arrest_data,
        match_data=match_data
    )

    st.divider()

    show_arrest_activity_charts(
        arrest_data
    )

    show_match_coverage(
        summary
    )

    show_charge_comparison(
        arrest_data,
        match_data
    )

    show_demographic_metadata(
        arrest_data
    )

    show_arrest_record_review(
        arrest_data,
        match_data
    )