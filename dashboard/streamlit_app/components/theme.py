"""
theme.py

Purpose:
Central theme configuration for the Terp Protect Streamlit dashboard.

This file stores colors, typography, spacing, and chart design settings in one place.
Edit this file to experiment with the dashboard look without changing every component.
"""


THEME = {
    "brand": {
        "name": "Terp Protect",
        "primary": "#C8102E",
        "primary_dark": "#7A0019",
        "secondary": "#FFD200",
        "accent": "#6EC6FF",
        "success": "#2ECC71",
        "warning": "#F4C430",
        "danger": "#FF4B4B"
    },

    "background": {
        "app": "#0E1117",
        "sidebar": "#171A23",
        "card": "#FFFFFF",
        "card_soft": "#FFF8E6",
        "surface": "#141821",
        "surface_light": "#F8F9FB"
    },

    "text": {
        "primary": "#FFFFFF",
        "secondary": "#D6D6D6",
        "dark": "#111111",
        "muted": "#6B7280",
        "on_card": "#1F2937"
    },

    "border": {
        "light": "#E5E7EB",
        "dark": "#2A2F3A",
        "highlight": "#C8102E"
    },

    "chart": {
        "primary": "#6EC6FF",
        "secondary": "#C8102E",
        "accent": "#FFD200",
        "muted": "#AAB2C0",
        "grid": "#2A2F3A",
        "background": "#0E1117",
        "paper": "#0E1117",
        "text": "#F5F5F5",
        "palette": [
            "#6EC6FF",
            "#C8102E",
            "#FFD200",
            "#8B5CF6",
            "#2ECC71",
            "#F97316",
            "#EC4899",
            "#94A3B8"
        ]
    },

    "layout": {
        "radius_small": "8px",
        "radius_medium": "12px",
        "radius_large": "18px",
        "shadow_soft": "0 4px 18px rgba(0, 0, 0, 0.18)",
        "shadow_card": "0 6px 24px rgba(0, 0, 0, 0.12)"
    },

    "font": {
        "family": "Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
        "title_size": "2.2rem",
        "subtitle_size": "1rem",
        "section_title_size": "1.45rem",
        "body_size": "0.95rem",
        "small_size": "0.82rem"
    }
}


def get_theme():
    """Return the dashboard theme dictionary."""
    return THEME


def get_chart_template():
    """Return reusable Plotly layout settings based on the dashboard theme."""
    return {
        "paper_bgcolor": THEME["chart"]["paper"],
        "plot_bgcolor": THEME["chart"]["background"],
        "font": {
            "family": THEME["font"]["family"],
            "color": THEME["chart"]["text"],
            "size": 12
        },
        "title": {
            "font": {
                "size": 16,
                "color": THEME["chart"]["text"]
            }
        },
        "legend": {
            "font": {
                "color": THEME["chart"]["text"]
            }
        },
        "margin": {
            "l": 10,
            "r": 10,
            "t": 55,
            "b": 10
        }
    }