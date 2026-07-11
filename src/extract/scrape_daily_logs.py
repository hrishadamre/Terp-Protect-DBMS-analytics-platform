"""
scrape_daily_logs.py

Purpose:
Collect UMPD Daily Crime and Incident Log records from public monthly webpages
for the years 2023, 2024, and 2025.

Output:
data/raw/daily_incident_logs_2023_2025.csv

Role in Pipeline:
This script belongs to the extract stage. It performs minimal transformation
and preserves source fields as raw values.

Cleaning, standardization, and feature engineering are handled later
in the transform stage.
"""

import re
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup


BASE_URL = "https://umpd.umd.edu/statistics-reports/daily-crime-and-incident-logs"

YEARS = [2023, 2024, 2025]

MONTHS = [
    f"{month:02d}"
    for month in range(1, 13)
]

OUTPUT_PATH = Path(
    "data/raw/daily_incident_logs_2023_2025.csv"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

CASE_PATTERN = re.compile(
    r"^\d{4}-\d{8}$"
)

OCCURRED_PATTERN = re.compile(
    r"\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}"
)

REPORTED_PATTERN = re.compile(
    r"\d{2}/\d{2}/\d{4}\s+-\s+\d{2}:\d{2}"
)


def fetch_page(url):
    """Download one monthly UMPD incident log page."""
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    return response.text


def clean_text(value):
    """Remove extra spaces from text."""
    if value is None:
        return ""

    return re.sub(
        r"\s+",
        " ",
        value
    ).strip()


def parse_month_page(html, year, month, url):
    """Extract incident records from one monthly webpage."""
    soup = BeautifulSoup(
        html,
        "lxml"
    )

    main_text = soup.get_text("\n")

    lines = [
        clean_text(line)
        for line in main_text.splitlines()
    ]

    lines = [
        line
        for line in lines
        if line
    ]

    records = []
    index = 0

    while index < len(lines):
        line = lines[index]

        if CASE_PATTERN.match(line):
            case_number = line

            occurred_raw = (
                lines[index + 1]
                if index + 1 < len(lines)
                else ""
            )

            reported_raw = (
                lines[index + 2]
                if index + 2 < len(lines)
                else ""
            )

            crime_type = (
                lines[index + 3]
                if index + 3 < len(lines)
                else ""
            )

            disposition = (
                lines[index + 4]
                if index + 4 < len(lines)
                else ""
            )

            location = (
                lines[index + 5]
                if index + 5 < len(lines)
                else ""
            )

            if (
                OCCURRED_PATTERN.search(occurred_raw)
                and REPORTED_PATTERN.search(reported_raw)
            ):
                records.append(
                    {
                        "source_year": year,
                        "source_month": month,
                        "case_number": case_number,
                        "occurred_datetime_raw": occurred_raw,
                        "reported_datetime_raw": reported_raw,
                        "crime_type_raw": crime_type,
                        "disposition_raw": disposition,
                        "location_raw": location,
                        "source_url": url,
                        "scraped_at": datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    }
                )

                index += 6

            else:
                index += 1

        else:
            index += 1

    return records


def scrape_daily_logs():
    """Scrape incident logs for 2023, 2024, and 2025."""
    all_records = []

    for year in YEARS:
        print(f"\nScraping incident logs for {year}")

        for month in MONTHS:
            url = f"{BASE_URL}/{year}/{month}"

            print(f"Scraping {url}")

            try:
                html = fetch_page(url)

                month_records = parse_month_page(
                    html,
                    year,
                    month,
                    url
                )

                print(
                    f"Found {len(month_records)} records "
                    f"for {year}-{month}"
                )

                all_records.extend(month_records)

                time.sleep(1)

            except requests.HTTPError as error:
                print(
                    f"HTTP error for {url}: {error}"
                )

            except requests.RequestException as error:
                print(
                    f"Request error for {url}: {error}"
                )

            except Exception as error:
                print(
                    f"Unexpected error for {url}: {error}"
                )

    incident_df = pd.DataFrame(
        all_records
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    incident_df = incident_df.drop_duplicates(
        subset=[
            "case_number",
            "occurred_datetime_raw",
            "reported_datetime_raw",
            "crime_type_raw",
            "disposition_raw",
            "location_raw"
        ]
    )

    incident_df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print(
        f"\nSaved {len(incident_df)} records "
        f"to {OUTPUT_PATH}"
    )

    if not incident_df.empty:
        print("\nRecord count by year:")

        print(
            incident_df["source_year"]
            .value_counts()
            .sort_index()
        )

        print("\nPreview:")

        print(
            incident_df
            .head()
            .to_string(index=False)
        )


if __name__ == "__main__":
    scrape_daily_logs()