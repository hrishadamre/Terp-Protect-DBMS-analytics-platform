"""
scrape_arrest_logs.py

Purpose:
Collect UMPD Arrest Log records from public annual arrest ledger webpages
for the years 2023, 2024, and 2025.

Output:
data/raw/arrest_logs_2023_2025.csv

Role in Pipeline:
This script belongs to the extract stage. It collects raw arrest log fields
with minimal transformation.

Cleaning, charge categorization, and incident-to-arrest matching are handled
later in the transform and load stages.
"""

from pathlib import Path
from datetime import datetime
import re
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup


YEARS = [2023, 2024, 2025]

BASE_URL = (
    "https://umpd.umd.edu/statistics-reports/"
    "arrest-report-ledgers"
)

OUTPUT_PATH = Path(
    "data/raw/arrest_logs_2023_2025.csv"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

RECORD_MARKER_PATTERN = re.compile(
    r"(?P<arrest_number>\d+)\s+"
    r"(?P<arrested_datetime>\d{2}/\d{2}/\d{4}\s*-\s*\d{2}:\d{2})\s+"
    r"(?P<case_number>\d{4}-\d{8})"
)

RACE_VALUES = [
    "American Indian/Alaskan",
    "Asian",
    "Black",
    "Native Hawaiian/Pacific Islander",
    "Unknown",
    "White"
]

SEX_VALUES = [
    "Female",
    "Male",
    "Unknown"
]


def fetch_page(url):
    """Download one yearly arrest ledger webpage."""
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    return response.text


def clean_text(value):
    """Clean spacing and handle empty values."""
    if value is None:
        return ""

    value = str(value).strip()
    value = re.sub(r"\s+", " ", value)

    return value


def extract_page_text(html):
    """Extract readable text from the webpage HTML."""
    soup = BeautifulSoup(
        html,
        "lxml"
    )

    page_text = soup.get_text(" ")

    return clean_text(page_text)


def remove_header_text(page_text):
    """Remove text before the arrest log table header."""
    header_text = (
        "Arrest Number Arrested Date Time "
        "UMPD Case Number Age Race Sex Arrested Charge"
    )

    if header_text in page_text:
        page_text = page_text.split(
            header_text,
            1
        )[1]

    return clean_text(page_text)


def parse_demographics_and_charge(segment_text):
    """
    Split record text into age, race, sex, and charge.

    Some records contain race and sex.
    Some records may be missing those fields.
    The age field is sometimes blank.
    """
    segment_text = clean_text(segment_text)

    age_raw = ""
    race_raw = ""
    sex_raw = ""
    arrested_charge_raw = segment_text

    for race in RACE_VALUES:
        for sex in SEX_VALUES:
            prefix = f"{race} {sex}"

            if segment_text.startswith(prefix):
                race_raw = race
                sex_raw = sex
                arrested_charge_raw = clean_text(
                    segment_text[len(prefix):]
                )

                return (
                    age_raw,
                    race_raw,
                    sex_raw,
                    arrested_charge_raw
                )

    age_match = re.match(
        r"^(?P<age>\d{1,3})\s+(?P<rest>.*)$",
        segment_text
    )

    if age_match:
        possible_age = age_match.group("age")
        rest_text = clean_text(
            age_match.group("rest")
        )

        for race in RACE_VALUES:
            for sex in SEX_VALUES:
                prefix = f"{race} {sex}"

                if rest_text.startswith(prefix):
                    age_raw = possible_age
                    race_raw = race
                    sex_raw = sex
                    arrested_charge_raw = clean_text(
                        rest_text[len(prefix):]
                    )

                    return (
                        age_raw,
                        race_raw,
                        sex_raw,
                        arrested_charge_raw
                    )

    return (
        age_raw,
        race_raw,
        sex_raw,
        arrested_charge_raw
    )


def parse_arrest_records(page_text, year, source_url):
    """
    Parse arrest records from the full webpage text.

    Each arrest marker contains:
    - Arrest number
    - Arrested date and time
    - UMPD case number

    The text between one marker and the next contains the demographic
    and charge information for that record.
    """
    records = []

    page_text = remove_header_text(page_text)

    matches = list(
        RECORD_MARKER_PATTERN.finditer(page_text)
    )

    print(
        f"Detected {len(matches):,} arrest record markers "
        f"for {year}."
    )

    for index, match in enumerate(matches):
        current_end = match.end()

        if index + 1 < len(matches):
            next_start = matches[index + 1].start()
            segment_text = page_text[
                current_end:next_start
            ]
        else:
            segment_text = page_text[current_end:]

        segment_text = clean_text(segment_text)

        (
            age_raw,
            race_raw,
            sex_raw,
            arrested_charge_raw
        ) = parse_demographics_and_charge(
            segment_text
        )

        records.append(
            {
                "source_year": year,
                "arrest_number": match.group(
                    "arrest_number"
                ),
                "arrested_datetime_raw": clean_text(
                    match.group("arrested_datetime")
                ),
                "case_number": match.group(
                    "case_number"
                ),
                "age_raw": age_raw,
                "race_raw": race_raw,
                "sex_raw": sex_raw,
                "arrested_charge_raw": arrested_charge_raw,
                "source_url": source_url,
                "scraped_at": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            }
        )

    return records


def scrape_arrest_logs():
    """Scrape arrest logs for 2023, 2024, and 2025."""
    all_records = []

    for year in YEARS:
        source_url = f"{BASE_URL}/{year}"

        print(f"\nScraping arrest logs for {year}")
        print(f"Source: {source_url}")

        try:
            html = fetch_page(source_url)

            page_text = extract_page_text(html)

            year_records = parse_arrest_records(
                page_text,
                year,
                source_url
            )

            print(
                f"Found {len(year_records):,} arrest records "
                f"for {year}"
            )

            all_records.extend(year_records)

            time.sleep(1)

        except requests.HTTPError as error:
            print(
                f"HTTP error for {source_url}: {error}"
            )

        except requests.RequestException as error:
            print(
                f"Request error for {source_url}: {error}"
            )

        except Exception as error:
            print(
                f"Unexpected error for {source_url}: {error}"
            )

    arrest_df = pd.DataFrame(
        all_records
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if not arrest_df.empty:
        arrest_df = arrest_df.drop_duplicates(
            subset=[
                "arrest_number",
                "arrested_datetime_raw",
                "case_number",
                "arrested_charge_raw"
            ]
        )

    arrest_df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print(
        f"\nSaved {len(arrest_df):,} arrest records "
        f"to {OUTPUT_PATH}"
    )

    if not arrest_df.empty:
        print("\nRecord count by year:")

        print(
            arrest_df["source_year"]
            .value_counts()
            .sort_index()
        )

        print("\nPreview:")

        print(
            arrest_df
            .head(10)
            .to_string(index=False)
        )


def main():
    """Run the multi-year arrest log scraper."""
    scrape_arrest_logs()


if __name__ == "__main__":
    main()