from __future__ import annotations

from dash import html, register_page

from src.dashboard.callbacks import styled_table
from src.dashboard.styles import CARD_STYLE


register_page(__name__, path="/risk", name="Risk", order=7)


layout = html.Div(
    [
        html.Div(
            [
                html.H2("Risk Controls", style={"margin": 0}),
                html.Div("Inspect current risk-adjusted targets and recent risk events.", style={"marginTop": "10px", "opacity": 0.8}),
            ],
            style={**CARD_STYLE, "marginBottom": "24px"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div("Latest Risk Status", style={"fontSize": "18px", "fontWeight": 600, "marginBottom": "14px"}),
                        styled_table(
                            "risk-table",
                            [
                                {"name": "Timestamp", "id": "timestamp"},
                                {"name": "Ticker", "id": "ticker"},
                                {"name": "Target Weight", "id": "target_weight"},
                                {"name": "Approved Weight", "id": "approved_weight"},
                                {"name": "Risk Flag", "id": "risk_flag"},
                                {"name": "Risk Notes", "id": "risk_notes"},
                            ],
                            [],
                        ),
                    ],
                    style={**CARD_STYLE, "flex": 1},
                ),
                html.Div(
                    [
                        html.Div("Recent Risk Events", style={"fontSize": "18px", "fontWeight": 600, "marginBottom": "14px"}),
                        styled_table(
                            "risk-summary-table",
                            [
                                {"name": "Timestamp", "id": "timestamp"},
                                {"name": "Ticker", "id": "ticker"},
                                {"name": "Target Weight", "id": "target_weight"},
                                {"name": "Approved Weight", "id": "approved_weight"},
                                {"name": "Risk Flag", "id": "risk_flag"},
                                {"name": "Risk Notes", "id": "risk_notes"},
                            ],
                            [],
                        ),
                    ],
                    style={**CARD_STYLE, "flex": 1},
                ),
            ],
            style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(420px, 1fr))", "gap": "18px"},
        ),
    ]
)
