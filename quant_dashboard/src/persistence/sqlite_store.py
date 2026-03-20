from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from src.persistence.state_store import StateStore
from src.utils.helpers import ensure_directories


class SQLiteStateStore(StateStore):
    """SQLite-backed state store for paper trading state."""

    TABLE_SCHEMAS = {
        "orders": """
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT,
                timestamp TEXT,
                ticker TEXT,
                side TEXT,
                quantity INTEGER,
                order_type TEXT,
                status TEXT
            )
        """,
        "fills": """
            CREATE TABLE IF NOT EXISTS fills (
                fill_id TEXT,
                order_id TEXT,
                timestamp TEXT,
                ticker TEXT,
                fill_price REAL,
                fill_quantity INTEGER,
                transaction_cost REAL
            )
        """,
        "positions": """
            CREATE TABLE IF NOT EXISTS positions (
                timestamp TEXT,
                ticker TEXT,
                quantity INTEGER,
                market_price REAL,
                market_value REAL,
                weight REAL,
                unrealized_pnl REAL
            )
        """,
        "account_snapshots": """
            CREATE TABLE IF NOT EXISTS account_snapshots (
                timestamp TEXT,
                cash REAL,
                equity REAL,
                gross_exposure REAL,
                net_exposure REAL,
                realized_pnl REAL,
                unrealized_pnl REAL
            )
        """,
        "risk_events": """
            CREATE TABLE IF NOT EXISTS risk_events (
                timestamp TEXT,
                ticker TEXT,
                target_weight REAL,
                approved_weight REAL,
                risk_flag TEXT,
                risk_notes TEXT
            )
        """,
        "signals_state": """
            CREATE TABLE IF NOT EXISTS signals_state (
                timestamp TEXT,
                ticker TEXT,
                signal REAL,
                confidence REAL,
                strategy_name TEXT
            )
        """,
        "targets_state": """
            CREATE TABLE IF NOT EXISTS targets_state (
                timestamp TEXT,
                ticker TEXT,
                target_weight REAL,
                approved_weight REAL,
                risk_flag TEXT,
                risk_notes TEXT
            )
        """,
        "market_snapshots": """
            CREATE TABLE IF NOT EXISTS market_snapshots (
                timestamp TEXT,
                ticker TEXT,
                close REAL,
                bid REAL,
                ask REAL,
                volume REAL
            )
        """,
        "broker_status": """
            CREATE TABLE IF NOT EXISTS broker_status (
                timestamp TEXT,
                data_provider TEXT,
                broker_provider TEXT,
                connection_status TEXT,
                runtime_mode TEXT,
                live_enabled INTEGER
            )
        """,
    }

    def __init__(self, sqlite_path: Path) -> None:
        self.sqlite_path = sqlite_path
        ensure_directories([sqlite_path.parent])

    def initialize(self) -> None:
        with sqlite3.connect(self.sqlite_path) as connection:
            for ddl in self.TABLE_SCHEMAS.values():
                connection.execute(ddl)
            connection.commit()

    def append_table(self, table_name: str, frame: pd.DataFrame) -> None:
        if frame.empty:
            return
        with sqlite3.connect(self.sqlite_path) as connection:
            frame.to_sql(table_name, connection, if_exists="append", index=False)

    def replace_table(self, table_name: str, frame: pd.DataFrame) -> None:
        with sqlite3.connect(self.sqlite_path) as connection:
            frame.to_sql(table_name, connection, if_exists="replace", index=False)

    def load_table(self, table_name: str) -> pd.DataFrame:
        with sqlite3.connect(self.sqlite_path) as connection:
            try:
                return pd.read_sql_query(f"SELECT * FROM {table_name}", connection)
            except Exception:
                return pd.DataFrame()
