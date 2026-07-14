"""
data_quality.py

Purpose:
Display the pipeline reliability profile section for the Terp Protect dashboard.

Responsibilities:
- Summarize incident and arrest quality checks
- Display valid and invalid record counts
- Identify records requiring review
- Provide collapsed diagnostic record samples
"""

import pandas as pd
import streamlit as st

from components.charts import (
    create_quality_bar_chart,
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
    format_percentage
)


QUALITY_CHART_HEIGHT = 500


def count_valid_records(
    data,
    column
):
    """
    Count records passing a binary quality check.
    """
    if (
        data.empty
        or column not in data.columns
    ):
        return 0

    values = pd.to_numeric(
        data[column],
        errors="coerce"
    ).fillna(0)

    return int(
        values.sum()
    )


def calculate_percentage(
    valid_count,
    total_count
):
    """
    Calculate a safe percentage.
    """
    if total_count == 0:
        return 0.0

    return valid_count / total_count * 100


def get_review_records(
    data,
    quality_columns
):
    """
    Return records failing at least one available quality check.
    """
    if data.empty:
        return data.copy()

    available_columns = [
        column
        for column in quality_columns
        if column in data.columns
    ]

    if not available_columns:
        return data.iloc[0:0].copy()

    review_mask = pd.Series(
        False,
        index=data.index
    )

    for column in available_columns:
        values = pd.to_numeric(
            data[column],
            errors="coerce"
        ).fillna(0)

        review_mask = review_mask | (
            values == 0
        )

    return data[
        review_mask
    ].copy()


def get_quality_metrics(
    incident_data,
    arrest_data
):
    """
    Calculate all quality counts and percentages.
    """
    total_incidents = len(
        incident_data
    )

    total_arrests = len(
        arrest_data
    )

    counts = {
        "incident_case": count_valid_records(
            incident_data,
            "has_valid_case_number"
        ),
        "incident_occurred": count_valid_records(
            incident_data,
            "has_valid_occurred_datetime"
        ),
        "incident_reported": count_valid_records(
            incident_data,
            "has_valid_reported_datetime"
        ),
        "incident_delay": count_valid_records(
            incident_data,
            "has_valid_reporting_delay"
        ),
        "arrest_number": count_valid_records(
            arrest_data,
            "has_valid_arrest_number"
        ),
        "arrest_case": count_valid_records(
            arrest_data,
            "has_valid_case_number"
        ),
        "arrest_date": count_valid_records(
            arrest_data,
            "has_valid_arrested_datetime"
        ),
        "arrest_charge": count_valid_records(
            arrest_data,
            "has_charge_text"
        )
    }

    percentages = {
        "incident_case": calculate_percentage(
            counts["incident_case"],
            total_incidents
        ),
        "incident_occurred": calculate_percentage(
            counts["incident_occurred"],
            total_incidents
        ),
        "incident_reported": calculate_percentage(
            counts["incident_reported"],
            total_incidents
        ),
        "incident_delay": calculate_percentage(
            counts["incident_delay"],
            total_incidents
        ),
        "arrest_number": calculate_percentage(
            counts["arrest_number"],
            total_arrests
        ),
        "arrest_case": calculate_percentage(
            counts["arrest_case"],
            total_arrests
        ),
        "arrest_date": calculate_percentage(
            counts["arrest_date"],
            total_arrests
        ),
        "arrest_charge": calculate_percentage(
            counts["arrest_charge"],
            total_arrests
        )
    }

    return {
        "total_incidents": total_incidents,
        "total_arrests": total_arrests,
        "counts": counts,
        "percentages": percentages
    }


def show_quality_summary(metrics):
    """
    Display compact quality summary cards.
    """
    percentages = metrics["percentages"]

    overview_items = [
        {
            "label": "Incident Records",
            "value": format_number(
                metrics["total_incidents"]
            ),
            "meta": "Current filtered view",
            "numeric": True
        },
        {
            "label": "Incident Case Validity",
            "value": format_percentage(
                percentages["incident_case"]
            ),
            "meta": "Valid case numbers",
            "numeric": True
        },
        {
            "label": "Occurred Date Validity",
            "value": format_percentage(
                percentages["incident_occurred"]
            ),
            "meta": "Valid occurrence dates",
            "numeric": True
        },
        {
            "label": "Reported Date Validity",
            "value": format_percentage(
                percentages["incident_reported"]
            ),
            "meta": "Valid report dates",
            "numeric": True
        },
        {
            "label": "Delay Validity",
            "value": format_percentage(
                percentages["incident_delay"]
            ),
            "meta": "Usable delay values",
            "numeric": True
        },
        {
            "label": "Arrest Records",
            "value": format_number(
                metrics["total_arrests"]
            ),
            "meta": "Linked filtered records",
            "numeric": True
        },
        {
            "label": "Arrest Case Validity",
            "value": format_percentage(
                percentages["arrest_case"]
            ),
            "meta": "Valid case numbers",
            "numeric": True
        },
        {
            "label": "Charge Text Validity",
            "value": format_percentage(
                percentages["arrest_charge"]
            ),
            "meta": "Usable charge text",
            "numeric": True
        }
    ]

    show_compact_overview_strip(
        overview_items
    )

    show_insight(
        f"{format_percentage(percentages['incident_case'])} of "
        f"selected incident records have valid case numbers, and "
        f"{format_percentage(percentages['arrest_case'])} of selected "
        f"arrest records have valid case numbers."
    )

    show_info_hint(
        "How to read quality checks",
        (
            "Valid counts passed the field-level check. Invalid counts "
            "identify missing, inconsistent, or unusable values that "
            "may require review."
        )
    )


def create_quality_dataframe(metrics):
    """
    Build the quality-check dataframe used by the chart.
    """
    counts = metrics["counts"]

    total_incidents = metrics[
        "total_incidents"
    ]

    total_arrests = metrics[
        "total_arrests"
    ]

    return pd.DataFrame(
        {
            "Quality Check": [
                "Incident Valid Case Number",
                "Incident Valid Occurred Datetime",
                "Incident Valid Reported Datetime",
                "Incident Valid Reporting Delay",
                "Arrest Valid Arrest Number",
                "Arrest Valid Case Number",
                "Arrest Valid Arrested Datetime",
                "Arrest Has Charge Text"
            ],
            "Valid Count": [
                counts["incident_case"],
                counts["incident_occurred"],
                counts["incident_reported"],
                counts["incident_delay"],
                counts["arrest_number"],
                counts["arrest_case"],
                counts["arrest_date"],
                counts["arrest_charge"]
            ],
            "Invalid Count": [
                total_incidents - counts["incident_case"],
                total_incidents - counts["incident_occurred"],
                total_incidents - counts["incident_reported"],
                total_incidents - counts["incident_delay"],
                total_arrests - counts["arrest_number"],
                total_arrests - counts["arrest_case"],
                total_arrests - counts["arrest_date"],
                total_arrests - counts["arrest_charge"]
            ]
        }
    )


def show_quality_chart(metrics):
    """
    Display valid and invalid quality counts.
    """
    quality_data = create_quality_dataframe(
        metrics
    )

    quality_chart = create_quality_bar_chart(
        quality_data
    )

    quality_chart.update_layout(
        height=QUALITY_CHART_HEIGHT
    )

    st.plotly_chart(
        quality_chart,
        use_container_width=True,
        key="quality_summary_chart",
        config=get_chart_config()
    )

    show_insight(
        "Quality checks with larger invalid counts should be reviewed "
        "before those fields are used for detailed operational analysis."
    )


def show_review_summary(
    incident_review_data,
    arrest_review_data,
    incident_total,
    arrest_total
):
    """
    Display compact review-volume cards.
    """
    incident_review_percentage = calculate_percentage(
        len(incident_review_data),
        incident_total
    )

    arrest_review_percentage = calculate_percentage(
        len(arrest_review_data),
        arrest_total
    )

    overview_items = [
        {
            "label": "Incident Records Needing Review",
            "value": format_number(
                len(incident_review_data)
            ),
            "meta": format_percentage(
                incident_review_percentage
            ),
            "numeric": True
        },
        {
            "label": "Arrest Records Needing Review",
            "value": format_number(
                len(arrest_review_data)
            ),
            "meta": format_percentage(
                arrest_review_percentage
            ),
            "numeric": True
        }
    ]

    show_compact_overview_strip(
        overview_items
    )


def show_quality_review_panel(
    incident_review_data,
    arrest_review_data,
    arrest_data
):
    """
    Display collapsed incident and arrest review tables.
    """
    with st.expander(
        "Records Needing Attention",
        expanded=False
    ):
        show_info_hint(
            "About this review panel",
            (
                "Use these samples to inspect records that failed one "
                "or more quality checks. The tables are hidden by "
                "default to keep the dashboard focused."
            )
        )

        incident_tab, arrest_tab = st.tabs(
            [
                (
                    "Incident review "
                    f"({format_number(len(incident_review_data))})"
                ),
                (
                    "Arrest review "
                    f"({format_number(len(arrest_review_data))})"
                )
            ]
        )

        with incident_tab:
            if incident_review_data.empty:
                st.success(
                    "No selected incident records require review under "
                    "the current quality checks."
                )
            else:
                show_compact_record_note(
                    "Showing the first 25 incident records that failed "
                    "at least one quality check."
                )

                incident_columns = [
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

                available_columns = [
                    column
                    for column in incident_columns
                    if column in incident_review_data.columns
                ]

                st.dataframe(
                    incident_review_data[
                        available_columns
                    ].head(25),
                    use_container_width=True,
                    hide_index=True
                )

        with arrest_tab:
            if arrest_data.empty:
                st.info(
                    "No arrest records are available for the selected "
                    "incident filters."
                )
            elif arrest_review_data.empty:
                st.success(
                    "No selected arrest records require review under "
                    "the current quality checks."
                )
            else:
                show_compact_record_note(
                    "Showing the first 25 arrest records that failed "
                    "at least one quality check."
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
                    "has_valid_arrest_number",
                    "has_valid_case_number",
                    "has_valid_arrested_datetime",
                    "has_charge_text"
                ]

                available_columns = [
                    column
                    for column in arrest_columns
                    if column in arrest_review_data.columns
                ]

                st.dataframe(
                    arrest_review_data[
                        available_columns
                    ].head(25),
                    use_container_width=True,
                    hide_index=True
                )


def show_data_quality(
    incident_data,
    arrest_data
):
    """
    Display the complete pipeline reliability section.
    """
    show_section_banner(
        eyebrow="",
        title="Pipeline Reliability Profile",
        description=(
            "Evaluate completeness, consistency, and usability of the "
            "incident and arrest fields supporting dashboard analysis."
        )
    )

    metrics = get_quality_metrics(
        incident_data,
        arrest_data
    )

    show_quality_summary(
        metrics
    )

    st.divider()

    show_quality_chart(
        metrics
    )

    incident_quality_columns = [
        "has_valid_case_number",
        "has_valid_occurred_datetime",
        "has_valid_reported_datetime",
        "has_valid_reporting_delay"
    ]

    arrest_quality_columns = [
        "has_valid_arrest_number",
        "has_valid_case_number",
        "has_valid_arrested_datetime",
        "has_charge_text"
    ]

    incident_review_data = get_review_records(
        incident_data,
        incident_quality_columns
    )

    arrest_review_data = get_review_records(
        arrest_data,
        arrest_quality_columns
    )

    show_review_summary(
        incident_review_data=incident_review_data,
        arrest_review_data=arrest_review_data,
        incident_total=len(incident_data),
        arrest_total=len(arrest_data)
    )

    show_quality_review_panel(
        incident_review_data,
        arrest_review_data,
        arrest_data
    )