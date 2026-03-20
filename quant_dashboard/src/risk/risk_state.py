from __future__ import annotations

import pandas as pd


def summarize_risk_state(approved_targets: pd.DataFrame) -> pd.DataFrame:
    """Summarize current risk state for dashboard consumption."""
    latest_timestamp = approved_targets["timestamp"].max()
    latest = approved_targets[approved_targets["timestamp"] == latest_timestamp].copy()
    latest["timestamp"] = pd.to_datetime(latest["timestamp"]).dt.strftime("%Y-%m-%d")
    return latest[["timestamp", "ticker", "target_weight", "approved_weight", "risk_flag", "risk_notes"]]
