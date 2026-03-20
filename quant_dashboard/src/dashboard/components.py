from __future__ import annotations

from dash import html

from src.dashboard.styles import CARD_STYLE, COLORS


def section_header(title: str, subtitle: str = "") -> html.Div:
    """Reusable section header block."""
    return html.Div(
        [
            html.Div(title, style={"fontSize": "20px", "fontWeight": 700}),
            html.Div(subtitle, style={"fontSize": "13px", "color": COLORS["muted"], "marginTop": "6px"}),
        ],
        style={**CARD_STYLE, "marginBottom": "18px"},
    )
