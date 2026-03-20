from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def compute_drawdown_series(equity_curve: pd.Series) -> pd.Series:
    """Return percentage drawdown series from an equity curve."""
    running_max = equity_curve.cummax()
    return equity_curve / running_max - 1.0


def summarize_metrics(
    portfolio_returns: pd.DataFrame,
    benchmark_returns: pd.DataFrame,
    trades: pd.DataFrame,
    annualization_factor: int,
) -> dict[str, Any]:
    """Compute a broader set of strategy, benchmark, and trade metrics."""
    merged = portfolio_returns.copy()
    if "benchmark_return" not in merged.columns or "cumulative_benchmark" not in merged.columns:
        merged = merged.merge(benchmark_returns, on="date", how="left")
    strategy_returns = merged["portfolio_net_return"].fillna(0.0)
    benchmark = merged["benchmark_return"].fillna(0.0)
    excess = strategy_returns - benchmark
    equity_curve = merged["cumulative_strategy"].fillna(1.0)
    total_return = float(equity_curve.iloc[-1] - 1.0)
    benchmark_total_return = float(merged["cumulative_benchmark"].fillna(1.0).iloc[-1] - 1.0)
    periods = max(len(strategy_returns), 1)

    annualized_return = float((1.0 + total_return) ** (annualization_factor / periods) - 1.0)
    annualized_volatility = float(strategy_returns.std(ddof=0) * np.sqrt(annualization_factor))
    sharpe_ratio = _safe_ratio(strategy_returns.mean(), strategy_returns.std(ddof=0)) * np.sqrt(annualization_factor)
    tracking_error = float(excess.std(ddof=0) * np.sqrt(annualization_factor))
    information_ratio = _safe_ratio(excess.mean(), excess.std(ddof=0)) * np.sqrt(annualization_factor)

    drawdown = compute_drawdown_series(equity_curve)
    max_drawdown = float(drawdown.min())
    calmar_ratio = float(annualized_return / abs(max_drawdown)) if max_drawdown != 0 else 0.0

    non_zero_return_days = strategy_returns[strategy_returns != 0]
    win_rate = float((non_zero_return_days > 0).mean()) if not non_zero_return_days.empty else 0.0
    avg_holding_period = float(trades["holding_period"].mean()) if not trades.empty else 0.0
    best_trade = float(trades["net_return"].max()) if not trades.empty else 0.0
    worst_trade = float(trades["net_return"].min()) if not trades.empty else 0.0

    metrics: dict[str, Any] = {
        "total_return": total_return,
        "benchmark_total_return": benchmark_total_return,
        "excess_return": total_return - benchmark_total_return,
        "annualized_return": annualized_return,
        "annualized_volatility": annualized_volatility,
        "sharpe_ratio": float(sharpe_ratio),
        "max_drawdown": max_drawdown,
        "turnover": float(portfolio_returns["turnover"].sum()),
        "number_of_trades": int(len(trades)),
        "win_rate": win_rate,
        "tracking_error": tracking_error,
        "information_ratio": float(information_ratio),
        "average_holding_period": avg_holding_period,
        "calmar_ratio": calmar_ratio,
        "best_trade": best_trade,
        "worst_trade": worst_trade,
        "latest_equity": float(equity_curve.iloc[-1]),
    }
    return metrics


def build_asset_summary(asset_frame: pd.DataFrame, trades: pd.DataFrame) -> pd.DataFrame:
    """Create asset-level summary statistics for the analytics page."""
    pnl_by_asset = (
        asset_frame.groupby("ticker", as_index=False)
        .agg(
            average_weight=("executed_weight", "mean"),
            turnover=("turnover", "sum"),
            net_return_contribution=("strategy_net_return", "sum"),
        )
    )
    trade_summary = (
        trades.groupby("ticker", as_index=False)
        .agg(
            trade_count=("ticker", "size"),
            average_trade_return=("net_return", "mean"),
            win_rate=("net_return", lambda values: float((values > 0).mean()) if len(values) else 0.0),
        )
        if not trades.empty
        else pd.DataFrame(columns=["ticker", "trade_count", "average_trade_return", "win_rate"])
    )
    return pnl_by_asset.merge(trade_summary, on="ticker", how="left").fillna(0.0)


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return float(numerator / denominator)
