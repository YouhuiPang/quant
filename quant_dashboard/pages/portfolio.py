from __future__ import annotations

from dash import dcc, html, register_page

from src.dashboard.callbacks import styled_table
from src.dashboard.styles import CARD_STYLE


register_page(__name__, path="/portfolio", name="Portfolio", order=4)


layout = html.Div(
    [
        html.Div(
            [
                html.H2("Portfolio Monitor", style={"margin": 0}),
                html.Div("Inspect live-like portfolio allocation and current active holdings.", style={"marginTop": "10px", "opacity": 0.8}),
            ],
            style={**CARD_STYLE, "marginBottom": "24px"},
        ),
        html.Div([dcc.Graph(id="portfolio-allocation-chart")], style={**CARD_STYLE, "marginBottom": "18px"}),
        html.Div(
            [
                html.Div("Current Positions", style={"fontSize": "18px", "fontWeight": 600, "marginBottom": "14px"}),
                styled_table(
                    "portfolio-positions-table",
                    [
                        {"name": "Timestamp", "id": "timestamp"},
                        {"name": "Ticker", "id": "ticker"},
                        {"name": "Quantity", "id": "quantity"},
                        {"name": "Market Price", "id": "market_price"},
                        {"name": "Market Value", "id": "market_value"},
                        {"name": "Weight", "id": "weight"},
                        {"name": "Unrealized PnL", "id": "unrealized_pnl"},
                    ],
                    [],
                ),
            ],
            style=CARD_STYLE,
        ),
    ]
)
