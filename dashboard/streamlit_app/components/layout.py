"""
layout.py

Shared visual components and styling for the Terp Protect dashboard.

Responsibilities:
- Apply global dashboard styling
- Display the dashboard header
- Display compact section banners
- Display reusable notes and insight messages
- Display sidebar filter summaries and help
- Display compact overview cards
- Display metric-definition tooltips
- Display contextual Data Review Panel help
"""

import html
import re

import streamlit as st

from components.metrics import get_metric_help
from components.theme import get_theme


def apply_custom_styles():
    """
    Apply global Streamlit styling.
    """
    theme = get_theme()

    st.markdown(
        f"""
<style>
html,
body,
[class*="css"] {{
    font-family: {theme["font"]["family"]};
}}

.stApp {{
    color: {theme["text"]["primary"]};

    background:
        radial-gradient(
            circle at 5% 5%,
            rgba(200, 16, 46, 0.10),
            transparent 24%
        ),
        radial-gradient(
            circle at 94% 9%,
            rgba(118, 199, 232, 0.08),
            transparent 25%
        ),
        linear-gradient(
            135deg,
            {theme["background"]["app_gradient_start"]} 0%,
            {theme["background"]["app_gradient_mid"]} 48%,
            {theme["background"]["app_gradient_end"]} 100%
        );
}}

.block-container {{
    width: 100% !important;
    max-width: none !important;

    padding-top: 1rem;
    padding-right: 1rem;
    padding-bottom: 2rem;
    padding-left: 1rem;
}}

h1,
h2,
h3,
h4 {{
    color: {theme["text"]["primary"]};
    letter-spacing: -0.035em;
}}

p,
span,
label {{
    font-family: {theme["font"]["family"]};
}}

/* ---------------------------------
   Sidebar
---------------------------------- */

section[data-testid="stSidebar"] {{
    background:
        radial-gradient(
            circle at top left,
            rgba(200, 16, 46, 0.11),
            transparent 28%
        ),
        linear-gradient(
            180deg,
            {theme["background"]["sidebar"]} 0%,
            {theme["background"]["sidebar_dark"]} 100%
        );

    border-right:
        1px solid {theme["border"]["soft"]};
}}

section[data-testid="stSidebar"] > div {{
    padding-top: 0.45rem;
}}

section[data-testid="stSidebar"] hr {{
    margin-top: 0.8rem;
    margin-bottom: 0.8rem;
}}

.sidebar-filter-heading {{
    margin-top: 0.15rem;
    margin-bottom: 0.2rem;

    color: {theme["text"]["primary"]};

    font-size: 1.25rem;
    font-weight: 850;
    letter-spacing: -0.035em;
}}

/* ---------------------------------
   Filter help
---------------------------------- */

.filter-help-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.55rem;

    margin-bottom: 0.7rem;
}}

.filter-help-label {{
    color: {theme["text"]["muted"]};

    font-size: 0.69rem;
    line-height: 1.35;
}}

.filter-help-tooltip {{
    position: relative;

    display: inline-flex;
    flex-shrink: 0;
}}

.filter-help-icon {{
    display: inline-flex;
    align-items: center;
    justify-content: center;

    width: 1.3rem;
    height: 1.3rem;

    color: {theme["text"]["secondary"]};
    background: rgba(255, 255, 255, 0.04);

    border:
        1px solid rgba(148, 163, 184, 0.78);
    border-radius: 999px;

    font-size: 0.75rem;
    font-weight: 850;

    cursor: help;
}}

.filter-help-tooltip-text {{
    position: absolute;
    top: 1.7rem;
    right: 0;
    z-index: 999999;

    width: 230px;
    padding: 0.65rem 0.75rem;

    visibility: hidden;
    opacity: 0;

    color: #172033;
    background: #F8FAFC;

    border: 1px solid #D9E2EC;
    border-radius: 10px;

    box-shadow:
        0 12px 28px rgba(0, 0, 0, 0.28);

    font-size: 0.7rem;
    font-weight: 500;
    line-height: 1.45;

    transition:
        visibility 0.15s ease,
        opacity 0.15s ease;
}}

.filter-help-tooltip:hover
.filter-help-tooltip-text {{
    visibility: visible;
    opacity: 1;
}}

/* ---------------------------------
   Filter expanders
---------------------------------- */

section[data-testid="stSidebar"]
div[data-testid="stExpander"] {{
    overflow: visible;

    margin-bottom: 0.55rem;

    background: rgba(255, 255, 255, 0.025);

    border:
        1px solid rgba(255, 255, 255, 0.10);
    border-radius: 13px;
}}

section[data-testid="stSidebar"]
div[data-testid="stExpander"] summary {{
    padding-top: 0.52rem;
    padding-bottom: 0.52rem;

    color: {theme["text"]["primary"]};
    background: rgba(255, 255, 255, 0.02);

    font-size: 0.82rem;
    font-weight: 780;
}}

section[data-testid="stSidebar"]
div[data-testid="stExpanderDetails"] {{
    padding-top: 0.15rem;
}}

/* ---------------------------------
   Filter labels and inputs
---------------------------------- */

section[data-testid="stSidebar"]
[data-testid="stWidgetLabel"] {{
    margin-bottom: 0.15rem;
}}

section[data-testid="stSidebar"]
[data-testid="stWidgetLabel"] p {{
    color: {theme["text"]["primary"]} !important;

    font-size: 0.7rem !important;
    font-weight: 680 !important;
    line-height: 1.2 !important;
}}

section[data-testid="stSidebar"]
div[data-testid="stMultiSelect"] {{
    margin-bottom: 0.4rem;
}}

section[data-testid="stSidebar"]
[data-baseweb="select"] {{
    min-height: 36px;

    color: {theme["text"]["primary"]};
    background: {theme["filters"]["input_background"]};

    border-color: {theme["filters"]["input_border"]};
    border-radius: 11px;

    font-size: 0.7rem;
}}

section[data-testid="stSidebar"]
[data-baseweb="select"] > div {{
    min-height: 36px;
}}

section[data-testid="stSidebar"]
[data-baseweb="select"] div {{
    color: {theme["text"]["primary"]} !important;
}}

section[data-testid="stSidebar"]
[data-baseweb="select"] input {{
    color: {theme["text"]["primary"]} !important;
    font-size: 0.7rem !important;
}}

section[data-testid="stSidebar"]
[data-baseweb="select"] input::placeholder {{
    color: {theme["text"]["secondary"]} !important;
    opacity: 0.9;
    font-size: 0.7rem !important;
}}

section[data-testid="stSidebar"]
[data-baseweb="select"]:focus-within {{
    border-color: {theme["filters"]["input_focus"]};

    box-shadow:
        0 0 0 2px rgba(118, 199, 232, 0.15);
}}

section[data-testid="stSidebar"]
[data-baseweb="select"] > div > div {{
    flex-wrap: wrap !important;
    row-gap: 0.25rem !important;
}}

/* Selected values */

section[data-testid="stSidebar"]
[data-baseweb="tag"] {{
    max-width: 100% !important;
    min-height: 1.4rem !important;
    height: auto !important;

    margin-top: 0.05rem !important;
    margin-bottom: 0.05rem !important;

    padding-top: 0.14rem !important;
    padding-bottom: 0.14rem !important;

    color:
        {theme["filters"]["selected_text"]}
        !important;

    background:
        {theme["filters"]["selected_background"]}
        !important;

    border:
        1px solid
        {theme["filters"]["selected_border"]};

    border-radius: 999px !important;

    font-size: 0.62rem !important;
    font-weight: 720 !important;
    line-height: 1.15 !important;
}}

section[data-testid="stSidebar"]
[data-baseweb="tag"] span {{
    max-width: 190px !important;

    overflow: visible !important;

    color:
        {theme["filters"]["selected_text"]}
        !important;

    font-size: 0.62rem !important;
    line-height: 1.15 !important;

    white-space: normal !important;
    text-overflow: unset !important;
}}

section[data-testid="stSidebar"]
[data-baseweb="tag"] svg {{
    width: 0.72rem !important;
    height: 0.72rem !important;

    flex-shrink: 0;
}}

/* Dropdown menu */

div[data-baseweb="popover"] {{
    z-index: 999999 !important;
}}

div[data-baseweb="popover"]
ul[role="listbox"] {{
    padding-top: 0.2rem !important;
    padding-bottom: 0.2rem !important;

    background: #0C111A !important;

    border: 1px solid #334155 !important;
    border-radius: 11px !important;
}}

div[data-baseweb="popover"]
li[role="option"] {{
    min-height: 1.9rem !important;

    padding:
        0.4rem
        0.65rem
        !important;

    color: #F8FAFC !important;
    background: #0C111A !important;

    font-size: 0.68rem !important;
    line-height: 1.3 !important;
}}

div[data-baseweb="popover"]
li[role="option"]:hover {{
    background: #242A36 !important;
}}

div[data-baseweb="popover"]
li[aria-selected="true"] {{
    background: #2A303D !important;
}}

/* ---------------------------------
   Filter summary
---------------------------------- */

.filter-summary-title {{
    margin-bottom: 0.45rem;

    color: {theme["text"]["primary"]};

    font-size: 0.78rem;
    font-weight: 800;
}}

.filter-summary-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.4rem;
}}

.filter-summary-card {{
    min-width: 0;
    padding: 0.58rem;

    background:
        linear-gradient(
            180deg,
            rgba(255, 255, 255, 0.065) 0%,
            rgba(255, 255, 255, 0.025) 100%
        );

    border:
        1px solid rgba(255, 255, 255, 0.10);
    border-radius: 11px;
}}

.filter-summary-card.filtered {{
    border-color:
        rgba(217, 96, 115, 0.48);
}}

.filter-summary-label {{
    margin-bottom: 0.2rem;

    color: {theme["text"]["secondary"]};

    font-size: 0.58rem;
    font-weight: 700;
    line-height: 1.2;
}}

.filter-summary-value {{
    color: {theme["text"]["primary"]};

    font-size: 1rem;
    font-weight: 900;
    line-height: 1;
    letter-spacing: -0.035em;
}}

.filter-active-count {{
    margin-top: 0.45rem;

    color: {theme["text"]["muted"]};

    font-size: 0.63rem;
}}

/* ---------------------------------
   Main dashboard header
---------------------------------- */

.dashboard-header {{
    position: relative;

    width: 100%;
    box-sizing: border-box;
    overflow: hidden;

    margin-bottom: 0.8rem;
    padding: 1.45rem 1.75rem;

    background:
        radial-gradient(
            circle at 88% 18%,
            rgba(255, 209, 102, 0.24),
            transparent 21%
        ),
        radial-gradient(
            circle at 78% 86%,
            rgba(118, 199, 232, 0.12),
            transparent 27%
        ),
        linear-gradient(
            120deg,
            #111827 0%,
            {theme["brand"]["primary_dark"]} 53%,
            {theme["brand"]["primary"]} 100%
        );

    border:
        1px solid rgba(255, 255, 255, 0.10);
    border-radius: {theme["layout"]["radius_large"]};

    box-shadow: {theme["layout"]["shadow_soft"]};
}}

.header-row {{
    position: relative;
    z-index: 2;

    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1.25rem;
}}

.header-main {{
    max-width: 980px;
    flex: 1;
}}

.header-kicker {{
    display: inline-flex;
    align-items: center;

    margin-bottom: 0.7rem;
    padding: 0.35rem 0.7rem;

    color: #FFFFFF;
    background: rgba(255, 255, 255, 0.11);

    border:
        1px solid rgba(255, 255, 255, 0.18);
    border-radius: 999px;

    font-size: 0.67rem;
    font-weight: 800;
    letter-spacing: 0.045em;
    text-transform: uppercase;
}}

.dashboard-header h1 {{
    margin-bottom: 0.55rem;

    color: {theme["text"]["primary"]};

    font-size: 2rem;
    font-weight: 900;
    line-height: 1.05;
    letter-spacing: -0.055em;
}}

.dashboard-header p {{
    max-width: 980px;
    margin-bottom: 0;

    color: {theme["text"]["secondary"]};

    font-size: 0.88rem;
    line-height: 1.5;
}}

.header-inline-badge {{
    margin-right: 0.3rem;

    color: #FFE5A1;

    font-weight: 850;
}}

.header-visual {{
    position: relative;

    width: 170px;
    min-width: 170px;
    height: 118px;

    overflow: hidden;

    background:
        linear-gradient(
            160deg,
            rgba(255, 255, 255, 0.20) 0%,
            rgba(255, 255, 255, 0.055) 100%
        );

    border:
        1px solid rgba(255, 255, 255, 0.16);
    border-radius: 24px;

    box-shadow:
        0 16px 34px rgba(0, 0, 0, 0.22);
}}

.visual-floor {{
    position: absolute;
    right: 0;
    bottom: 15px;
    left: 0;

    height: 12px;

    background:
        linear-gradient(
            90deg,
            rgba(255, 255, 255, 0.10),
            rgba(255, 209, 102, 0.27),
            rgba(255, 255, 255, 0.10)
        );
}}

.visual-car {{
    position: absolute;
    bottom: 29px;
    left: 27px;

    width: 82px;
    height: 34px;
}}

.visual-car-body {{
    position: absolute;
    bottom: 6px;
    left: 0;

    width: 82px;
    height: 21px;

    background:
        linear-gradient(
            135deg,
            #FFE08A 0%,
            #F2A23A 65%,
            #E77761 100%
        );

    border-radius: 13px 15px 9px 9px;

    box-shadow:
        0 7px 15px rgba(0, 0, 0, 0.22);
}}

.visual-car-top {{
    position: absolute;
    bottom: 21px;
    left: 16px;

    width: 37px;
    height: 12px;

    background: #E9EFF6;
    border-radius: 9px 9px 3px 3px;
}}

.visual-window {{
    position: absolute;
    bottom: 24px;
    left: 21px;

    width: 14px;
    height: 7px;

    background:
        rgba(17, 24, 39, 0.56);

    border-radius: 3px;
}}

.visual-beacon {{
    position: absolute;
    bottom: 32px;
    left: 36px;

    width: 9px;
    height: 7px;

    background:
        linear-gradient(
            135deg,
            #93C5FD,
            #EF4444
        );

    border-radius: 4px 4px 2px 2px;
}}

.visual-wheel {{
    position: absolute;
    bottom: 0;

    width: 14px;
    height: 14px;

    background: #111827;

    border-radius: 999px;

    box-shadow:
        inset 0 0 0 3px #475569;
}}

.visual-wheel.left {{
    left: 14px;
}}

.visual-wheel.right {{
    right: 10px;
}}

.visual-shield {{
    position: absolute;
    top: 20px;
    right: 18px;

    width: 53px;
    height: 64px;

    background:
        linear-gradient(
            180deg,
            #1E293B,
            #475569
        );

    clip-path:
        polygon(
            50% 0%,
            92% 12%,
            96% 42%,
            84% 83%,
            50% 100%,
            16% 83%,
            4% 42%,
            8% 12%
        );
}}

.visual-star {{
    position: absolute;
    top: 50%;
    left: 50%;

    width: 26px;
    height: 26px;

    transform:
        translate(-50%, -42%);

    background:
        linear-gradient(
            135deg,
            #FFE08A,
            #F2A23A
        );

    clip-path:
        polygon(
            50% 0%,
            61% 35%,
            98% 35%,
            68% 57%,
            79% 91%,
            50% 70%,
            21% 91%,
            32% 57%,
            2% 35%,
            39% 35%
        );
}}

/* ---------------------------------
   Sticky tabs
---------------------------------- */

.stTabs [data-baseweb="tab-list"] {{
    position: sticky !important;
    top: 0 !important;
    z-index: 99999 !important;

    display: flex !important;
    flex-wrap: nowrap !important;
    gap: 0.35rem;

    width: 100%;

    overflow-x: auto;
    overflow-y: hidden;

    margin-bottom: 0.55rem;
    padding: 0.48rem 0.2rem 0.3rem;

    background:
        rgba(11, 17, 28, 0.97);

    backdrop-filter: blur(14px);
}}

.stTabs [data-baseweb="tab"] {{
    min-width: max-content;
    min-height: 38px;

    flex: 0 0 auto !important;

    padding: 0.5rem 0.85rem;

    color: {theme["tabs"]["text"]};
    background: {theme["tabs"]["background"]};

    border:
        1px solid {theme["border"]["light"]};
    border-radius: 10px 10px 0 0;

    font-size: 0.72rem;
    font-weight: 780;
    white-space: nowrap;
}}

.stTabs [data-baseweb="tab"]:hover {{
    background:
        {theme["tabs"]["background_hover"]};
}}

.stTabs [aria-selected="true"] {{
    color:
        {theme["tabs"]["selected_text"]};

    background:
        {theme["tabs"]["selected_background"]};

    border-color:
        {theme["tabs"]["selected_border"]};

    box-shadow:
        inset 0 -3px 0
        {theme["tabs"]["selected_border"]};
}}

.stTabs [data-baseweb="tab"] p {{
    margin: 0 !important;

    color: inherit !important;

    font-size: inherit !important;
    font-weight: inherit !important;
    white-space: nowrap !important;
}}

/* ---------------------------------
   Standard metric cards
---------------------------------- */

div[data-testid="stMetric"] {{
    min-height: 78px;

    padding: 0.65rem 0.75rem;

    background:
        linear-gradient(
            180deg,
            #FFFFFF 0%,
            #F4F7FA 100%
        );

    border:
        1px solid #D9E2EC;
    border-radius: 12px;

    box-shadow:
        0 5px 14px rgba(0, 0, 0, 0.08);
}}

div[data-testid="stMetric"] * {{
    color: #0F172A !important;
}}

div[data-testid="stMetricLabel"] p {{
    font-size: 0.67rem !important;
    font-weight: 720 !important;
}}

div[data-testid="stMetricValue"] {{
    font-size: 1.08rem !important;
    font-weight: 900 !important;
    letter-spacing: -0.03em;
}}

/* ---------------------------------
   Compact section banner
---------------------------------- */

.section-banner {{
    position: relative;

    display: flex;
    align-items: center;

    width: 100%;
    box-sizing: border-box;

    margin-top: 0.05rem;
    margin-bottom: 0.55rem;
    padding: 0.35rem 0.85rem 0.62rem 1rem;

    overflow: hidden;

    background:
        linear-gradient(
            100deg,
            rgba(255, 255, 255, 0.065) 0%,
            rgba(255, 255, 255, 0.025) 58%,
            rgba(200, 16, 46, 0.055) 100%
        );

    border-left:
        4px solid {theme["brand"]["primary_muted"]};

    border-radius: 11px;

    box-shadow:
        0 4px 12px rgba(0, 0, 0, 0.10);
}}

.section-banner::after {{
    content: "";

    position: absolute;
    top: -42px;
    right: -34px;

    width: 112px;
    height: 112px;

    background:
        radial-gradient(
            circle,
            rgba(200, 16, 46, 0.10) 0%,
            transparent 68%
        );

    border-radius: 999px;
}}

.section-banner-content {{
    position: relative;
    z-index: 2;

    min-width: 0;
}}

.section-banner-eyebrow {{
    margin-bottom: 0.12rem;

    color: {theme["brand"]["accent"]} !important;

    font-size: 0.56rem;
    font-weight: 850;
    line-height: 1.1;
    letter-spacing: 0.095em;
    text-transform: uppercase;
}}

.section-banner-title {{
    margin: 0;

    color: {theme["text"]["primary"]} !important;

    font-size: 1.22rem;
    font-weight: 900;
    line-height: 1.15;
    letter-spacing: -0.035em;
}}

.section-banner-description {{
    max-width: 1100px;

    color: {theme["text"]["muted"]} !important;

    font-size: 0.90rem;
    font-weight: 500;
    line-height: 1.35;
}}

/* ---------------------------------
   Compact overview strip
---------------------------------- */

.overview-strip-container {{
    width: 100%;

    margin-top: 0.15rem;
    margin-bottom: 0.6rem;

    overflow-x: auto;
    overflow-y: hidden;
}}

.overview-strip-track {{
    display: flex;
    flex-wrap: nowrap;
    gap: 0.55rem;

    min-width: max-content;

    padding-bottom: 0.2rem;

    scrollbar-width: thin;
    scrollbar-color:
        rgba(148, 163, 184, 0.40)
        transparent;
}}

.overview-strip-track::-webkit-scrollbar {{
    height: 6px;
}}

.overview-strip-track::-webkit-scrollbar-track {{
    background: transparent;
}}

.overview-strip-track::-webkit-scrollbar-thumb {{
    background:
        rgba(148, 163, 184, 0.40);

    border-radius: 999px;
}}

.overview-strip-card {{
    display: flex;
    flex: 0 0 195px;
    flex-direction: column;
    justify-content: space-between;

    min-width: 195px;
    min-height: 82px;

    padding: 0.54rem 0.68rem;

    background:
        linear-gradient(
            145deg,
            #F7F5FF 0%,
            #EEE9FF 100%
        );

    border: 1px solid #D8E0EA;
    border-radius: 11px;

    box-shadow:
        0 4px 12px rgba(0, 0, 0, 0.07);
}}

.overview-strip-card * {{
    color: #111827 !important;
}}

.overview-strip-label-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.35rem;
}}

.overview-strip-label {{
    min-width: 0;

    color: #475569 !important;

    font-size: 0.67rem;
    font-weight: 800;
    line-height: 1.12;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}}

.overview-strip-metric-help {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;

    width: 1rem;
    height: 1rem;

    color: #475569 !important;
    background: rgba(255, 255, 255, 0.58);

    border: 1px solid rgba(100, 116, 139, 0.38);
    border-radius: 999px;

    font-size: 0.61rem;
    font-weight: 850;
    line-height: 1;

    cursor: help;
}}

.overview-strip-metric-help:hover {{
    color: #0F172A !important;
    background: #FFFFFF;

    border-color: rgba(71, 85, 105, 0.65);
}}

.overview-strip-value {{
    margin-top: 0.12rem;
    margin-bottom: 0.14rem;

    color: #0F172A !important;

    font-size: 0.96rem;
    font-weight: 850;
    line-height: 1.15;
    letter-spacing: -0.02em;
    word-break: break-word;
}}

.overview-strip-value.numeric {{
    font-size: 1.12rem;
    font-weight: 900;
    letter-spacing: -0.04em;
}}

.overview-strip-footer {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.35rem;
}}

.overview-strip-meta {{
    color: #64748B !important;

    font-size: 0.62rem;
    font-weight: 650;
    line-height: 1.15;
}}

.overview-strip-badge {{
    flex-shrink: 0;

    padding: 0.14rem 0.4rem;

    color: #111827 !important;
    background:
        rgba(255, 255, 255, 0.72);

    border:
        1px solid rgba(148, 163, 184, 0.25);
    border-radius: 999px;

    font-size: 0.7rem;
    font-weight: 800;
    line-height: 1.1;
}}

/* ---------------------------------
   Notes and insights
---------------------------------- */

.section-note {{
    margin-bottom: 0.75rem;
    padding: 0.65rem 0.85rem;

    color: {theme["text"]["on_card"]};
    background:
        linear-gradient(
            90deg,
            {theme["background"]["card"]} 0%,
            {theme["background"]["card_alt"]} 100%
        );

    border-left:
        5px solid
        {theme["brand"]["primary_muted"]};
    border-radius: 9px;

    box-shadow:
        0 2px 10px rgba(0, 0, 0, 0.05);

    font-size: 0.78rem;
    line-height: 1.42;
}}

.insight-box {{
    box-sizing: border-box;
    width: 100%;

    margin-top: 0.35rem;
    margin-bottom: 0.72rem;
    padding: 0.62rem 0.8rem;

    color: {theme["text"]["on_card"]};
    background:
        linear-gradient(
            90deg,
            {theme["background"]["insight"]} 0%,
            {theme["background"]["insight_alt"]} 100%
        );

    border-left:
        5px solid
        {theme["semantic"]["attention"]};
    border-radius: 9px;

    box-shadow:
        0 2px 9px rgba(0, 0, 0, 0.04);

    font-size: 0.75rem;
    line-height: 1.4;
}}

.insight-box strong {{
    color: {theme["brand"]["primary_dark"]};

    font-weight: 850;
}}

.insight-keyword {{
    padding: 0.01rem 0.18rem;

    color: {theme["text"]["dark"]};
    background:
        rgba(255, 209, 102, 0.28);

    border-radius: 5px;

    font-weight: 850;
}}

/* ---------------------------------
   Data Review Panel heading + help
---------------------------------- */

.data-review-header {{
    display: flex;
    align-items: center;
    gap: 0.5rem;

    width: 100%;

    margin-top: 0.1rem;
    margin-bottom: 0.45rem;
}}

.data-review-title {{
    color: {theme["text"]["primary"]} !important;

    font-size: 1rem;
    font-weight: 820;
    line-height: 1.2;
    letter-spacing: -0.02em;
}}

.data-review-tooltip {{
    position: relative;

    display: inline-flex;
    align-items: center;
    flex-shrink: 0;
}}

.data-review-tooltip-icon {{
    display: inline-flex;
    align-items: center;
    justify-content: center;

    width: 1.12rem;
    height: 1.12rem;

    color: {theme["brand"]["accent"]};
    background:
        rgba(118, 199, 232, 0.12);

    border:
        1px solid rgba(118, 199, 232, 0.55);
    border-radius: 999px;

    font-size: 0.68rem;
    font-weight: 850;

    cursor: help;
}}

.data-review-tooltip-text {{
    position: absolute;
    left: 0;
    top: 1.55rem;
    z-index: 999999;

    width: 255px;
    padding: 0.68rem 0.78rem;

    visibility: hidden;
    opacity: 0;

    color: #172033 !important;
    background: #F8FAFC;

    border: 1px solid #D9E2EC;
    border-radius: 10px;

    box-shadow:
        0 12px 28px rgba(0, 0, 0, 0.28);

    font-size: 0.7rem;
    font-weight: 500;
    line-height: 1.45;

    transition:
        visibility 0.15s ease,
        opacity 0.15s ease;
}}

.data-review-tooltip:hover
.data-review-tooltip-text {{
    visibility: visible;
    opacity: 1;
}}

/* Data Review Panel expander */

.data-review-panel
div[data-testid="stExpander"] {{
    overflow: visible;

    background:
        rgba(255, 255, 255, 0.025);

    border:
        1px solid rgba(148, 163, 184, 0.24);
    border-radius: 12px;
}}

.data-review-panel
div[data-testid="stExpander"] summary {{
    min-height: 42px;

    color: {theme["text"]["primary"]};

    font-size: 0.82rem;
    font-weight: 750;
}}

.mini-info-wrapper {{
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;

    margin-bottom: 0.35rem;

    color: {theme["text"]["muted"]};

    font-size: 0.7rem;
}}

.mini-info {{
    display: inline-flex;
    align-items: center;
    justify-content: center;

    width: 1rem;
    height: 1rem;

    color: {theme["brand"]["accent"]};
    background:
        rgba(118, 199, 232, 0.12);

    border:
        1px solid rgba(118, 199, 232, 0.35);
    border-radius: 999px;

    font-size: 0.65rem;
    font-weight: 800;
    cursor: help;
}}

.compact-record-note {{
    margin-top: -0.2rem;
    margin-bottom: 0.5rem;

    color: {theme["text"]["muted"]};

    font-size: 0.72rem;
}}

/* ---------------------------------
   Dataframes and expanders
---------------------------------- */

div[data-testid="stDataFrame"] {{
    overflow: hidden;

    border:
        1px solid {theme["border"]["soft"]};
    border-radius: 12px;
}}

div[data-testid="stExpander"] {{
    background:
        rgba(255, 255, 255, 0.02);

    border-color:
        {theme["border"]["soft"]};
    border-radius: 12px;
}}

div[data-testid="stExpander"] summary {{
    color: {theme["text"]["primary"]};

    font-weight: 800;
}}

/* ---------------------------------
   Responsive behavior
---------------------------------- */

@media (max-width: 980px) {{
    .header-row {{
        align-items: flex-start;
        flex-direction: column;
    }}

    .header-visual {{
        width: 155px;
        min-width: 155px;
        height: 105px;
    }}

    .overview-strip-card {{
        flex: 0 0 205px;
        min-width: 205px;
    }}
}}

@media (max-width: 640px) {{
    .dashboard-header {{
        padding: 1.15rem;
    }}

    .dashboard-header h1 {{
        font-size: 1.55rem;
    }}

    .header-visual {{
        display: none;
    }}

    .section-banner {{
        padding:
            0.58rem
            0.68rem
            0.58rem
            0.8rem;
    }}

    .section-banner-title {{
        font-size: 1.05rem;
    }}

    .section-banner-description {{
        font-size: 0.63rem;
    }}

    .overview-strip-card {{
        flex: 0 0 185px;

        min-width: 185px;
        min-height: 78px;

        padding: 0.5rem 0.58rem;
    }}

    .overview-strip-value {{
        font-size: 0.78rem;
    }}

    .overview-strip-value.numeric {{
        font-size: 1rem;
    }}

    .data-review-tooltip-text {{
        left: auto;
        right: 0;

        width: 220px;
    }}
}}
</style>
        """,
        unsafe_allow_html=True
    )


def show_dashboard_header():
    """
    Display the main dashboard header.
    """
    theme = get_theme()

    subtitle = theme["copy"]["dashboard_subtitle"].replace(
        "DBMS-powered public safety intelligence for ",
        ""
    )

    header_html = (
        '<div class="dashboard-header">'
        '<div class="header-row">'
        '<div class="header-main">'
        '<div class="header-kicker">'
        f'{html.escape(theme["copy"]["dashboard_label"])}'
        '</div>'
        '<h1>'
        f'{html.escape(theme["copy"]["dashboard_title"])}'
        '</h1>'
        '<p>'
        '<span class="header-inline-badge">'
        'DBMS-powered public safety intelligence.'
        '</span> '
        f'{html.escape(subtitle.capitalize())}'
        '</p>'
        '</div>'
        '<div class="header-visual">'
        '<div class="visual-shield">'
        '<div class="visual-star"></div>'
        '</div>'
        '<div class="visual-car">'
        '<div class="visual-car-top"></div>'
        '<div class="visual-window"></div>'
        '<div class="visual-beacon"></div>'
        '<div class="visual-car-body"></div>'
        '<div class="visual-wheel left"></div>'
        '<div class="visual-wheel right"></div>'
        '</div>'
        '<div class="visual-floor"></div>'
        '</div>'
        '</div>'
        '</div>'
    )

    st.markdown(
        header_html,
        unsafe_allow_html=True
    )


def show_filter_summary(
    total_records,
    filtered_records,
    active_filter_count
):
    """
    Display available and filtered incident counts together.
    """
    filter_word = (
        "filter group"
        if active_filter_count == 1
        else "filter groups"
    )

    summary_html = (
        '<div class="filter-summary-title">'
        'Incident View'
        '</div>'
        '<div class="filter-summary-grid">'
        '<div class="filter-summary-card">'
        '<div class="filter-summary-label">'
        'Available'
        '</div>'
        '<div class="filter-summary-value">'
        f'{total_records:,}'
        '</div>'
        '</div>'
        '<div class="filter-summary-card filtered">'
        '<div class="filter-summary-label">'
        'Filtered'
        '</div>'
        '<div class="filter-summary-value">'
        f'{filtered_records:,}'
        '</div>'
        '</div>'
        '</div>'
        '<div class="filter-active-count">'
        f'{active_filter_count} active {filter_word}'
        '</div>'
    )

    st.markdown(
        summary_html,
        unsafe_allow_html=True
    )


def show_section_banner(
    title,
    description,
    eyebrow=""
):
    """
    Display a compact section banner.
    """
    safe_eyebrow = html.escape(
        str(eyebrow)
    )

    safe_title = html.escape(
        str(title)
    )

    safe_description = html.escape(
        str(description)
    )

    eyebrow_html = ""

    if safe_eyebrow:
        eyebrow_html = (
            '<div class="section-banner-eyebrow">'
            f'{safe_eyebrow}'
            '</div>'
        )

    banner_html = (
        '<div class="section-banner">'
        '<div class="section-banner-content">'
        f'{eyebrow_html}'
        '<h3 class="section-banner-title">'
        f'{safe_title}'
        '</h3>'
        '<div class="section-banner-description">'
        f'{safe_description}'
        '</div>'
        '</div>'
        '</div>'
    )

    st.markdown(
        banner_html,
        unsafe_allow_html=True
    )


def show_compact_overview_strip(items):
    """
    Display compact overview cards in one horizontal row.

    Supported item properties:
    - label: visible metric label
    - value: visible metric value
    - meta: optional supporting text
    - badge: optional count or status badge
    - numeric: whether the value should use numeric styling
    - metric_key: optional key from METRIC_DEFINITIONS
    - help: optional custom tooltip text

    When both metric_key and help are provided, the custom help text
    takes precedence.
    """
    cards = []

    for item in items:
        label = html.escape(
            str(
                item.get(
                    "label",
                    ""
                )
            )
        )

        value = html.escape(
            str(
                item.get(
                    "value",
                    ""
                )
            )
        )

        meta = html.escape(
            str(
                item.get(
                    "meta",
                    ""
                )
            )
        )

        badge = html.escape(
            str(
                item.get(
                    "badge",
                    ""
                )
            )
        )

        metric_key = item.get(
            "metric_key"
        )

        custom_help = item.get(
            "help"
        )

        is_numeric = bool(
            item.get(
                "numeric",
                False
            )
        )

        value_class = "overview-strip-value"

        if is_numeric:
            value_class += " numeric"

        help_text = ""

        if custom_help:
            help_text = str(
                custom_help
            )

        elif metric_key:
            help_text = get_metric_help(
                metric_key
            )

        safe_help_text = html.escape(
            help_text,
            quote=True
        )

        help_html = ""

        if safe_help_text:
            help_html = (
                '<span '
                'class="overview-strip-metric-help" '
                f'title="{safe_help_text}" '
                'aria-label="Metric definition">'
                '?'
                '</span>'
            )

        badge_html = ""

        if badge:
            badge_html = (
                '<span class="overview-strip-badge">'
                f'{badge}'
                '</span>'
            )

        meta_html = ""

        if meta:
            meta_html = (
                '<span class="overview-strip-meta">'
                f'{meta}'
                '</span>'
            )

        card_html = (
            '<div class="overview-strip-card">'
            '<div>'
            '<div class="overview-strip-label-row">'
            '<div class="overview-strip-label">'
            f'{label}'
            '</div>'
            f'{help_html}'
            '</div>'
            f'<div class="{value_class}">'
            f'{value}'
            '</div>'
            '</div>'
            '<div class="overview-strip-footer">'
            f'{meta_html}'
            f'{badge_html}'
            '</div>'
            '</div>'
        )

        cards.append(
            card_html
        )

    strip_html = (
        '<div class="overview-strip-container">'
        '<div class="overview-strip-track">'
        f'{"".join(cards)}'
        '</div>'
        '</div>'
    )

    st.markdown(
        strip_html,
        unsafe_allow_html=True
    )


def show_metric_definition(
    metric_key,
    label="Metric definition"
):
    """
    Display a compact metric-definition hint using the centralized
    definition stored in components.metrics.
    """
    show_info_hint(
        label=label,
        help_text=get_metric_help(
            metric_key
        )
    )


def show_data_review_heading(help_text):
    """
    Display the Data Review Panel title with a hover tooltip.

    The tooltip explains that the panel is intended for inspecting
    sample records and validating the dashboard's filtered data.
    """
    safe_help = html.escape(
        str(help_text)
    )

    heading_html = (
        '<div class="data-review-header">'
        '<div class="data-review-title">'
        'Data Review Panel'
        '</div>'
        '<div class="data-review-tooltip">'
        '<span class="data-review-tooltip-icon">?</span>'
        '<div class="data-review-tooltip-text">'
        f'{safe_help}'
        '</div>'
        '</div>'
        '</div>'
    )

    st.markdown(
        heading_html,
        unsafe_allow_html=True
    )


def highlight_keywords(text):
    """
    Highlight important terms in analytical insight text.
    """
    safe_text = html.escape(
        str(text)
    )

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

    for keyword in sorted(
        keywords,
        key=len,
        reverse=True
    ):
        pattern = re.compile(
            rf"\b({re.escape(keyword)})\b",
            re.IGNORECASE
        )

        safe_text = pattern.sub(
            (
                '<span class="insight-keyword">'
                r'\1'
                '</span>'
            ),
            safe_text
        )

    return safe_text


def show_section_note(text):
    """
    Display a compact explanatory note.
    """
    safe_text = html.escape(
        str(text)
    )

    note_html = (
        '<div class="section-note">'
        f'{safe_text}'
        '</div>'
    )

    st.markdown(
        note_html,
        unsafe_allow_html=True
    )


def show_insight(text):
    """
    Display a reusable analytical insight box.
    """
    insight_html = (
        '<div class="insight-box">'
        '<strong>Insight:</strong> '
        f'{text}'
        '</div>'
    )

    st.markdown(
        insight_html,
        unsafe_allow_html=True
    )


def show_info_hint(
    label,
    help_text
):
    """
    Display contextual help.
    """
    safe_label = html.escape(
        str(label)
    )

    safe_help = html.escape(
        str(help_text)
    )

    if safe_label.lower() == "filter guide":
        filter_help_html = (
            '<div class="filter-help-row">'
            '<div class="filter-help-label">'
            'Leave filters empty to include all records.'
            '</div>'
            '<div class="filter-help-tooltip">'
            '<span class="filter-help-icon">?</span>'
            '<div class="filter-help-tooltip-text">'
            f'{safe_help} '
            'Select one or more values to narrow every dashboard view. '
            'Remove selected values with the × icon.'
            '</div>'
            '</div>'
            '</div>'
        )

        st.markdown(
            filter_help_html,
            unsafe_allow_html=True
        )

        return

    info_html = (
        '<div class="mini-info-wrapper">'
        f'<span>{safe_label}</span>'
        '<span '
        'class="mini-info" '
        f'title="{safe_help}">'
        '?'
        '</span>'
        '</div>'
    )

    st.markdown(
        info_html,
        unsafe_allow_html=True
    )


def show_compact_record_note(text):
    """
    Display a muted note above a record table.
    """
    safe_text = html.escape(
        str(text)
    )

    note_html = (
        '<div class="compact-record-note">'
        f'{safe_text}'
        '</div>'
    )

    st.markdown(
        note_html,
        unsafe_allow_html=True
    )