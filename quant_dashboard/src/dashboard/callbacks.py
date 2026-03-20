from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, dash_table, dcc, html

from src.analytics.reporting import latest_snapshot, load_dashboard_bundle
from src.dashboard.styles import CARD_STYLE, COLORS
from src.utils.helpers import format_metric_value


def register_callbacks(app: Dash) -> None:
    """Register shared and page-level Dash callbacks."""

    @app.callback(
        Output("home-summary-cards", "children"),
        Output("home-latest-status", "children"),
        Input("url", "pathname"),
    )
    def render_home_summary(_: str):
        bundle = load_dashboard_bundle()
        snapshot = latest_snapshot(bundle)
        cards = [
            _summary_card("Strategy Return", format_metric_value(bundle.metrics["total_return"])),
            _summary_card("Benchmark Return", format_metric_value(bundle.metrics["benchmark_total_return"])),
            _summary_card("Account Equity", format_metric_value(snapshot["equity"], percentage=False, decimals=2)),
            _summary_card("Cash", format_metric_value(snapshot["cash"], percentage=False, decimals=2)),
            _summary_card("Active Positions", str(snapshot["active_positions"])),
            _summary_card("Risk Status", snapshot["risk_status"]),
            _summary_card("Data Provider", str(snapshot["data_provider"]).upper()),
            _summary_card("Broker Mode", f"{snapshot['broker_provider']}/{bundle.config['runtime']['mode']}"),
        ]
        status = (
            f"Latest data date: {snapshot['latest_date']} | "
            f"Latest portfolio return: {format_metric_value(snapshot['latest_portfolio_return'])} | "
            f"Latest benchmark return: {format_metric_value(snapshot['latest_benchmark_return'])} | "
            f"Connection: {snapshot['connection_status']} | "
            f"Latest snapshot cache: {snapshot['latest_market_snapshot']}"
        )
        return cards, status

    @app.callback(
        Output("backtest-equity-chart", "figure"),
        Output("backtest-drawdown-chart", "figure"),
        Output("backtest-vol-chart", "figure"),
        Output("backtest-metrics-table", "data"),
        Input("backtest-date-range", "start_date"),
        Input("backtest-date-range", "end_date"),
    )
    def update_backtest_page(start_date: str | None, end_date: str | None):
        bundle = load_dashboard_bundle()
        frame = _filter_by_date(bundle.portfolio_returns, start_date, end_date)
        asset_summary = bundle.asset_summary.copy()

        equity_fig = go.Figure()
        equity_fig.add_trace(go.Scatter(x=frame["date"], y=frame["cumulative_strategy"], name="Strategy", line={"color": COLORS["accent"], "width": 2.5}))
        equity_fig.add_trace(go.Scatter(x=frame["date"], y=frame["cumulative_benchmark"], name="Benchmark", line={"color": COLORS["secondary"], "width": 2.0}))
        equity_fig.update_layout(**_base_figure_layout("Strategy vs Benchmark"))

        drawdown_fig = go.Figure()
        drawdown_fig.add_trace(go.Scatter(x=frame["date"], y=frame["drawdown"], fill="tozeroy", line={"color": COLORS["danger"], "width": 2}))
        drawdown_fig.update_layout(**_base_figure_layout("Portfolio Drawdown"))

        vol_fig = go.Figure()
        vol_fig.add_trace(go.Scatter(x=frame["date"], y=frame["rolling_volatility"], line={"color": COLORS["warning"], "width": 2.2}, name="Rolling Volatility"))
        vol_fig.update_layout(**_base_figure_layout("20D Rolling Volatility"))

        metrics_table = [{"metric": key, "value": _format_metric_cell(key, value)} for key, value in bundle.metrics.items()]
        asset_data = asset_summary.to_dict("records")
        return equity_fig, drawdown_fig, vol_fig, metrics_table

    @app.callback(
        Output("signals-price-chart", "figure"),
        Output("signals-table", "data"),
        Output("targets-table", "data"),
        Input("signals-date-range", "start_date"),
        Input("signals-date-range", "end_date"),
        Input("signals-ticker-filter", "value"),
    )
    def update_signals_page(start_date: str | None, end_date: str | None, ticker: str):
        bundle = load_dashboard_bundle()
        merged = bundle.enriched.merge(bundle.approved_targets, left_on=["date", "ticker"], right_on=["timestamp", "ticker"], how="left")
        filtered = _filter_ticker(merged, ticker)
        frame = _filter_by_date(filtered, start_date, end_date)
        if frame.empty:
            return go.Figure().update_layout(**_base_figure_layout("Signal View")), [], []

        chart_frame = frame if ticker != "ALL" else frame[frame["ticker"] == frame["ticker"].iloc[0]]
        price_fig = go.Figure()
        price_fig.add_trace(go.Scatter(x=chart_frame["date"], y=chart_frame["close"], name="Close", line={"color": COLORS["secondary"], "width": 2.4}))
        price_fig.add_trace(go.Scatter(x=chart_frame["date"], y=chart_frame["rolling_mean_20"], name="MA20", line={"color": COLORS["warning"], "width": 1.8}))
        buy_points = chart_frame[chart_frame["signal"] > 0]
        if not buy_points.empty:
            price_fig.add_trace(go.Scatter(x=buy_points["date"], y=buy_points["close"], mode="markers", name="Signal", marker={"size": 9, "color": COLORS["accent"]}))
        title_ticker = ticker if ticker != "ALL" else chart_frame["ticker"].iloc[0]
        price_fig.update_layout(**_base_figure_layout(f"Signal View: {title_ticker}"))

        latest_date = frame["date"].max()
        latest_rows = frame[frame["date"] == latest_date].copy()
        latest_rows["date"] = latest_rows["date"].dt.strftime("%Y-%m-%d")
        signals_data = latest_rows[["date", "ticker", "signal", "confidence", "strategy_name"]].sort_values("ticker").to_dict("records")
        targets_data = latest_rows[["date", "ticker", "target_weight", "approved_weight", "risk_flag", "risk_notes"]].sort_values("ticker").to_dict("records")
        return price_fig, signals_data, targets_data

    @app.callback(
        Output("analytics-trade-hist", "figure"),
        Output("analytics-sharpe-chart", "figure"),
        Output("analytics-correlation-chart", "figure"),
        Output("trade-summary-table", "data"),
        Input("analytics-date-range", "start_date"),
        Input("analytics-date-range", "end_date"),
        Input("analytics-ticker-filter", "value"),
    )
    def update_analytics_page(start_date: str | None, end_date: str | None, ticker: str):
        bundle = load_dashboard_bundle()
        feature_frame = _filter_ticker(bundle.enriched, ticker)
        feature_frame = _filter_by_date(feature_frame, start_date, end_date)
        trade_frame = bundle.trades.copy()
        if ticker != "ALL":
            trade_frame = trade_frame[trade_frame["ticker"] == ticker]

        trade_hist = px.histogram(trade_frame, x="net_return", nbins=25, title="Trade Return Distribution") if not trade_frame.empty else go.Figure()
        if trade_frame.empty:
            trade_hist.add_annotation(text="No trades for selected filter.", x=0.5, y=0.5, showarrow=False, xref="paper", yref="paper", font={"color": COLORS["muted"]})
        else:
            trade_hist.update_traces(marker_color=COLORS["warning"])
        trade_hist.update_layout(**_base_figure_layout("Trade Return Distribution"))

        portfolio_frame = _filter_by_date(bundle.portfolio_returns, start_date, end_date)
        sharpe_fig = go.Figure()
        sharpe_fig.add_trace(go.Scatter(x=portfolio_frame["date"], y=portfolio_frame["rolling_sharpe"], line={"color": COLORS["accent"], "width": 2.3}, name="Rolling Sharpe"))
        sharpe_fig.update_layout(**_base_figure_layout("20D Rolling Sharpe"))

        correlation_columns = ["return_1d", "rolling_std_5", "rolling_std_20", "momentum_10", "drawdown_20", "high_low_range", "price_above_ma20"]
        correlation_matrix = feature_frame[correlation_columns].corr().fillna(0.0)
        corr_fig = px.imshow(correlation_matrix, color_continuous_scale=[[0, "#24334f"], [0.5, "#3a537f"], [1, "#3bc18b"]], aspect="auto", title="Feature Correlation Heatmap")
        corr_fig.update_layout(**_base_figure_layout("Feature Correlation Heatmap"))

        if not trade_frame.empty:
            trade_frame = trade_frame.copy()
            trade_frame["entry_date"] = pd.to_datetime(trade_frame["entry_date"]).dt.strftime("%Y-%m-%d")
            trade_frame["exit_date"] = pd.to_datetime(trade_frame["exit_date"]).dt.strftime("%Y-%m-%d")
        return trade_hist, sharpe_fig, corr_fig, trade_frame.tail(20).to_dict("records")

    @app.callback(
        Output("portfolio-allocation-chart", "figure"),
        Output("portfolio-positions-table", "data"),
        Input("url", "pathname"),
    )
    def update_portfolio_page(_: str):
        bundle = load_dashboard_bundle()
        positions = bundle.state["positions"]
        account = bundle.state["account"]
        if positions.empty:
            return go.Figure().update_layout(**_base_figure_layout("Current Allocation")), []
        latest_timestamp = positions["timestamp"].max()
        current_positions = positions[positions["timestamp"] == latest_timestamp].copy()
        pie_fig = px.pie(current_positions, names="ticker", values="weight", title="Current Portfolio Weights")
        pie_fig.update_layout(**_base_figure_layout("Current Portfolio Weights"))
        return pie_fig, current_positions.to_dict("records")

    @app.callback(
        Output("orders-table", "data"),
        Output("fills-table", "data"),
        Input("url", "pathname"),
    )
    def update_orders_page(_: str):
        bundle = load_dashboard_bundle()
        orders = bundle.state["orders"].copy()
        fills = bundle.state["fills"].copy()
        return orders.tail(20).to_dict("records"), fills.tail(20).to_dict("records")

    @app.callback(
        Output("positions-table-live", "data"),
        Output("account-table", "data"),
        Input("url", "pathname"),
    )
    def update_positions_page(_: str):
        bundle = load_dashboard_bundle()
        positions = bundle.state["positions"].copy()
        account = bundle.state["account"].copy()
        if not positions.empty:
            positions = positions[positions["timestamp"] == positions["timestamp"].max()]
        if not account.empty:
            account = account[account["timestamp"] == account["timestamp"].max()]
        return positions.to_dict("records"), account.to_dict("records")

    @app.callback(
        Output("risk-table", "data"),
        Output("risk-summary-table", "data"),
        Input("url", "pathname"),
    )
    def update_risk_page(_: str):
        bundle = load_dashboard_bundle()
        latest_risk = bundle.risk_summary.copy()
        risk_events = bundle.state["risk_events"].copy()
        return latest_risk.to_dict("records"), risk_events.tail(20).to_dict("records")

    @app.callback(
        Output("download-trades", "data"),
        Input("download-trades-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def download_trades(_: int):
        bundle = load_dashboard_bundle()
        trades_path = Path(bundle.config["project_root"]) / bundle.config["paths"]["outputs_dir"] / "trades.csv"
        return dcc.send_file(str(trades_path))

    @app.callback(
        Output("download-metrics", "data"),
        Input("download-metrics-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def download_metrics(_: int):
        bundle = load_dashboard_bundle()
        metrics_path = Path(bundle.config["project_root"]) / bundle.config["paths"]["outputs_dir"] / "metrics.json"
        return dcc.send_file(str(metrics_path))


def styled_table(table_id: str, columns: list[dict[str, str]], data: list[dict]) -> dash_table.DataTable:
    """Create a consistent dark-theme table."""
    return dash_table.DataTable(
        id=table_id,
        columns=columns,
        data=data,
        style_as_list_view=True,
        style_table={"overflowX": "auto"},
        style_header={"backgroundColor": COLORS["surface_alt"], "color": COLORS["text"], "border": f"1px solid {COLORS['border']}", "fontWeight": 600},
        style_cell={
            "backgroundColor": COLORS["surface"],
            "color": COLORS["text"],
            "border": f"1px solid {COLORS['border']}",
            "padding": "10px 12px",
            "fontFamily": "'IBM Plex Sans', 'Segoe UI', sans-serif",
            "fontSize": "13px",
            "textAlign": "left",
        },
        page_size=12,
    )


def _summary_card(title: str, value: str) -> html.Div:
    return html.Div(
        [html.Div(title, style={"fontSize": "13px", "color": COLORS["muted"]}), html.Div(value, style={"fontSize": "26px", "fontWeight": 700, "marginTop": "10px"})],
        style=CARD_STYLE,
    )


def _filter_by_date(df: pd.DataFrame, start_date: str | None, end_date: str | None) -> pd.DataFrame:
    frame = df.copy()
    if frame.empty:
        return frame
    date_column = "date" if "date" in frame.columns else "timestamp"
    frame[date_column] = pd.to_datetime(frame[date_column])
    if start_date:
        frame = frame[frame[date_column] >= pd.Timestamp(start_date)]
    if end_date:
        frame = frame[frame[date_column] <= pd.Timestamp(end_date)]
    return frame


def _filter_ticker(df: pd.DataFrame, ticker: str | None) -> pd.DataFrame:
    if df.empty or not ticker or ticker == "ALL" or "ticker" not in df.columns:
        return df.copy()
    return df[df["ticker"] == ticker].copy()


def _base_figure_layout(title: str) -> dict:
    return {
        "title": {"text": title, "x": 0.02, "font": {"size": 18}},
        "paper_bgcolor": COLORS["surface"],
        "plot_bgcolor": COLORS["surface"],
        "font": {"color": COLORS["text"], "family": "'IBM Plex Sans', 'Segoe UI', sans-serif"},
        "margin": {"l": 48, "r": 28, "t": 54, "b": 42},
        "height": 380,
        "xaxis": {"gridcolor": COLORS["grid"], "zerolinecolor": COLORS["grid"]},
        "yaxis": {"gridcolor": COLORS["grid"], "zerolinecolor": COLORS["grid"]},
        "legend": {"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
    }


def _format_metric_cell(key: str, value: object) -> str:
    if isinstance(value, (int, float)):
        if any(token in key for token in ["return", "drawdown", "rate", "volatility"]):
            return format_metric_value(float(value))
        return f"{float(value):.2f}"
    return str(value)
