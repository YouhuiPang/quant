from __future__ import annotations

import pandas as pd


def preprocess_price_data(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize types and ordering for a combined multi-asset OHLCV dataset."""
    processed = df.copy()
    processed["date"] = pd.to_datetime(processed["date"], errors="coerce")
    processed["ticker"] = processed["ticker"].astype(str).str.upper().str.strip()

    numeric_columns = ["open", "high", "low", "close", "volume"]
    for column in numeric_columns:
        if column in processed.columns:
            processed[column] = pd.to_numeric(processed[column], errors="coerce")

    processed = processed.dropna(subset=["date"])
    processed = processed.sort_values(["ticker", "date"]).reset_index(drop=True)
    return processed
