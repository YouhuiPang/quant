from __future__ import annotations

import pandas as pd


def calculate_turnover(executed_positions: pd.DataFrame) -> pd.DataFrame:
    """Estimate one-way turnover from per-asset changes in deployed portfolio weight."""
    frame = executed_positions.sort_values(["ticker", "date"]).copy()
    turnover_source = "executed_weight" if "executed_weight" in frame.columns else "weight"
    frame["turnover"] = frame.groupby("ticker", group_keys=False)[turnover_source].diff().abs().fillna(frame[turnover_source].abs())
    return frame


def calculate_transaction_costs(turnover_frame: pd.DataFrame, transaction_cost_bps: float) -> pd.DataFrame:
    """Apply linear transaction costs from turnover in basis points."""
    frame = turnover_frame.copy()
    rate = transaction_cost_bps / 10_000.0
    frame["transaction_cost"] = frame["turnover"] * rate
    return frame
