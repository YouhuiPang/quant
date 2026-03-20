from __future__ import annotations

from dash import dcc, html, register_page

from src.analytics.reporting import load_dashboard_bundle
from src.dashboard.callbacks import styled_table
from src.dashboard.styles import BUTTON_STYLE, CARD_STYLE


register_page(__name__, path="/backtest", name="Backtest", order=1)

bundle = load_dashboard_bundle()
start_date = bundle.portfolio_returns["date"].min().date()
end_date = bundle.portfolio_returns["date"].max().date()


layout = html.Div(
    [
        html.Div(
            [
                html.H2("Backtest and Benchmark", style={"margin": 0}),
                html.Div("Inspect portfolio performance, benchmark-relative behavior, and asset-level contribution summaries.", style={"marginTop": "10px", "opacity": 0.8}),
                dcc.DatePickerRange(
                    id="backtest-date-range",
                    min_date_allowed=start_date,
                    max_date_allowed=end_date,
                    start_date=start_date,
                    end_date=end_date,
                    display_format="YYYY-MM-DD",
                    style={"marginTop": "18px"},
                ),
            ],
            style={**CARD_STYLE, "marginBottom": "24px"},
        ),
        html.Div([dcc.Graph(id="backtest-equity-chart")], style={**CARD_STYLE, "marginBottom": "18px"}),
        html.Div(
            [
                html.Div([dcc.Graph(id="backtest-drawdown-chart")], style={**CARD_STYLE, "flex": 1}),
                html.Div([dcc.Graph(id="backtest-vol-chart")], style={**CARD_STYLE, "flex": 1}),
            ],
            style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(380px, 1fr))", "gap": "18px", "marginBottom": "18px"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div("Performance Metrics", style={"fontSize": "18px", "fontWeight": 600, "marginBottom": "14px"}),
                        styled_table("backtest-metrics-table", [{"name": "Metric", "id": "metric"}, {"name": "Value", "id": "value"}], []),
                    ],
                    style={**CARD_STYLE, "flex": 1},
                ),
                html.Div(
                    [
                        html.Div("Exports", style={"fontSize": "18px", "fontWeight": 600, "marginBottom": "14px"}),
                        html.Button("Download Trades CSV", id="download-trades-button", n_clicks=0, style={**BUTTON_STYLE, "marginRight": "12px"}),
                        html.Button("Download Metrics JSON", id="download-metrics-button", n_clicks=0, style=BUTTON_STYLE),
                    ],
                    style={**CARD_STYLE, "minWidth": "320px"},
                ),
            ],
            style={"display": "grid", "gridTemplateColumns": "minmax(420px, 2fr) minmax(280px, 1fr)", "gap": "18px"},
        ),
    ]
)
