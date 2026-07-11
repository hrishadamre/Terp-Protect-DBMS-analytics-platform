"""
clean_daily_incidents.py

Purpose:
Clean and standardize UMPD Daily Crime and Incident Log records
for the years 2023, 2024, and 2025.

Current Scope:
- Source: UMPD Daily Crime and Incident Logs
- Years: 2023 through 2025
- Input: data/raw/daily_incident_logs_2023_2025.csv
- Output: data/processed/clean_daily_incidents_2023_2025.csv
- Summary Report: reports/daily_incident_cleaning_summary_2023_2025.md

Role in Pipeline:
This script belongs to the transform stage. It converts raw scraped fields
into structured, analysis-ready columns for database loading, SQL analysis,
dashboards, and future modeling.
"""

from pathlib import Path
from datetime import datetime
import re

import numpy as np
import pandas as pd


RAW_INPUT_PATH = Path(
    "data/raw/daily_incident_logs_2023_2025.csv"
)

CLEAN_OUTPUT_PATH = Path(
    "data/processed/clean_daily_incidents_2023_2025.csv"
)

SUMMARY_OUTPUT_PATH = Path(
    "reports/daily_incident_cleaning_summary_2023_2025.md"
)


def clean_text(value):
    """Standardize spacing and handle missing text values."""
    if pd.isna(value):
        return np.nan

    value = str(value).strip()
    value = re.sub(r"\s+", " ", value)

    if value == "":
        return np.nan

    return value


def contains_any(text, keywords):
    """Return True when the text contains at least one keyword."""
    return any(keyword in text for keyword in keywords)


def standardize_case_number(value):
    """Standardize UMPD case numbers."""
    value = clean_text(value)

    if pd.isna(value):
        return np.nan

    return value.upper()


def parse_occurred_datetime(value):
    """Parse the raw occurred datetime field."""
    value = clean_text(value)

    if pd.isna(value):
        return pd.NaT

    return pd.to_datetime(
        value,
        format="%m/%d/%Y %H:%M:%S",
        errors="coerce"
    )


def parse_reported_datetime(value):
    """Parse the raw reported datetime field."""
    value = clean_text(value)

    if pd.isna(value):
        return pd.NaT

    value = value.replace(" - ", " ")

    return pd.to_datetime(
        value,
        format="%m/%d/%Y %H:%M",
        errors="coerce"
    )


def assign_semester_period(month):
    """Assign a broad academic period based on month."""
    if pd.isna(month):
        return "Unknown"

    month = int(month)

    if month == 1:
        return "Winter Break"

    if month in [2, 3, 4, 5]:
        return "Spring Semester"

    if month in [6, 7, 8]:
        return "Summer"

    if month in [9, 10, 11, 12]:
        return "Fall Semester"

    return "Unknown"


def standardize_crime_type(value):
    """Clean the crime type while preserving the source wording."""
    value = clean_text(value)

    if pd.isna(value):
        return "Unknown"

    return value


def assign_crime_group(crime_type):
    """Map detailed incident types into broader analytical groups."""
    value = clean_text(crime_type)

    if pd.isna(value):
        return "Unknown"

    text = value.lower()

    if contains_any(
        text,
        [
            "dwi",
            "dui",
            "driving while impaired"
        ]
    ):
        return "DUI / Impaired Driving"

    if contains_any(
        text,
        [
            "sex offense",
            "rape",
            "indecent exposure",
            "peeping tom",
            "pornography",
            "obscene material",
            "title ix"
        ]
    ):
        return "Sex Offense / Title IX"

    if contains_any(
        text,
        [
            "weapon violation",
            "firearm",
            "handgun",
            "knife",
            "weapon"
        ]
    ):
        return "Weapon-Related"

    if contains_any(
        text,
        [
            "burglary",
            "robbery",
            "carjacking",
            "breaking and entering"
        ]
    ):
        return "Burglary / Robbery"

    if contains_any(
        text,
        [
            "theft",
            "larceny",
            "stolen motor vehicle",
            "stolen property",
            "shoplifting",
            "vehicle tampering"
        ]
    ):
        return "Theft / Property"

    if contains_any(
        text,
        [
            "lost property",
            "found/recovered property",
            "recovered stolen property",
            "recovered stolen motor vehicle"
        ]
    ):
        return "Lost / Recovered Property"

    if contains_any(
        text,
        [
            "vandalism",
            "damage to state property",
            "dept property damage",
            "damaged property",
            "property damage",
            "malicious destruction"
        ]
    ):
        return "Property Damage"

    if contains_any(
        text,
        [
            "assault",
            "domestic",
            "cutting",
            "stabbing",
            "reckless endangerment",
            "fight",
            "battery"
        ]
    ):
        return "Assault / Violence"

    if contains_any(
        text,
        [
            "harassment",
            "stalking",
            "threat assessment",
            "hate bias incident",
            "telephone/email misuse",
            "telephone/email",
            "extortion"
        ]
    ):
        return "Harassment / Threats"

    if contains_any(
        text,
        [
            "cds violation",
            "drug",
            "narcotic",
            "marijuana",
            "cannabis",
            "controlled dangerous substance",
            "overdose"
        ]
    ):
        return "Drug / CDS"

    if contains_any(
        text,
        [
            "alcohol violation"
        ]
    ):
        return "Alcohol Violation"

    if contains_any(
        text,
        [
            "fraud",
            "identity theft",
            "forgery",
            "embezzlement",
            "false report",
            "false statement",
            "scam"
        ]
    ):
        return "Fraud / Financial Crime"

    if contains_any(
        text,
        [
            "traffic offense",
            "traffic arrest",
            "accident",
            "pedestrian struck",
            "hit and run"
        ]
    ):
        return "Traffic / Vehicle"

    if contains_any(
        text,
        [
            "disorderly conduct",
            "trespassing",
            "resisting arrest",
            "noise complaint",
            "juvenile offense",
            "disturbance"
        ]
    ):
        return "Public Order"

    if contains_any(
        text,
        [
            "injured/sick person",
            "injured officer",
            "check on the welfare",
            "emergency petition",
            "death investigation",
            "suicide",
            "missing person",
            "runaway"
        ]
    ):
        return "Medical / Welfare"

    if contains_any(
        text,
        [
            "fire",
            "hazardous condition",
            "alarm"
        ]
    ):
        return "Fire / Hazard"

    if contains_any(
        text,
        [
            "assist other agency",
            "assist fire department",
            "police information",
            "other service call",
            "suspicious activity",
            "suspicious person",
            "animal complaint"
        ]
    ):
        return "Service / Assistance"

    if contains_any(
        text,
        [
            "warrant",
            "summons service"
        ]
    ):
        return "Warrant / Summons Service"

    if "other incident" in text:
        return "Other Incident"

    return "Other"


def standardize_disposition(value):
    """Clean disposition text while preserving the source wording."""
    value = clean_text(value)

    if pd.isna(value):
        return "Unknown"

    return value


def assign_disposition_group(disposition):
    """Map detailed dispositions into broader outcome groups."""
    value = clean_text(disposition)

    if pd.isna(value):
        return "Unknown"

    text = value.lower()

    if "arrest" in text:
        return "Arrest"

    if contains_any(
        text,
        [
            "cbe",
            "closed",
            "cleared",
            "exceptionally cleared"
        ]
    ):
        return "Closed / Cleared"

    if contains_any(
        text,
        [
            "investigation pending",
            "active/pending",
            "pending",
            "active",
            "open"
        ]
    ):
        return "Pending / Active"

    if "unfounded" in text:
        return "Unfounded"

    if contains_any(
        text,
        [
            "summons issued",
            "warrant issued"
        ]
    ):
        return "Summons / Warrant Issued"

    if contains_any(
        text,
        [
            "referred",
            "referral",
            "judicial"
        ]
    ):
        return "Referred"

    if contains_any(
        text,
        [
            "inactive",
            "suspended"
        ]
    ):
        return "Inactive / Suspended"

    return "Other"


def standardize_location(value):
    """Clean location text while preserving names and abbreviations."""
    value = clean_text(value)

    if pd.isna(value):
        return "Unknown"

    return value


def has_roadway_term(text):
    """Check for common roadway words using complete words."""
    roadway_pattern = (
        r"\b("
        r"road|rd|avenue|ave|boulevard|blvd|street|st|"
        r"drive|dr|lane|ln|court|ct|parkway|pkwy|"
        r"highway|hwy|route"
        r")\b"
    )

    return bool(
        re.search(
            roadway_pattern,
            text,
            flags=re.IGNORECASE
        )
    )


def assign_location_group(location):
    """Map detailed locations into broader location groups."""
    value = clean_text(location)

    if pd.isna(value):
        return "Unknown"

    text = value.lower()

    if contains_any(
        text,
        [
            "parking",
            "parking garage",
            "garage",
            "lot ",
            "lot,"
        ]
    ):
        return "Parking Area"

    if contains_any(
        text,
        [
            "hall",
            "dorm",
            "residence",
            "commons",
            "apartment",
            "fraternity",
            "sorority",
            "greek"
        ]
    ):
        return "Residence / Housing"

    if contains_any(
        text,
        [
            "stadium",
            "field",
            "recreation",
            "gym",
            "arena",
            "golf course",
            "tennis",
            "athletic"
        ]
    ):
        return "Athletic / Recreation"

    if contains_any(
        text,
        [
            "library",
            "center",
            "building",
            "school",
            "college",
            "laboratory",
            " lab",
            "classroom",
            "student union",
            "stamp",
            "chapel"
        ]
    ):
        return "Campus Building / Facility"

    if contains_any(
        text,
        [
            "police",
            "umpd",
            "umdps",
            "health center",
            "fire department"
        ]
    ):
        return "Campus Service / Administrative"

    if contains_any(
        text,
        [
            "unknown",
            "n/a",
            "not available"
        ]
    ):
        return "Unknown"

    if has_roadway_term(text):
        return "Roadway / Street"

    return "Other Campus / Nearby Area"


def calculate_reporting_delay_hours(
    occurred_datetime,
    reported_datetime
):
    """Calculate the reporting delay in hours."""
    if (
        pd.isna(occurred_datetime)
        or pd.isna(reported_datetime)
    ):
        return np.nan

    delay = reported_datetime - occurred_datetime
    delay_hours = delay.total_seconds() / 3600

    if delay_hours < 0:
        return np.nan

    return round(delay_hours, 2)


def assign_delay_bucket(delay_hours):
    """Group reporting delay into easy-to-read buckets."""
    if pd.isna(delay_hours):
        return "Unknown"

    if delay_hours <= 24:
        return "Same Day / Within 24 Hours"

    if delay_hours <= 72:
        return "1-3 Days"

    if delay_hours <= 168:
        return "4-7 Days"

    return "Over 7 Days"


def add_incident_ids(clean_df):
    """Create a unique incident ID within each source year."""
    clean_df["record_number"] = (
        clean_df.groupby("source_year").cumcount() + 1
    )

    clean_df["incident_id"] = (
        "INC"
        + clean_df["source_year"].astype("Int64").astype(str)
        + "_"
        + clean_df["record_number"]
        .astype(str)
        .str.zfill(6)
    )

    return clean_df.drop(
        columns=["record_number"]
    )


def build_clean_dataset(df):
    """Apply all cleaning and feature-engineering steps."""
    clean_df = df.copy()

    text_columns = [
        "case_number",
        "occurred_datetime_raw",
        "reported_datetime_raw",
        "crime_type_raw",
        "disposition_raw",
        "location_raw",
        "source_url",
        "scraped_at"
    ]

    for column in text_columns:
        clean_df[column] = clean_df[column].apply(
            clean_text
        )

    duplicate_columns = [
        "source_year",
        "source_month",
        "case_number",
        "occurred_datetime_raw",
        "reported_datetime_raw",
        "crime_type_raw",
        "disposition_raw",
        "location_raw"
    ]

    clean_df = (
        clean_df
        .drop_duplicates(subset=duplicate_columns)
        .reset_index(drop=True)
    )

    clean_df["source_year"] = pd.to_numeric(
        clean_df["source_year"],
        errors="coerce"
    ).astype("Int64")

    clean_df["source_month"] = pd.to_numeric(
        clean_df["source_month"],
        errors="coerce"
    ).astype("Int64")

    clean_df["case_number"] = (
        clean_df["case_number"]
        .apply(standardize_case_number)
    )

    clean_df["occurred_datetime"] = (
        clean_df["occurred_datetime_raw"]
        .apply(parse_occurred_datetime)
    )

    clean_df["reported_datetime"] = (
        clean_df["reported_datetime_raw"]
        .apply(parse_reported_datetime)
    )

    clean_df = clean_df.sort_values(
        by=[
            "source_year",
            "source_month",
            "occurred_datetime",
            "case_number"
        ]
    ).reset_index(drop=True)

    clean_df = add_incident_ids(
        clean_df
    )

    clean_df["report_delay_hours"] = clean_df.apply(
        lambda row: calculate_reporting_delay_hours(
            row["occurred_datetime"],
            row["reported_datetime"]
        ),
        axis=1
    )

    clean_df["report_delay_days"] = (
        clean_df["report_delay_hours"] / 24
    ).round(2)

    clean_df["delay_bucket"] = (
        clean_df["report_delay_hours"]
        .apply(assign_delay_bucket)
    )

    clean_df["crime_type"] = (
        clean_df["crime_type_raw"]
        .apply(standardize_crime_type)
    )

    clean_df["crime_group"] = (
        clean_df["crime_type"]
        .apply(assign_crime_group)
    )

    clean_df["disposition"] = (
        clean_df["disposition_raw"]
        .apply(standardize_disposition)
    )

    clean_df["disposition_group"] = (
        clean_df["disposition"]
        .apply(assign_disposition_group)
    )

    clean_df["location_raw"] = (
        clean_df["location_raw"]
        .apply(standardize_location)
    )

    clean_df["location_group"] = (
        clean_df["location_raw"]
        .apply(assign_location_group)
    )

    clean_df["year"] = (
        clean_df["occurred_datetime"].dt.year
    )

    clean_df["month"] = (
        clean_df["occurred_datetime"].dt.month
    )

    clean_df["month_name"] = (
        clean_df["occurred_datetime"].dt.month_name()
    )

    clean_df["weekday"] = (
        clean_df["occurred_datetime"].dt.day_name()
    )

    clean_df["hour"] = (
        clean_df["occurred_datetime"].dt.hour
    )

    clean_df["is_weekend"] = (
        clean_df["weekday"]
        .isin(["Saturday", "Sunday"])
        .astype(int)
    )

    clean_df["semester_period"] = (
        clean_df["month"]
        .apply(assign_semester_period)
    )

    clean_df["source_type"] = (
        "Daily Crime and Incident Log"
    )

    clean_df["has_valid_case_number"] = (
        clean_df["case_number"]
        .str.match(r"^\d{4}-\d{8}$")
        .fillna(False)
        .astype(int)
    )

    clean_df["has_valid_occurred_datetime"] = (
        clean_df["occurred_datetime"]
        .notna()
        .astype(int)
    )

    clean_df["has_valid_reported_datetime"] = (
        clean_df["reported_datetime"]
        .notna()
        .astype(int)
    )

    clean_df["has_valid_reporting_delay"] = (
        clean_df["report_delay_hours"]
        .notna()
        .astype(int)
    )

    final_columns = [
        "incident_id",
        "case_number",
        "occurred_datetime",
        "reported_datetime",
        "report_delay_hours",
        "report_delay_days",
        "delay_bucket",
        "crime_type",
        "crime_group",
        "disposition",
        "disposition_group",
        "location_raw",
        "location_group",
        "year",
        "month",
        "month_name",
        "weekday",
        "hour",
        "is_weekend",
        "semester_period",
        "source_year",
        "source_month",
        "source_type",
        "source_url",
        "scraped_at",
        "has_valid_case_number",
        "has_valid_occurred_datetime",
        "has_valid_reported_datetime",
        "has_valid_reporting_delay"
    ]

    return clean_df[final_columns]


def create_cleaning_summary(raw_df, clean_df):
    """Create a markdown summary of the cleaning output."""
    summary_lines = [
        "# Daily Incident Log Cleaning Summary 2023-2025",
        "",
        (
            "Generated At: "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ),
        "",
        "## Input and Output",
        "",
        f"- Raw input file: `{RAW_INPUT_PATH}`",
        f"- Clean output file: `{CLEAN_OUTPUT_PATH}`",
        f"- Raw records: {len(raw_df):,}",
        f"- Clean records: {len(clean_df):,}",
        "",
        "## Records by Source Year",
        ""
    ]

    source_year_counts = (
        clean_df["source_year"]
        .value_counts()
        .sort_index()
    )

    for year, count in source_year_counts.items():
        summary_lines.append(
            f"- {int(year)}: {count:,}"
        )

    summary_lines.extend(
        [
            "",
            "## Records by Occurred Year",
            ""
        ]
    )

    occurred_year_counts = (
        clean_df["year"]
        .value_counts()
        .sort_index()
    )

    for year, count in occurred_year_counts.items():
        summary_lines.append(
            f"- {int(year)}: {count:,}"
        )

    summary_lines.extend(
        [
            "",
            "## Data Quality Checks",
            "",
            (
                "- Valid case numbers: "
                f"{clean_df['has_valid_case_number'].sum():,}"
            ),
            (
                "- Valid occurred datetimes: "
                f"{clean_df['has_valid_occurred_datetime'].sum():,}"
            ),
            (
                "- Valid reported datetimes: "
                f"{clean_df['has_valid_reported_datetime'].sum():,}"
            ),
            (
                "- Valid reporting delays: "
                f"{clean_df['has_valid_reporting_delay'].sum():,}"
            ),
            "",
            "## Crime Group Counts",
            ""
        ]
    )

    for group, count in (
        clean_df["crime_group"]
        .value_counts()
        .items()
    ):
        summary_lines.append(
            f"- {group}: {count:,}"
        )

    summary_lines.extend(
        [
            "",
            "## Disposition Group Counts",
            ""
        ]
    )

    for group, count in (
        clean_df["disposition_group"]
        .value_counts()
        .items()
    ):
        summary_lines.append(
            f"- {group}: {count:,}"
        )

    summary_lines.extend(
        [
            "",
            "## Location Group Counts",
            ""
        ]
    )

    for group, count in (
        clean_df["location_group"]
        .value_counts()
        .items()
    ):
        summary_lines.append(
            f"- {group}: {count:,}"
        )

    return "\n".join(summary_lines)


def main():
    """Run the full incident cleaning process."""
    if not RAW_INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Raw input file not found: {RAW_INPUT_PATH}"
        )

    print(
        f"Reading raw data from {RAW_INPUT_PATH}"
    )

    raw_df = pd.read_csv(
        RAW_INPUT_PATH
    )

    print(
        f"Raw records loaded: {len(raw_df):,}"
    )

    clean_df = build_clean_dataset(
        raw_df
    )

    CLEAN_OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    SUMMARY_OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    clean_df.to_csv(
        CLEAN_OUTPUT_PATH,
        index=False
    )

    summary_text = create_cleaning_summary(
        raw_df,
        clean_df
    )

    SUMMARY_OUTPUT_PATH.write_text(
        summary_text,
        encoding="utf-8"
    )

    print(
        f"Clean records saved to {CLEAN_OUTPUT_PATH}"
    )

    print(
        f"Cleaning summary saved to {SUMMARY_OUTPUT_PATH}"
    )

    print("")
    print("Incident records by source year:")

    print(
        clean_df["source_year"]
        .value_counts()
        .sort_index()
    )

    print("")
    print(
        f"Clean dataset shape: {clean_df.shape}"
    )


if __name__ == "__main__":
    main()