"""
theme.py

Purpose:
Central theme configuration for the Terp Protect Streamlit dashboard.

This file controls colors, typography, spacing, chart palettes, semantic status colors,
dashboard copy, and reusable Plotly layout settings.

Edit this file first when experimenting with the dashboard look.
"""


THEME = {
    "brand": {
        "name": "Terp Protect",
        "primary": "#C8102E",
        "primary_dark": "#7A0019",
        "primary_soft": "#F9DDE4",
        "primary_muted": "#B94A61",
        "secondary": "#FFD166",
        "secondary_soft": "#FFF3C4",
        "accent": "#76C7E8",
        "accent_dark": "#21657E",
        "accent_soft": "#DDF3FB"
    },

    "semantic": {
        "critical": "#C84A4A",
        "critical_soft": "#F8DDDD",
        "warning": "#D98B2B",
        "warning_soft": "#FBE8CF",
        "attention": "#E8BF45",
        "attention_soft": "#FFF6D8",
        "stable": "#4AAE9B",
        "stable_soft": "#DDF4EF",
        "positive": "#55B87A",
        "positive_soft": "#E3F5EA",
        "neutral": "#9AA8BA",
        "neutral_soft": "#EEF2F7",
        "info": "#6CAED6",
        "info_soft": "#E2F2FA"
    },

    "background": {
        "app": "#0B111C",
        "app_gradient_start": "#090D14",
        "app_gradient_mid": "#0E1624",
        "app_gradient_end": "#111C2D",

        "sidebar": "#111827",
        "sidebar_dark": "#0B101A",
        "sidebar_surface": "#182131",
        "sidebar_surface_soft": "#202B3D",

        "surface": "#101827",
        "surface_alt": "#151F31",
        "surface_soft": "#1E293B",
        "surface_light": "#F6F8FB",

        "card": "#F8FAFC",
        "card_alt": "#FFFFFF",
        "card_soft": "#F1F5F9",
        "card_dark": "#111827",

        "info": "#F8FAFC",
        "insight": "#FFF8E6",
        "insight_alt": "#FFFDF5"
    },

    "text": {
        "primary": "#F8FAFC",
        "secondary": "#CBD5E1",
        "muted": "#94A3B8",

        "dark": "#0F172A",
        "dark_secondary": "#334155",
        "dark_muted": "#64748B",

        "on_card": "#1E293B",
        "on_card_muted": "#475569",
        "on_dark": "#F8FAFC",

        "danger": "#A8323A",
        "success": "#237A63"
    },

    "border": {
        "dark": "#273244",
        "soft": "#334155",
        "light": "#D9E2EC",
        "extra_light": "#EAF0F6",
        "white_subtle": "rgba(255, 255, 255, 0.12)",
        "highlight": "#C8102E"
    },

    "tabs": {
        "background": "#EAF0F7",
        "background_hover": "#DDE8F3",
        "selected_background": "#F4CDD6",
        "selected_border": "#D96073",
        "selected_text": "#7A0019",
        "text": "#172033",
        "sticky_background": "rgba(11, 17, 28, 0.92)"
    },

    "filters": {
        "input_background": "#0E1522",
        "input_border": "#334155",
        "input_focus": "#76C7E8",
        "selected_background": "#EAF0F7",
        "selected_text": "#0F172A",
        "selected_border": "#B8C7D8",
        "selected_hover": "#DDE8F3"
    },

    "chart": {
        "paper": "#0B111C",
        "background": "#0B111C",
        "surface": "#0D1420",
        "grid": "#253246",
        "axis": "#344258",
        "text": "#F8FAFC",
        "muted_text": "#C9D3E0",

        "primary": "#8ED8F3",
        "primary_dark": "#4EA8C8",
        "secondary": "#E78A98",
        "secondary_dark": "#B94A61",
        "attention": "#F2CC68",
        "stable": "#6AC7B6",
        "neutral": "#AAB7C8",

        "incident": "#8ED8F3",
        "incident_soft": "#BEEBFA",
        "arrest": "#E78A98",
        "arrest_soft": "#F4C2CB",
        "delay": "#F2CC68",
        "delay_soft": "#FFE9A8",
        "quality_valid": "#6AC7B6",
        "quality_invalid": "#E78A98",

        "area_line": "#8EC5FF",
        "area_fill": "rgba(142, 197, 255, 0.22)",

        "sequential_blue": [
            "#E5F6FE",
            "#C8ECFA",
            "#A4DFF5",
            "#7FCFED",
            "#59BCE0",
            "#349DCA",
            "#1F6F9F"
        ],

        "heatmap_public_safety": [
            "#F3F8FC",
            "#D9ECF7",
            "#B7DBEF",
            "#8FC7E2",
            "#68AFCF",
            "#447FA8",
            "#263B67"
        ],

        "risk_scale": [
            "#6AC7B6",
            "#F2CC68",
            "#E9A85D",
            "#E78A5E",
            "#D95F65"
        ],

        "categorical": [
            "#8ED8F3",
            "#F2CC68",
            "#6AC7B6",
            "#E78A98",
            "#B6A6E9",
            "#F2B880",
            "#C5D3E3",
            "#AAB7C8"
        ]
    },

    "font": {
        "family": "Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
        "title_size": "2.35rem",
        "subtitle_size": "1rem",
        "section_title_size": "1.55rem",
        "body_size": "0.95rem",
        "small_size": "0.82rem",
        "caption_size": "0.78rem",
        "metric_label_size": "0.78rem",
        "metric_value_size": "1.35rem"
    },

    "layout": {
        "content_width": "100%",
        "radius_xs": "6px",
        "radius_small": "10px",
        "radius_medium": "14px",
        "radius_large": "22px",
        "radius_pill": "999px",
        "shadow_soft": "0 12px 36px rgba(0, 0, 0, 0.22)",
        "shadow_card": "0 8px 24px rgba(0, 0, 0, 0.10)",
        "shadow_hover": "0 14px 32px rgba(0, 0, 0, 0.16)"
    },

    "copy": {
        "dashboard_label": "UMPD Public Safety Intelligence",
        "dashboard_title": "Terp Protect: Campus Safety Analytics",
        "dashboard_subtitle": (
            "DBMS-powered public safety intelligence for exploring campus incidents, "
            "case outcomes, reporting delays, arrest records, and location-based safety patterns "
            "through a structured analytical workflow."
        ),
        "sidebar_filter_help": (
            "Filters narrow the dashboard. Leave a filter empty to include all values."
        ),
        "data_review_help": (
            "This panel shows a small sample of records behind the charts. Use it for quick validation, "
            "not for primary analysis."
        )
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
            },
            "x": 0,
            "xanchor": "left"
        },
        "legend": {
            "font": {
                "color": THEME["chart"]["text"]
            },
            "bgcolor": "rgba(0, 0, 0, 0)"
        },
        "margin": {
            "l": 14,
            "r": 14,
            "t": 54,
            "b": 18
        }
    }


def get_status_color(status):
    """
    Return a semantic color for status-like values.

    This keeps dashboard coloring consistent:
    - muted red for urgent/arrest/invalid
    - amber/orange for pending/delay/attention
    - green/teal for valid/stable/closed
    - blue/gray for neutral categories
    """
    normalized_status = str(status).strip().lower()

    if any(keyword in normalized_status for keyword in ["arrest", "invalid", "critical"]):
        return THEME["semantic"]["critical"]

    if any(keyword in normalized_status for keyword in ["pending", "active", "delay", "warning"]):
        return THEME["semantic"]["warning"]

    if any(keyword in normalized_status for keyword in ["closed", "cleared", "valid", "same day"]):
        return THEME["semantic"]["stable"]

    return THEME["chart"]["primary"]


def get_chart_color(chart_type):
    """Return a consistent chart color by chart purpose."""
    chart_colors = {
        "incident": THEME["chart"]["incident"],
        "incident_soft": THEME["chart"]["incident_soft"],
        "arrest": THEME["chart"]["arrest"],
        "arrest_soft": THEME["chart"]["arrest_soft"],
        "delay": THEME["chart"]["delay"],
        "delay_soft": THEME["chart"]["delay_soft"],
        "valid": THEME["chart"]["quality_valid"],
        "invalid": THEME["chart"]["quality_invalid"],
        "neutral": THEME["chart"]["neutral"],
        "attention": THEME["chart"]["attention"],
        "stable": THEME["chart"]["stable"]
    }

    return chart_colors.get(chart_type, THEME["chart"]["primary"])


def get_soft_categorical_palette():
    """Return the default soft categorical chart palette."""
    return THEME["chart"]["categorical"]


def get_risk_scale():
    """Return the risk scale used for delays and urgency-style views."""
    return THEME["chart"]["risk_scale"]


def get_heatmap_scale():
    """Return the dashboard heatmap color scale."""
    return THEME["chart"]["heatmap_public_safety"]