from __future__ import annotations

from typing import Any

import pandas as pd


def apply_risk_rules(targets: pd.DataFrame, feature_frame: pd.DataFrame, risk_config: dict[str, Any]) -> pd.DataFrame:
    """Apply simple pre-trade risk rules with explicit notes."""
    frame = targets.copy()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"])
    frame["approved_weight"] = frame["target_weight"]
    frame["risk_flag"] = "APPROVED"
    frame["risk_notes"] = "Approved"

    if bool(risk_config.get("kill_switch", False)):
        frame["approved_weight"] = 0.0
        frame["risk_flag"] = "BLOCKED"
        frame["risk_notes"] = "Kill switch enabled"
        return frame

    max_weight = float(risk_config.get("max_weight_per_asset", 1.0))
    high_weight_mask = frame["approved_weight"] > max_weight
    frame.loc[high_weight_mask, "approved_weight"] = max_weight
    frame.loc[high_weight_mask, "risk_flag"] = "CAPPED"
    frame.loc[high_weight_mask, "risk_notes"] = "Max asset weight cap applied"

    confidence_threshold = float(risk_config.get("min_confidence_threshold", 0.0))
    low_confidence_mask = frame["confidence"] < confidence_threshold
    frame.loc[low_confidence_mask, "approved_weight"] = 0.0
    frame.loc[low_confidence_mask, "risk_flag"] = "BLOCKED"
    frame.loc[low_confidence_mask, "risk_notes"] = "Below confidence threshold"

    latest_features = feature_frame[["date", "ticker", "rolling_std_20"]].rename(columns={"date": "timestamp"})
    latest_features["timestamp"] = pd.to_datetime(latest_features["timestamp"])
    merged = frame.merge(latest_features, on=["timestamp", "ticker"], how="left")
    vol_cap = float(risk_config.get("volatility_cap", 1.0))
    high_vol_mask = merged["rolling_std_20"].fillna(0.0) > vol_cap
    merged.loc[high_vol_mask, "approved_weight"] = 0.0
    merged.loc[high_vol_mask, "risk_flag"] = "BLOCKED"
    merged.loc[high_vol_mask, "risk_notes"] = "Blocked by volatility filter"

    max_positions = int(risk_config.get("max_concurrent_positions", 999))
    trimmed_frames: list[pd.DataFrame] = []
    for timestamp, group in merged.groupby("timestamp", sort=False):
        approved = group[group["approved_weight"] > 0].sort_values(["confidence", "approved_weight"], ascending=[False, False]).copy()
        if len(approved) > max_positions:
            blocked_index = approved.index[max_positions:]
            group.loc[blocked_index, "approved_weight"] = 0.0
            group.loc[blocked_index, "risk_flag"] = "BLOCKED"
            group.loc[blocked_index, "risk_notes"] = "Blocked by max concurrent positions"
        trimmed_frames.append(group)
    merged = pd.concat(trimmed_frames, ignore_index=True)

    gross_limit = float(risk_config.get("gross_exposure_limit", 1.0))
    for timestamp, group in merged.groupby("timestamp"):
        gross = float(group["approved_weight"].sum())
        if gross > gross_limit and gross > 0:
            scale = gross_limit / gross
            idx = group.index
            merged.loc[idx, "approved_weight"] = merged.loc[idx, "approved_weight"] * scale
            capped = merged.loc[idx, "approved_weight"] > 0
            merged.loc[idx[capped], "risk_flag"] = "CAPPED"
            merged.loc[idx[capped], "risk_notes"] = "Scaled to gross exposure limit"

    return merged[["timestamp", "ticker", "signal", "confidence", "strategy_name", "target_weight", "approved_weight", "risk_flag", "risk_notes"]]
