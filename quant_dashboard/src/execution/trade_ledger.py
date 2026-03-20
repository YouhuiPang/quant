from __future__ import annotations

import pandas as pd


def build_execution_trade_ledger(fills: pd.DataFrame) -> pd.DataFrame:
    """Build a simple execution blotter from fills."""
    if fills.empty:
        return pd.DataFrame(columns=["timestamp", "ticker", "fill_quantity", "fill_price", "transaction_cost"])
    return fills[["timestamp", "ticker", "fill_quantity", "fill_price", "transaction_cost"]].copy()
