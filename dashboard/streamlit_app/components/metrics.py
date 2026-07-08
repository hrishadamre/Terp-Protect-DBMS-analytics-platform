"""
metrics.py

Purpose:
Store reusable formatting and metric helper functions for the Terp Protect dashboard.

This file keeps small calculation and formatting utilities separate from dashboard page code.
"""

import pandas as pd


def format_number(value):
    """Format large numbers with commas."""
    if pd.isna(value):
        return "0"

    return f"{int(value):,}"


def format_percentage(value):
    """Format percentage values."""
    if pd.isna(value):
        return "0.0%"

    return f"{value:.1f}%"


def get_top_value(data, column):
    """Return the most frequent value and its count for a column."""
    if data.empty or column not in data.columns:
        return "N/A", 0

    counts = data[column].dropna().value_counts()

    if counts.empty:
        return "N/A", 0

    return counts.index[0], int(counts.iloc[0])