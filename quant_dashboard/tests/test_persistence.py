from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.persistence.sqlite_store import SQLiteStateStore


def test_sqlite_tables_initialize(tmp_path: Path) -> None:
    store = SQLiteStateStore(tmp_path / "state.db")
    store.initialize()
    store.append_table("orders", pd.DataFrame([{"order_id": "1", "timestamp": "2024-01-01", "ticker": "AAA", "side": "BUY", "quantity": 1, "order_type": "MKT", "status": "NEW"}]))
    assert not store.load_table("orders").empty


def test_latest_state_reload_works(tmp_path: Path) -> None:
    store = SQLiteStateStore(tmp_path / "state.db")
    store.initialize()
    frame = pd.DataFrame([{"timestamp": "2024-01-01", "cash": 100000.0, "equity": 100000.0, "gross_exposure": 0.0, "net_exposure": 0.0, "realized_pnl": 0.0, "unrealized_pnl": 0.0}])
    store.append_table("account_snapshots", frame)
    loaded = store.load_table("account_snapshots")
    assert loaded.iloc[0]["cash"] == 100000.0
