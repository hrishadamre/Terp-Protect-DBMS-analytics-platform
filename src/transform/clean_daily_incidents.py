"""
clean_daily_incidents.py

Purpose:
Clean and standardize UMPD Daily Crime and Incident Log records collected from public monthly webpages.

Current Scope:
- Source: UMPD Daily Crime and Incident Logs
- Year: 2025
- Input: data/raw/daily_incident_logs_2025.csv
- Output: data/processed/clean_daily_incidents_2025.csv
- Summary Report: reports/daily_incident_cleaning_summary_2025.md

Role in Pipeline:
This script belongs to the transform stage. It converts raw scraped fields into structured,
analysis-ready columns for database loading, SQL analysis, dashboards, and future modeling.
"""

from pathlib import Path
from datetime import datetime
import re
import pandas as pd
import numpy as np


RAW_INPUT_PATH = Path("data/raw/daily_incident_logs_2025.csv")
CLEAN_OUTPUT_PATH = Path("data/processed/clean_daily_incidents_2025.csv")
SUMMARY_OUTPUT_PATH = Path("reports/daily_incident_cleaning_summary_2025.md")

PROJECT_YEAR = 2025


def clean_text(value):
    """Standardize spacing and handle missing text values."""
    if pd.isna(value):
        return np.nan

    value = str(value).strip()
    value = re.sub(r"\s+", " ", value)

    if value == "":
        return np.nan

    return value


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

    return pd.to_datetime(value, format="%m/%d/%Y %H:%M:%S", errors="coerce")


def parse_reported_datetime(value):
    """Parse the raw reported datetime field."""
    value = clean_text(value)

    if pd.isna(value):
        return pd.NaT

    value = value.replace(" - ", " ")

    return pd.to_datetime(value, format="%m/%d/%Y %H:%M", errors="coerce")


def assign_semester_period(month):
    """Assign a broad academic period based on the incident month."""
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
    """Clean the raw crime type text."""
    value = clean_text(value)

    if pd.isna(value):
        return "Unknown"

    return value.title()


def assign_crime_group(crime_type):
    """Map detailed crime types into broader analytical groups."""
    value = clean_text(crime_type)

    if pd.isna(value):
        return "Unknown"

    value_lower = value.lower()

    if any(keyword in value_lower for keyword in ["dwi", "dui", "driving while impaired"]):
        return "DUI / Traffic Alcohol"

    if any(keyword in value_lower for keyword in ["theft", "larceny", "stolen", "shoplifting"]):
        return "Theft / Property"

    if any(keyword in value_lower for keyword in ["assault", "fight", "battery"]):
        return "Assault / Violence"

    if any(keyword in value_lower for keyword in ["burglary", "robbery", "breaking"]):
        return "Burglary / Robbery"

    if any(keyword in value_lower for keyword in ["cds", "drug", "narcotic", "marijuana", "controlled"]):
        return "Drug / CDS"

    if any(keyword in value_lower for keyword in ["sex", "sexual", "rape"]):
        return "Sex Offense"

    if any(keyword in value_lower for keyword in ["traffic", "vehicle", "accident", "crash", "hit and run"]):
        return "Traffic / Vehicle"

    if any(keyword in value_lower for keyword in ["disorderly", "disturbance", "trespass", "trespassing"]):
        return "Public Order"

    if any(keyword in value_lower for keyword in ["fraud", "identity", "forgery", "scam"]):
        return "Fraud / Identity"

    if any(keyword in value_lower for keyword in ["property damage", "malicious destruction", "vandalism"]):
        return "Property Damage"

    if any(keyword in value_lower for keyword in ["assist", "suspicious", "check", "information"]):
        return "Service / Assistance"

    return "Other"


def standardize_disposition(value):
    """Clean the raw disposition text."""
    value = clean_text(value)

    if pd.isna(value):
        return "Unknown"

    return value.title()


def assign_disposition_group(disposition):
    """Map detailed dispositions into broader outcome groups."""
    value = clean_text(disposition)

    if pd.isna(value):
        return "Unknown"

    value_lower = value.lower()

    if "arrest" in value_lower:
        return "Arrest"

    if any(keyword in value_lower for keyword in ["cbe", "closed", "cleared", "exceptionally cleared"]):
        return "Closed / Cleared"

    if any(keyword in value_lower for keyword in ["pending", "active", "open", "investigation"]):
        return "Pending / Active"

    if "unfounded" in value_lower:
        return "Unfounded"

    if any(keyword in value_lower for keyword in ["referred", "referral", "judicial"]):
        return "Referred"

    if any(keyword in value_lower for keyword in ["inactive", "suspended"]):
        return "Inactive / Suspended"

    return "Other"


def standardize_location(value):
    """Clean the raw location text."""
    value = clean_text(value)

    if pd.isna(value):
        return "Unknown"

    return value.title()


def assign_location_group(location):
    """Map detailed locations into broader location groups."""
    value = clean_text(location)

    if pd.isna(value):
        return "Unknown"

    value_lower = value.lower()

    if any(keyword in value_lower for keyword in ["rd", "road", "ave", "blvd", "street", "st ", "drive", "dr ", "lane"]):
        return "Roadway / Street"

    if any(keyword in value_lower for keyword in ["parking", "garage", "lot"]):
        return "Parking Area"

    if any(keyword in value_lower for keyword in ["hall", "dorm", "residence", "commons", "apartment"]):
        return "Residence / Housing"

    if any(keyword in value_lower for keyword in ["library", "center", "building", "school", "college", "lab"]):
        return "Academic / Campus Building"

    if any(keyword in value_lower for keyword in ["stadium", "field", "recreation", "gym", "arena"]):
        return "Athletic / Recreation"

    if any(keyword in value_lower for keyword in ["fraternity", "sorority", "greek"]):
        return "Greek Life"

    if any(keyword in value_lower for keyword in ["unknown", "n/a", "not available"]):
        return "Unknown"

    return "Other Campus / Nearby Area"


def calculate_reporting_delay_hours(occurred_datetime, reported_datetime):
    """Calculate reporting delay in hours."""
    if pd.isna(occurred_datetime) or pd.isna(reported_datetime):
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


def build_clean_dataset(df):
    """Apply all cleaning and feature engineering steps."""
    clean_df = df.copy()

    clean_df = clean_df.drop_duplicates().reset_index(drop=True)

    clean_df["incident_id"] = [
        f"INC{PROJECT_YEAR}_{str(index + 1).zfill(6)}"
        for index in range(len(clean_df))
    ]

    clean_df["case_number"] = clean_df["case_number"].apply(standardize_case_number)

    clean_df["occurred_datetime"] = clean_df["occurred_datetime_raw"].apply(parse_occurred_datetime)
    clean_df["reported_datetime"] = clean_df["reported_datetime_raw"].apply(parse_reported_datetime)

    clean_df["report_delay_hours"] = clean_df.apply(
        lambda row: calculate_reporting_delay_hours(
            row["occurred_datetime"],
            row["reported_datetime"]
        ),
        axis=1
    )

    clean_df["report_delay_days"] = (clean_df["report_delay_hours"] / 24).round(2)
    clean_df["delay_bucket"] = clean_df["report_delay_hours"].apply(assign_delay_bucket)

    clean_df["crime_type"] = clean_df["crime_type_raw"].apply(standardize_crime_type)
    clean_df["crime_group"] = clean_df["crime_type"].apply(assign_crime_group)

    clean_df["disposition"] = clean_df["disposition_raw"].apply(standardize_disposition)
    clean_df["disposition_group"] = clean_df["disposition"].apply(assign_disposition_group)

    clean_df["location_raw"] = clean_df["location_raw"].apply(standardize_location)
    clean_df["location_group"] = clean_df["location_raw"].apply(assign_location_group)

    clean_df["year"] = clean_df["occurred_datetime"].dt.year
    clean_df["month"] = clean_df["occurred_datetime"].dt.month
    clean_df["month_name"] = clean_df["occurred_datetime"].dt.month_name()
    clean_df["weekday"] = clean_df["occurred_datetime"].dt.day_name()
    clean_df["hour"] = clean_df["occurred_datetime"].dt.hour
    clean_df["is_weekend"] = clean_df["weekday"].isin(["Saturday", "Sunday"])
    clean_df["semester_period"] = clean_df["month"].apply(assign_semester_period)

    clean_df["source_type"] = "Daily Crime and Incident Log"

    clean_df["has_valid_case_number"] = clean_df["case_number"].notna()
    clean_df["has_valid_occurred_datetime"] = clean_df["occurred_datetime"].notna()
    clean_df["has_valid_reported_datetime"] = clean_df["reported_datetime"].notna()
    clean_df["has_valid_reporting_delay"] = clean_df["report_delay_hours"].notna()

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
    """Create a simple markdown summary of the cleaning output."""
    summary_lines = []

    summary_lines.append("# Daily Incident Log Cleaning Summary")
    summary_lines.append("")
    summary_lines.append(f"Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary_lines.append("")
    summary_lines.append("## Input and Output")
    summary_lines.append("")
    summary_lines.append(f"- Raw input file: `{RAW_INPUT_PATH}`")
    summary_lines.append(f"- Clean output file: `{CLEAN_OUTPUT_PATH}`")
    summary_lines.append(f"- Raw records: {len(raw_df):,}")
    summary_lines.append(f"- Clean records: {len(clean_df):,}")
    summary_lines.append("")
    summary_lines.append("## Data Quality Checks")
    summary_lines.append("")
    summary_lines.append(f"- Valid case numbers: {clean_df['has_valid_case_number'].sum():,}")
    summary_lines.append(f"- Valid occurred datetimes: {clean_df['has_valid_occurred_datetime'].sum():,}")
    summary_lines.append(f"- Valid reported datetimes: {clean_df['has_valid_reported_datetime'].sum():,}")
    summary_lines.append(f"- Valid reporting delays: {clean_df['has_valid_reporting_delay'].sum():,}")
    summary_lines.append("")
    summary_lines.append("## Top Crime Groups")
    summary_lines.append("")

    top_crime_groups = clean_df["crime_group"].value_counts().head(10)

    for group, count in top_crime_groups.items():
        summary_lines.append(f"- {group}: {count:,}")

    summary_lines.append("")
    summary_lines.append("## Top Disposition Groups")
    summary_lines.append("")

    top_disposition_groups = clean_df["disposition_group"].value_counts().head(10)

    for group, count in top_disposition_groups.items():
        summary_lines.append(f"- {group}: {count:,}")

    summary_lines.append("")
    summary_lines.append("## Top Location Groups")
    summary_lines.append("")

    top_location_groups = clean_df["location_group"].value_counts().head(10)

    for group, count in top_location_groups.items():
        summary_lines.append(f"- {group}: {count:,}")

    return "\n".join(summary_lines)


def main():
    """Run the full cleaning process."""
    if not RAW_INPUT_PATH.exists():
        raise FileNotFoundError(f"Raw input file not found: {RAW_INPUT_PATH}")

    print(f"Reading raw data from {RAW_INPUT_PATH}")

    raw_df = pd.read_csv(RAW_INPUT_PATH)

    print(f"Raw records loaded: {len(raw_df):,}")

    clean_df = build_clean_dataset(raw_df)

    CLEAN_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    clean_df.to_csv(CLEAN_OUTPUT_PATH, index=False)

    summary_text = create_cleaning_summary(raw_df, clean_df)
    SUMMARY_OUTPUT_PATH.write_text(summary_text)

    print(f"Clean records saved to {CLEAN_OUTPUT_PATH}")
    print(f"Cleaning summary saved to {SUMMARY_OUTPUT_PATH}")
    print("")
    print("Clean dataset preview:")
    print(clean_df.head())
    print("")
    print("Clean dataset shape:")
    print(clean_df.shape)


if __name__ == "__main__":
    main()