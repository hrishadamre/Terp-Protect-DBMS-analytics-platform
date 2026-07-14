"""
data_quality.py

Purpose:
Display data-quality and validation diagnostics for the
Terp Protect dashboard.

Responsibilities:
- Compare validity percentages across incident and arrest fields
- Show valid and invalid record counts
- Identify duplicates, missing values, and invalid delays
- Present a compact quality-check table
- Keep invalid-record review collapsed
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


QUALITY_CHART_HEIGHT = 500

PASS_THRESHOLD = 99.5
WARNING_THRESHOLD = 95.0


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


def safe_distinct_count(
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


def clean_string_series(series):
    """
    Clean a text series for missing-value checks.
    """
    return (
        series
        .fillna("")
        .astype(str)
        .str.strip()
    )


def create_not_null_check(
    data,
    column,
    label,
    dataset_name
):
    """
    Create a completeness check for one column.
    """
    total_records = len(
        data
    )

    if column not in data.columns:
        return {
            "dataset": dataset_name,
            "check": label,
            "column": column,
            "valid_count": 0,
            "invalid_count": total_records,
            "valid_percentage": 0.0,
            "invalid_percentage": 100.0 if total_records > 0 else 0.0,
            "status": "Unavailable",
            "issue": f"Column '{column}' is unavailable"
        }

    values = data[
        column
    ]

    if (
        pd.api.types.is_object_dtype(values)
        or pd.api.types.is_string_dtype(values)
    ):
        valid_mask = (
            clean_string_series(
                values
            )
            != ""
        )
    else:
        valid_mask = values.notna()

    valid_count = int(
        valid_mask.sum()
    )

    invalid_count = int(
        total_records - valid_count
    )

    valid_percentage = calculate_percentage(
        valid_count,
        total_records
    )

    return build_quality_result(
        dataset_name=dataset_name,
        check_label=label,
        column=column,
        valid_count=valid_count,
        invalid_count=invalid_count,
        valid_percentage=valid_percentage,
        issue=(
            f"{invalid_count:,} records contain missing values"
            if invalid_count > 0
            else "No missing values detected"
        )
    )


def create_datetime_check(
    data,
    column,
    label,
    dataset_name
):
    """
    Create a valid-datetime check.
    """
    total_records = len(
        data
    )

    if column not in data.columns:
        return {
            "dataset": dataset_name,
            "check": label,
            "column": column,
            "valid_count": 0,
            "invalid_count": total_records,
            "valid_percentage": 0.0,
            "invalid_percentage": 100.0 if total_records > 0 else 0.0,
            "status": "Unavailable",
            "issue": f"Column '{column}' is unavailable"
        }

    parsed_values = pd.to_datetime(
        data[column],
        errors="coerce"
    )

    valid_count = int(
        parsed_values.notna().sum()
    )

    invalid_count = int(
        total_records - valid_count
    )

    valid_percentage = calculate_percentage(
        valid_count,
        total_records
    )

    return build_quality_result(
        dataset_name=dataset_name,
        check_label=label,
        column=column,
        valid_count=valid_count,
        invalid_count=invalid_count,
        valid_percentage=valid_percentage,
        issue=(
            f"{invalid_count:,} invalid or missing datetime values"
            if invalid_count > 0
            else "All datetime values are valid"
        )
    )


def create_non_negative_numeric_check(
    data,
    column,
    label,
    dataset_name
):
    """
    Create a check requiring a numeric value greater than or equal to zero.
    """
    total_records = len(
        data
    )

    if column not in data.columns:
        return {
            "dataset": dataset_name,
            "check": label,
            "column": column,
            "valid_count": 0,
            "invalid_count": total_records,
            "valid_percentage": 0.0,
            "invalid_percentage": 100.0 if total_records > 0 else 0.0,
            "status": "Unavailable",
            "issue": f"Column '{column}' is unavailable"
        }

    numeric_values = pd.to_numeric(
        data[column],
        errors="coerce"
    )

    valid_mask = (
        numeric_values.notna()
        & (
            numeric_values >= 0
        )
    )

    valid_count = int(
        valid_mask.sum()
    )

    invalid_count = int(
        total_records - valid_count
    )

    valid_percentage = calculate_percentage(
        valid_count,
        total_records
    )

    return build_quality_result(
        dataset_name=dataset_name,
        check_label=label,
        column=column,
        valid_count=valid_count,
        invalid_count=invalid_count,
        valid_percentage=valid_percentage,
        issue=(
            f"{invalid_count:,} missing or negative values"
            if invalid_count > 0
            else "All values are valid and non-negative"
        )
    )


def create_binary_flag_check(
    data,
    column,
    label,
    dataset_name
):
    """
    Create a check for binary 0/1 fields.
    """
    total_records = len(
        data
    )

    if column not in data.columns:
        return {
            "dataset": dataset_name,
            "check": label,
            "column": column,
            "valid_count": 0,
            "invalid_count": total_records,
            "valid_percentage": 0.0,
            "invalid_percentage": 100.0 if total_records > 0 else 0.0,
            "status": "Unavailable",
            "issue": f"Column '{column}' is unavailable"
        }

    numeric_values = pd.to_numeric(
        data[column],
        errors="coerce"
    )

    valid_mask = numeric_values.isin(
        [
            0,
            1
        ]
    )

    valid_count = int(
        valid_mask.sum()
    )

    invalid_count = int(
        total_records - valid_count
    )

    valid_percentage = calculate_percentage(
        valid_count,
        total_records
    )

    return build_quality_result(
        dataset_name=dataset_name,
        check_label=label,
        column=column,
        valid_count=valid_count,
        invalid_count=invalid_count,
        valid_percentage=valid_percentage,
        issue=(
            f"{invalid_count:,} values are not valid binary flags"
            if invalid_count > 0
            else "All values are valid binary flags"
        )
    )


def build_quality_result(
    dataset_name,
    check_label,
    column,
    valid_count,
    invalid_count,
    valid_percentage,
    issue
):
    """
    Build a standardized quality-check result.
    """
    invalid_percentage = max(
        100 - valid_percentage,
        0
    )

    if valid_percentage >= PASS_THRESHOLD:
        status = "Pass"

    elif valid_percentage >= WARNING_THRESHOLD:
        status = "Review"

    else:
        status = "Attention"

    return {
        "dataset": dataset_name,
        "check": check_label,
        "column": column,
        "valid_count": int(
            valid_count
        ),
        "invalid_count": int(
            invalid_count
        ),
        "valid_percentage": float(
            valid_percentage
        ),
        "invalid_percentage": float(
            invalid_percentage
        ),
        "status": status,
        "issue": issue
    }


def prepare_quality_checks(
    incident_data,
    arrest_data
):
    """
    Create the primary percentage-based quality checks.
    """
    checks = []

    incident_checks = [
        create_not_null_check(
            data=incident_data,
            column="incident_id",
            label="Incident ID",
            dataset_name="Incident"
        ),
        create_not_null_check(
            data=incident_data,
            column="case_number",
            label="Incident Case Number",
            dataset_name="Incident"
        ),
        create_datetime_check(
            data=incident_data,
            column="occurred_datetime",
            label="Occurred Datetime",
            dataset_name="Incident"
        ),
        create_datetime_check(
            data=incident_data,
            column="reported_datetime",
            label="Reported Datetime",
            dataset_name="Incident"
        ),
        create_not_null_check(
            data=incident_data,
            column="crime_group",
            label="Crime Group",
            dataset_name="Incident"
        ),
        create_not_null_check(
            data=incident_data,
            column="location_group",
            label="Location Group",
            dataset_name="Incident"
        ),
        create_not_null_check(
            data=incident_data,
            column="disposition_group",
            label="Disposition Group",
            dataset_name="Incident"
        ),
        create_non_negative_numeric_check(
            data=incident_data,
            column="report_delay_hours",
            label="Reporting Delay",
            dataset_name="Incident"
        )
    ]

    arrest_checks = [
        create_not_null_check(
            data=arrest_data,
            column="arrest_id",
            label="Arrest ID",
            dataset_name="Arrest"
        ),
        create_not_null_check(
            data=arrest_data,
            column="arrest_number",
            label="Arrest Number",
            dataset_name="Arrest"
        ),
        create_not_null_check(
            data=arrest_data,
            column="case_number",
            label="Arrest Case Number",
            dataset_name="Arrest"
        ),
        create_datetime_check(
            data=arrest_data,
            column="arrested_datetime",
            label="Arrest Datetime",
            dataset_name="Arrest"
        ),
        create_not_null_check(
            data=arrest_data,
            column="charge_category",
            label="Charge Category",
            dataset_name="Arrest"
        )
    ]

    checks.extend(
        incident_checks
    )

    checks.extend(
        arrest_checks
    )

    return pd.DataFrame(
        checks
    )


def create_percentage_validity_chart(
    quality_checks
):
    """
    Create a 100% stacked horizontal validity chart.

    Each row displays:
    - valid percentage
    - invalid percentage
    - valid and invalid counts in hover
    """
    figure = go.Figure()

    if quality_checks.empty:
        figure.add_annotation(
            text="Data-quality checks are unavailable.",
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
            title="Data Validity by Field",
            height=QUALITY_CHART_HEIGHT,
            paper_bgcolor="#0B111C",
            plot_bgcolor="#0B111C"
        )

        return figure

    chart_data = quality_checks.copy()

    chart_data["display_check"] = (
        chart_data["dataset"]
        + " — "
        + chart_data["check"]
    )

    chart_data = chart_data.iloc[
        ::-1
    ].copy()

    figure.add_trace(
        go.Bar(
            x=chart_data[
                "valid_percentage"
            ],
            y=chart_data[
                "display_check"
            ],
            name="Valid",
            orientation="h",
            marker={
                "color": "#6AC7B6"
            },
            customdata=chart_data[
                [
                    "valid_count",
                    "invalid_count",
                    "status"
                ]
            ],
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Valid: %{x:.1f}%<br>"
                "Valid records: %{customdata[0]:,}<br>"
                "Invalid records: %{customdata[1]:,}<br>"
                "Status: %{customdata[2]}"
                "<extra></extra>"
            )
        )
    )

    figure.add_trace(
        go.Bar(
            x=chart_data[
                "invalid_percentage"
            ],
            y=chart_data[
                "display_check"
            ],
            name="Invalid",
            orientation="h",
            marker={
                "color": "#D95F65"
            },
            customdata=chart_data[
                [
                    "invalid_count",
                    "valid_count",
                    "status"
                ]
            ],
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Invalid: %{x:.1f}%<br>"
                "Invalid records: %{customdata[0]:,}<br>"
                "Valid records: %{customdata[1]:,}<br>"
                "Status: %{customdata[2]}"
                "<extra></extra>"
            )
        )
    )

    figure.update_layout(
        title={
            "text": "Data Validity by Field",
            "x": 0,
            "xanchor": "left",
            "font": {
                "size": 17,
                "color": "#F8FAFC"
            }
        },
        barmode="stack",
        height=QUALITY_CHART_HEIGHT,
        margin={
            "l": 205,
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
                "text": "Record Validity"
            },
            "range": [
                0,
                100
            ],
            "ticksuffix": "%",
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


def count_duplicate_records(
    data,
    column
):
    """
    Count records participating in duplicate values.
    """
    if (
        data is None
        or data.empty
        or column not in data.columns
    ):
        return 0

    values = data[
        column
    ].dropna()

    return int(
        values.duplicated(
            keep=False
        ).sum()
    )


def count_missing_or_unknown(
    data,
    column
):
    """
    Count missing or unknown categorical values.
    """
    if (
        data is None
        or data.empty
        or column not in data.columns
    ):
        return 0

    values = clean_string_series(
        data[
            column
        ]
    ).str.lower()

    invalid_values = {
        "",
        "unknown",
        "n/a",
        "na",
        "none",
        "missing",
        "not available"
    }

    return int(
        values.isin(
            invalid_values
        ).sum()
    )


def count_invalid_reporting_delays(
    incident_data
):
    """
    Count missing or negative reporting-delay values.
    """
    if (
        incident_data is None
        or incident_data.empty
        or "report_delay_hours" not in incident_data.columns
    ):
        return len(
            incident_data
        )

    delay_values = pd.to_numeric(
        incident_data[
            "report_delay_hours"
        ],
        errors="coerce"
    )

    invalid_mask = (
        delay_values.isna()
        | (
            delay_values < 0
        )
    )

    return int(
        invalid_mask.sum()
    )


def prepare_diagnostic_checks(
    incident_data,
    arrest_data
):
    """
    Prepare a compact set of operational quality diagnostics.
    """
    incident_count = len(
        incident_data
    )

    arrest_count = len(
        arrest_data
    )

    diagnostics = [
        {
            "Check": "Duplicate incident IDs",
            "Dataset": "Incident",
            "Affected Records": count_duplicate_records(
                incident_data,
                "incident_id"
            )
        },
        {
            "Check": "Duplicate arrest IDs",
            "Dataset": "Arrest",
            "Affected Records": count_duplicate_records(
                arrest_data,
                "arrest_id"
            )
        },
        {
            "Check": "Missing incident case numbers",
            "Dataset": "Incident",
            "Affected Records": (
                incident_count
                - (
                    clean_string_series(
                        incident_data[
                            "case_number"
                        ]
                    )
                    != ""
                ).sum()
                if "case_number" in incident_data.columns
                else incident_count
            )
        },
        {
            "Check": "Missing arrest case numbers",
            "Dataset": "Arrest",
            "Affected Records": (
                arrest_count
                - (
                    clean_string_series(
                        arrest_data[
                            "case_number"
                        ]
                    )
                    != ""
                ).sum()
                if "case_number" in arrest_data.columns
                else arrest_count
            )
        },
        {
            "Check": "Invalid reporting delays",
            "Dataset": "Incident",
            "Affected Records": count_invalid_reporting_delays(
                incident_data
            )
        },
        {
            "Check": "Unknown incident locations",
            "Dataset": "Incident",
            "Affected Records": count_missing_or_unknown(
                incident_data,
                "location_group"
            )
        },
        {
            "Check": "Unknown incident outcomes",
            "Dataset": "Incident",
            "Affected Records": count_missing_or_unknown(
                incident_data,
                "disposition_group"
            )
        },
        {
            "Check": "Unknown arrest charge categories",
            "Dataset": "Arrest",
            "Affected Records": count_missing_or_unknown(
                arrest_data,
                "charge_category"
            )
        }
    ]

    diagnostic_data = pd.DataFrame(
        diagnostics
    )

    diagnostic_data[
        "Affected Records"
    ] = pd.to_numeric(
        diagnostic_data[
            "Affected Records"
        ],
        errors="coerce"
    ).fillna(0).astype(int)

    diagnostic_data["Status"] = diagnostic_data[
        "Affected Records"
    ].apply(
        lambda count: (
            "Pass"
            if count == 0
            else "Review"
        )
    )

    diagnostic_data = diagnostic_data[
        [
            "Dataset",
            "Check",
            "Status",
            "Affected Records"
        ]
    ]

    return diagnostic_data


def get_overall_validity(
    quality_checks
):
    """
    Calculate the weighted validity percentage across all checks.
    """
    if quality_checks.empty:
        return 0.0

    total_valid = quality_checks[
        "valid_count"
    ].sum()

    total_checked = (
        quality_checks[
            "valid_count"
        ].sum()
        + quality_checks[
            "invalid_count"
        ].sum()
    )

    return calculate_percentage(
        total_valid,
        total_checked
    )


def get_lowest_quality_check(
    quality_checks
):
    """
    Return the check with the lowest validity percentage.
    """
    if quality_checks.empty:
        return {
            "check": "N/A",
            "dataset": "N/A",
            "valid_percentage": 0.0,
            "invalid_count": 0
        }

    lowest_row = quality_checks.sort_values(
        [
            "valid_percentage",
            "invalid_count"
        ],
        ascending=[
            True,
            False
        ]
    ).iloc[0]

    return {
        "check": lowest_row[
            "check"
        ],
        "dataset": lowest_row[
            "dataset"
        ],
        "valid_percentage": float(
            lowest_row[
                "valid_percentage"
            ]
        ),
        "invalid_count": int(
            lowest_row[
                "invalid_count"
            ]
        )
    }


def show_quality_summary(
    incident_data,
    arrest_data,
    quality_checks,
    diagnostic_checks
):
    """
    Display compact data-quality summary metrics.
    """
    incident_count = len(
        incident_data
    )

    arrest_count = len(
        arrest_data
    )

    overall_validity = get_overall_validity(
        quality_checks
    )

    passing_checks = int(
        (
            quality_checks[
                "status"
            ]
            == "Pass"
        ).sum()
    )

    checks_requiring_review = int(
        (
            quality_checks[
                "status"
            ]
            != "Pass"
        ).sum()
    )

    total_affected_diagnostics = int(
        diagnostic_checks[
            "Affected Records"
        ].sum()
    )

    lowest_check = get_lowest_quality_check(
        quality_checks
    )

    overview_items = [
        {
            "label": "Incident Records",
            "value": format_number(
                incident_count
            ),
            "meta": "Current filtered view",
            "numeric": True
        },
        {
            "label": "Arrest Records",
            "value": format_number(
                arrest_count
            ),
            "meta": "Linked arrest view",
            "numeric": True
        },
        {
            "label": "Overall Validity",
            "value": format_percentage(
                overall_validity
            ),
            "meta": "Across field checks",
            "numeric": True
        },
        {
            "label": "Passing Checks",
            "value": format_number(
                passing_checks
            ),
            "meta": f"Out of {len(quality_checks)} checks",
            "numeric": True
        },
        {
            "label": "Checks to Review",
            "value": format_number(
                checks_requiring_review
            ),
            "meta": "Below pass threshold",
            "numeric": True
        },
        {
            "label": "Lowest Validity",
            "value": lowest_check[
                "check"
            ],
            "meta": format_percentage(
                lowest_check[
                    "valid_percentage"
                ]
            ),
            "badge": format_number(
                lowest_check[
                    "invalid_count"
                ]
            )
        },
        {
            "label": "Diagnostic Flags",
            "value": format_number(
                total_affected_diagnostics
            ),
            "meta": "Affected record occurrences",
            "numeric": True
        }
    ]

    show_compact_overview_strip(
        overview_items
    )

    if checks_requiring_review == 0:
        show_insight(
            f"All {format_number(len(quality_checks))} primary field "
            f"checks meet the {PASS_THRESHOLD:.1f}% validity threshold. "
            f"Overall weighted validity is "
            f"{format_percentage(overall_validity)}."
        )
    else:
        show_insight(
            f"{format_number(checks_requiring_review)} primary checks "
            f"require review. {lowest_check['dataset']} — "
            f"{lowest_check['check']} has the lowest validity at "
            f"{format_percentage(lowest_check['valid_percentage'])}, "
            f"with {format_number(lowest_check['invalid_count'])} "
            f"affected records."
        )


def show_quality_chart(
    quality_checks
):
    """
    Display percentage-based validity by field.
    """
    figure = create_percentage_validity_chart(
        quality_checks
    )

    st.plotly_chart(
        figure,
        use_container_width=True,
        key="data_quality_percentage_validity_chart",
        config=get_chart_config()
    )

    lowest_check = get_lowest_quality_check(
        quality_checks
    )

    show_insight(
        f"{lowest_check['dataset']} — {lowest_check['check']} is the "
        f"lowest-validity primary field check at "
        f"{format_percentage(lowest_check['valid_percentage'])}. "
        f"Hover over each bar to inspect valid and invalid counts."
    )


def show_diagnostic_table(
    diagnostic_checks
):
    """
    Display a compact quality-diagnostics table.
    """
    st.markdown(
        "#### Quality Check Diagnostics"
    )

    show_info_hint(
        "How to read this table",
        (
            "A Pass indicates that no affected records were detected. "
            "Review indicates that one or more records should be inspected. "
            "Affected-record totals may overlap across checks."
        )
    )

    display_data = diagnostic_checks.copy()

    display_data["Affected Records"] = (
        display_data["Affected Records"]
        .map(
            lambda value: f"{int(value):,}"
        )
    )

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Dataset": st.column_config.TextColumn(
                "Dataset",
                width="small"
            ),
            "Check": st.column_config.TextColumn(
                "Quality Check",
                width="large"
            ),
            "Status": st.column_config.TextColumn(
                "Status",
                width="small"
            ),
            "Affected Records": st.column_config.TextColumn(
                "Affected Records",
                width="small"
            )
        }
    )


def get_invalid_incident_records(
    incident_data
):
    """
    Return incident records with one or more core quality issues.
    """
    if incident_data is None or incident_data.empty:
        return pd.DataFrame()

    invalid_mask = pd.Series(
        False,
        index=incident_data.index
    )

    if "incident_id" in incident_data.columns:
        incident_ids = clean_string_series(
            incident_data[
                "incident_id"
            ]
        )

        invalid_mask = (
            invalid_mask
            | (
                incident_ids
                == ""
            )
            | incident_data[
                "incident_id"
            ].duplicated(
                keep=False
            )
        )

    if "case_number" in incident_data.columns:
        invalid_mask = (
            invalid_mask
            | (
                clean_string_series(
                    incident_data[
                        "case_number"
                    ]
                )
                == ""
            )
        )

    if "occurred_datetime" in incident_data.columns:
        invalid_mask = (
            invalid_mask
            | pd.to_datetime(
                incident_data[
                    "occurred_datetime"
                ],
                errors="coerce"
            ).isna()
        )

    if "reported_datetime" in incident_data.columns:
        invalid_mask = (
            invalid_mask
            | pd.to_datetime(
                incident_data[
                    "reported_datetime"
                ],
                errors="coerce"
            ).isna()
        )

    if "report_delay_hours" in incident_data.columns:
        delay_values = pd.to_numeric(
            incident_data[
                "report_delay_hours"
            ],
            errors="coerce"
        )

        invalid_mask = (
            invalid_mask
            | delay_values.isna()
            | (
                delay_values < 0
            )
        )

    return incident_data[
        invalid_mask
    ].copy()


def get_invalid_arrest_records(
    arrest_data
):
    """
    Return arrest records with one or more core quality issues.
    """
    if arrest_data is None or arrest_data.empty:
        return pd.DataFrame()

    invalid_mask = pd.Series(
        False,
        index=arrest_data.index
    )

    if "arrest_id" in arrest_data.columns:
        arrest_ids = clean_string_series(
            arrest_data[
                "arrest_id"
            ]
        )

        invalid_mask = (
            invalid_mask
            | (
                arrest_ids
                == ""
            )
            | arrest_data[
                "arrest_id"
            ].duplicated(
                keep=False
            )
        )

    if "arrest_number" in arrest_data.columns:
        invalid_mask = (
            invalid_mask
            | (
                clean_string_series(
                    arrest_data[
                        "arrest_number"
                    ]
                )
                == ""
            )
        )

    if "case_number" in arrest_data.columns:
        invalid_mask = (
            invalid_mask
            | (
                clean_string_series(
                    arrest_data[
                        "case_number"
                    ]
                )
                == ""
            )
        )

    if "arrested_datetime" in arrest_data.columns:
        invalid_mask = (
            invalid_mask
            | pd.to_datetime(
                arrest_data[
                    "arrested_datetime"
                ],
                errors="coerce"
            ).isna()
        )

    if "charge_category" in arrest_data.columns:
        invalid_mask = (
            invalid_mask
            | (
                clean_string_series(
                    arrest_data[
                        "charge_category"
                    ]
                )
                == ""
            )
        )

    return arrest_data[
        invalid_mask
    ].copy()


def show_invalid_record_review(
    incident_data,
    arrest_data
):
    """
    Display collapsed invalid-record review tables.
    """
    invalid_incidents = get_invalid_incident_records(
        incident_data
    )

    invalid_arrests = get_invalid_arrest_records(
        arrest_data
    )

    with st.expander(
        "Invalid and Duplicate Record Review",
        expanded=False
    ):
        show_info_hint(
            "About this review panel",
            (
                "These tables show records affected by missing identifiers, "
                "invalid dates, invalid reporting delays, or duplicate IDs. "
                "A record may contain more than one quality issue."
            )
        )

        incident_tab, arrest_tab = st.tabs(
            [
                (
                    "Incident records "
                    f"({format_number(len(invalid_incidents))})"
                ),
                (
                    "Arrest records "
                    f"({format_number(len(invalid_arrests))})"
                )
            ]
        )

        with incident_tab:
            if invalid_incidents.empty:
                st.success(
                    "No invalid or duplicate incident records were "
                    "identified by the current checks."
                )
            else:
                show_compact_record_note(
                    "Showing the first 25 incident records with one "
                    "or more detected quality issues."
                )

                incident_columns = [
                    "incident_id",
                    "case_number",
                    "occurred_datetime",
                    "reported_datetime",
                    "crime_group",
                    "location_group",
                    "disposition_group",
                    "report_delay_hours"
                ]

                visible_columns = [
                    column
                    for column in incident_columns
                    if column in invalid_incidents.columns
                ]

                st.dataframe(
                    invalid_incidents[
                        visible_columns
                    ].head(25),
                    use_container_width=True,
                    hide_index=True
                )

        with arrest_tab:
            if invalid_arrests.empty:
                st.success(
                    "No invalid or duplicate arrest records were "
                    "identified by the current checks."
                )
            else:
                show_compact_record_note(
                    "Showing the first 25 arrest records with one "
                    "or more detected quality issues."
                )

                arrest_columns = [
                    "arrest_id",
                    "arrest_number",
                    "case_number",
                    "arrested_datetime",
                    "charge_category",
                    "arrested_charge",
                    "race",
                    "sex"
                ]

                visible_columns = [
                    column
                    for column in arrest_columns
                    if column in invalid_arrests.columns
                ]

                st.dataframe(
                    invalid_arrests[
                        visible_columns
                    ].head(25),
                    use_container_width=True,
                    hide_index=True
                )


def show_data_quality(
    incident_data,
    arrest_data
):
    """
    Display the complete data-quality section.
    """
    show_section_banner(
        eyebrow="Trust and Validation",
        title="Data Quality Profile",
        description=(
            "Assess field validity, identify records requiring review, "
            "and verify the reliability of the filtered incident and "
            "arrest datasets."
        )
    )

    quality_checks = prepare_quality_checks(
        incident_data=incident_data,
        arrest_data=arrest_data
    )

    diagnostic_checks = prepare_diagnostic_checks(
        incident_data=incident_data,
        arrest_data=arrest_data
    )

    show_quality_summary(
        incident_data=incident_data,
        arrest_data=arrest_data,
        quality_checks=quality_checks,
        diagnostic_checks=diagnostic_checks
    )

    st.divider()

    show_quality_chart(
        quality_checks
    )

    show_diagnostic_table(
        diagnostic_checks
    )

    show_invalid_record_review(
        incident_data=incident_data,
        arrest_data=arrest_data
    )