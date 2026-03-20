from __future__ import annotations

import pandas as pd

from src.backtest.metrics import compute_drawdown_series, summarize_metrics


def test_max_drawdown_is_correct_on_known_sequence() -> None:
    equity = pd.Series([1.0, 1.1, 1.05, 0.99, 1.2])
    drawdown = compute_drawdown_series(equity)
    assert round(drawdown.min(), 4) == -0.1


def test_metrics_values_are_reasonable_on_controlled_data() -> None:
    portfolio = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=4, freq="B"),
            "portfolio_net_return": [0.01, 0.0, -0.005, 0.02],
            "cumulative_strategy": [1.01, 1.01, 1.00495, 1.025049],
            "turnover": [0.5, 0.0, 0.2, 0.1],
        }
    )
    benchmark = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=4, freq="B"),
            "benchmark_return": [0.005, 0.0, -0.002, 0.01],
            "cumulative_benchmark": [1.005, 1.005, 1.00299, 1.0130199],
        }
    )
    trades = pd.DataFrame({"ticker": ["AAA", "BBB"], "holding_period": [5, 7], "net_return": [0.02, -0.01]})
    metrics = summarize_metrics(portfolio, benchmark, trades, 252)
    assert metrics["total_return"] > metrics["benchmark_total_return"]
    assert metrics["number_of_trades"] == 2


def test_excess_return_is_computed_correctly() -> None:
    portfolio = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=2, freq="B"),
            "portfolio_net_return": [0.01, 0.0],
            "cumulative_strategy": [1.01, 1.01],
            "turnover": [0.0, 0.0],
        }
    )
    benchmark = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=2, freq="B"),
            "benchmark_return": [0.005, 0.0],
            "cumulative_benchmark": [1.005, 1.005],
        }
    )
    metrics = summarize_metrics(portfolio, benchmark, pd.DataFrame(columns=["ticker", "holding_period", "net_return"]), 252)
    assert round(metrics["excess_return"], 4) == 0.005
