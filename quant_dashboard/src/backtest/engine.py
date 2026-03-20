from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from src.backtest.benchmark import build_benchmark_returns
from src.backtest.costs import calculate_transaction_costs, calculate_turnover
from src.backtest.execution import apply_execution_lag
from src.backtest.metrics import build_asset_summary, compute_drawdown_series, summarize_metrics
from src.backtest.trade_ledger import build_trade_ledger
from src.portfolio.allocation import allocate_equal_weight_active
from src.portfolio.portfolio_builder import build_portfolio_returns


@dataclass
class BacktestResult:
    enriched_frame: pd.DataFrame
    signals: pd.DataFrame
    positions: pd.DataFrame
    asset_returns: pd.DataFrame
    portfolio_returns: pd.DataFrame
    benchmark_returns: pd.DataFrame
    trades: pd.DataFrame
    metrics: dict[str, Any]
    asset_summary: pd.DataFrame


def run_backtest(
    feature_frame: pd.DataFrame,
    approved_targets: pd.DataFrame,
    config: dict[str, Any],
) -> BacktestResult:
    """Run a multi-asset vectorized backtest with lagged execution and benchmark comparison."""
    backtest_config = config["backtest"]
    annualization_factor = int(backtest_config.get("annualization_factor", 252))
    transaction_cost_bps = float(backtest_config.get("transaction_cost_bps", 0.0))

    prepared_targets = approved_targets.copy()
    feature_frame = feature_frame.copy()
    feature_frame["date"] = pd.to_datetime(feature_frame["date"])
    prepared_targets["date"] = pd.to_datetime(prepared_targets["timestamp"])
    enriched = feature_frame.merge(prepared_targets, on=["date", "ticker"], how="left")
    enriched = apply_execution_lag(enriched, backtest_config)
    enriched = calculate_turnover(enriched)
    enriched = calculate_transaction_costs(enriched, transaction_cost_bps)
    enriched["asset_return"] = enriched.groupby("ticker", group_keys=False)["close"].pct_change().fillna(0.0)
    enriched["strategy_gross_return"] = enriched["executed_weight"] * enriched["asset_return"]
    enriched["strategy_net_return"] = enriched["strategy_gross_return"] - enriched["transaction_cost"]

    positions = enriched[["date", "ticker", "signal", "confidence", "target_weight", "approved_weight", "executed_weight"]].copy()
    signals = enriched[["date", "ticker", "signal", "confidence", "strategy_name"]].copy()
    asset_returns = enriched[
        [
            "date",
            "ticker",
            "asset_return",
            "signal",
            "target_weight",
            "approved_weight",
            "executed_weight",
            "turnover",
            "transaction_cost",
            "strategy_gross_return",
            "strategy_net_return",
        ]
    ].copy()

    portfolio_returns = build_portfolio_returns(asset_returns)
    benchmark_returns = build_benchmark_returns(feature_frame)
    portfolio_returns = portfolio_returns.merge(benchmark_returns, on="date", how="left")
    portfolio_returns["excess_return"] = portfolio_returns["portfolio_net_return"] - portfolio_returns["benchmark_return"]
    portfolio_returns["drawdown"] = compute_drawdown_series(portfolio_returns["cumulative_strategy"])
    portfolio_returns["rolling_volatility"] = (
        portfolio_returns["portfolio_net_return"].rolling(20, min_periods=10).std().fillna(0.0)
        * (annualization_factor ** 0.5)
    )
    rolling_mean = portfolio_returns["portfolio_net_return"].rolling(20, min_periods=10).mean()
    rolling_std = portfolio_returns["portfolio_net_return"].rolling(20, min_periods=10).std().replace(0, pd.NA)
    portfolio_returns["rolling_sharpe"] = (rolling_mean / rolling_std).fillna(0.0) * (annualization_factor ** 0.5)

    trades = build_trade_ledger(enriched)
    metrics = summarize_metrics(portfolio_returns, benchmark_returns, trades, annualization_factor)
    asset_summary = build_asset_summary(asset_returns, trades)

    return BacktestResult(
        enriched_frame=enriched,
        signals=signals,
        positions=positions,
        asset_returns=asset_returns,
        portfolio_returns=portfolio_returns,
        benchmark_returns=benchmark_returns,
        trades=trades,
        metrics=metrics,
        asset_summary=asset_summary,
    )
