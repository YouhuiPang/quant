from __future__ import annotations

import pandas as pd


def build_target_positions(signals: pd.DataFrame) -> pd.DataFrame:
    """Convert standardized signals into target portfolio weights."""
    frame = signals.copy()
    active_mask = frame["signal"] > 0
    active_counts = frame.groupby("timestamp")["signal"].transform(lambda values: int((values > 0).sum()))
    frame["target_weight"] = 0.0
    frame.loc[active_mask, "target_weight"] = 1.0 / active_counts[active_mask]
    return frame[["timestamp", "ticker", "signal", "confidence", "strategy_name", "target_weight"]]
