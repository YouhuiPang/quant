from __future__ import annotations

from typing import Any

import pandas as pd

from src.utils.validation import (
    validate_columns,
    validate_no_nulls,
    validate_numeric_columns,
    validate_ticker_values,
)


def validate_price_frame(df: pd.DataFrame, data_config: dict[str, Any]) -> None:
    """Validate a multi-asset OHLCV frame before research logic runs."""
    required_columns = data_config.get("required_columns", [])
    validate_columns(df, required_columns)
    validate_no_nulls(df, ["date", "ticker", "open", "high", "low", "close", "volume"])
    validate_numeric_columns(df, ["open", "high", "low", "close", "volume"])
    validate_ticker_values(df)

    duplicate_mask = df.duplicated(subset=["ticker", "date"])
    if duplicate_mask.any():
        duplicate_count = int(duplicate_mask.sum())
        raise ValueError(f"Duplicate ticker/date rows detected: {duplicate_count}")

    for ticker, group in df.groupby("ticker"):
        if not group["date"].is_monotonic_increasing:
            raise ValueError(f"Dates are not sorted for ticker '{ticker}'.")
        min_history = int(data_config.get("min_history_rows", 1))
        if len(group) < min_history:
            raise ValueError(
                f"Ticker '{ticker}' has insufficient history: {len(group)} rows, requires at least {min_history}."
            )
