"""
arrest_analysis.py

Purpose:
Display arrest activity, charge categories, and validated
incident-to-arrest linkages for the Terp Protect dashboard.

Responsibilities:
- Separate all cleaned arrest records from linked arrest records
- Calculate incident-to-arrest match coverage using distinct incidents
- Display arrest activity by calendar month
- Compare all cleaned arrests with linked arrests by charge category
- Explain the difference between arrest outcomes and arrest-record matches
- Keep demographic metadata and record review collapsed
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.charts import get_chart_config
from components.layout import (
    show_compact_overview_strip,
    show_compact_record_note,
    show_info_hint,
    show_insight,
    show_section_banner
)
from components.metrics import (
    format_number,
    format_percentage
)


MONTH_ORDER = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
]


TOP_CHARGE_CATEGORIES = 10

MONTHLY_CHART_HEIGHT = 430
CHARGE_CHART_HEIGHT = 460
MATCH_CHART_HEIGHT = 230
DEMOGRAPHIC_CHART_HEIGHT = 360


def safe_percentage(
    numerator,
    denominator
):
    """
    Calculate a percentage safely.
    """
    numeric_numerator = pd.to_numeric(
        numerator,
        errors="coerce"
    )

    numeric_denominator = pd.to_numeric(
        denominator,
        errors="coerce"
    )

    if (
        pd.isna(numeric_numerator)
        or pd.isna(numeric_denominator)
        or numeric_denominator <= 0
    ):
        return 0.0

    return float(
        numeric_numerator
        / numeric_denominator
        * 100
    )


def clean_category_value(value):
    """
    Return a cleaned category value.
    """
    if pd.isna(value):
        return "Unknown"

    cleaned_value = str(
        value
    ).strip()

    if not cleaned_value:
        return "Unknown"

    return cleaned_value


def distinct_count(
    data,
    candidate_columns
):
    """
    Return a distinct count using the first available identifier.
    """
    if data is None or data.empty:
        return 0

    for column in candidate_columns:
        if column in data.columns:
            return int(
                data[column]
                .dropna()
                .nunique()
            )

    return len(
        data
    )


def get_selected_incident_count(incident_data):
    """
    Return the number of distinct selected incidents.
    """
    return distinct_count(
        incident_data,
        [
            "incident_id",
            "case_number"
        ]
    )


def get_linked_arrest_count(arrest_data):
    """
    Return the number of distinct arrests linked to selected incidents.
    """
    return distinct_count(
        arrest_data,
        [
            "arrest_id",
            "arrest_number"
        ]
    )


def get_unique_arrest_case_count(arrest_data):
    """
    Return the number of distinct linked arrest case numbers.
    """
    return distinct_count(
        arrest_data,
        [
            "case_number"
        ]
    )


def get_valid_match_rows(match_data):
    """
    Return valid incident-to-arrest match rows.
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

    return match_data.iloc[
        0:0
    ].copy()


def get_matched_incident_count(match_data):
    """
    Return the number of distinct incidents with at least one arrest.
    """
    matched_rows = get_valid_match_rows(
        match_data
    )

    return distinct_count(
        matched_rows,
        [
            "incident_id",
            "case_number"
        ]
    )


def get_all_cleaned_arrest_count(
    charge_summary,
    arrest_data
):
    """
    Return the total number of cleaned arrest records.

    charge_summary is preferred because it represents the complete
    exported arrest population rather than only linked arrests.
    """
    if (
        charge_summary is not None
        and not charge_summary.empty
        and "arrest_count" in charge_summary.columns
    ):
        arrest_counts = pd.to_numeric(
            charge_summary["arrest_count"],
            errors="coerce"
        ).fillna(0)

        return int(
            arrest_counts.sum()
        )

    return get_linked_arrest_count(
        arrest_data
    )


def prepare_overall_charge_summary(charge_summary):
    """
    Prepare all cleaned arrest counts by charge category.
    """
    if (
        charge_summary is None
        or charge_summary.empty
        or "charge_category" not in charge_summary.columns
        or "arrest_count" not in charge_summary.columns
    ):
        return pd.DataFrame(
            columns=[
                "charge_category",
                "all_cleaned_arrests"
            ]
        )

    working_data = charge_summary[
        [
            "charge_category",
            "arrest_count"
        ]
    ].copy()

    working_data["charge_category"] = (
        working_data["charge_category"]
        .apply(
            clean_category_value
        )
    )

    working_data["arrest_count"] = pd.to_numeric(
        working_data["arrest_count"],
        errors="coerce"
    ).fillna(0)

    return (
        working_data
        .groupby(
            "charge_category",
            as_index=False
        )["arrest_count"]
        .sum()
        .rename(
            columns={
                "arrest_count": "all_cleaned_arrests"
            }
        )
    )


def prepare_linked_charge_summary(arrest_data):
    """
    Prepare distinct linked arrest counts by charge category.
    """
    if (
        arrest_data is None
        or arrest_data.empty
        or "charge_category" not in arrest_data.columns
    ):
        return pd.DataFrame(
            columns=[
                "charge_category",
                "linked_arrests"
            ]
        )

    working_data = arrest_data.copy()

    working_data["charge_category"] = (
        working_data["charge_category"]
        .apply(
            clean_category_value
        )
    )

    if "arrest_id" in working_data.columns:
        working_data = working_data.drop_duplicates(
            subset=[
                "arrest_id",
                "charge_category"
            ]
        )

    elif "arrest_number" in working_data.columns:
        working_data = working_data.drop_duplicates(
            subset=[
                "arrest_number",
                "charge_category"
            ]
        )

    return (
        working_data
        .groupby(
            "charge_category"
        )
        .size()
        .reset_index(
            name="linked_arrests"
        )
    )


def prepare_charge_linkage_comparison(
    charge_summary,
    arrest_data
):
    """
    Compare all cleaned arrests with arrests linked to selected incidents.

    Linkage rate:
        linked arrests in charge category
        ÷
        all cleaned arrests in charge category
    """
    overall_data = prepare_overall_charge_summary(
        charge_summary
    )

    linked_data = prepare_linked_charge_summary(
        arrest_data
    )

    if overall_data.empty and linked_data.empty:
        return pd.DataFrame()

    comparison_data = overall_data.merge(
        linked_data,
        on="charge_category",
        how="outer"
    )

    comparison_data["all_cleaned_arrests"] = pd.to_numeric(
        comparison_data["all_cleaned_arrests"],
        errors="coerce"
    ).fillna(0).astype(int)

    comparison_data["linked_arrests"] = pd.to_numeric(
        comparison_data["linked_arrests"],
        errors="coerce"
    ).fillna(0).astype(int)

    comparison_data["linkage_rate"] = comparison_data.apply(
        lambda row: safe_percentage(
            row["linked_arrests"],
            row["all_cleaned_arrests"]
        ),
        axis=1
    )

    return (
        comparison_data
        .sort_values(
            [
                "all_cleaned_arrests",
                "linked_arrests"
            ],
            ascending=[
                False,
                False
            ]
        )
        .head(
            TOP_CHARGE_CATEGORIES
        )
    )


def get_top_charge_category(
    charge_summary,
    arrest_data
):
    """
    Return the leading charge category from the complete arrest dataset.
    """
    overall_data = prepare_overall_charge_summary(
        charge_summary
    )

    if overall_data.empty:
        linked_data = prepare_linked_charge_summary(
            arrest_data
        )

        if linked_data.empty:
            return "N/A", 0

        top_row = linked_data.sort_values(
            "linked_arrests",
            ascending=False
        ).iloc[
            0
        ]

        return (
            top_row["charge_category"],
            int(
                top_row["linked_arrests"]
            )
        )

    top_row = overall_data.sort_values(
        "all_cleaned_arrests",
        ascending=False
    ).iloc[
        0
    ]

    return (
        top_row["charge_category"],
        int(
            top_row["all_cleaned_arrests"]
        )
    )


def get_charge_category_count(
    charge_summary,
    arrest_data
):
    """
    Return the number of distinct charge categories.
    """
    overall_data = prepare_overall_charge_summary(
        charge_summary
    )

    if not overall_data.empty:
        return int(
            overall_data["charge_category"]
            .nunique()
        )

    if (
        arrest_data is not None
        and not arrest_data.empty
        and "charge_category" in arrest_data.columns
    ):
        return int(
            arrest_data["charge_category"]
            .dropna()
            .nunique()
        )

    return 0


def prepare_monthly_arrest_data(arrest_data):
    """
    Prepare linked arrest volume by calendar month.

    The same calendar month is combined across represented years.
    """
    if arrest_data is None or arrest_data.empty:
        return pd.DataFrame()

    working_data = arrest_data.copy()

    if "arrested_month_name" in working_data.columns:
        working_data["_month_name"] = (
            working_data["arrested_month_name"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    elif "arrested_datetime" in working_data.columns:
        arrested_datetime = pd.to_datetime(
            working_data["arrested_datetime"],
            errors="coerce"
        )

        working_data["_month_name"] = (
            arrested_datetime.dt.month_name()
        )

    else:
        return pd.DataFrame()

    working_data = working_data[
        working_data["_month_name"].isin(
            MONTH_ORDER
        )
    ].copy()

    if working_data.empty:
        return pd.DataFrame()

    if "arrest_id" in working_data.columns:
        summary = (
            working_data
            .groupby(
                "_month_name"
            )["arrest_id"]
            .nunique()
            .reindex(
                MONTH_ORDER,
                fill_value=0
            )
            .rename(
                "arrest_count"
            )
            .reset_index()
        )

    elif "arrest_number" in working_data.columns:
        summary = (
            working_data
            .groupby(
                "_month_name"
            )["arrest_number"]
            .nunique()
            .reindex(
                MONTH_ORDER,
                fill_value=0
            )
            .rename(
                "arrest_count"
            )
            .reset_index()
        )

    else:
        summary = (
            working_data
            .groupby(
                "_month_name"
            )
            .size()
            .reindex(
                MONTH_ORDER,
                fill_value=0
            )
            .rename(
                "arrest_count"
            )
            .reset_index()
        )

    summary = summary.rename(
        columns={
            "_month_name": "month_name"
        }
    )

    return summary


def create_monthly_arrest_chart(arrest_data):
    """
    Create linked arrest volume by calendar month.
    """
    monthly_data = prepare_monthly_arrest_data(
        arrest_data
    )

    figure = go.Figure()

    if monthly_data.empty:
        figure.add_annotation(
            text="Monthly arrest data is unavailable.",
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
            title="Linked Arrest Volume by Calendar Month",
            height=MONTHLY_CHART_HEIGHT,
            paper_bgcolor="#0B111C",
            plot_bgcolor="#0B111C"
        )

        return figure

    figure.add_trace(
        go.Scatter(
            x=monthly_data[
                "month_name"
            ],
            y=monthly_data[
                "arrest_count"
            ],
            mode="lines+markers",
            line={
                "color": "#E78A98",
                "width": 2.5,
                "shape": "spline"
            },
            marker={
                "size": 7,
                "color": "#F4C2CB",
                "line": {
                    "color": "#B94A61",
                    "width": 1
                }
            },
            fill="tozeroy",
            fillcolor="rgba(231, 138, 152, 0.18)",
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Distinct linked arrests: %{y:,}<br>"
                "The same calendar month is combined across years."
                "<extra></extra>"
            )
        )
    )

    figure.update_layout(
        title={
            "text": "Linked Arrest Volume by Calendar Month",
            "x": 0,
            "xanchor": "left",
            "font": {
                "size": 17,
                "color": "#F8FAFC"
            }
        },
        height=MONTHLY_CHART_HEIGHT,
        margin={
            "l": 60,
            "r": 24,
            "t": 70,
            "b": 70
        },
        paper_bgcolor="#0B111C",
        plot_bgcolor="#0B111C",
        showlegend=False,
        font={
            "color": "#F8FAFC"
        },
        xaxis={
            "title": {
                "text": "Calendar Month"
            },
            "categoryorder": "array",
            "categoryarray": MONTH_ORDER,
            "tickangle": -35,
            "tickfont": {
                "size": 10,
                "color": "#CBD5E1"
            },
            "showgrid": False,
            "showline": True,
            "linecolor": "#334155"
        },
        yaxis={
            "title": {
                "text": "Distinct Linked Arrest Count"
            },
            "rangemode": "tozero",
            "gridcolor": "rgba(71, 85, 105, 0.50)",
            "tickfont": {
                "size": 11,
                "color": "#CBD5E1"
            },
            "showline": True,
            "linecolor": "#334155"
        }
    )

    return figure


def create_charge_comparison_chart(
    charge_summary,
    arrest_data
):
    """
    Create all-cleaned versus linked arrest comparison by charge category.
    """
    comparison_data = prepare_charge_linkage_comparison(
        charge_summary=charge_summary,
        arrest_data=arrest_data
    )

    figure = go.Figure()

    if comparison_data.empty:
        figure.add_annotation(
            text="Charge-category comparison data is unavailable.",
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
            title="All Cleaned vs Linked Arrests by Charge Category",
            height=CHARGE_CHART_HEIGHT,
            paper_bgcolor="#0B111C",
            plot_bgcolor="#0B111C"
        )

        return figure

    chart_data = comparison_data.sort_values(
        "all_cleaned_arrests",
        ascending=True
    )

    figure.add_trace(
        go.Bar(
            x=chart_data[
                "all_cleaned_arrests"
            ],
            y=chart_data[
                "charge_category"
            ],
            name="All Cleaned Arrests",
            orientation="h",
            marker={
                "color": "#AAB7C8"
            },
            hovertemplate=(
                "<b>%{y}</b><br>"
                "All cleaned arrests: %{x:,}"
                "<extra></extra>"
            )
        )
    )

    figure.add_trace(
        go.Bar(
            x=chart_data[
                "linked_arrests"
            ],
            y=chart_data[
                "charge_category"
            ],
            name="Linked to Selected Incidents",
            orientation="h",
            marker={
                "color": "#E78A98"
            },
            customdata=chart_data[
                [
                    "all_cleaned_arrests",
                    "linkage_rate"
                ]
            ],
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Linked arrests: %{x:,}<br>"
                "All cleaned arrests: %{customdata[0]:,}<br>"
                "Charge-category linkage rate: %{customdata[1]:.1f}%"
                "<extra></extra>"
            )
        )
    )

    figure.update_layout(
        title={
            "text": "All Cleaned vs Linked Arrests by Charge Category",
            "x": 0,
            "xanchor": "left",
            "font": {
                "size": 17,
                "color": "#F8FAFC"
            }
        },
        barmode="group",
        height=CHARGE_CHART_HEIGHT,
        margin={
            "l": 180,
            "r": 30,
            "t": 85,
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
                "size": 10,
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
            "linecolor": "#334155"
        },
        yaxis={
            "title": {
                "text": ""
            },
            "showgrid": False,
            "automargin": True
        }
    )

    return figure


def create_match_coverage_chart(
    matched_incidents,
    selected_incidents
):
    """
    Create a 100% stacked incident-to-arrest match coverage chart.
    """
    unmatched_incidents = max(
        selected_incidents - matched_incidents,
        0
    )

    matched_percentage = safe_percentage(
        matched_incidents,
        selected_incidents
    )

    unmatched_percentage = safe_percentage(
        unmatched_incidents,
        selected_incidents
    )

    figure = go.Figure()

    figure.add_trace(
        go.Bar(
            y=[
                "Selected incidents"
            ],
            x=[
                matched_percentage
            ],
            name="At Least One Linked Arrest",
            orientation="h",
            marker={
                "color": "#E78A98"
            },
            customdata=[
                matched_incidents
            ],
            hovertemplate=(
                "<b>At Least One Linked Arrest</b><br>"
                "Share: %{x:.1f}%<br>"
                "Distinct incidents: %{customdata:,}"
                "<extra></extra>"
            )
        )
    )

    figure.add_trace(
        go.Bar(
            y=[
                "Selected incidents"
            ],
            x=[
                unmatched_percentage
            ],
            name="No Linked Arrest",
            orientation="h",
            marker={
                "color": "#AAB7C8"
            },
            customdata=[
                unmatched_incidents
            ],
            hovertemplate=(
                "<b>No Linked Arrest</b><br>"
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
        height=MATCH_CHART_HEIGHT,
        margin={
            "l": 20,
            "r": 20,
            "t": 75,
            "b": 45
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
                "size": 10,
                "color": "#E2E8F0"
            }
        },
        xaxis={
            "title": {
                "text": "Share of Distinct Selected Incidents"
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


def show_arrest_summary(
    incident_data,
    arrest_data,
    match_data,
    charge_summary
):
    """
    Display arrest and linkage summary metrics.
    """
    selected_incidents = get_selected_incident_count(
        incident_data
    )

    all_cleaned_arrests = get_all_cleaned_arrest_count(
        charge_summary=charge_summary,
        arrest_data=arrest_data
    )

    linked_arrests = get_linked_arrest_count(
        arrest_data
    )

    linked_arrest_cases = get_unique_arrest_case_count(
        arrest_data
    )

    matched_incidents = get_matched_incident_count(
        match_data
    )

    match_coverage = safe_percentage(
        matched_incidents,
        selected_incidents
    )

    linked_arrest_share = safe_percentage(
        linked_arrests,
        all_cleaned_arrests
    )

    (
        top_charge_category,
        top_charge_count
    ) = get_top_charge_category(
        charge_summary=charge_summary,
        arrest_data=arrest_data
    )

    charge_category_count = get_charge_category_count(
        charge_summary=charge_summary,
        arrest_data=arrest_data
    )

    overview_items = [
        {
            "label": "Selected Incidents",
            "value": format_number(
                selected_incidents
            ),
            "meta": "Distinct filtered incidents",
            "numeric": True,
            "metric_key": "selected_incidents"
        },
        {
            "label": "All Cleaned Arrests",
            "value": format_number(
                all_cleaned_arrests
            ),
            "meta": "Complete arrest dataset",
            "numeric": True,
            "help": (
                "The total number of cleaned arrest records represented "
                "in the complete arrest charge summary."
            )
        },
        {
            "label": "Linked Arrest Records",
            "value": format_number(
                linked_arrests
            ),
            "meta": "Linked to selected incidents",
            "numeric": True,
            "metric_key": "arrest_records"
        },
        {
            "label": "Linked Arrest Cases",
            "value": format_number(
                linked_arrest_cases
            ),
            "meta": "Distinct linked case numbers",
            "numeric": True,
            "metric_key": "unique_arrest_cases"
        },
        {
            "label": "Matched Incidents",
            "value": format_number(
                matched_incidents
            ),
            "meta": "At least one linked arrest",
            "numeric": True,
            "metric_key": "matched_incidents"
        },
        {
            "label": "Incident Match Coverage",
            "value": format_percentage(
                match_coverage
            ),
            "meta": "Matched incidents ÷ selected",
            "numeric": True,
            "metric_key": "match_coverage"
        },
        # {
        #     "label": "Linked Arrest Share",
        #     "value": format_percentage(
        #         linked_arrest_share
        #     ),
        #     "meta": "Linked arrests ÷ all cleaned",
        #     "numeric": True,
        #     "help": (
        #         "Distinct arrest records linked to the selected incident "
        #         "view divided by all cleaned arrest records."
        #     )
        # },
        {
            "label": "Top Charge Category",
            "value": top_charge_category,
            "meta": "Complete arrest dataset",
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
        f"The complete cleaned arrest dataset contains "
        f"{format_number(all_cleaned_arrests)} records. "
        f"{format_number(linked_arrests)} are linked to the current "
        f"incident analysis, and "
        f"{format_number(matched_incidents)} of "
        f"{format_number(selected_incidents)} selected incidents have at "
        f"least one linked arrest."
    )

    show_info_hint(
        "Arrest count distinction",
        (
            "All Cleaned Arrests represents the complete arrest dataset. "
            "Linked Arrest Records represents only arrests connected to the "
            "currently selected incident population."
        )
    )

    # show_info_hint(
    #     "Match coverage denominator",
    #     (
    #         "Incident match coverage equals distinct selected incidents "
    #         "with at least one linked arrest divided by all distinct "
    #         "selected incidents. Multiple arrests linked to one incident "
    #         "do not increase the matched-incident count."
    #     )
    # )

    # show_info_hint(
    #     "Outcome versus linkage",
    #     (
    #         "Arrest-related case outcome is based on the incident disposition "
    #         "field. Incident-to-arrest matching is based on links between "
    #         "incident and arrest records. The two measures are not expected "
    #         "to be identical."
    #     )
    # )

    return {
        "selected_incidents": selected_incidents,
        "all_cleaned_arrests": all_cleaned_arrests,
        "linked_arrests": linked_arrests,
        "linked_arrest_cases": linked_arrest_cases,
        "matched_incidents": matched_incidents,
        "match_coverage": match_coverage,
        "linked_arrest_share": linked_arrest_share,
        "top_charge_category": top_charge_category,
        "top_charge_count": top_charge_count
    }


def show_primary_arrest_charts(
    arrest_data,
    charge_summary
):
    """
    Display monthly linked arrest activity and charge linkage comparison.
    """
    monthly_chart = create_monthly_arrest_chart(
        arrest_data
    )

    charge_chart = create_charge_comparison_chart(
        charge_summary=charge_summary,
        arrest_data=arrest_data
    )

    chart_left, chart_right = st.columns(
        2,
        gap="small"
    )

    with chart_left:
        st.plotly_chart(
            monthly_chart,
            use_container_width=True,
            key="arrest_calendar_month_chart",
            config=get_chart_config()
        )

        show_info_hint(
            "Monthly chart definition",
            (
                "This is a seasonal calendar-month comparison. January "
                "arrests from represented years are combined, February "
                "arrests are combined, and so on. It is not a chronological "
                "year-month timeline."
            )
        )

    with chart_right:
        st.plotly_chart(
            charge_chart,
            use_container_width=True,
            key="arrest_charge_linkage_comparison_chart",
            config=get_chart_config()
        )

        show_info_hint(
            "Charge-category linkage rate",
            (
                "For each charge category, linkage rate equals distinct "
                "arrests linked to selected incidents divided by all cleaned "
                "arrests in that charge category."
            )
        )


def show_match_coverage(summary):
    """
    Display incident-to-arrest match coverage.
    """
    match_chart = create_match_coverage_chart(
        matched_incidents=summary[
            "matched_incidents"
        ],
        selected_incidents=summary[
            "selected_incidents"
        ]
    )

    st.plotly_chart(
        match_chart,
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
        f"{format_number(summary['matched_incidents'])} distinct selected "
        f"incidents have at least one linked arrest record, while "
        f"{format_number(unmatched_incidents)} do not."
    )


def has_meaningful_category_data(
    data,
    column
):
    """
    Check whether a descriptive field contains usable values.
    """
    if (
        data is None
        or data.empty
        or column not in data.columns
    ):
        return False

    values = (
        data[column]
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

    return (
        ~values.isin(
            invalid_values
        )
    ).any()


def prepare_demographic_data(
    arrest_data,
    column,
    maximum_categories=10
):
    """
    Prepare descriptive arrest metadata counts.
    """
    if not has_meaningful_category_data(
        arrest_data,
        column
    ):
        return pd.DataFrame()

    selected_columns = [
        column
    ]

    if "arrest_id" in arrest_data.columns:
        selected_columns.append(
            "arrest_id"
        )

    working_data = arrest_data[
        selected_columns
    ].copy()

    working_data[column] = (
        working_data[column]
        .apply(
            clean_category_value
        )
    )

    if "arrest_id" in working_data.columns:
        summary = (
            working_data
            .groupby(
                column
            )["arrest_id"]
            .nunique()
            .reset_index(
                name="arrest_count"
            )
        )

    else:
        summary = (
            working_data
            .groupby(
                column
            )
            .size()
            .reset_index(
                name="arrest_count"
            )
        )

    return (
        summary
        .sort_values(
            "arrest_count",
            ascending=False
        )
        .head(
            maximum_categories
        )
    )


def create_demographic_chart(
    arrest_data,
    column,
    title
):
    """
    Create a descriptive metadata chart.
    """
    summary = prepare_demographic_data(
        arrest_data=arrest_data,
        column=column
    )

    figure = go.Figure()

    if summary.empty:
        figure.add_annotation(
            text="Descriptive data is unavailable.",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font={
                "size": 13,
                "color": "#CBD5E1"
            }
        )

        figure.update_layout(
            title=title,
            height=DEMOGRAPHIC_CHART_HEIGHT,
            paper_bgcolor="#0B111C",
            plot_bgcolor="#0B111C"
        )

        return figure

    chart_data = summary.sort_values(
        "arrest_count",
        ascending=True
    )

    figure.add_trace(
        go.Bar(
            x=chart_data[
                "arrest_count"
            ],
            y=chart_data[
                column
            ],
            orientation="h",
            marker={
                "color": "#AAB7C8"
            },
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Distinct linked arrests: %{x:,}"
                "<extra></extra>"
            )
        )
    )

    figure.update_layout(
        title={
            "text": title,
            "x": 0,
            "xanchor": "left",
            "font": {
                "size": 16,
                "color": "#F8FAFC"
            }
        },
        height=DEMOGRAPHIC_CHART_HEIGHT,
        margin={
            "l": 135,
            "r": 20,
            "t": 65,
            "b": 45
        },
        paper_bgcolor="#0B111C",
        plot_bgcolor="#0B111C",
        showlegend=False,
        font={
            "color": "#F8FAFC"
        },
        xaxis={
            "title": {
                "text": "Distinct Linked Arrest Count"
            },
            "rangemode": "tozero",
            "gridcolor": "rgba(71, 85, 105, 0.45)"
        },
        yaxis={
            "title": {
                "text": ""
            },
            "showgrid": False,
            "automargin": True
        }
    )

    return figure


def show_demographic_metadata(arrest_data):
    """
    Display descriptive arrest metadata in a collapsed panel.
    """
    with st.expander(
        "Descriptive Arrest Metadata",
        expanded=False
    ):
        show_info_hint(
            "Responsible use",
            (
                "These fields summarize public arrest records only. They "
                "should not be used for individual prediction, profiling, "
                "risk scoring, or causal conclusions."
            )
        )

        if arrest_data is None or arrest_data.empty:
            st.info(
                "No linked arrest records are available for descriptive "
                "metadata analysis."
            )

            return

        chart_left, chart_right = st.columns(
            2,
            gap="small"
        )

        with chart_left:
            race_chart = create_demographic_chart(
                arrest_data=arrest_data,
                column="race",
                title="Linked Arrest Records by Race Field"
            )

            st.plotly_chart(
                race_chart,
                use_container_width=True,
                key="arrest_race_metadata_chart",
                config=get_chart_config()
            )

        with chart_right:
            sex_chart = create_demographic_chart(
                arrest_data=arrest_data,
                column="sex",
                title="Linked Arrest Records by Sex Field"
            )

            st.plotly_chart(
                sex_chart,
                use_container_width=True,
                key="arrest_sex_metadata_chart",
                config=get_chart_config()
            )


def show_arrest_record_review(
    arrest_data,
    match_data
):
    """
    Display linked arrest and match samples.
    """
    matched_rows = get_valid_match_rows(
        match_data
    )

    with st.expander(
        "Arrest and Matched Case Review",
        expanded=False
    ):
        show_info_hint(
            "Review scope",
            (
                "These tables are provided for validation. One incident may "
                "appear in multiple match rows when it is linked to more than "
                "one arrest."
            )
        )

        arrest_tab, match_tab = st.tabs(
            [
                "Linked Arrest Records",
                "Incident-Arrest Matches"
            ]
        )

        with arrest_tab:
            if arrest_data is None or arrest_data.empty:
                st.info(
                    "No linked arrest records are available."
                )

            else:
                show_compact_record_note(
                    "Showing the first 25 linked arrest rows."
                )

                columns = [
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
                    for column in columns
                    if column in arrest_data.columns
                ]

                st.dataframe(
                    arrest_data[
                        visible_columns
                    ].head(
                        25
                    ),
                    use_container_width=True,
                    hide_index=True
                )

        with match_tab:
            if matched_rows.empty:
                st.info(
                    "No incident-to-arrest match rows are available."
                )

            else:
                show_compact_record_note(
                    "Showing the first 25 valid incident-to-arrest match rows."
                )

                columns = [
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
                    for column in columns
                    if column in matched_rows.columns
                ]

                st.dataframe(
                    matched_rows[
                        visible_columns
                    ].head(
                        25
                    ),
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
    Display the complete arrests and charges section.

    demographic_summary remains accepted for compatibility with the
    current application interface.
    """
    show_section_banner(
        eyebrow="Enforcement Linkage",
        title="Arrests and Charges Profile",
        description=(
            "Compare the complete cleaned arrest population with records "
            "linked to selected incidents, then review charge categories "
            "and incident-to-arrest match coverage."
        )
    )

    summary = show_arrest_summary(
        incident_data=incident_data,
        arrest_data=arrest_data,
        match_data=match_data,
        charge_summary=charge_summary
    )

    # st.divider()

    show_primary_arrest_charts(
        arrest_data=arrest_data,
        charge_summary=charge_summary
    )

    show_match_coverage(
        summary
    )

    show_demographic_metadata(
        arrest_data
    )

    show_arrest_record_review(
        arrest_data=arrest_data,
        match_data=match_data
    )