"""
metrics.py

Purpose:
Store reusable formatting, calculation, and metric-definition helpers
for the Terp Protect dashboard.

Responsibilities:
- Format numbers, percentages, and durations
- Return the most frequent categorical value
- Calculate safe percentages
- Store consistent metric definitions
- Provide numerator and denominator explanations for dashboard metrics
"""

import pandas as pd


METRIC_DEFINITIONS = {
    "selected_incidents": {
        "label": "Selected Incidents",
        "definition": (
            "The number of distinct incident records remaining after "
            "the current dashboard filters are applied."
        ),
        "formula": (
            "Distinct incident_id values in the filtered incident dataset."
        )
    },

    "arrest_records": {
        "label": "Arrest Records",
        "definition": (
            "The number of distinct arrest records linked to the current "
            "filtered incident view."
        ),
        "formula": (
            "Distinct arrest_id values in the filtered arrest dataset."
        )
    },

    "unique_arrest_cases": {
        "label": "Unique Arrest Cases",
        "definition": (
            "The number of distinct arrest case numbers represented in "
            "the filtered arrest dataset."
        ),
        "formula": (
            "Distinct non-null arrest case_number values."
        )
    },

    "matched_incidents": {
        "label": "Matched Incidents",
        "definition": (
            "The number of distinct selected incidents that have at least "
            "one linked arrest record."
        ),
        "formula": (
            "Distinct incident_id values in valid incident-arrest match rows."
        )
    },

    "match_coverage": {
        "label": "Match Coverage",
        "definition": (
            "The percentage of selected incidents with at least one linked "
            "arrest record. Multiple arrest records linked to the same "
            "incident do not increase the matched-incident count."
        ),
        "formula": (
            "Distinct matched incidents ÷ distinct selected incidents × 100."
        )
    },

    "closed_share": {
        "label": "Closed / Cleared Share",
        "definition": (
            "The percentage of selected incidents classified as closed "
            "or cleared."
        ),
        "formula": (
            "Closed or cleared incidents ÷ selected incidents × 100."
        )
    },

    "pending_share": {
        "label": "Pending / Active Share",
        "definition": (
            "The percentage of selected incidents classified as pending "
            "or active."
        ),
        "formula": (
            "Pending or active incidents ÷ selected incidents × 100."
        )
    },

    "arrest_related_share": {
        "label": "Arrest-Related Share",
        "definition": (
            "The percentage of selected incidents whose disposition is "
            "classified as arrest-related."
        ),
        "formula": (
            "Arrest-related incidents ÷ selected incidents × 100."
        )
    },

    "same_day_share": {
        "label": "Same-Day Reporting Share",
        "definition": (
            "The percentage of records with a valid reporting delay that "
            "were reported within 24 hours of occurrence."
        ),
        "formula": (
            "Valid incidents reported within 24 hours ÷ incidents with a "
            "valid non-negative reporting delay × 100."
        )
    },

    "over_seven_day_share": {
        "label": "Over-Seven-Day Share",
        "definition": (
            "The percentage of records with a valid reporting delay that "
            "were reported more than seven days after occurrence."
        ),
        "formula": (
            "Valid incidents reported after seven days ÷ incidents with a "
            "valid non-negative reporting delay × 100."
        )
    },

    "valid_delay_coverage": {
        "label": "Valid Delay Coverage",
        "definition": (
            "The percentage of selected incidents containing a usable, "
            "non-negative reporting-delay value."
        ),
        "formula": (
            "Incidents with valid reporting delay ÷ selected incidents × 100."
        )
    },

    "median_delay": {
        "label": "Median Reporting Delay",
        "definition": (
            "The middle reporting-delay value after valid delays are sorted. "
            "Half of valid records have a lower delay and half have a higher "
            "delay."
        ),
        "formula": (
            "Median of valid non-negative report_delay_hours values."
        )
    },

    "p90_delay": {
        "label": "P90 Reporting Delay",
        "definition": (
            "The reporting-delay value within which 90% of valid incidents "
            "were reported. The remaining 10% had longer delays."
        ),
        "formula": (
            "90th percentile of valid non-negative report_delay_hours values."
        )
    },

    "weekend_share": {
        "label": "Weekend Share",
        "definition": (
            "The percentage of selected incidents that occurred on Saturday "
            "or Sunday."
        ),
        "formula": (
            "Weekend incidents ÷ selected incidents × 100."
        )
    },

    "academic_period_rate": {
        "label": "Incidents per Active Week",
        "definition": (
            "A normalized incident rate that accounts for the number of "
            "distinct dates represented within an academic period."
        ),
        "formula": (
            "Incident count ÷ (distinct represented dates ÷ 7)."
        )
    },

    "validity_rate": {
        "label": "Validity Rate",
        "definition": (
            "The percentage of records that pass a specific field-level "
            "quality check."
        ),
        "formula": (
            "Valid records for the check ÷ all records evaluated × 100."
        )
    },

    "overall_validity": {
        "label": "Overall Validity",
        "definition": (
            "The weighted percentage of valid results across all primary "
            "field-level quality checks."
        ),
        "formula": (
            "Total valid check results ÷ total evaluated check results × 100."
        )
    },

    "crime_group_share": {
        "label": "Crime-Group Share",
        "definition": (
            "The percentage of selected incidents assigned to a specific "
            "crime group."
        ),
        "formula": (
            "Incidents in the crime group ÷ selected incidents × 100."
        )
    },

    "outcome_composition": {
        "label": "Outcome Composition",
        "definition": (
            "The distribution of case outcomes within a specific crime group."
        ),
        "formula": (
            "Incidents in an outcome category ÷ all incidents in the same "
            "crime group × 100."
        )
    },

    "location_crime_composition": {
        "label": "Location Crime Composition",
        "definition": (
            "The distribution of crime groups within a specific location "
            "group."
        ),
        "formula": (
            "Incidents in the crime category and location group ÷ all "
            "displayed incidents in that location group × 100."
        )
    },

    "active_filter_count": {
        "label": "Active Filter Count",
        "definition": (
            "The number of filter groups currently narrowing the dashboard."
        ),
        "formula": (
            "Count of filter groups with one or more selected values."
        )
    }
}


def format_number(value):
    """
    Format a numeric value with thousands separators.

    Missing values are displayed as zero.
    """
    if pd.isna(value):
        return "0"

    return f"{int(value):,}"


def format_decimal(
    value,
    decimal_places=1
):
    """
    Format a decimal value with a configurable number of places.
    """
    if pd.isna(value):
        return "0.0"

    return f"{float(value):.{decimal_places}f}"


def format_percentage(
    value,
    decimal_places=1
):
    """
    Format a percentage value.

    The function expects a value already expressed on the 0–100 scale.
    """
    if pd.isna(value):
        return "0.0%"

    return f"{float(value):.{decimal_places}f}%"


def format_duration_hours(value):
    """
    Format a duration expressed in hours.

    Values below 48 hours are displayed in hours.
    Values of 48 hours or more are displayed in days.
    """
    numeric_value = pd.to_numeric(
        value,
        errors="coerce"
    )

    if pd.isna(numeric_value):
        return "N/A"

    numeric_value = float(
        numeric_value
    )

    if numeric_value < 48:
        return f"{numeric_value:.1f} hrs"

    return f"{numeric_value / 24:.1f} days"


def safe_percentage(
    numerator,
    denominator
):
    """
    Calculate a percentage safely.

    Returns zero when the denominator is missing, zero, or negative.
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


def get_top_value(
    data,
    column
):
    """
    Return the most frequent non-null value and its record count.
    """
    if (
        data is None
        or data.empty
        or column not in data.columns
    ):
        return "N/A", 0

    counts = (
        data[column]
        .dropna()
        .value_counts()
    )

    if counts.empty:
        return "N/A", 0

    return (
        counts.index[0],
        int(
            counts.iloc[0]
        )
    )


def get_metric_definition(metric_key):
    """
    Return the full definition dictionary for a metric.

    Unknown keys return a safe generic definition.
    """
    if metric_key in METRIC_DEFINITIONS:
        return METRIC_DEFINITIONS[
            metric_key
        ].copy()

    readable_label = str(
        metric_key
    ).replace(
        "_",
        " "
    ).title()

    return {
        "label": readable_label,
        "definition": (
            "A calculated dashboard metric based on the current "
            "filtered dataset."
        ),
        "formula": (
            "Refer to the section-specific chart or metric logic."
        )
    }


def get_metric_help(metric_key):
    """
    Return a combined tooltip explanation for a metric.
    """
    metric_definition = get_metric_definition(
        metric_key
    )

    return (
        f"{metric_definition['definition']} "
        f"Formula: {metric_definition['formula']}"
    )


def get_metric_label(metric_key):
    """
    Return the standardized display label for a metric.
    """
    return get_metric_definition(
        metric_key
    )["label"]