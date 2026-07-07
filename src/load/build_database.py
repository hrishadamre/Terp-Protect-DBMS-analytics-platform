"""
build_database.py

Purpose:
Build the Terp Protect SQLite database and load cleaned incident and arrest records.

Current Scope:
- Daily Crime and Incident Logs: 2025
- Arrest Logs: 2025

Inputs:
- data/processed/clean_daily_incidents_2025.csv
- data/processed/clean_arrest_logs_2025.csv
- sql/01_schema.sql

Output:
- data/database/terp_protect.db

Role in Pipeline:
This script belongs to the load stage. It creates the relational database schema,
loads dimension tables, and loads fact tables for analysis and dashboarding.
"""

from pathlib import Path
import sqlite3

import pandas as pd


YEAR = 2025

DATABASE_PATH = Path("data/database/terp_protect.db")
SCHEMA_PATH = Path("sql/01_schema.sql")

INCIDENT_INPUT_PATH = Path(f"data/processed/clean_daily_incidents_{YEAR}.csv")
ARREST_INPUT_PATH = Path(f"data/processed/clean_arrest_logs_{YEAR}.csv")


def connect_database():
    """Create a SQLite database connection."""
    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(DATABASE_PATH)

    connection.execute("PRAGMA foreign_keys = ON;")

    return connection


def run_schema(connection):
    """Run the database schema SQL file."""
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_PATH}")

    schema_sql = SCHEMA_PATH.read_text(
        encoding="utf-8"
    )

    connection.executescript(schema_sql)

    connection.commit()


def load_clean_incident_data():
    """Load cleaned incident CSV."""
    if not INCIDENT_INPUT_PATH.exists():
        raise FileNotFoundError(f"Incident input file not found: {INCIDENT_INPUT_PATH}")

    data = pd.read_csv(INCIDENT_INPUT_PATH)

    data["occurred_datetime"] = pd.to_datetime(
        data["occurred_datetime"],
        errors="coerce"
    )

    data["reported_datetime"] = pd.to_datetime(
        data["reported_datetime"],
        errors="coerce"
    )

    return data


def load_clean_arrest_data():
    """Load cleaned arrest CSV."""
    if not ARREST_INPUT_PATH.exists():
        print(f"Arrest input file not found: {ARREST_INPUT_PATH}")
        print("Continuing with incident data only.")
        return pd.DataFrame()

    data = pd.read_csv(ARREST_INPUT_PATH)

    data["arrested_datetime"] = pd.to_datetime(
        data["arrested_datetime"],
        errors="coerce"
    )

    return data


def assign_semester_period(month):
    """Assign academic period based on month."""
    if month in [1]:
        return "Winter Break"

    if month in [2, 3, 4, 5]:
        return "Spring"

    if month in [6, 7, 8]:
        return "Summer"

    if month in [9, 10, 11, 12]:
        return "Fall"

    return "Unknown"


def assign_age_group(age):
    """Assign broad age group for arrest demographic analysis."""
    if pd.isna(age):
        return "Unknown"

    age = int(age)

    if age < 18:
        return "Under 18"

    if age <= 24:
        return "18-24"

    if age <= 34:
        return "25-34"

    if age <= 44:
        return "35-44"

    if age <= 54:
        return "45-54"

    return "55+"


def create_dim_date(incident_data, arrest_data):
    """Create date dimension from incident and arrest dates."""
    incident_dates = pd.concat(
        [
            incident_data["occurred_datetime"].dt.date,
            incident_data["reported_datetime"].dt.date
        ],
        ignore_index=True
    )

    date_series_list = [incident_dates]

    if not arrest_data.empty:
        arrest_dates = arrest_data["arrested_datetime"].dt.date
        date_series_list.append(arrest_dates)

    all_dates = pd.concat(
        date_series_list,
        ignore_index=True
    ).dropna().drop_duplicates()

    dim_date = pd.DataFrame(
        {
            "full_date": pd.to_datetime(all_dates)
        }
    )

    dim_date = dim_date.sort_values("full_date").reset_index(drop=True)

    dim_date["year"] = dim_date["full_date"].dt.year
    dim_date["quarter"] = dim_date["full_date"].dt.quarter
    dim_date["month"] = dim_date["full_date"].dt.month
    dim_date["month_name"] = dim_date["full_date"].dt.month_name()
    dim_date["day"] = dim_date["full_date"].dt.day
    dim_date["weekday"] = dim_date["full_date"].dt.day_name()
    dim_date["day_of_week_number"] = dim_date["full_date"].dt.dayofweek + 1
    dim_date["is_weekend"] = dim_date["weekday"].isin(["Saturday", "Sunday"]).astype(int)
    dim_date["semester_period"] = dim_date["month"].apply(assign_semester_period)

    dim_date.insert(
        0,
        "date_id",
        range(1, len(dim_date) + 1)
    )

    dim_date["full_date"] = dim_date["full_date"].dt.date.astype(str)

    return dim_date


def create_dim_crime_type(incident_data):
    """Create crime type dimension."""
    dim_crime_type = (
        incident_data[["crime_type", "crime_group", "source_type"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    dim_crime_type.insert(
        0,
        "crime_type_id",
        range(1, len(dim_crime_type) + 1)
    )

    return dim_crime_type


def create_dim_disposition(incident_data):
    """Create disposition dimension from incident disposition fields."""
    data = incident_data.copy()

    data["is_arrest_related"] = (
        data["disposition_group"]
        .fillna("")
        .str.lower()
        .str.contains("arrest")
        .astype(int)
    )

    data["is_pending"] = (
        data["disposition_group"]
        .fillna("")
        .str.lower()
        .str.contains("pending|active")
        .astype(int)
    )

    data["is_closed"] = (
        data["disposition_group"]
        .fillna("")
        .str.lower()
        .str.contains("closed|cleared")
        .astype(int)
    )

    dim_disposition = (
        data[
            [
                "disposition",
                "disposition_group",
                "is_arrest_related",
                "is_pending",
                "is_closed"
            ]
        ]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    dim_disposition.insert(
        0,
        "disposition_id",
        range(1, len(dim_disposition) + 1)
    )

    return dim_disposition


def create_dim_location(incident_data):
    """Create location dimension."""
    dim_location = (
        incident_data[["location_raw", "location_group"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    dim_location["jurisdiction_group"] = "Unknown"
    dim_location["is_on_campus"] = None

    dim_location.insert(
        0,
        "location_id",
        range(1, len(dim_location) + 1)
    )

    return dim_location


def create_dim_demographic(arrest_data):
    """Create demographic dimension from arrest data."""
    if arrest_data.empty:
        return pd.DataFrame(
            columns=[
                "demographic_id",
                "race",
                "sex",
                "age_group"
            ]
        )

    data = arrest_data.copy()

    data["age_group"] = data["age"].apply(assign_age_group)

    dim_demographic = (
        data[["race", "sex", "age_group"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    dim_demographic.insert(
        0,
        "demographic_id",
        range(1, len(dim_demographic) + 1)
    )

    return dim_demographic


def create_dim_charge_category(arrest_data):
    """Create charge category dimension from arrest data."""
    if arrest_data.empty:
        return pd.DataFrame(
            columns=[
                "charge_category_id",
                "charge_category",
                "is_alcohol_related",
                "is_drug_related",
                "is_theft_related"
            ]
        )

    dim_charge_category = (
        arrest_data[
            [
                "charge_category",
                "is_alcohol_related",
                "is_drug_related",
                "is_theft_related"
            ]
        ]
        .groupby("charge_category", as_index=False)
        .agg(
            {
                "is_alcohol_related": "max",
                "is_drug_related": "max",
                "is_theft_related": "max"
            }
        )
        .reset_index(drop=True)
    )

    dim_charge_category.insert(
        0,
        "charge_category_id",
        range(1, len(dim_charge_category) + 1)
    )

    return dim_charge_category


def load_table(connection, table_name, data):
    """Load a dataframe into SQLite."""
    data.to_sql(
        table_name,
        connection,
        if_exists="append",
        index=False
    )


def build_date_lookup(dim_date):
    """Build date lookup dictionary."""
    return dict(
        zip(
            dim_date["full_date"],
            dim_date["date_id"]
        )
    )


def build_incident_fact(incident_data, dim_date, dim_crime_type, dim_disposition, dim_location):
    """Build fact_incident table."""
    data = incident_data.copy()

    date_lookup = build_date_lookup(dim_date)

    crime_lookup = {
        (row["crime_type"], row["crime_group"], row["source_type"]): row["crime_type_id"]
        for _, row in dim_crime_type.iterrows()
    }

    disposition_lookup = {
        (row["disposition"], row["disposition_group"]): row["disposition_id"]
        for _, row in dim_disposition.iterrows()
    }

    location_lookup = {
        (row["location_raw"], row["location_group"]): row["location_id"]
        for _, row in dim_location.iterrows()
    }

    data["occurred_date_id"] = data["occurred_datetime"].dt.date.astype(str).map(date_lookup)
    data["reported_date_id"] = data["reported_datetime"].dt.date.astype(str).map(date_lookup)

    data["crime_type_id"] = data.apply(
        lambda row: crime_lookup.get(
            (
                row["crime_type"],
                row["crime_group"],
                row["source_type"]
            )
        ),
        axis=1
    )

    data["disposition_id"] = data.apply(
        lambda row: disposition_lookup.get(
            (
                row["disposition"],
                row["disposition_group"]
            )
        ),
        axis=1
    )

    data["location_id"] = data.apply(
        lambda row: location_lookup.get(
            (
                row["location_raw"],
                row["location_group"]
            )
        ),
        axis=1
    )

    fact_incident = data[
        [
            "incident_id",
            "case_number",
            "occurred_date_id",
            "reported_date_id",
            "crime_type_id",
            "disposition_id",
            "location_id",
            "occurred_datetime",
            "reported_datetime",
            "report_delay_hours",
            "report_delay_days",
            "delay_bucket",
            "hour",
            "source_type",
            "source_url",
            "scraped_at",
            "has_valid_case_number",
            "has_valid_occurred_datetime",
            "has_valid_reported_datetime",
            "has_valid_reporting_delay"
        ]
    ]

    return fact_incident


def build_arrest_fact(arrest_data, dim_date, dim_demographic, dim_charge_category):
    """Build fact_arrest table."""
    if arrest_data.empty:
        return pd.DataFrame(
            columns=[
                "arrest_id",
                "arrest_number",
                "case_number",
                "arrest_date_id",
                "demographic_id",
                "charge_category_id",
                "arrested_datetime",
                "arrested_charge",
                "arrested_hour",
                "source_year",
                "source_url",
                "scraped_at",
                "has_valid_arrest_number",
                "has_valid_case_number",
                "has_valid_arrested_datetime",
                "has_charge_text"
            ]
        )

    data = arrest_data.copy()

    date_lookup = build_date_lookup(dim_date)

    demographic_lookup = {
        (row["race"], row["sex"], row["age_group"]): row["demographic_id"]
        for _, row in dim_demographic.iterrows()
    }

    charge_lookup = {
        row["charge_category"]: row["charge_category_id"]
        for _, row in dim_charge_category.iterrows()
    }

    data["age_group"] = data["age"].apply(assign_age_group)

    data["arrest_date_id"] = data["arrested_datetime"].dt.date.astype(str).map(date_lookup)

    data["demographic_id"] = data.apply(
        lambda row: demographic_lookup.get(
            (
                row["race"],
                row["sex"],
                row["age_group"]
            )
        ),
        axis=1
    )

    data["charge_category_id"] = data["charge_category"].map(charge_lookup)

    fact_arrest = data[
        [
            "arrest_id",
            "arrest_number",
            "case_number",
            "arrest_date_id",
            "demographic_id",
            "charge_category_id",
            "arrested_datetime",
            "arrested_charge",
            "arrested_hour",
            "source_year",
            "source_url",
            "scraped_at",
            "has_valid_arrest_number",
            "has_valid_case_number",
            "has_valid_arrested_datetime",
            "has_charge_text"
        ]
    ]

    return fact_arrest


def print_table_counts(connection):
    """Print database table row counts."""
    table_names = [
        "dim_date",
        "dim_crime_type",
        "dim_disposition",
        "dim_location",
        "dim_demographic",
        "dim_charge_category",
        "fact_incident",
        "fact_arrest"
    ]

    print("")
    print("Database table counts:")

    for table_name in table_names:
        count = connection.execute(
            f"SELECT COUNT(*) FROM {table_name};"
        ).fetchone()[0]

        print(f"- {table_name}: {count:,}")


def main():
    """Build and load the SQLite database."""
    print("Building Terp Protect database...")

    connection = connect_database()

    try:
        print("Running schema...")
        run_schema(connection)

        print("Loading cleaned incident data...")
        incident_data = load_clean_incident_data()

        print("Loading cleaned arrest data...")
        arrest_data = load_clean_arrest_data()

        print("Creating dimension tables...")
        dim_date = create_dim_date(incident_data, arrest_data)
        dim_crime_type = create_dim_crime_type(incident_data)
        dim_disposition = create_dim_disposition(incident_data)
        dim_location = create_dim_location(incident_data)
        dim_demographic = create_dim_demographic(arrest_data)
        dim_charge_category = create_dim_charge_category(arrest_data)

        print("Loading dimension tables...")
        load_table(connection, "dim_date", dim_date)
        load_table(connection, "dim_crime_type", dim_crime_type)
        load_table(connection, "dim_disposition", dim_disposition)
        load_table(connection, "dim_location", dim_location)

        if not dim_demographic.empty:
            load_table(connection, "dim_demographic", dim_demographic)

        if not dim_charge_category.empty:
            load_table(connection, "dim_charge_category", dim_charge_category)

        print("Creating fact tables...")
        fact_incident = build_incident_fact(
            incident_data,
            dim_date,
            dim_crime_type,
            dim_disposition,
            dim_location
        )

        fact_arrest = build_arrest_fact(
            arrest_data,
            dim_date,
            dim_demographic,
            dim_charge_category
        )

        print("Loading fact tables...")
        load_table(connection, "fact_incident", fact_incident)

        if not fact_arrest.empty:
            load_table(connection, "fact_arrest", fact_arrest)

        connection.commit()

        print_table_counts(connection)

        print("")
        print(f"Database built successfully at: {DATABASE_PATH}")

    finally:
        connection.close()


if __name__ == "__main__":
    main()