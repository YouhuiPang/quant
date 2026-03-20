from __future__ import annotations

from typing import Any

import pandas as pd

from src.data.adapters.base import MarketDataAdapter
from src.brokers.ibkr_models import build_contract_definition


class IBKRMarketDataAdapter(MarketDataAdapter):
    """Snapshot-oriented adapter for latest IBKR market data."""

    def __init__(self, broker_client: Any) -> None:
        self.broker_client = broker_client

    def fetch_historical_data(self, symbols: list[dict[str, Any]], sync_config: dict[str, Any]) -> pd.DataFrame:
        raise NotImplementedError("Use IBKRHistoricalDataAdapter for historical data.")

    def fetch_latest_snapshot(self, symbols: list[dict[str, Any]]) -> pd.DataFrame:
        rows = []
        for symbol_config in symbols:
            contract = build_contract_definition(symbol_config)
            snapshot = self.broker_client.request_market_snapshot(contract)
            rows.append(
                {
                    "timestamp": pd.to_datetime(snapshot["timestamp"]).strftime("%Y-%m-%d %H:%M:%S"),
                    "ticker": symbol_config["symbol"],
                    "close": float(snapshot.get("last", snapshot.get("close", 0.0))),
                    "bid": float(snapshot.get("bid", 0.0)),
                    "ask": float(snapshot.get("ask", 0.0)),
                    "volume": float(snapshot.get("volume", 0.0)),
                }
            )
        return pd.DataFrame(rows)

    def fetch_contract_metadata(self, symbol_config: dict[str, Any]) -> dict[str, Any]:
        return build_contract_definition(symbol_config)
