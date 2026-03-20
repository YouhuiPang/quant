from __future__ import annotations

from typing import Any, Iterable

import pandas as pd


REQUIRED_CONFIG_KEYS = {
    "project",
    "runtime",
    "paths",
    "data",
    "features",
    "strategy",
    "portfolio",
    "backtest",
    "benchmark",
    "risk",
    "paper_execution",
    "ibkr",
    "data_sync",
    "dashboard",
}


def validate_config(config: dict[str, Any]) -> None:
    """Validate that the configuration has the required sections."""
    missing = REQUIRED_CONFIG_KEYS - set(config)
    if missing:
        raise ValueError(f"Config missing required top-level keys: {sorted(missing)}")
    _validate_runtime_safety(config)


def validate_columns(df: pd.DataFrame, required_columns: Iterable[str]) -> None:
    """Ensure all required columns exist."""
    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")


def validate_no_nulls(df: pd.DataFrame, columns: Iterable[str]) -> None:
    """Ensure required columns are non-null."""
    null_columns = [column for column in columns if df[column].isnull().any()]
    if null_columns:
        raise ValueError(f"Null values detected in key columns: {null_columns}")


def validate_numeric_columns(df: pd.DataFrame, columns: Iterable[str]) -> None:
    """Ensure the given columns are numeric."""
    invalid = [column for column in columns if not pd.api.types.is_numeric_dtype(df[column])]
    if invalid:
        raise ValueError(f"Non-numeric columns found where numeric data is required: {invalid}")


def validate_ticker_values(df: pd.DataFrame) -> None:
    """Ensure ticker values are present and well-formed."""
    if "ticker" not in df.columns:
        raise ValueError("Ticker column is required for multi-asset support.")
    if df["ticker"].isnull().any():
        raise ValueError("Ticker column contains null values.")
    invalid = df["ticker"].astype(str).str.strip().eq("")
    if invalid.any():
        raise ValueError("Ticker column contains empty values.")


def _validate_runtime_safety(config: dict[str, Any]) -> None:
    runtime = config["runtime"]
    ibkr = config["ibkr"]
    if runtime["broker_provider"] == "ibkr" and not ibkr.get("readonly_mode", True):
        if not ibkr.get("enable_live_orders", False) or not ibkr.get("confirm_live_orders", False):
            raise ValueError(
                "IBKR live order mode requires both 'enable_live_orders: true' and 'confirm_live_orders: true'."
            )
