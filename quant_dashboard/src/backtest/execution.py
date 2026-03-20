from __future__ import annotations

from typing import Any

import pandas as pd


def apply_execution_lag(signal_frame: pd.DataFrame, backtest_config: dict[str, Any]) -> pd.DataFrame:
    """Map target positions to executed positions with an explicit lag."""
    lag_days = int(backtest_config.get("execution_lag_days", 1))
    frame = signal_frame.sort_values(["ticker", "date"]).copy()
    frame["executed_weight"] = (
        frame.groupby("ticker", group_keys=False)["approved_weight"].shift(lag_days).fillna(0.0)
    )
    return frame
