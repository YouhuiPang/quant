from __future__ import annotations

from dash import dcc, html, register_page

from src.analytics.reporting import load_dashboard_bundle
from src.dashboard.callbacks import styled_table
from src.dashboard.styles import CARD_STYLE


register_page(__name__, path="/signals", name="Signals", order=2)

bundle = load_dashboard_bundle()
start_date = bundle.positions["date"].min().date()
end_date = bundle.positions["date"].max().date()
ticker_options = [{"label": "All Tickers", "value": "ALL"}] + [
    {"label": ticker, "value": ticker} for ticker in sorted(bundle.positions["ticker"].unique())
]


layout = html.Div(
    [
        html.Div(
            [
                html.H2("Signal Monitor", style={"margin": 0}),
                html.Div("Filter signals and executed positions by ticker and date, then inspect the price context.", style={"marginTop": "10px", "opacity": 0.8}),
                html.Div(
                    [
                        dcc.Dropdown(id="signals-ticker-filter", options=ticker_options, value="ALL", clearable=False, style={"minWidth": "220px"}),
                        dcc.DatePickerRange(
                            id="signals-date-range",
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
        html.Div([dcc.Graph(id="signals-price-chart")], style={**CARD_STYLE, "marginBottom": "18px"}),
        html.Div(
            [
                html.Div(
                    [
                        html.Div("Latest Signals by Asset", style={"fontSize": "18px", "fontWeight": 600, "marginBottom": "14px"}),
                        styled_table(
                            "signals-table",
                            [
                                {"name": "Date", "id": "date"},
                                {"name": "Ticker", "id": "ticker"},
                                {"name": "Signal", "id": "signal"},
                                {"name": "Confidence", "id": "confidence"},
                                {"name": "Strategy", "id": "strategy_name"},
                            ],
                            [],
                        ),
                    ],
                    style={**CARD_STYLE, "flex": 1},
                ),
                html.Div(
                    [
                        html.Div("Latest Executed Positions", style={"fontSize": "18px", "fontWeight": 600, "marginBottom": "14px"}),
                        styled_table(
                            "targets-table",
                            [
                                {"name": "Date", "id": "date"},
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
            style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(360px, 1fr))", "gap": "18px"},
        ),
    ]
)
