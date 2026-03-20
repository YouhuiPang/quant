from __future__ import annotations

from dash import dcc, html, register_page

from src.analytics.reporting import load_dashboard_bundle
from src.dashboard.callbacks import styled_table
from src.dashboard.styles import CARD_STYLE


register_page(__name__, path="/analytics", name="Analytics", order=3)

bundle = load_dashboard_bundle()
start_date = bundle.portfolio_returns["date"].min().date()
end_date = bundle.portfolio_returns["date"].max().date()
ticker_options = [{"label": "All Tickers", "value": "ALL"}] + [
    {"label": ticker, "value": ticker} for ticker in sorted(bundle.enriched["ticker"].unique())
]


layout = html.Div(
    [
        html.Div(
            [
                html.H2("Analytics and Trade Review", style={"margin": 0}),
                html.Div("Review trade outcomes, rolling Sharpe, and feature relationships across the research universe.", style={"marginTop": "10px", "opacity": 0.8}),
                html.Div(
                    [
                        dcc.Dropdown(id="analytics-ticker-filter", options=ticker_options, value="ALL", clearable=False, style={"minWidth": "220px"}),
                        dcc.DatePickerRange(
                            id="analytics-date-range",
                            min_date_allowed=start_date,
                            max_date_allowed=end_date,
                            start_date=start_date,
                            end_date=end_date,
                            display_format="YYYY-MM-DD",
                        ),
                    ],
                    style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginTop": "18px"},
                ),
            ],
            style={**CARD_STYLE, "marginBottom": "24px"},
        ),
        html.Div(
            [
                html.Div([dcc.Graph(id="analytics-trade-hist")], style={**CARD_STYLE, "flex": 1}),
                html.Div([dcc.Graph(id="analytics-sharpe-chart")], style={**CARD_STYLE, "flex": 1}),
            ],
            style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(380px, 1fr))", "gap": "18px", "marginBottom": "18px"},
        ),
        html.Div([dcc.Graph(id="analytics-correlation-chart")], style={**CARD_STYLE, "marginBottom": "18px"}),
        html.Div(
            [
                html.Div("Trade Ledger", style={"fontSize": "18px", "fontWeight": 600, "marginBottom": "14px"}),
                styled_table(
                    "trade-summary-table",
                    [
                        {"name": "Ticker", "id": "ticker"},
                        {"name": "Entry Date", "id": "entry_date"},
                        {"name": "Exit Date", "id": "exit_date"},
                        {"name": "Entry Price", "id": "entry_price"},
                        {"name": "Exit Price", "id": "exit_price"},
                        {"name": "Holding Period", "id": "holding_period"},
                        {"name": "Gross Return", "id": "gross_return"},
                        {"name": "Net Return", "id": "net_return"},
                        {"name": "Cost", "id": "transaction_cost"},
                    ],
                    [],
                ),
            ],
            style=CARD_STYLE,
        ),
    ]
)
