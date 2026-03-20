from __future__ import annotations

from src.data.adapters.ibkr_historical_adapter import IBKRHistoricalDataAdapter


class MockIBHistoryClient:
    def request_historical_data(self, contract: dict, duration: str, bar_size: str) -> list[dict]:
        return [
            {"date": "2024-01-01", "open": 100, "high": 101, "low": 99, "close": 100.5, "volume": 1000},
            {"date": "2024-01-02", "open": 101, "high": 102, "low": 100, "close": 101.5, "volume": 1100},
        ]

    def request_market_snapshot(self, contract: dict) -> dict:
        return {"timestamp": "2024-01-02 16:00:00", "last": 101.5, "volume": 1100}


def test_historical_bars_normalize_to_common_schema() -> None:
    adapter = IBKRHistoricalDataAdapter(MockIBHistoryClient())
    frame = adapter.fetch_historical_data([{"symbol": "AAA"}], {"duration": "1 Y", "bar_size": "1 day", "throttle_seconds": 0.0})
    assert {"date", "ticker", "open", "high", "low", "close", "volume"}.issubset(frame.columns)


def test_timestamps_parse_correctly() -> None:
    adapter = IBKRHistoricalDataAdapter(MockIBHistoryClient())
    frame = adapter.fetch_historical_data([{"symbol": "AAA"}], {"duration": "1 Y", "bar_size": "1 day", "throttle_seconds": 0.0})
    assert frame.iloc[0]["date"] == "2024-01-01"
