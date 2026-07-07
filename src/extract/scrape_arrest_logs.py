"""
scrape_arrest_logs.py

Purpose:
Collect UMPD Arrest Log records from the public annual arrest ledger webpage and save them as a raw CSV dataset.

Current Scope:
- Source: UMPD Arrest Logs
- Year: 2025
- Output: data/raw/arrest_logs_2025.csv

Role in Pipeline:
This script belongs to the extract stage. It collects raw arrest log fields with minimal transformation.
Cleaning, charge categorization, and incident-to-arrest matching are handled later in the transform and load stages.
"""

from pathlib import Path
from datetime import datetime
import re
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup


YEAR = 2025
BASE_URL = "https://umpd.umd.edu/statistics-reports/arrest-report-ledgers"
SOURCE_URL = f"{BASE_URL}/{YEAR}"
OUTPUT_PATH = Path(f"data/raw/arrest_logs_{YEAR}.csv")

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
    """Download the arrest ledger webpage."""
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
    """Extract the readable page text from HTML."""
    soup = BeautifulSoup(html, "lxml")

    page_text = soup.get_text(" ")

    page_text = clean_text(page_text)

    return page_text


def remove_header_text(page_text):
    """Remove text before the arrest log table header."""
    header_text = "Arrest Number Arrested Date Time UMPD Case Number Age Race Sex Arrested Charge"

    if header_text in page_text:
        page_text = page_text.split(header_text, 1)[1]

    return clean_text(page_text)


def parse_demographics_and_charge(segment_text):
    """
    Split remaining record text into age, race, sex, and charge.

    Some rows include race and sex.
    Some rows are missing race and sex and only contain charge text.
    The age field appears in the header but is often blank in the visible rows.
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
                arrested_charge_raw = clean_text(segment_text[len(prefix):])
                return age_raw, race_raw, sex_raw, arrested_charge_raw

    age_match = re.match(r"^(?P<age>\d{1,3})\s+(?P<rest>.*)$", segment_text)

    if age_match:
        possible_age = age_match.group("age")
        rest_text = clean_text(age_match.group("rest"))

        for race in RACE_VALUES:
            for sex in SEX_VALUES:
                prefix = f"{race} {sex}"

                if rest_text.startswith(prefix):
                    age_raw = possible_age
                    race_raw = race
                    sex_raw = sex
                    arrested_charge_raw = clean_text(rest_text[len(prefix):])
                    return age_raw, race_raw, sex_raw, arrested_charge_raw

    return age_raw, race_raw, sex_raw, arrested_charge_raw


def parse_arrest_records(page_text):
    """
    Parse arrest records from the full page text.

    This approach finds every arrest marker:
    Arrest Number + Arrested Date Time + UMPD Case Number

    Then it treats all text until the next marker as the charge/demographic segment.
    """
    records = []

    page_text = remove_header_text(page_text)

    matches = list(RECORD_MARKER_PATTERN.finditer(page_text))

    print(f"Detected {len(matches):,} arrest record markers.")

    for index, match in enumerate(matches):
        current_end = match.end()

        if index + 1 < len(matches):
            next_start = matches[index + 1].start()
            segment_text = page_text[current_end:next_start]
        else:
            segment_text = page_text[current_end:]

        segment_text = clean_text(segment_text)

        age_raw, race_raw, sex_raw, arrested_charge_raw = parse_demographics_and_charge(
            segment_text
        )

        records.append(
            {
                "source_year": YEAR,
                "arrest_number": match.group("arrest_number"),
                "arrested_datetime_raw": clean_text(match.group("arrested_datetime")),
                "case_number": match.group("case_number"),
                "age_raw": age_raw,
                "race_raw": race_raw,
                "sex_raw": sex_raw,
                "arrested_charge_raw": arrested_charge_raw,
                "source_url": SOURCE_URL,
                "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )

    return records


def scrape_arrest_logs():
    """Scrape annual UMPD arrest log records and save them to CSV."""
    print(f"Scraping arrest logs from: {SOURCE_URL}")

    html = fetch_page(SOURCE_URL)

    page_text = extract_page_text(html)

    records = parse_arrest_records(page_text)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    arrest_df = pd.DataFrame(records)

    arrest_df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print(f"Saved {len(arrest_df):,} arrest records to {OUTPUT_PATH}")

    if not arrest_df.empty:
        print("")
        print("Preview:")
        print(arrest_df.head(10).to_string(index=False))


def main():
    """Run the arrest log scraping process."""
    scrape_arrest_logs()

    time.sleep(1)


if __name__ == "__main__":
    main()