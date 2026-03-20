from __future__ import annotations

import pandas as pd


def allocate_equal_weight_active(executed_positions: pd.DataFrame) -> pd.DataFrame:
    """Normalize active approved weights to equal-weight allocations on each date."""
    frame = executed_positions.copy()
    active_counts = frame.groupby("timestamp")["approved_weight"].transform(lambda values: int((values > 0).sum()))
    frame["target_weight"] = 0.0
    active_mask = frame["approved_weight"] > 0
    frame.loc[active_mask, "target_weight"] = 1.0 / active_counts[active_mask]
    return frame
