from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


def ensure_directories(paths: Iterable[Path]) -> None:
    """Create a collection of directories if they do not exist."""
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def format_metric_value(value: float, percentage: bool = True, decimals: int = 2) -> str:
    """Format dashboard metric values consistently."""
    if percentage:
        return f"{value * 100:.{decimals}f}%"
    return f"{value:.{decimals}f}"


def latest_date(df: pd.DataFrame) -> pd.Timestamp | None:
    """Return the latest available date from a frame, if any."""
    if df.empty or "date" not in df.columns:
        return None
    return pd.to_datetime(df["date"]).max()
