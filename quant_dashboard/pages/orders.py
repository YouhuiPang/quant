from __future__ import annotations

from dash import html, register_page

from src.dashboard.callbacks import styled_table
from src.dashboard.styles import CARD_STYLE


register_page(__name__, path="/orders", name="Orders", order=5)


layout = html.Div(
    [
        html.Div(
            [
                html.H2("Orders and Fills", style={"margin": 0}),
                html.Div("Monitor the local paper order blotter and simulated fills.", style={"marginTop": "10px", "opacity": 0.8}),
            ],
            style={**CARD_STYLE, "marginBottom": "24px"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div("Order Blotter", style={"fontSize": "18px", "fontWeight": 600, "marginBottom": "14px"}),
                        styled_table(
                            "orders-table",
                            [
                                {"name": "Order ID", "id": "order_id"},
                                {"name": "Timestamp", "id": "timestamp"},
                                {"name": "Ticker", "id": "ticker"},
                                {"name": "Side", "id": "side"},
                                {"name": "Quantity", "id": "quantity"},
                                {"name": "Type", "id": "order_type"},
                                {"name": "Status", "id": "status"},
                            ],
                            [],
                        ),
                    ],
                    style={**CARD_STYLE, "flex": 1},
                ),
                html.Div(
                    [
                        html.Div("Fill Blotter", style={"fontSize": "18px", "fontWeight": 600, "marginBottom": "14px"}),
                        styled_table(
                            "fills-table",
                            [
                                {"name": "Fill ID", "id": "fill_id"},
                                {"name": "Order ID", "id": "order_id"},
                                {"name": "Timestamp", "id": "timestamp"},
                                {"name": "Ticker", "id": "ticker"},
                                {"name": "Fill Price", "id": "fill_price"},
                                {"name": "Fill Quantity", "id": "fill_quantity"},
                                {"name": "Cost", "id": "transaction_cost"},
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
