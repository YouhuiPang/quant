from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
from pandas.errors import EmptyDataError

from src.utils.config import load_config as load_platform_config, project_root


def load_config(config_path: str | Path | None = None) -> dict[str, Any]:
    """Backwards-compatible wrapper around the central config loader."""
    return load_platform_config(config_path)


def save_dataframe(df: pd.DataFrame, output_path: Path) -> None:
    """Persist a DataFrame as CSV, handling common date formatting consistently."""
    frame = df.copy()
    for column in ["date", "entry_date", "exit_date"]:
        if column in frame.columns:
            frame[column] = pd.to_datetime(frame[column], errors="coerce").dt.strftime("%Y-%m-%d")
    frame.to_csv(output_path, index=False)


def read_csv_if_exists(path: Path, parse_dates: list[str] | None = None) -> pd.DataFrame:
    """Read a CSV file if present, otherwise return an empty frame."""
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path, parse_dates=parse_dates)
    except EmptyDataError:
        return pd.DataFrame()


def save_json(payload: dict[str, Any], output_path: Path) -> None:
    """Write JSON output with readable indentation."""
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def load_json(path: Path) -> dict[str, Any]:
    """Load JSON data if present, otherwise return an empty dict."""
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
