from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def engineer_features(df: pd.DataFrame, feature_config: dict[str, Any]) -> pd.DataFrame:
    """Create reusable per-asset research features from OHLCV price data."""
    ma_short = int(feature_config.get("ma_short_window", 5))
    ma_long = int(feature_config.get("ma_long_window", 20))
    momentum_window = int(feature_config.get("momentum_window", 10))
    drawdown_window = int(feature_config.get("drawdown_window", 20))

    frames: list[pd.DataFrame] = []
    for ticker, group in df.groupby("ticker", sort=False):
        asset = group.copy()
        asset["return_1d"] = asset["close"].pct_change().fillna(0.0)
        asset["rolling_mean_5"] = asset["close"].rolling(ma_short, min_periods=ma_short).mean()
        asset["rolling_mean_20"] = asset["close"].rolling(ma_long, min_periods=ma_long).mean()
        asset["rolling_std_5"] = asset["return_1d"].rolling(ma_short, min_periods=ma_short).std()
        asset["rolling_std_20"] = asset["return_1d"].rolling(ma_long, min_periods=ma_long).std()
        asset["momentum_10"] = asset["close"] / asset["close"].shift(momentum_window) - 1.0
        asset_peak = asset["close"].rolling(drawdown_window, min_periods=1).max()
        asset["drawdown_20"] = asset["close"] / asset_peak - 1.0
        asset["high_low_range"] = (asset["high"] - asset["low"]) / asset["close"]
        asset["price_above_ma20"] = (asset["close"] > asset["rolling_mean_20"]).astype(int)
        asset["ticker"] = ticker
        frames.append(asset)

    features = pd.concat(frames, ignore_index=True)
    numeric_columns = [column for column in features.columns if column not in {"date", "ticker"}]
    features[numeric_columns] = features[numeric_columns].replace([np.inf, -np.inf], np.nan)
    return features
