from __future__ import annotations

import pandas as pd

from src.backtest.trade_ledger import build_trade_ledger


def test_trade_ledger_records_entry_exit_correctly() -> None:
    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
            "ticker": ["AAA"] * 3,
            "executed_weight": [0.0, 0.5, 0.0],
            "close": [100.0, 101.0, 102.0],
            "transaction_cost": [0.0, 0.001, 0.001],
        }
    )
    trades = build_trade_ledger(frame)
    assert len(trades) == 1
    assert trades.iloc[0]["entry_date"] == pd.Timestamp("2024-01-02")


def test_holding_period_and_returns_sensible() -> None:
    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-05", "2024-01-08"]),
            "ticker": ["AAA"] * 3,
            "executed_weight": [0.0, 0.5, 0.0],
            "close": [100.0, 105.0, 106.0],
            "transaction_cost": [0.0, 0.001, 0.001],
        }
    )
    trades = build_trade_ledger(frame)
    assert trades.iloc[0]["holding_period"] == 3
    assert trades.iloc[0]["gross_return"] > 0
