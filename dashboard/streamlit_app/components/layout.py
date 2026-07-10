"""
layout.py

Purpose:
Reusable layout, styling, and UI helper functions for the Terp Protect Streamlit dashboard.

This file controls:
- Global Streamlit styling
- Header / hero section
- Sticky tab navigation styling
- Sidebar filter styling
- KPI card styling
- Insight cards with highlighted keywords
- Compact notes and info helpers
"""

import html
import re

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
                radial-gradient(circle at 5% 5%, rgba(200, 16, 46, 0.11), transparent 23%),
                radial-gradient(circle at 94% 10%, rgba(118, 199, 232, 0.10), transparent 24%),
                linear-gradient(135deg, {theme["background"]["app_gradient_start"]} 0%, {theme["background"]["app_gradient_mid"]} 48%, {theme["background"]["app_gradient_end"]} 100%);
            color: {theme["text"]["primary"]};
        }}

        .block-container {{
            padding-top: 1rem;
            padding-bottom: 2rem;
            padding-left: 1rem;
            padding-right: 1rem;
            max-width: none !important;
            width: 100% !important;
        }}

        h1, h2, h3, h4 {{
            color: {theme["text"]["primary"]};
            letter-spacing: -0.035em;
        }}

        h2 {{
            font-size: {theme["font"]["section_title_size"]};
            font-weight: 850;
            margin-top: 0.1rem;
            margin-bottom: 0.65rem;
        }}

        p, span, label {{
            font-family: {theme["font"]["family"]};
        }}

        a {{
            color: {theme["brand"]["accent"]};
        }}

        /* -----------------------------
           Sidebar / Filters
        ------------------------------ */

        section[data-testid="stSidebar"] {{
            background:
                radial-gradient(circle at top left, rgba(200, 16, 46, 0.12), transparent 28%),
                linear-gradient(180deg, {theme["background"]["sidebar"]} 0%, {theme["background"]["sidebar_dark"]} 100%);
            border-right: 1px solid {theme["border"]["soft"]};
        }}

        section[data-testid="stSidebar"] > div {{
            padding-top: 0.65rem;
        }}

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p {{
            color: {theme["text"]["primary"]};
        }}

        section[data-testid="stSidebar"] h2 {{
            font-size: 1.15rem;
            margin-bottom: 0.35rem;
        }}

        section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {{
            color: {theme["text"]["muted"]};
            font-size: {theme["font"]["caption_size"]};
            line-height: 1.45;
        }}

        section[data-testid="stSidebar"] [data-testid="stMetric"] {{
            background:
                linear-gradient(180deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.04) 100%);
            border: 1px solid rgba(255, 255, 255, 0.11);
            border-radius: {theme["layout"]["radius_medium"]};
            box-shadow: none;
        }}

        section[data-testid="stSidebar"] [data-testid="stMetricLabel"],
        section[data-testid="stSidebar"] [data-testid="stMetricLabel"] p {{
            color: {theme["text"]["secondary"]} !important;
            opacity: 1 !important;
            font-weight: 750 !important;
        }}

        section[data-testid="stSidebar"] [data-testid="stMetricValue"],
        section[data-testid="stSidebar"] [data-testid="stMetricValue"] div {{
            color: {theme["text"]["primary"]} !important;
            opacity: 1 !important;
            font-weight: 850 !important;
        }}

        section[data-testid="stSidebar"] div[data-testid="stExpander"] {{
            background-color: rgba(255, 255, 255, 0.035);
            border: 1px solid rgba(255, 255, 255, 0.10);
            border-radius: {theme["layout"]["radius_medium"]};
            overflow: hidden;
            margin-bottom: 0.7rem;
        }}

        section[data-testid="stSidebar"] div[data-testid="stExpander"] summary {{
            color: {theme["text"]["primary"]};
            font-weight: 800;
            font-size: 0.95rem;
            background: rgba(255, 255, 255, 0.035);
            padding-top: 0.7rem;
            padding-bottom: 0.7rem;
        }}

        section[data-testid="stSidebar"] [data-baseweb="select"] {{
            background-color: {theme["filters"]["input_background"]};
            border-radius: {theme["layout"]["radius_medium"]};
            border-color: {theme["filters"]["input_border"]};
            min-height: 42px;
        }}

        section[data-testid="stSidebar"] [data-baseweb="select"] div {{
            color: {theme["text"]["primary"]} !important;
        }}

        section[data-testid="stSidebar"] [data-baseweb="select"] input {{
            color: {theme["text"]["primary"]} !important;
        }}

        section[data-testid="stSidebar"] [data-baseweb="select"]:focus-within {{
            border-color: {theme["filters"]["input_focus"]};
            box-shadow: 0 0 0 2px rgba(118, 199, 232, 0.18);
        }}

        section[data-testid="stSidebar"] [data-baseweb="tag"] {{
            background: {theme["filters"]["selected_background"]} !important;
            color: {theme["filters"]["selected_text"]} !important;
            border-radius: {theme["layout"]["radius_pill"]};
            font-weight: 750;
            border: 1px solid {theme["filters"]["selected_border"]};
        }}

        section[data-testid="stSidebar"] [data-baseweb="tag"] span {{
            color: {theme["filters"]["selected_text"]} !important;
        }}

        section[data-testid="stSidebar"] [data-baseweb="tag"]:hover {{
            background: {theme["filters"]["selected_hover"]} !important;
        }}

        section[data-testid="stSidebar"] svg {{
            color: {theme["text"]["secondary"]};
        }}

        /* -----------------------------
           Dashboard Header
        ------------------------------ */

        .dashboard-header {{
            position: relative;
            overflow: hidden;
            width: 100%;
            box-sizing: border-box;
            margin-left: 0;
            margin-right: 0;
            background:
                radial-gradient(circle at 88% 18%, rgba(255, 209, 102, 0.26), transparent 21%),
                radial-gradient(circle at 78% 86%, rgba(118, 199, 232, 0.14), transparent 27%),
                linear-gradient(120deg, #111827 0%, {theme["brand"]["primary_dark"]} 53%, {theme["brand"]["primary"]} 100%);
            padding: 1.75rem 2rem;
            border-radius: {theme["layout"]["radius_large"]};
            margin-bottom: 1rem;
            box-shadow: {theme["layout"]["shadow_soft"]};
            border: 1px solid rgba(255, 255, 255, 0.10);
        }}

        .dashboard-header::before {{
            content: "";
            position: absolute;
            width: 330px;
            height: 330px;
            right: -130px;
            top: -150px;
            background: rgba(255, 255, 255, 0.07);
            border-radius: 999px;
            animation: terpPulse 8s ease-in-out infinite;
        }}

        .dashboard-header::after {{
            content: "";
            position: absolute;
            width: 190px;
            height: 190px;
            right: 112px;
            bottom: -112px;
            background: rgba(255, 209, 102, 0.11);
            border-radius: 999px;
            animation: terpFloatSoft 7s ease-in-out infinite;
        }}

        .header-content {{
            position: relative;
            z-index: 2;
        }}

        .header-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1.4rem;
        }}

        .header-main {{
            max-width: 980px;
            flex: 1;
        }}

        .header-kicker {{
            display: inline-flex;
            align-items: center;
            gap: 0.55rem;
            background: rgba(255, 255, 255, 0.11);
            border: 1px solid rgba(255, 255, 255, 0.18);
            color: #FFFFFF;
            padding: 0.42rem 0.78rem;
            border-radius: {theme["layout"]["radius_pill"]};
            font-size: 0.76rem;
            font-weight: 800;
            letter-spacing: 0.045em;
            text-transform: uppercase;
            margin-bottom: 0.85rem;
            backdrop-filter: blur(10px);
        }}

        .dashboard-header h1 {{
            color: {theme["text"]["primary"]};
            font-size: {theme["font"]["title_size"]};
            line-height: 1.04;
            margin-bottom: 0.7rem;
            letter-spacing: -0.06em;
            font-weight: 900;
        }}

        .dashboard-header p {{
            color: {theme["text"]["secondary"]};
            font-size: {theme["font"]["subtitle_size"]};
            margin-bottom: 0;
            max-width: 980px;
            line-height: 1.55;
        }}

        .header-inline-badge {{
            color: #FFE5A1;
            font-weight: 850;
            margin-right: 0.35rem;
        }}

        .header-visual {{
            position: relative;
            min-width: 198px;
            width: 198px;
            height: 142px;
            border-radius: 28px;
            background:
                linear-gradient(160deg, rgba(255,255,255,0.20) 0%, rgba(255,255,255,0.055) 100%);
            border: 1px solid rgba(255,255,255,0.16);
            box-shadow:
                0 18px 38px rgba(0, 0, 0, 0.22),
                inset 0 1px 0 rgba(255,255,255,0.14);
            backdrop-filter: blur(10px);
            overflow: hidden;
        }}

        .header-visual::before {{
            content: "";
            position: absolute;
            width: 110px;
            height: 110px;
            right: -22px;
            top: -20px;
            background: radial-gradient(circle, rgba(255,255,255,0.34) 0%, rgba(255,255,255,0.03) 62%, transparent 70%);
            border-radius: 999px;
        }}

        .visual-floor {{
            position: absolute;
            left: 0;
            right: 0;
            bottom: 18px;
            height: 14px;
            background: linear-gradient(90deg, rgba(255,255,255,0.12), rgba(255,209,102,0.28), rgba(255,255,255,0.12));
            filter: blur(0.2px);
        }}

        .visual-car {{
            position: absolute;
            left: 34px;
            bottom: 35px;
            width: 95px;
            height: 38px;
            animation: patrolMove 6s ease-in-out infinite;
        }}

        .visual-car-body {{
            position: absolute;
            bottom: 7px;
            left: 0;
            width: 95px;
            height: 24px;
            border-radius: 14px 16px 10px 10px;
            background: linear-gradient(135deg, #FFE08A 0%, #F2A23A 65%, #E77761 100%);
            box-shadow: 0 8px 18px rgba(0,0,0,0.22);
        }}

        .visual-car-top {{
            position: absolute;
            left: 18px;
            bottom: 24px;
            width: 42px;
            height: 14px;
            border-radius: 10px 10px 4px 4px;
            background: linear-gradient(135deg, #F8FAFC 0%, #DDE7F2 100%);
        }}

        .visual-window {{
            position: absolute;
            left: 24px;
            bottom: 27px;
            width: 16px;
            height: 8px;
            border-radius: 4px;
            background: rgba(17,24,39,0.55);
        }}

        .visual-beacon {{
            position: absolute;
            left: 42px;
            bottom: 37px;
            width: 10px;
            height: 8px;
            border-radius: 4px 4px 2px 2px;
            background: linear-gradient(135deg, #93C5FD 0%, #EF4444 100%);
            box-shadow: 0 0 12px rgba(255,255,255,0.55);
            animation: beaconBlink 1.2s ease-in-out infinite;
        }}

        .visual-wheel {{
            position: absolute;
            bottom: 0;
            width: 16px;
            height: 16px;
            border-radius: 999px;
            background: #111827;
            box-shadow: inset 0 0 0 4px #475569;
        }}

        .visual-wheel.left {{
            left: 16px;
        }}

        .visual-wheel.right {{
            right: 12px;
        }}

        .visual-shield {{
            position: absolute;
            right: 22px;
            top: 24px;
            width: 62px;
            height: 74px;
            background: linear-gradient(180deg, rgba(30,41,59,0.95) 0%, rgba(71,85,105,0.95) 100%);
            clip-path: polygon(50% 0%, 92% 12%, 96% 42%, 84% 83%, 50% 100%, 16% 83%, 4% 42%, 8% 12%);
            box-shadow: 0 12px 22px rgba(0,0,0,0.22);
            animation: terpFloatSoft 5s ease-in-out infinite;
        }}

        .visual-star {{
            position: absolute;
            left: 50%;
            top: 50%;
            width: 30px;
            height: 30px;
            transform: translate(-50%, -42%);
            background: linear-gradient(135deg, #FFE08A 0%, #F2A23A 100%);
            clip-path: polygon(50% 0%, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%);
        }}

        .visual-scan {{
            position: absolute;
            left: 118px;
            bottom: 38px;
            width: 34px;
            height: 34px;
            border-radius: 999px;
            border: 2px solid rgba(255,255,255,0.62);
            box-shadow: 0 0 0 6px rgba(255,255,255,0.05);
            animation: scanPulse 2.3s ease-in-out infinite;
        }}

        .visual-scan::after {{
            content: "";
            position: absolute;
            width: 16px;
            height: 3px;
            border-radius: 999px;
            background: rgba(255,255,255,0.72);
            transform: rotate(42deg);
            right: -9px;
            bottom: -5px;
        }}

        /* -----------------------------
           Sticky Tabs
        ------------------------------ */

        .stTabs [data-baseweb="tab-list"] {{
            position: sticky;
            top: 0;
            z-index: 999;
            gap: 0.45rem;
            border-bottom: 1px solid {theme["border"]["soft"]};
            flex-wrap: wrap;
            background:
                linear-gradient(180deg, {theme["tabs"]["sticky_background"]} 0%, rgba(11, 17, 28, 0.84) 100%);
            backdrop-filter: blur(14px);
            padding: 0.65rem 0 0.1rem 0;
            margin-bottom: 0.85rem;
        }}

        .stTabs [data-baseweb="tab"] {{
            background-color: {theme["tabs"]["background"]};
            color: {theme["tabs"]["text"]};
            border-radius: 12px 12px 0 0;
            padding: 0.7rem 1.1rem;
            border: 1px solid {theme["border"]["light"]};
            font-weight: 800;
            transition: background-color 0.15s ease, color 0.15s ease, transform 0.15s ease, border-color 0.15s ease;
        }}

        .stTabs [data-baseweb="tab"]:hover {{
            background-color: {theme["tabs"]["background_hover"]};
            transform: translateY(-1px);
        }}

        .stTabs [aria-selected="true"] {{
            background: {theme["tabs"]["selected_background"]};
            color: {theme["tabs"]["selected_text"]};
            border-color: {theme["tabs"]["selected_border"]};
            box-shadow: inset 0 -3px 0 {theme["tabs"]["selected_border"]};
        }}

        /* -----------------------------
           Notes, Insights, Cards
        ------------------------------ */

        .section-note {{
            background:
                linear-gradient(90deg, {theme["background"]["card"]} 0%, {theme["background"]["card_alt"]} 100%);
            border-left: 5px solid {theme["brand"]["primary_muted"]};
            padding: 0.82rem 1rem;
            border-radius: {theme["layout"]["radius_small"]};
            margin-bottom: 0.95rem;
            color: {theme["text"]["on_card"]};
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.055);
            line-height: 1.48;
        }}

        .section-note strong {{
            color: {theme["brand"]["primary_dark"]};
        }}

        .insight-box {{
            background:
                linear-gradient(90deg, {theme["background"]["insight"]} 0%, {theme["background"]["insight_alt"]} 100%);
            border-left: 5px solid {theme["semantic"]["attention"]};
            padding: 0.78rem 0.95rem;
            border-radius: {theme["layout"]["radius_small"]};
            margin-top: 0.4rem;
            margin-bottom: 0.9rem;
            color: {theme["text"]["on_card"]};
            font-size: {theme["font"]["body_size"]};
            line-height: 1.45;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
        }}

        .insight-box strong {{
            color: {theme["brand"]["primary_dark"]};
            font-weight: 850;
        }}

        .insight-keyword {{
            color: {theme["text"]["dark"]};
            font-weight: 850;
            background: rgba(255, 209, 102, 0.28);
            border-radius: 6px;
            padding: 0.02rem 0.22rem;
        }}

        .mini-info {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 1.05rem;
            height: 1.05rem;
            border-radius: 999px;
            background: rgba(118, 199, 232, 0.12);
            color: {theme["brand"]["accent"]};
            border: 1px solid rgba(118, 199, 232, 0.35);
            font-size: 0.72rem;
            font-weight: 800;
            margin-left: 0.35rem;
            cursor: help;
        }}

        div[data-testid="stMetric"] {{
            background:
                linear-gradient(180deg, {theme["background"]["card_alt"]} 0%, {theme["background"]["card"]} 100%);
            padding: 0.82rem 0.9rem;
            border-radius: {theme["layout"]["radius_medium"]};
            border: 1px solid {theme["border"]["extra_light"]};
            box-shadow: {theme["layout"]["shadow_card"]};
            transition: transform 0.16s ease, box-shadow 0.16s ease, border-color 0.16s ease;
            min-height: 92px;
        }}

        div[data-testid="stMetric"]:hover {{
            transform: translateY(-2px);
            box-shadow: {theme["layout"]["shadow_hover"]};
            border-color: rgba(185, 74, 97, 0.25);
        }}

        div[data-testid="stMetricLabel"] {{
            font-size: {theme["font"]["metric_label_size"]};
            color: {theme["text"]["on_card_muted"]} !important;
            font-weight: 800;
            opacity: 1 !important;
        }}

        div[data-testid="stMetricLabel"] p {{
            color: {theme["text"]["on_card_muted"]} !important;
            opacity: 1 !important;
            font-weight: 800 !important;
        }}

        div[data-testid="stMetricValue"] {{
            font-size: {theme["font"]["metric_value_size"]};
            color: {theme["text"]["dark"]} !important;
            font-weight: 900;
            letter-spacing: -0.035em;
            opacity: 1 !important;
        }}

        div[data-testid="stMetricValue"] div {{
            color: {theme["text"]["dark"]} !important;
            opacity: 1 !important;
        }}

        div[data-testid="stMetricDelta"] {{
            color: {theme["text"]["on_card_muted"]} !important;
        }}

        div[data-testid="stDataFrame"] {{
            border-radius: {theme["layout"]["radius_medium"]};
            overflow: hidden;
            border: 1px solid {theme["border"]["soft"]};
        }}

        button[kind="secondary"] {{
            border-radius: {theme["layout"]["radius_small"]};
        }}

        div[data-testid="stExpander"] {{
            border-radius: {theme["layout"]["radius_medium"]};
            border-color: {theme["border"]["soft"]};
            background: rgba(255, 255, 255, 0.02);
        }}

        div[data-testid="stExpander"] summary {{
            font-weight: 800;
            color: {theme["text"]["primary"]};
        }}

        hr {{
            border-color: {theme["border"]["soft"]};
            margin-top: 1.2rem;
            margin-bottom: 1.2rem;
        }}

        .compact-record-note {{
            color: {theme["text"]["muted"]};
            font-size: {theme["font"]["small_size"]};
            margin-top: -0.3rem;
            margin-bottom: 0.6rem;
        }}

        /* -----------------------------
           Animations
        ------------------------------ */

        @keyframes terpFloatSoft {{
            0% {{
                transform: translateY(0px);
            }}
            50% {{
                transform: translateY(-6px);
            }}
            100% {{
                transform: translateY(0px);
            }}
        }}

        @keyframes terpPulse {{
            0% {{
                transform: scale(1);
                opacity: 0.9;
            }}
            50% {{
                transform: scale(1.06);
                opacity: 0.72;
            }}
            100% {{
                transform: scale(1);
                opacity: 0.9;
            }}
        }}

        @keyframes beaconBlink {{
            0% {{
                opacity: 0.45;
                box-shadow: 0 0 6px rgba(255,255,255,0.15);
            }}
            50% {{
                opacity: 1;
                box-shadow: 0 0 15px rgba(255,255,255,0.6);
            }}
            100% {{
                opacity: 0.45;
                box-shadow: 0 0 6px rgba(255,255,255,0.15);
            }}
        }}

        @keyframes patrolMove {{
            0% {{
                transform: translateX(0px);
            }}
            50% {{
                transform: translateX(9px);
            }}
            100% {{
                transform: translateX(0px);
            }}
        }}

        @keyframes scanPulse {{
            0% {{
                transform: scale(0.95);
                opacity: 0.65;
            }}
            50% {{
                transform: scale(1.08);
                opacity: 1;
            }}
            100% {{
                transform: scale(0.95);
                opacity: 0.65;
            }}
        }}

        /* -----------------------------
           Responsive
        ------------------------------ */

        @media (max-width: 980px) {{
            .header-row {{
                flex-direction: column;
                align-items: flex-start;
            }}

            .header-visual {{
                width: 170px;
                height: 126px;
            }}

            .dashboard-header h1 {{
                font-size: 2rem;
            }}
        }}

        @media (max-width: 900px) {{
            .block-container {{
                padding-left: 0.8rem;
                padding-right: 0.8rem;
            }}
        }}

        @media (max-width: 640px) {{
            .header-visual {{
                display: none;
            }}

            .dashboard-header {{
                padding: 1.35rem 1.1rem;
            }}

            .dashboard-header h1 {{
                font-size: 1.75rem;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


def show_dashboard_header():
    """Display the main dashboard header."""
    theme = get_theme()

    st.markdown(
        f"""
        <div class="dashboard-header">
            <div class="header-content">
                <div class="header-row">
                    <div class="header-main">
                        <div class="header-kicker">{theme["copy"]["dashboard_label"]}</div>
                        <h1>{theme["copy"]["dashboard_title"]}</h1>
                        <p><span class="header-inline-badge">DBMS-powered public safety intelligence.</span>{theme["copy"]["dashboard_subtitle"].replace("DBMS-powered public safety intelligence for ", "").capitalize()}</p>
                    </div>
                    <div class="header-visual">
                        <div class="visual-shield">
                            <div class="visual-star"></div>
                        </div>
                        <div class="visual-car">
                            <div class="visual-car-top"></div>
                            <div class="visual-window"></div>
                            <div class="visual-beacon"></div>
                            <div class="visual-car-body"></div>
                            <div class="visual-wheel left"></div>
                            <div class="visual-wheel right"></div>
                        </div>
                        <div class="visual-scan"></div>
                        <div class="visual-floor"></div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def highlight_keywords(text):
    """Bold and softly highlight important keywords in insight text."""
    safe_text = html.escape(text)

    keywords = [
        "highest",
        "leading",
        "most common",
        "average",
        "arrest-related",
        "matched",
        "valid",
        "invalid",
        "same-day",
        "same day",
        "over 7 days",
        "closed",
        "cleared",
        "pending",
        "active"
    ]

    for keyword in sorted(keywords, key=len, reverse=True):
        pattern = re.compile(rf"\\b({re.escape(keyword)})\\b", re.IGNORECASE)
        safe_text = pattern.sub(
            r'<span class="insight-keyword">\\1</span>',
            safe_text
        )

    return safe_text


def show_section_note(text):
    """Display a short styled note under a section heading."""
    safe_text = html.escape(text)

    st.markdown(
        f"""
        <div class="section-note">
            {safe_text}
        </div>
        """,
        unsafe_allow_html=True
    )


def show_insight(text):
    """Display a short analytical insight below a chart or section."""
    highlighted_text = highlight_keywords(text)

    st.markdown(
        f"""
        <div class="insight-box">
            <strong>Insight:</strong> {highlighted_text}
        </div>
        """,
        unsafe_allow_html=True
    )


def show_info_hint(label, help_text):
    """
    Display a compact label with an information icon.

    Use this for helpful explanatory text that should not clutter the screen.
    """
    safe_label = html.escape(label)
    safe_help = html.escape(help_text)

    st.markdown(
        f"""
        <span>{safe_label}</span>
        <span class="mini-info" title="{safe_help}">i</span>
        """,
        unsafe_allow_html=True
    )


def show_compact_record_note(text):
    """Display a small muted note above compact record tables."""
    safe_text = html.escape(text)

    st.markdown(
        f"""
        <div class="compact-record-note">
            {safe_text}
        </div>
        """,
        unsafe_allow_html=True
    )