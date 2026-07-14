"""
data_quality.py

Purpose:
Display the data reliability profile for the Terp Protect dashboard.

Responsibilities:
- Measure completeness and format validity for key fields
- Calculate a weighted primary field-check pass rate
- Display field-level validity percentages
- Identify records that fail configured quality checks
- Provide a compact record-review panel
- Explain the limitations of automated quality checks
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
from components.metrics import format_number


QUALITY_CHART_HEIGHT = 500


INCIDENT_PRIMARY_CHECKS = [
    {
        "label": "Incident Case Number",
        "column": "has_valid_case_number"
    },
    {
        "label": "Incident Occurred Datetime",
        "column": "has_valid_occurred_datetime"
    },
    {
        "label": "Incident Reported Datetime",
        "column": "has_valid_reported_datetime"
    },
    {
        "label": "Incident Reporting Delay",
        "column": "has_valid_reporting_delay"
    }
]


ARREST_PRIMARY_CHECKS = [
    {
        "label": "Arrest Number",
        "column": "has_valid_arrest_number"
    },
    {
        "label": "Arrest Case Number",
        "column": "has_valid_case_number"
    },
    {
        "label": "Arrest Datetime",
        "column": "has_valid_arrested_datetime"
    },
    {
        "label": "Arrest Charge Text",
        "column": "has_charge_text"
    }
]


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


def format_precise_percentage(
    value,
    decimal_places=2
):
    """
    Format a percentage without hiding small failure rates.
    """
    numeric_value = pd.to_numeric(
        value,
        errors="coerce"
    )

    if pd.isna(
        numeric_value
    ):
        return "0.00%"

    return (
        f"{float(numeric_value):.{decimal_places}f}%"
    )


def get_distinct_data(
    data,
    candidate_identifiers
):
    """
    Return one row per distinct record using the first available ID.

    Rows with missing identifiers are retained because they may represent
    records requiring quality review.
    """
    if data is None or data.empty:
        return pd.DataFrame()

    working_data = data.copy()

    for identifier in candidate_identifiers:
        if identifier not in working_data.columns:
            continue

        non_null_data = (
            working_data[
                working_data[
                    identifier
                ].notna()
            ]
            .drop_duplicates(
                subset=[
                    identifier
                ]
            )
        )

        null_data = working_data[
            working_data[
                identifier
            ].isna()
        ]

        return pd.concat(
            [
                non_null_data,
                null_data
            ],
            ignore_index=True
        )

    return working_data.drop_duplicates()


def get_distinct_incident_data(data):
    """
    Return one row per incident.
    """
    return get_distinct_data(
        data,
        [
            "incident_id",
            "case_number"
        ]
    )


def get_distinct_arrest_data(data):
    """
    Return one row per arrest.
    """
    return get_distinct_data(
        data,
        [
            "arrest_id",
            "arrest_number"
        ]
    )


def normalize_binary_flag(series):
    """
    Convert a quality flag into binary values.

    A value equal to one passes the configured check.
    All other values are treated as needing review.
    """
    numeric_values = pd.to_numeric(
        series,
        errors="coerce"
    ).fillna(0)

    return (
        numeric_values == 1
    ).astype(int)


def calculate_check_result(
    data,
    label,
    column,
    record_type
):
    """
    Calculate one primary field-check result.
    """
    if data is None:
        total_records = 0
    else:
        total_records = len(
            data
        )

    if (
        data is None
        or data.empty
        or column not in data.columns
    ):
        return {
            "record_type": record_type,
            "quality_check": label,
            "column": column,
            "available": False,
            "total_count": total_records,
            "valid_count": 0,
            "invalid_count": total_records,
            "validity_rate": 0.0
        }

    valid_flags = normalize_binary_flag(
        data[
            column
        ]
    )

    valid_count = int(
        valid_flags.sum()
    )

    invalid_count = max(
        total_records - valid_count,
        0
    )

    return {
        "record_type": record_type,
        "quality_check": label,
        "column": column,
        "available": True,
        "total_count": total_records,
        "valid_count": valid_count,
        "invalid_count": invalid_count,
        "validity_rate": safe_percentage(
            valid_count,
            total_records
        )
    }


def prepare_primary_quality_results(
    incident_data,
    arrest_data
):
    """
    Calculate all configured primary quality checks.
    """
    results = []

    for check in INCIDENT_PRIMARY_CHECKS:
        results.append(
            calculate_check_result(
                data=incident_data,
                label=check[
                    "label"
                ],
                column=check[
                    "column"
                ],
                record_type="Incident"
            )
        )

    for check in ARREST_PRIMARY_CHECKS:
        results.append(
            calculate_check_result(
                data=arrest_data,
                label=check[
                    "label"
                ],
                column=check[
                    "column"
                ],
                record_type="Arrest"
            )
        )

    return pd.DataFrame(
        results
    )


def calculate_weighted_pass_rate(quality_results):
    """
    Calculate a weighted pass rate across available checks.

    Each evaluated record-field combination contributes once.
    """
    if (
        quality_results is None
        or quality_results.empty
    ):
        return {
            "valid_results": 0,
            "evaluated_results": 0,
            "failed_results": 0,
            "pass_rate": 0.0,
            "available_checks": 0
        }

    available_results = quality_results[
        quality_results[
            "available"
        ]
        == True
    ].copy()

    if available_results.empty:
        return {
            "valid_results": 0,
            "evaluated_results": 0,
            "failed_results": 0,
            "pass_rate": 0.0,
            "available_checks": 0
        }

    valid_results = int(
        available_results[
            "valid_count"
        ].sum()
    )

    evaluated_results = int(
        available_results[
            "total_count"
        ].sum()
    )

    failed_results = max(
        evaluated_results - valid_results,
        0
    )

    return {
        "valid_results": valid_results,
        "evaluated_results": evaluated_results,
        "failed_results": failed_results,
        "pass_rate": safe_percentage(
            valid_results,
            evaluated_results
        ),
        "available_checks": len(
            available_results
        )
    }


def get_records_needing_review(
    data,
    quality_columns
):
    """
    Return records failing at least one available primary check.
    """
    if data is None or data.empty:
        return pd.DataFrame()

    available_columns = [
        column
        for column in quality_columns
        if column in data.columns
    ]

    if not available_columns:
        return data.iloc[
            0:0
        ].copy()

    review_mask = pd.Series(
        False,
        index=data.index
    )

    for column in available_columns:
        valid_flag = normalize_binary_flag(
            data[
                column
            ]
        )

        review_mask = (
            review_mask
            | (
                valid_flag == 0
            )
        )

    return data[
        review_mask
    ].copy()


def add_review_reason(
    data,
    quality_definitions
):
    """
    Add a readable explanation of which primary checks failed.
    """
    if data is None or data.empty:
        return pd.DataFrame()

    review_data = data.copy()

    def get_failed_checks(row):
        failed_checks = []

        for definition in quality_definitions:
            column = definition[
                "column"
            ]

            if column not in review_data.columns:
                continue

            value = pd.to_numeric(
                row[
                    column
                ],
                errors="coerce"
            )

            if pd.isna(
                value
            ) or value != 1:
                failed_checks.append(
                    definition[
                        "label"
                    ]
                )

        if not failed_checks:
            return "Review required"

        return ", ".join(
            failed_checks
        )

    review_data[
        "review_reason"
    ] = review_data.apply(
        get_failed_checks,
        axis=1
    )

    return review_data


def add_reporting_delay_context(data):
    """
    Add a simple reporting-delay issue description.

    This makes it clear when a report datetime occurs before the
    occurrence datetime.
    """
    if data is None or data.empty:
        return pd.DataFrame()

    working_data = data.copy()

    if (
        "occurred_datetime" not in working_data.columns
        or "reported_datetime" not in working_data.columns
    ):
        return working_data

    occurred_values = pd.to_datetime(
        working_data[
            "occurred_datetime"
        ],
        errors="coerce"
    )

    reported_values = pd.to_datetime(
        working_data[
            "reported_datetime"
        ],
        errors="coerce"
    )

    reported_before_occurrence = (
        occurred_values.notna()
        & reported_values.notna()
        & (
            reported_values
            < occurred_values
        )
    )

    working_data[
        "delay_review_note"
    ] = ""

    working_data.loc[
        reported_before_occurrence,
        "delay_review_note"
    ] = (
        "Reported datetime is earlier than occurred datetime"
    )

    if "report_delay_hours" in working_data.columns:
        delay_values = pd.to_numeric(
            working_data[
                "report_delay_hours"
            ],
            errors="coerce"
        )

        missing_delay_mask = (
            working_data[
                "delay_review_note"
            ]
            == ""
        ) & delay_values.isna()

        working_data.loc[
            missing_delay_mask,
            "delay_review_note"
        ] = (
            "Reporting delay is missing or unusable"
        )

    return working_data


def create_quality_percentage_chart(quality_results):
    """
    Create a field-level quality percentage chart.
    """
    available_data = quality_results[
        quality_results[
            "available"
        ]
        == True
    ].copy()

    figure = go.Figure()

    if available_data.empty:
        figure.add_annotation(
            text="Primary quality-check data is unavailable.",
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
            title="Primary Field Check Results",
            height=QUALITY_CHART_HEIGHT,
            paper_bgcolor="#0B111C",
            plot_bgcolor="#0B111C"
        )

        return figure

    chart_data = available_data.sort_values(
        "validity_rate",
        ascending=True
    )

    chart_data[
        "invalidity_rate"
    ] = (
        100
        - chart_data[
            "validity_rate"
        ]
    ).clip(
        lower=0
    )

    figure.add_trace(
        go.Bar(
            x=chart_data[
                "validity_rate"
            ],
            y=chart_data[
                "quality_check"
            ],
            name="Passed",
            orientation="h",
            marker={
                "color": "#6AC7B6"
            },
            customdata=chart_data[
                [
                    "valid_count",
                    "total_count"
                ]
            ],
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Pass rate: %{x:.2f}%<br>"
                "Passed results: %{customdata[0]:,}<br>"
                "Records evaluated: %{customdata[1]:,}"
                "<extra></extra>"
            )
        )
    )

    figure.add_trace(
        go.Bar(
            x=chart_data[
                "invalidity_rate"
            ],
            y=chart_data[
                "quality_check"
            ],
            name="Needs Review",
            orientation="h",
            marker={
                "color": "#E78A98"
            },
            customdata=chart_data[
                [
                    "invalid_count",
                    "total_count"
                ]
            ],
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Needs-review rate: %{x:.2f}%<br>"
                "Flagged results: %{customdata[0]:,}<br>"
                "Records evaluated: %{customdata[1]:,}"
                "<extra></extra>"
            )
        )
    )

    figure.update_layout(
        title={
            "text": "Primary Field Completeness and Format Checks",
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
            "l": 225,
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
                "size": 10,
                "color": "#E2E8F0"
            }
        },
        xaxis={
            "title": {
                "text": "Share of Records Evaluated"
            },
            "range": [
                0,
                100
            ],
            "ticksuffix": "%",
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


def show_quality_summary(
    incident_data,
    arrest_data,
    quality_results
):
    """
    Display compact quality summary metrics.
    """
    incident_count = len(
        incident_data
    )

    arrest_count = len(
        arrest_data
    )

    weighted_result = calculate_weighted_pass_rate(
        quality_results
    )

    incident_review_data = get_records_needing_review(
        incident_data,
        [
            check[
                "column"
            ]
            for check in INCIDENT_PRIMARY_CHECKS
        ]
    )

    arrest_review_data = get_records_needing_review(
        arrest_data,
        [
            check[
                "column"
            ]
            for check in ARREST_PRIMARY_CHECKS
        ]
    )

    overview_items = [
        {
            "label": "Incident Records Evaluated",
            "value": format_number(
                incident_count
            ),
            "meta": "Distinct selected incidents",
            "numeric": True
        },
        {
            "label": "Arrest Records Evaluated",
            "value": format_number(
                arrest_count
            ),
            "meta": "Distinct linked arrests",
            "numeric": True
        },
        {
            "label": "Primary Field Check Pass Rate",
            "value": format_precise_percentage(
                weighted_result[
                    "pass_rate"
                ]
            ),
            "meta": (
                f"{format_number(weighted_result['valid_results'])} "
                "passed results"
            ),
            "numeric": True,
            "help": (
                "Total passed record-field checks divided by all evaluated "
                "record-field checks. This measures configured completeness "
                "and format rules; it does not prove perfect source accuracy."
            )
        },
        {
            "label": "Primary Checks Available",
            "value": format_number(
                weighted_result[
                    "available_checks"
                ]
            ),
            "meta": "Configured field checks",
            "numeric": True
        },
        {
            "label": "Incident Records for Review",
            "value": format_number(
                len(
                    incident_review_data
                )
            ),
            "meta": "Failed at least one check",
            "numeric": True
        },
        {
            "label": "Arrest Records for Review",
            "value": format_number(
                len(
                    arrest_review_data
                )
            ),
            "meta": "Failed at least one check",
            "numeric": True
        }
    ]

    show_compact_overview_strip(
        overview_items
    )

    show_insight(
        f"The configured primary field checks achieved a "
        f"{format_precise_percentage(weighted_result['pass_rate'])} "
        f"weighted pass rate. "
        f"{format_number(len(incident_review_data))} incident records and "
        f"{format_number(len(arrest_review_data))} arrest records failed "
        f"at least one available primary check."
    )

    show_info_hint(
        "What this score means",
        (
            "The pass rate measures whether configured fields are present, "
            "formatted, and usable according to project rules. It does not "
            "confirm that every source value, category assignment, location, "
            "or incident-to-arrest match is factually correct."
        )
    )

    return {
        "weighted_result": weighted_result,
        "incident_review_data": incident_review_data,
        "arrest_review_data": arrest_review_data
    }


def show_primary_quality_chart(quality_results):
    """
    Display field-level primary quality results.
    """
    figure = create_quality_percentage_chart(
        quality_results
    )

    st.plotly_chart(
        figure,
        use_container_width=True,
        key="data_quality_primary_checks_chart",
        config=get_chart_config()
    )

    show_insight(
        "The chart shows field-level pass percentages. Red segments identify "
        "the portion of evaluated records that failed each configured check."
    )

    show_info_hint(
        "Reporting-delay review",
        (
            "Records with an impossible or unusable reporting-delay sequence "
            "remain visible in the review panel and are excluded from median, "
            "P90, and delay-bucket calculations."
        )
    )


def show_review_records(
    incident_review_data,
    arrest_review_data
):
    """
    Display primary-check failures in a collapsed review panel.
    """
    total_review_records = (
        len(
            incident_review_data
        )
        + len(
            arrest_review_data
        )
    )

    with st.expander(
        (
            "Records Requiring Primary-Check Review "
            f"({format_number(total_review_records)})"
        ),
        expanded=False
    ):
        show_info_hint(
            "Review panel scope",
            (
                "These tables contain records that failed at least one "
                "available primary completeness, format, or reporting-delay "
                "check."
            )
        )

        incident_tab, arrest_tab = st.tabs(
            [
                (
                    "Incident Review "
                    f"({format_number(len(incident_review_data))})"
                ),
                (
                    "Arrest Review "
                    f"({format_number(len(arrest_review_data))})"
                )
            ]
        )

        with incident_tab:
            if incident_review_data.empty:
                st.success(
                    "No selected incident records failed the available "
                    "primary quality checks."
                )

            else:
                incident_review_data = add_review_reason(
                    data=incident_review_data,
                    quality_definitions=INCIDENT_PRIMARY_CHECKS
                )

                incident_review_data = add_reporting_delay_context(
                    incident_review_data
                )

                show_compact_record_note(
                    "Showing the first 25 incident records that failed "
                    "at least one primary check."
                )

                incident_columns = [
                    "incident_id",
                    "case_number",
                    "occurred_datetime",
                    "reported_datetime",
                    "report_delay_hours",
                    "delay_review_note",
                    "crime_group",
                    "location_group",
                    "disposition_group",
                    "review_reason",
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
                    ].head(
                        25
                    ),
                    use_container_width=True,
                    hide_index=True
                )

        with arrest_tab:
            if arrest_review_data.empty:
                st.success(
                    "No selected arrest records failed the available "
                    "primary quality checks."
                )

            else:
                arrest_review_data = add_review_reason(
                    data=arrest_review_data,
                    quality_definitions=ARREST_PRIMARY_CHECKS
                )

                show_compact_record_note(
                    "Showing the first 25 arrest records that failed "
                    "at least one primary check."
                )

                arrest_columns = [
                    "arrest_id",
                    "arrest_number",
                    "case_number",
                    "arrested_datetime",
                    "charge_category",
                    "arrested_charge",
                    "review_reason",
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
                    ].head(
                        25
                    ),
                    use_container_width=True,
                    hide_index=True
                )


def show_data_quality(
    incident_data,
    arrest_data
):
    """
    Display the complete data quality section.
    """
    distinct_incident_data = get_distinct_incident_data(
        incident_data
    )

    distinct_arrest_data = get_distinct_arrest_data(
        arrest_data
    )

    show_section_banner(
        eyebrow="Data Reliability",
        title="Field Quality and Review Profile",
        description=(
            "Evaluate configured completeness and format checks, then "
            "inspect records requiring additional review."
        )
    )

    quality_results = prepare_primary_quality_results(
        incident_data=distinct_incident_data,
        arrest_data=distinct_arrest_data
    )

    summary = show_quality_summary(
        incident_data=distinct_incident_data,
        arrest_data=distinct_arrest_data,
        quality_results=quality_results
    )

    # st.divider()

    show_primary_quality_chart(
        quality_results
    )

    show_review_records(
        incident_review_data=summary[
            "incident_review_data"
        ],
        arrest_review_data=summary[
            "arrest_review_data"
        ]
    )