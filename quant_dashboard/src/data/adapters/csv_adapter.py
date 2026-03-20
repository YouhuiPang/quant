from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.data.adapters.base import MarketDataAdapter


class CSVMarketDataAdapter(MarketDataAdapter):
    """Adapter for local cached CSV data."""

    def __init__(self, csv_path: Path) -> None:
        self.csv_path = csv_path

    def fetch_historical_data(self, symbols: list[dict[str, Any]], sync_config: dict[str, Any]) -> pd.DataFrame:
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV market data cache not found: {self.csv_path}")
        return pd.read_csv(self.csv_path)

    def fetch_latest_snapshot(self, symbols: list[dict[str, Any]]) -> pd.DataFrame:
        frame = self.fetch_historical_data(symbols, {})
        frame["date"] = pd.to_datetime(frame["date"])
        latest = frame.groupby("ticker", as_index=False)["date"].max().merge(frame, on=["ticker", "date"], how="left")
        return latest.rename(columns={"date": "timestamp"})[["timestamp", "ticker", "close", "volume"]]

    def fetch_contract_metadata(self, symbol_config: dict[str, Any]) -> dict[str, Any]:
        return {
            "ticker": symbol_config["symbol"],
            "sec_type": symbol_config.get("sec_type", "STK"),
            "exchange": symbol_config.get("exchange", "SMART"),
            "currency": symbol_config.get("currency", "USD"),
        }
