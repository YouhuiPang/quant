from __future__ import annotations

from dash import html, register_page

from src.dashboard.callbacks import styled_table
from src.dashboard.styles import CARD_STYLE


register_page(__name__, path="/positions", name="Positions", order=6)


layout = html.Div(
    [
        html.Div(
            [
                html.H2("Live-Like Positions and Account", style={"margin": 0}),
                html.Div("Track persisted paper positions, market values, and current account state.", style={"marginTop": "10px", "opacity": 0.8}),
            ],
            style={**CARD_STYLE, "marginBottom": "24px"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div("Positions", style={"fontSize": "18px", "fontWeight": 600, "marginBottom": "14px"}),
                        styled_table(
                            "positions-table-live",
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
                    style={**CARD_STYLE, "flex": 1},
                ),
                html.Div(
                    [
                        html.Div("Account Snapshot", style={"fontSize": "18px", "fontWeight": 600, "marginBottom": "14px"}),
                        styled_table(
                            "account-table",
                            [
                                {"name": "Timestamp", "id": "timestamp"},
                                {"name": "Cash", "id": "cash"},
                                {"name": "Equity", "id": "equity"},
                                {"name": "Gross Exposure", "id": "gross_exposure"},
                                {"name": "Net Exposure", "id": "net_exposure"},
                                {"name": "Realized PnL", "id": "realized_pnl"},
                                {"name": "Unrealized PnL", "id": "unrealized_pnl"},
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
