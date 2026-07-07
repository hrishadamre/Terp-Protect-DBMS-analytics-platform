"""
clean_arrest_logs.py

Purpose:
Clean and standardize raw UMPD Arrest Log records collected from the public arrest ledger.

Current Scope:
- Source: UMPD Arrest Logs
- Year: 2025
- Input: data/raw/arrest_logs_2025.csv
- Output: data/processed/clean_arrest_logs_2025.csv

Role in Pipeline:
This script belongs to the transform stage. It prepares arrest records for database loading,
charge analysis, and future incident-to-arrest matching using UMPD case numbers.
"""

from pathlib import Path
import re

import pandas as pd


YEAR = 2025

INPUT_PATH = Path(f"data/raw/arrest_logs_{YEAR}.csv")
OUTPUT_PATH = Path(f"data/processed/clean_arrest_logs_{YEAR}.csv")
REPORT_PATH = Path(f"reports/arrest_log_cleaning_summary_{YEAR}.md")


def clean_text(value):
    """Clean spacing and handle missing values."""
    if pd.isna(value):
        return ""

    value = str(value).strip()
    value = re.sub(r"\s+", " ", value)

    return value


def standardize_case_number(value):
    """Standardize UMPD case number text."""
    value = clean_text(value)

    return value


def parse_arrested_datetime(value):
    """Parse arrested date and time."""
    value = clean_text(value)

    if not value:
        return pd.NaT

    value = value.replace(" - ", " ")

    return pd.to_datetime(
        value,
        format="%m/%d/%Y %H:%M",
        errors="coerce"
    )


def standardize_race(value):
    """Standardize race field from raw arrest log."""
    value = clean_text(value)

    if not value:
        return "Unknown"

    return value.title()


def standardize_sex(value):
    """Standardize sex field from raw arrest log."""
    value = clean_text(value)

    if not value:
        return "Unknown"

    return value.title()


def clean_charge_text(value):
    """Clean arrested charge text."""
    value = clean_text(value)

    return value


def assign_charge_category(charge_text):
    """Assign a broad charge category based on arrested charge text."""
    text = clean_text(charge_text).lower()

    if not text:
        return "Unknown"

    if any(keyword in text for keyword in ["dui", "dwi", "impaired", "influence of alcohol", "alcohol per se"]):
        return "DUI / Alcohol-Related Driving"

    if any(keyword in text for keyword in ["theft", "stolen", "shoplifting", "unlawful taking"]):
        return "Theft / Property"

    if any(keyword in text for keyword in ["assault", "battery", "fight", "violence"]):
        return "Assault / Violence"

    if any(keyword in text for keyword in ["cds", "drug", "marijuana", "paraphernalia", "controlled dangerous substance"]):
        return "Drug / CDS"

    if any(keyword in text for keyword in ["burglary", "robbery", "breaking"]):
        return "Burglary / Robbery"

    if any(keyword in text for keyword in ["fraud", "identity", "forgery", "false"]):
        return "Fraud / Identity"

    if any(keyword in text for keyword in ["traffic", "license", "vehicle", "driving", "motor vehicle"]):
        return "Traffic / Vehicle"

    if any(keyword in text for keyword in ["disorderly", "trespass", "disturbance", "resist", "obstruct"]):
        return "Public Order"

    if any(keyword in text for keyword in ["weapon", "firearm", "handgun", "knife"]):
        return "Weapon-Related"

    return "Other"


def flag_alcohol_related(charge_text):
    """Flag alcohol-related charges."""
    text = clean_text(charge_text).lower()

    keywords = [
        "alcohol",
        "dui",
        "dwi",
        "impaired",
        "under the influence"
    ]

    return int(any(keyword in text for keyword in keywords))


def flag_drug_related(charge_text):
    """Flag drug-related charges."""
    text = clean_text(charge_text).lower()

    keywords = [
        "cds",
        "drug",
        "marijuana",
        "paraphernalia",
        "controlled dangerous substance"
    ]

    return int(any(keyword in text for keyword in keywords))


def flag_theft_related(charge_text):
    """Flag theft-related charges."""
    text = clean_text(charge_text).lower()

    keywords = [
        "theft",
        "stolen",
        "shoplifting",
        "unlawful taking"
    ]

    return int(any(keyword in text for keyword in keywords))


def create_clean_arrest_data(raw_data):
    """Create cleaned arrest dataset."""
    data = raw_data.copy()

    for column in data.columns:
        data[column] = data[column].apply(clean_text)

    data["arrest_id"] = [
        f"ARR{YEAR}_{str(index + 1).zfill(6)}"
        for index in range(len(data))
    ]

    data["arrest_number"] = data["arrest_number"].apply(clean_text)
    data["case_number"] = data["case_number"].apply(standardize_case_number)

    data["arrested_datetime"] = data["arrested_datetime_raw"].apply(
        parse_arrested_datetime
    )

    data["arrested_date"] = data["arrested_datetime"].dt.date
    data["arrested_year"] = data["arrested_datetime"].dt.year
    data["arrested_month"] = data["arrested_datetime"].dt.month
    data["arrested_month_name"] = data["arrested_datetime"].dt.month_name()
    data["arrested_weekday"] = data["arrested_datetime"].dt.day_name()
    data["arrested_hour"] = data["arrested_datetime"].dt.hour

    data["race"] = data["race_raw"].apply(standardize_race)
    data["sex"] = data["sex_raw"].apply(standardize_sex)

    data["age"] = pd.to_numeric(
        data["age_raw"],
        errors="coerce"
    )

    data["arrested_charge"] = data["arrested_charge_raw"].apply(
        clean_charge_text
    )

    data["charge_category"] = data["arrested_charge"].apply(
        assign_charge_category
    )

    data["is_alcohol_related"] = data["arrested_charge"].apply(
        flag_alcohol_related
    )

    data["is_drug_related"] = data["arrested_charge"].apply(
        flag_drug_related
    )

    data["is_theft_related"] = data["arrested_charge"].apply(
        flag_theft_related
    )

    data["has_valid_arrest_number"] = data["arrest_number"].ne("").astype(int)
    data["has_valid_case_number"] = data["case_number"].str.match(r"^\d{4}-\d{8}$").astype(int)
    data["has_valid_arrested_datetime"] = data["arrested_datetime"].notna().astype(int)
    data["has_charge_text"] = data["arrested_charge"].ne("").astype(int)

    final_columns = [
        "arrest_id",
        "arrest_number",
        "case_number",
        "arrested_datetime",
        "arrested_date",
        "arrested_year",
        "arrested_month",
        "arrested_month_name",
        "arrested_weekday",
        "arrested_hour",
        "age",
        "race",
        "sex",
        "arrested_charge",
        "charge_category",
        "is_alcohol_related",
        "is_drug_related",
        "is_theft_related",
        "source_year",
        "source_url",
        "scraped_at",
        "has_valid_arrest_number",
        "has_valid_case_number",
        "has_valid_arrested_datetime",
        "has_charge_text"
    ]

    return data[final_columns]


def create_cleaning_summary(clean_data):
    """Create markdown summary for cleaned arrest data."""
    total_records = len(clean_data)

    summary_lines = [
        f"# Arrest Log Cleaning Summary {YEAR}",
        "",
        "## Overview",
        f"- Total arrest records cleaned: {total_records:,}",
        f"- Records with valid arrest number: {int(clean_data['has_valid_arrest_number'].sum()):,}",
        f"- Records with valid case number: {int(clean_data['has_valid_case_number'].sum()):,}",
        f"- Records with valid arrested datetime: {int(clean_data['has_valid_arrested_datetime'].sum()):,}",
        f"- Records with charge text: {int(clean_data['has_charge_text'].sum()):,}",
        "",
        "## Charge Category Counts",
        clean_data["charge_category"].value_counts().to_markdown(),
        "",
        "## Race Counts",
        clean_data["race"].value_counts().to_markdown(),
        "",
        "## Sex Counts",
        clean_data["sex"].value_counts().to_markdown(),
        "",
        "## Monthly Arrest Counts",
        clean_data["arrested_month_name"].value_counts().to_markdown(),
        ""
    ]

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    REPORT_PATH.write_text(
        "\n".join(summary_lines),
        encoding="utf-8"
    )


def main():
    """Run the arrest log cleaning pipeline."""
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_PATH}")

    raw_data = pd.read_csv(INPUT_PATH)

    print(f"Loaded raw arrest records: {len(raw_data):,}")

    clean_data = create_clean_arrest_data(raw_data)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    clean_data.to_csv(
        OUTPUT_PATH,
        index=False
    )

    create_cleaning_summary(clean_data)

    print(f"Saved clean arrest records to {OUTPUT_PATH}")
    print(f"Saved cleaning summary to {REPORT_PATH}")
    print(f"Clean dataset shape: {clean_data.shape}")


if __name__ == "__main__":
    main()