from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.brokers.ibkr_broker import IBKRBroker
from src.data.adapters.ibkr_historical_adapter import IBKRHistoricalDataAdapter


class MockIBClient:
    def connect(self, host: str, port: int, client_id: int) -> None:
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False

    def request_historical_data(self, contract: dict, duration: str, bar_size: str) -> list[dict]:
        return [{"date": "2024-01-01", "open": 100, "high": 101, "low": 99, "close": 100.5, "volume": 1000}]

    def request_market_snapshot(self, contract: dict) -> dict:
        return {"timestamp": "2024-01-01 16:00:00", "last": 101.0, "bid": 100.9, "ask": 101.1, "volume": 1200}

    def request_account_summary(self) -> list[dict]:
        return [{"tag": "NetLiquidation", "value": "100000"}, {"tag": "TotalCashValue", "value": "75000"}]

    def request_positions(self) -> list[dict]:
        return [{"symbol": "AAA", "position": 10, "marketPrice": 101.0, "marketValue": 1010.0, "unrealizedPnL": 10.0}]


def test_adapter_initializes_and_normalizes(temp_config) -> None:
    broker = IBKRBroker(temp_config["ibkr"], Path(temp_config["project_root"]) / temp_config["paths"]["sqlite_path"], client_factory=MockIBClient)
    assert broker.connect() is True
    adapter = IBKRHistoricalDataAdapter(broker.client)
    frame = adapter.fetch_historical_data(temp_config["data_sync"]["symbols"], temp_config["data_sync"])
    assert {"date", "ticker", "open", "high", "low", "close", "volume"}.issubset(frame.columns)


def test_config_validation_works_for_ibkr_safety(temp_config) -> None:
    assert temp_config["ibkr"]["readonly_mode"] is True
