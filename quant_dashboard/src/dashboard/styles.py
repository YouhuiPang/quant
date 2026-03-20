from __future__ import annotations

from dash import html


COLORS = {
    "background": "#09111f",
    "surface": "#10192b",
    "surface_alt": "#16243b",
    "border": "#22324f",
    "text": "#e8eef8",
    "muted": "#97a8c5",
    "accent": "#3bc18b",
    "danger": "#ef6e7b",
    "warning": "#f3ba63",
    "secondary": "#7ea3ff",
    "grid": "#22324d",
}

FONT_STACK = "'IBM Plex Sans', 'Segoe UI', sans-serif"

APP_STYLE = {
    "backgroundColor": COLORS["background"],
    "minHeight": "100vh",
    "color": COLORS["text"],
    "fontFamily": FONT_STACK,
}

CONTENT_STYLE = {
    "padding": "24px 32px 40px 32px",
    "maxWidth": "1500px",
    "margin": "0 auto",
}

CARD_STYLE = {
    "backgroundColor": COLORS["surface"],
    "border": f"1px solid {COLORS['border']}",
    "borderRadius": "18px",
    "padding": "18px 20px",
    "boxShadow": "0 16px 28px rgba(4, 10, 20, 0.28)",
}

NAV_STYLE = {
    "padding": "18px 32px",
    "borderBottom": f"1px solid {COLORS['border']}",
    "background": "linear-gradient(90deg, rgba(16,25,43,0.98), rgba(9,17,31,0.98))",
    "position": "sticky",
    "top": 0,
    "zIndex": 20,
    "backdropFilter": "blur(10px)",
}

LINK_STYLE = {
    "color": COLORS["muted"],
    "textDecoration": "none",
    "padding": "8px 12px",
    "borderRadius": "10px",
    "transition": "all 0.2s ease",
}

BUTTON_STYLE = {
    "padding": "12px 16px",
    "borderRadius": "10px",
    "backgroundColor": COLORS["surface_alt"],
    "color": COLORS["text"],
    "border": f"1px solid {COLORS['border']}",
    "cursor": "pointer",
}


def metric_card(title: str, value: str, subtitle: str = "") -> html.Div:
    """Render a reusable KPI card."""
    return html.Div(
        [
            html.Div(title, style={"fontSize": "13px", "color": COLORS["muted"], "marginBottom": "10px"}),
            html.Div(value, style={"fontSize": "28px", "fontWeight": 700, "letterSpacing": "-0.03em"}),
            html.Div(subtitle, style={"fontSize": "12px", "color": COLORS["muted"], "marginTop": "8px"}),
        ],
        style=CARD_STYLE,
    )
