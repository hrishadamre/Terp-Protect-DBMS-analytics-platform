"""
layout.py

Purpose:
Store reusable layout and styling helpers for the Terp Protect Streamlit dashboard.

This file keeps visual presentation code separate from dashboard logic.
"""

import streamlit as st


def apply_custom_styles():
    """Apply custom dashboard styling."""
    st.markdown(
        """
        <style>
        .main {
            background-color: #fafafa;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        .dashboard-header {
            background: linear-gradient(90deg, #111111 0%, #b00020 100%);
            padding: 1.4rem 1.6rem;
            border-radius: 14px;
            margin-bottom: 1.4rem;
        }

        .dashboard-header h1 {
            color: white;
            font-size: 2rem;
            margin-bottom: 0.25rem;
        }

        .dashboard-header p {
            color: #f2f2f2;
            font-size: 1rem;
            margin-bottom: 0;
        }

        .section-note {
            background-color: #ffffff;
            border-left: 5px solid #b00020;
            padding: 0.9rem 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            color: #333333;
        }

        .insight-box {
            background-color: #fff8e6;
            border-left: 5px solid #f4c430;
            padding: 0.8rem 1rem;
            border-radius: 8px;
            margin-top: 0.4rem;
            margin-bottom: 1rem;
            color: #333333;
            font-size: 0.95rem;
        }

        div[data-testid="stMetric"] {
            background-color: #ffffff;
            padding: 1rem;
            border-radius: 12px;
            border: 1px solid #e6e6e6;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
        }

        div[data-testid="stMetricLabel"] {
            font-size: 0.9rem;
            color: #444444;
        }

        div[data-testid="stMetricValue"] {
            font-size: 1.4rem;
            color: #111111;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.4rem;
        }

        .stTabs [data-baseweb="tab"] {
            background-color: #ffffff;
            border-radius: 10px 10px 0 0;
            padding: 0.6rem 1rem;
            border: 1px solid #e6e6e6;
        }

        .stTabs [aria-selected="true"] {
            background-color: #b00020;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def show_dashboard_header():
    """Display the main dashboard header."""
    st.markdown(
        """
        <div class="dashboard-header">
            <h1>Terp Protect: Campus Safety Analytics</h1>
            <p>
                Interactive DBMS-powered dashboard for exploring UMPD incident records,
                arrest records, reporting delays, case outcomes, and charge patterns.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def show_section_note(text):
    """Display a short styled note under a section heading."""
    st.markdown(
        f"""
        <div class="section-note">
            {text}
        </div>
        """,
        unsafe_allow_html=True
    )


def show_insight(text):
    """Display a short analytical insight below a chart or section."""
    st.markdown(
        f"""
        <div class="insight-box">
            <strong>Insight:</strong> {text}
        </div>
        """,
        unsafe_allow_html=True
    )