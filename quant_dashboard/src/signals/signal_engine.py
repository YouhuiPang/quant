from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def generate_signals(feature_frame: pd.DataFrame, strategy_config: dict[str, Any]) -> pd.DataFrame:
    """Generate standardized multi-asset signals with confidence scores."""
    frame = feature_frame[["date", "ticker", "close", "rolling_mean_20", "momentum_10", "rolling_std_20"]].copy()
    allow_short = bool(strategy_config.get("allow_short", False))
    strategy_name = str(strategy_config.get("name", "trend_momentum_v1"))
    default_confidence = float(strategy_config.get("default_confidence", 0.75))

    long_condition = (frame["close"] > frame["rolling_mean_20"]) & (frame["momentum_10"] > 0)
    if allow_short:
        short_condition = (frame["close"] < frame["rolling_mean_20"]) & (frame["momentum_10"] < 0)
        frame["signal"] = np.select([long_condition, short_condition], [1.0, -1.0], default=0.0)
    else:
        frame["signal"] = np.where(long_condition, 1.0, 0.0)

    scaled_momentum = frame["momentum_10"].fillna(0.0).clip(lower=0.0, upper=0.2) / 0.2
    volatility_penalty = 1.0 - frame["rolling_std_20"].fillna(0.0).clip(lower=0.0, upper=0.08) / 0.08
    frame["confidence"] = ((scaled_momentum * 0.7) + (volatility_penalty * 0.3)).clip(lower=0.0, upper=1.0)
    frame.loc[frame["signal"] == 0, "confidence"] = default_confidence * 0.25
    frame["strategy_name"] = strategy_name
    frame["timestamp"] = pd.to_datetime(frame["date"])
    return frame[["timestamp", "ticker", "signal", "confidence", "strategy_name"]]
