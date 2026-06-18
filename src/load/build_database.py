"""
build_database.py

Purpose:
Build the Terp Protect SQLite database and load cleaned UMPD Daily Crime and Incident Log records.

Current Scope:
- Source: UMPD Daily Crime and Incident Logs
- Year: 2025
- Schema File: sql/01_schema.sql
- Input File: data/processed/clean_daily_incidents_2025.csv
- Output Database: data/database/terp_protect.db

Role in Pipeline:
This script belongs to the load stage. It creates the relational database tables,
loads dimension tables, and loads the fact_incident table using cleaned incident data.
"""

from pathlib import Path
import sqlite3
import pandas as pd


SCHEMA_PATH = Path("sql/01_schema.sql")
CLEAN_INPUT_PATH = Path("data/processed/clean_daily_incidents_2025.csv")
DATABASE_PATH = Path("data/database/terp_protect.db")


def connect_database():
    """Create a database connection and enable foreign key support."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON;")

    return connection


def run_schema(connection):
    """Run the SQL schema file to create all database tables."""
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_PATH}")

    schema_sql = SCHEMA_PATH.read_text()

    connection.executescript(schema_sql)
    connection.commit()


def load_clean_data():
    """Read cleaned incident data from CSV."""
    if not CLEAN_INPUT_PATH.exists():
        raise FileNotFoundError(f"Clean input file not found: {CLEAN_INPUT_PATH}")

    df = pd.read_csv(CLEAN_INPUT_PATH)

    df["occurred_datetime"] = pd.to_datetime(df["occurred_datetime"], errors="coerce")
    df["reported_datetime"] = pd.to_datetime(df["reported_datetime"], errors="coerce")

    return df


def create_date_dimension(df):
    """Create unique date records from occurred and reported datetime fields."""
    occurred_dates = df["occurred_datetime"].dt.date
    reported_dates = df["reported_datetime"].dt.date

    all_dates = pd.concat(
        [
            occurred_dates.rename("full_date"),
            reported_dates.rename("full_date")
        ],
        ignore_index=True
    )

    date_df = pd.DataFrame({"full_date": all_dates})
    date_df = date_df.dropna().drop_duplicates().sort_values("full_date").reset_index(drop=True)

    date_df["date_id"] = range(1, len(date_df) + 1)
    date_df["full_date"] = pd.to_datetime(date_df["full_date"])

    date_df["year"] = date_df["full_date"].dt.year
    date_df["quarter"] = date_df["full_date"].dt.quarter
    date_df["month"] = date_df["full_date"].dt.month
    date_df["month_name"] = date_df["full_date"].dt.month_name()
    date_df["day"] = date_df["full_date"].dt.day
    date_df["weekday"] = date_df["full_date"].dt.day_name()
    date_df["day_of_week_number"] = date_df["full_date"].dt.dayofweek + 1
    date_df["is_weekend"] = date_df["weekday"].isin(["Saturday", "Sunday"]).astype(int)
    date_df["semester_period"] = date_df["month"].apply(assign_semester_period)

    date_df["full_date"] = date_df["full_date"].dt.strftime("%Y-%m-%d")

    return date_df


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


def create_crime_type_dimension(df):
    """Create unique crime type dimension records."""
    crime_df = df[
        [
            "crime_type",
            "crime_group",
            "source_type"
        ]
    ].drop_duplicates().reset_index(drop=True)

    crime_df["crime_type_id"] = range(1, len(crime_df) + 1)

    return crime_df[
        [
            "crime_type_id",
            "crime_type",
            "crime_group",
            "source_type"
        ]
    ]


def create_disposition_dimension(df):
    """Create unique disposition dimension records."""
    disposition_df = df[
        [
            "disposition",
            "disposition_group"
        ]
    ].drop_duplicates().reset_index(drop=True)

    disposition_df["disposition_id"] = range(1, len(disposition_df) + 1)

    disposition_df["is_arrest_related"] = (
        disposition_df["disposition_group"] == "Arrest"
    ).astype(int)

    disposition_df["is_pending"] = (
        disposition_df["disposition_group"] == "Pending / Active"
    ).astype(int)

    disposition_df["is_closed"] = (
        disposition_df["disposition_group"].isin(["Closed / Cleared", "Unfounded"])
    ).astype(int)

    return disposition_df[
        [
            "disposition_id",
            "disposition",
            "disposition_group",
            "is_arrest_related",
            "is_pending",
            "is_closed"
        ]
    ]


def create_location_dimension(df):
    """Create unique location dimension records."""
    location_df = df[
        [
            "location_raw",
            "location_group"
        ]
    ].drop_duplicates().reset_index(drop=True)

    location_df["location_id"] = range(1, len(location_df) + 1)
    location_df["jurisdiction_group"] = "Unknown"
    location_df["is_on_campus"] = None

    return location_df[
        [
            "location_id",
            "location_raw",
            "location_group",
            "jurisdiction_group",
            "is_on_campus"
        ]
    ]


def create_fact_incident(df, date_df, crime_df, disposition_df, location_df):
    """Create the fact_incident table by mapping cleaned records to dimension IDs."""
    fact_df = df.copy()

    date_lookup = date_df.set_index("full_date")["date_id"].to_dict()

    crime_lookup = crime_df.set_index(
        [
            "crime_type",
            "crime_group",
            "source_type"
        ]
    )["crime_type_id"].to_dict()

    disposition_lookup = disposition_df.set_index(
        [
            "disposition",
            "disposition_group"
        ]
    )["disposition_id"].to_dict()

    location_lookup = location_df.set_index(
        [
            "location_raw",
            "location_group"
        ]
    )["location_id"].to_dict()

    fact_df["occurred_date_key"] = fact_df["occurred_datetime"].dt.strftime("%Y-%m-%d")
    fact_df["reported_date_key"] = fact_df["reported_datetime"].dt.strftime("%Y-%m-%d")

    fact_df["occurred_date_id"] = fact_df["occurred_date_key"].map(date_lookup)
    fact_df["reported_date_id"] = fact_df["reported_date_key"].map(date_lookup)

    fact_df["crime_type_id"] = fact_df.apply(
        lambda row: crime_lookup.get(
            (
                row["crime_type"],
                row["crime_group"],
                row["source_type"]
            )
        ),
        axis=1
    )

    fact_df["disposition_id"] = fact_df.apply(
        lambda row: disposition_lookup.get(
            (
                row["disposition"],
                row["disposition_group"]
            )
        ),
        axis=1
    )

    fact_df["location_id"] = fact_df.apply(
        lambda row: location_lookup.get(
            (
                row["location_raw"],
                row["location_group"]
            )
        ),
        axis=1
    )

    fact_df["occurred_datetime"] = fact_df["occurred_datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")
    fact_df["reported_datetime"] = fact_df["reported_datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")

    boolean_columns = [
        "has_valid_case_number",
        "has_valid_occurred_datetime",
        "has_valid_reported_datetime",
        "has_valid_reporting_delay"
    ]

    for column in boolean_columns:
        fact_df[column] = fact_df[column].astype(int)

    final_columns = [
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

    return fact_df[final_columns]


def load_table(connection, table_name, df):
    """Load a dataframe into a database table."""
    df.to_sql(
        table_name,
        connection,
        if_exists="append",
        index=False
    )


def print_table_counts(connection):
    """Print row counts for loaded database tables."""
    tables = [
        "dim_date",
        "dim_crime_type",
        "dim_disposition",
        "dim_location",
        "fact_incident"
    ]

    print("")
    print("Database table counts:")

    for table in tables:
        count = connection.execute(f"SELECT COUNT(*) FROM {table};").fetchone()[0]
        print(f"- {table}: {count:,}")


def main():
    """Run the full database build and load process."""
    print("Connecting to database...")
    connection = connect_database()

    print("Running schema...")
    run_schema(connection)

    print("Loading cleaned incident data...")
    clean_df = load_clean_data()

    print("Creating dimension tables...")
    date_df = create_date_dimension(clean_df)
    crime_df = create_crime_type_dimension(clean_df)
    disposition_df = create_disposition_dimension(clean_df)
    location_df = create_location_dimension(clean_df)

    print("Creating fact table...")
    fact_df = create_fact_incident(
        clean_df,
        date_df,
        crime_df,
        disposition_df,
        location_df
    )

    print("Loading tables into SQLite database...")
    load_table(connection, "dim_date", date_df)
    load_table(connection, "dim_crime_type", crime_df)
    load_table(connection, "dim_disposition", disposition_df)
    load_table(connection, "dim_location", location_df)
    load_table(connection, "fact_incident", fact_df)

    connection.commit()

    print_table_counts(connection)

    connection.close()

    print("")
    print(f"Database build complete: {DATABASE_PATH}")


if __name__ == "__main__":
    main()