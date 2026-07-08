"""
layout.py

Purpose:
Store reusable layout and styling helpers for the Terp Protect Streamlit dashboard.

This file keeps visual presentation code separate from dashboard logic.
"""

import streamlit as st

from components.theme import get_theme


def apply_custom_styles():
    """Apply custom dashboard styling using the centralized theme."""
    theme = get_theme()

    st.markdown(
        f"""
        <style>
        html, body, [class*="css"] {{
            font-family: {theme["font"]["family"]};
        }}

        .stApp {{
            background:
                radial-gradient(circle at top left, rgba(200, 16, 46, 0.12), transparent 28%),
                radial-gradient(circle at bottom right, rgba(110, 198, 255, 0.10), transparent 26%),
                {theme["background"]["app"]};
        }}

        .block-container {{
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1280px;
        }}

        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #171A23 0%, #11141C 100%);
            border-right: 1px solid {theme["border"]["dark"]};
        }}

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p {{
            color: {theme["text"]["primary"]};
        }}

        section[data-testid="stSidebar"] [data-testid="stMetric"] {{
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.10);
            box-shadow: none;
        }}

        section[data-testid="stSidebar"] [data-testid="stMetricLabel"] {{
            color: #B8BFCC;
        }}

        section[data-testid="stSidebar"] [data-testid="stMetricValue"] {{
            color: white;
        }}

        section[data-testid="stSidebar"] [data-baseweb="tag"] {{
            background-color: {theme["brand"]["primary"]};
            color: white;
            border-radius: 8px;
            font-weight: 600;
        }}

        section[data-testid="stSidebar"] [data-baseweb="select"] {{
            background-color: #0B0E14;
            border-radius: {theme["layout"]["radius_medium"]};
            border-color: rgba(255, 255, 255, 0.12);
        }}

        .dashboard-header {{
            position: relative;
            overflow: hidden;
            background:
                radial-gradient(circle at 90% 15%, rgba(255, 210, 0, 0.28), transparent 22%),
                radial-gradient(circle at 75% 80%, rgba(110, 198, 255, 0.18), transparent 26%),
                linear-gradient(120deg, #11141C 0%, {theme["brand"]["primary_dark"]} 48%, {theme["brand"]["primary"]} 100%);
            padding: 1.9rem 2rem;
            border-radius: {theme["layout"]["radius_large"]};
            margin-bottom: 1.35rem;
            box-shadow: {theme["layout"]["shadow_soft"]};
            border: 1px solid rgba(255, 255, 255, 0.10);
        }}

        .dashboard-header::before {{
            content: "";
            position: absolute;
            width: 320px;
            height: 320px;
            right: -140px;
            top: -150px;
            background: rgba(255, 255, 255, 0.10);
            border-radius: 999px;
            filter: blur(1px);
        }}

        .dashboard-header::after {{
            content: "";
            position: absolute;
            width: 180px;
            height: 180px;
            right: 80px;
            bottom: -110px;
            background: rgba(255, 210, 0, 0.16);
            border-radius: 999px;
        }}

        .header-content {{
            position: relative;
            z-index: 2;
        }}

        .header-eyebrow {{
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            background: rgba(255, 255, 255, 0.12);
            border: 1px solid rgba(255, 255, 255, 0.18);
            color: #FFFFFF;
            padding: 0.36rem 0.7rem;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            margin-bottom: 0.9rem;
        }}

        .dashboard-header h1 {{
            color: {theme["text"]["primary"]};
            font-size: {theme["font"]["title_size"]};
            line-height: 1.05;
            margin-bottom: 0.55rem;
            letter-spacing: -0.055em;
            font-weight: 850;
        }}

        .dashboard-header p {{
            color: {theme["text"]["secondary"]};
            font-size: {theme["font"]["subtitle_size"]};
            margin-bottom: 1rem;
            max-width: 930px;
            line-height: 1.55;
        }}

        .header-badges {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
            margin-top: 0.7rem;
        }}

        .header-badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.38rem;
            background: rgba(255, 255, 255, 0.11);
            border: 1px solid rgba(255, 255, 255, 0.16);
            color: #FFFFFF;
            padding: 0.48rem 0.72rem;
            border-radius: 999px;
            font-size: 0.84rem;
            font-weight: 600;
            backdrop-filter: blur(8px);
        }}

        h1, h2, h3 {{
            color: {theme["text"]["primary"]};
            letter-spacing: -0.03em;
        }}

        h2, h3 {{
            margin-top: 0.4rem;
        }}

        .section-note {{
            background: linear-gradient(90deg, #FFFFFF 0%, #F9FAFB 100%);
            border-left: 5px solid {theme["brand"]["primary"]};
            padding: 0.9rem 1rem;
            border-radius: {theme["layout"]["radius_small"]};
            margin-bottom: 1rem;
            color: {theme["text"]["on_card"]};
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
            line-height: 1.5;
        }}

        .insight-box {{
            background:
                linear-gradient(90deg, rgba(255, 248, 230, 1) 0%, rgba(255, 252, 242, 1) 100%);
            border-left: 5px solid {theme["brand"]["secondary"]};
            padding: 0.82rem 1rem;
            border-radius: {theme["layout"]["radius_small"]};
            margin-top: 0.45rem;
            margin-bottom: 1rem;
            color: {theme["text"]["on_card"]};
            font-size: {theme["font"]["body_size"]};
            line-height: 1.5;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
        }}

        div[data-testid="stMetric"] {{
            background:
                linear-gradient(180deg, #FFFFFF 0%, #F8F9FB 100%);
            padding: 1rem 1.05rem;
            border-radius: {theme["layout"]["radius_medium"]};
            border: 1px solid {theme["border"]["light"]};
            box-shadow: {theme["layout"]["shadow_card"]};
            transition: transform 0.16s ease, box-shadow 0.16s ease, border-color 0.16s ease;
        }}

        div[data-testid="stMetric"]:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 28px rgba(0, 0, 0, 0.16);
            border-color: rgba(200, 16, 46, 0.26);
        }}

        div[data-testid="stMetricLabel"] {{
            font-size: {theme["font"]["small_size"]};
            color: {theme["text"]["muted"]};
            font-weight: 700;
        }}

        div[data-testid="stMetricValue"] {{
            font-size: 1.45rem;
            color: {theme["text"]["dark"]};
            font-weight: 850;
            letter-spacing: -0.03em;
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 0.45rem;
            border-bottom: 1px solid {theme["border"]["dark"]};
        }}

        .stTabs [data-baseweb="tab"] {{
            background-color: {theme["background"]["card"]};
            color: {theme["text"]["dark"]};
            border-radius: 10px 10px 0 0;
            padding: 0.65rem 1rem;
            border: 1px solid {theme["border"]["light"]};
            font-weight: 700;
        }}

        .stTabs [aria-selected="true"] {{
            background-color: {theme["brand"]["primary"]};
            color: white;
            border-color: {theme["brand"]["primary"]};
        }}

        div[data-testid="stDataFrame"] {{
            border-radius: {theme["layout"]["radius_medium"]};
            overflow: hidden;
        }}

        button[kind="secondary"] {{
            border-radius: {theme["layout"]["radius_small"]};
        }}

        .stMultiSelect [data-baseweb="select"] {{
            border-radius: {theme["layout"]["radius_medium"]};
        }}

        div[data-testid="stExpander"] {{
            border-radius: {theme["layout"]["radius_medium"]};
            border-color: {theme["border"]["dark"]};
        }}

        div[data-testid="stExpander"] summary {{
            font-weight: 700;
        }}

        hr {{
            border-color: {theme["border"]["dark"]};
            margin-top: 1.5rem;
            margin-bottom: 1.5rem;
        }}

        @keyframes softFloat {{
            0% {{
                transform: translateY(0px);
            }}
            50% {{
                transform: translateY(-4px);
            }}
            100% {{
                transform: translateY(0px);
            }}
        }}

        .header-badge:first-child {{
            animation: softFloat 4s ease-in-out infinite;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


def show_dashboard_header():
    """Display the main dashboard header."""
    st.markdown(
        """
        <div class="dashboard-header">
            <div class="header-content">
                <div class="header-eyebrow">🐢 UMPD Public Safety Intelligence</div>
                <h1>Terp Protect: Campus Safety Analytics</h1>
                <p>
                    A DBMS-powered command dashboard for exploring campus incident patterns,
                    arrest records, reporting delays, case outcomes, and location-based safety trends.
                </p>
                <div class="header-badges">
                    <div class="header-badge">📊 Incident Intelligence</div>
                    <div class="header-badge">⏱ Reporting Delay</div>
                    <div class="header-badge">📍 Location Patterns</div>
                    <div class="header-badge">⚖️ Arrest Matching</div>
                    <div class="header-badge">✅ Data Quality</div>
                </div>
            </div>
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