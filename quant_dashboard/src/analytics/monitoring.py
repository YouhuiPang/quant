from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.persistence.sqlite_store import SQLiteStateStore
from src.utils.config import load_config


def load_live_state(config_path: str | None = None) -> dict[str, pd.DataFrame]:
    """Load persisted live-like paper trading state from SQLite."""
    config = load_config(config_path)
    sqlite_path = Path(config["project_root"]) / config["paths"]["sqlite_path"]
    store = SQLiteStateStore(sqlite_path)
    store.initialize()
    return {
        "orders": store.load_table("orders"),
        "fills": store.load_table("fills"),
        "positions": store.load_table("positions"),
        "account": store.load_table("account_snapshots"),
        "risk_events": store.load_table("risk_events"),
        "targets": store.load_table("targets_state"),
        "signals": store.load_table("signals_state"),
    }
