"""
clean_arrest_logs.py

Purpose:
Clean and standardize raw UMPD Arrest Log records
for the years 2023, 2024, and 2025.

Current Scope:
- Source: UMPD Arrest Logs
- Years: 2023 through 2025
- Input: data/raw/arrest_logs_2023_2025.csv
- Output: data/processed/clean_arrest_logs_2023_2025.csv
- Summary Report: reports/arrest_log_cleaning_summary_2023_2025.md

Role in Pipeline:
This script belongs to the transform stage. It prepares arrest records
for database loading, charge analysis, and incident-to-arrest matching
using UMPD case numbers.
"""

from pathlib import Path
import re

import pandas as pd


INPUT_PATH = Path(
    "data/raw/arrest_logs_2023_2025.csv"
)

OUTPUT_PATH = Path(
    "data/processed/clean_arrest_logs_2023_2025.csv"
)

REPORT_PATH = Path(
    "reports/arrest_log_cleaning_summary_2023_2025.md"
)


def clean_text(value):
    """Clean spacing and handle missing values."""
    if pd.isna(value):
        return ""

    value = str(value).strip()
    value = re.sub(r"\s+", " ", value)

    return value


def standardize_case_number(value):
    """Standardize UMPD case number text."""
    return clean_text(value).upper()


def parse_arrested_datetime(value):
    """Convert the raw arrest date and time into a datetime value."""
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
    """Standardize race values from the arrest log."""
    value = clean_text(value)

    if not value:
        return "Unknown"

    race_mapping = {
        "asian/pacific islander": "Asian",
        "hawaiian/other pacific islander":
            "Native Hawaiian/Pacific Islander",
        "native hawaiian/pacific islander":
            "Native Hawaiian/Pacific Islander",
        "american indian/alaskan":
            "American Indian/Alaskan"
    }

    return race_mapping.get(
        value.lower(),
        value.title()
    )


def standardize_sex(value):
    """Standardize sex values from the arrest log."""
    value = clean_text(value)

    if not value:
        return "Unknown"

    return value.title()


def recover_demographics_from_charge(row):
    """
    Recover race and sex when they were included
    at the beginning of the charge text.
    """
    race = clean_text(row["race_raw"])
    sex = clean_text(row["sex_raw"])
    charge = clean_text(row["arrested_charge_raw"])

    if race and sex:
        return pd.Series(
            [race, sex, charge]
        )

    race_prefixes = {
        "Asian/Pacific Islander": "Asian",
        "Hawaiian/Other Pacific Islander":
            "Native Hawaiian/Pacific Islander",
        "Native Hawaiian/Pacific Islander":
            "Native Hawaiian/Pacific Islander",
        "American Indian/Alaskan":
            "American Indian/Alaskan",
        "Asian": "Asian",
        "Black": "Black",
        "White": "White"
    }

    sex_values = [
        "Male",
        "Female",
        "Unknown"
    ]

    for raw_race, standard_race in race_prefixes.items():
        for possible_sex in sex_values:
            prefix = f"{raw_race} {possible_sex}"

            if charge.lower().startswith(prefix.lower()):
                cleaned_charge = clean_text(
                    charge[len(prefix):]
                )

                return pd.Series(
                    [
                        standard_race,
                        possible_sex,
                        cleaned_charge
                    ]
                )

    return pd.Series(
        [race, sex, charge]
    )


def clean_charge_text(value):
    """Clean arrested charge text."""
    return clean_text(value)


def assign_charge_category(charge_text):
    """
    Assign one broad primary category based on the charge text.

    The first matching category is used when one record
    contains multiple charges.
    """
    text = clean_text(charge_text).lower()

    if not text:
        return "Unknown"

    if any(
        keyword in text
        for keyword in [
            "suspicion/no charges",
            "released without charges"
        ]
    ):
        return "No Charge / Suspicion"

    if any(
        keyword in text
        for keyword in [
            "dui",
            "dwi",
            "while impaired",
            "under the influence of alcohol",
            "alcohol per se",
            "drug(s) and alcohol"
        ]
    ):
        return "DUI / Impaired Driving"

    if any(
        keyword in text
        for keyword in [
            "sex offense",
            "sexual offense",
            "indecent exposure",
            "peeping tom",
            "prostitution",
            "prurient intent",
            "intimate/sex image",
            "rape"
        ]
    ):
        return "Sex Offense"

    if any(
        keyword in text
        for keyword in [
            "weapon",
            "firearm",
            "handgun",
            "hangun",
            "knife",
            "deadly weapon"
        ]
    ):
        return "Weapon-Related"

    if any(
        keyword in text
        for keyword in [
            "burglary",
            "robbery",
            "breaking and entering",
            "unlawful entry"
        ]
    ):
        return "Burglary / Robbery"

    if any(
        keyword in text
        for keyword in [
            "theft",
            "stolen",
            "shoplifting",
            "unlawful taking",
            "unauth removal",
            "unauthorized removal",
            "grocery cart removal"
        ]
    ):
        return "Theft / Property"

    if any(
        keyword in text
        for keyword in [
            "malicious destruction",
            "property damage",
            "damage to property",
            "vandalism"
        ]
    ):
        return "Property Damage"

    if any(
        keyword in text
        for keyword in [
            "assault",
            "battery",
            "fight",
            "violence"
        ]
    ):
        return "Assault / Violence"

    if any(
        keyword in text
        for keyword in [
            "cds",
            "drug",
            "marijuana",
            "cannabis",
            "paraphernalia",
            "controlled dangerous substance",
            "narcotic"
        ]
    ):
        return "Drug / CDS"

    if any(
        keyword in text
        for keyword in [
            "credit card",
            "fraud",
            "identity",
            "forgery",
            "false statement",
            "false identification",
            "false id",
            "counterfeit",
            "extort",
            "illegal access"
        ]
    ):
        return "Fraud / Identity"

    if any(
        keyword in text
        for keyword in [
            "open alcoholic beverage",
            "open container",
            "underage possession",
            "alcoholic beverage",
            "furnishing alcohol",
            "intoxicated public"
        ]
    ):
        return "Alcohol / Public Consumption"

    if any(
        keyword in text
        for keyword in [
            "traffic",
            "license",
            "vehicle",
            "driving",
            "motor vehicle",
            "driver",
            "reckless driving",
            "negligent driving",
            "stop sign"
        ]
    ):
        return "Traffic / Vehicle"

    if any(
        keyword in text
        for keyword in [
            "disorderly",
            "trespass",
            "disturb",
            "resist",
            "obstruct",
            "rogue and vagabond",
            "urinating",
            "defecating",
            "litter",
            "hinder passage",
            "school molest",
            "harass",
            "hate item"
        ]
    ):
        return "Public Order"

    return "Other"


def flag_alcohol_related(charge_text):
    """Flag records containing alcohol-related charges."""
    text = clean_text(charge_text).lower()

    keywords = [
        "alcohol",
        "alcoholic beverage",
        "open container",
        "dui",
        "dwi",
        "impaired by alcohol",
        "under the influence of alcohol",
        "intoxicated public"
    ]

    return int(
        any(keyword in text for keyword in keywords)
    )


def flag_drug_related(charge_text):
    """Flag records containing drug-related charges."""
    text = clean_text(charge_text).lower()

    keywords = [
        "cds",
        "drug",
        "marijuana",
        "cannabis",
        "paraphernalia",
        "controlled dangerous substance",
        "narcotic"
    ]

    return int(
        any(keyword in text for keyword in keywords)
    )


def flag_theft_related(charge_text):
    """Flag records containing theft-related charges."""
    text = clean_text(charge_text).lower()

    keywords = [
        "theft",
        "stolen",
        "shoplifting",
        "unlawful taking",
        "unauth removal",
        "unauthorized removal",
        "grocery cart removal"
    ]

    return int(
        any(keyword in text for keyword in keywords)
    )


def add_arrest_ids(data):
    """
    Create a unique arrest ID using each record's source year.

    Examples:
    ARR2023_000001
    ARR2024_000001
    ARR2025_000001
    """
    data["record_number"] = (
        data.groupby("source_year").cumcount() + 1
    )

    data["arrest_id"] = (
        "ARR"
        + data["source_year"].astype("Int64").astype(str)
        + "_"
        + data["record_number"]
        .astype(str)
        .str.zfill(6)
    )

    return data.drop(
        columns=["record_number"]
    )


def create_clean_arrest_data(raw_data):
    """Create the cleaned multi-year arrest dataset."""
    data = raw_data.copy()

    for column in data.columns:
        data[column] = data[column].apply(
            clean_text
        )

    duplicate_columns = [
        "source_year",
        "arrest_number",
        "arrested_datetime_raw",
        "case_number",
        "arrested_charge_raw"
    ]

    data = (
        data
        .drop_duplicates(subset=duplicate_columns)
        .reset_index(drop=True)
    )

    data["source_year"] = pd.to_numeric(
        data["source_year"],
        errors="coerce"
    ).astype("Int64")

    data[
        [
            "race_raw",
            "sex_raw",
            "arrested_charge_raw"
        ]
    ] = data.apply(
        recover_demographics_from_charge,
        axis=1
    )

    data["arrest_number"] = (
        data["arrest_number"]
        .apply(clean_text)
    )

    data["case_number"] = (
        data["case_number"]
        .apply(standardize_case_number)
    )

    data["arrested_datetime"] = (
        data["arrested_datetime_raw"]
        .apply(parse_arrested_datetime)
    )

    data = data.sort_values(
        by=[
            "source_year",
            "arrested_datetime",
            "arrest_number",
            "case_number"
        ]
    ).reset_index(drop=True)

    data = add_arrest_ids(data)

    data["arrested_date"] = (
        data["arrested_datetime"].dt.date
    )

    data["arrested_year"] = (
        data["arrested_datetime"].dt.year
    )

    data["arrested_month"] = (
        data["arrested_datetime"].dt.month
    )

    data["arrested_month_name"] = (
        data["arrested_datetime"].dt.month_name()
    )

    data["arrested_weekday"] = (
        data["arrested_datetime"].dt.day_name()
    )

    data["arrested_hour"] = (
        data["arrested_datetime"].dt.hour
    )

    data["race"] = (
        data["race_raw"]
        .apply(standardize_race)
    )

    data["sex"] = (
        data["sex_raw"]
        .apply(standardize_sex)
    )

    data["age"] = pd.to_numeric(
        data["age_raw"],
        errors="coerce"
    )

    data["arrested_charge"] = (
        data["arrested_charge_raw"]
        .apply(clean_charge_text)
    )

    data["charge_category"] = (
        data["arrested_charge"]
        .apply(assign_charge_category)
    )

    data["is_alcohol_related"] = (
        data["arrested_charge"]
        .apply(flag_alcohol_related)
    )

    data["is_drug_related"] = (
        data["arrested_charge"]
        .apply(flag_drug_related)
    )

    data["is_theft_related"] = (
        data["arrested_charge"]
        .apply(flag_theft_related)
    )

    data["has_valid_arrest_number"] = (
        data["arrest_number"]
        .ne("")
        .astype(int)
    )

    data["has_valid_case_number"] = (
        data["case_number"]
        .str.match(r"^\d{4}-\d{8}$")
        .fillna(False)
        .astype(int)
    )

    data["has_valid_arrested_datetime"] = (
        data["arrested_datetime"]
        .notna()
        .astype(int)
    )

    data["has_charge_text"] = (
        data["arrested_charge"]
        .ne("")
        .astype(int)
    )

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
    """Create a markdown summary for the cleaned arrest data."""
    total_records = len(clean_data)
    records_with_age = clean_data["age"].notna().sum()
    unknown_race = clean_data["race"].eq("Unknown").sum()
    unknown_sex = clean_data["sex"].eq("Unknown").sum()

    summary_lines = [
        "# Arrest Log Cleaning Summary 2023-2025",
        "",
        "## Overview",
        f"- Total arrest records cleaned: {total_records:,}",
        (
            "- Records with valid arrest number: "
            f"{clean_data['has_valid_arrest_number'].sum():,}"
        ),
        (
            "- Records with valid case number: "
            f"{clean_data['has_valid_case_number'].sum():,}"
        ),
        (
            "- Records with valid arrested datetime: "
            f"{clean_data['has_valid_arrested_datetime'].sum():,}"
        ),
        (
            "- Records with charge text: "
            f"{clean_data['has_charge_text'].sum():,}"
        ),
        f"- Records with age available: {records_with_age:,}",
        f"- Records with unknown race: {unknown_race:,}",
        f"- Records with unknown sex: {unknown_sex:,}",
        "",
        "## Arrest Records by Year",
        clean_data["arrested_year"]
        .value_counts()
        .sort_index()
        .to_markdown(),
        "",
        "## Charge Category Counts",
        clean_data["charge_category"]
        .value_counts()
        .to_markdown(),
        "",
        "## Race Counts",
        clean_data["race"]
        .value_counts()
        .to_markdown(),
        "",
        "## Sex Counts",
        clean_data["sex"]
        .value_counts()
        .to_markdown(),
        "",
        "## Monthly Arrest Counts",
        clean_data["arrested_month_name"]
        .value_counts()
        .to_markdown(),
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
        raise FileNotFoundError(
            f"Input file not found: {INPUT_PATH}"
        )

    raw_data = pd.read_csv(
        INPUT_PATH
    )

    print(
        f"Loaded raw arrest records: {len(raw_data):,}"
    )

    clean_data = create_clean_arrest_data(
        raw_data
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    clean_data.to_csv(
        OUTPUT_PATH,
        index=False
    )

    create_cleaning_summary(
        clean_data
    )

    print(
        f"Saved clean arrest records to {OUTPUT_PATH}"
    )

    print(
        f"Saved cleaning summary to {REPORT_PATH}"
    )

    print("")
    print("Arrest records by year:")

    print(
        clean_data["arrested_year"]
        .value_counts()
        .sort_index()
    )

    print("")
    print(
        f"Clean dataset shape: {clean_data.shape}"
    )


if __name__ == "__main__":
    main()