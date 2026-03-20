from __future__ import annotations

import time
from typing import Any

import pandas as pd

from src.data.adapters.base import MarketDataAdapter
from src.brokers.ibkr_models import build_contract_definition


class IBKRHistoricalDataAdapter(MarketDataAdapter):
    """Historical data adapter that normalizes IBKR-style bar payloads."""

    def __init__(self, broker_client: Any) -> None:
        self.broker_client = broker_client

    def fetch_historical_data(self, symbols: list[dict[str, Any]], sync_config: dict[str, Any]) -> pd.DataFrame:
        frames: list[pd.DataFrame] = []
        throttle_seconds = float(sync_config.get("throttle_seconds", 1.0))
        for symbol_config in symbols:
            contract = build_contract_definition(symbol_config)
            raw_bars = self.broker_client.request_historical_data(
                contract=contract,
                duration=sync_config.get("duration", "1 Y"),
                bar_size=sync_config.get("bar_size", "1 day"),
            )
            normalized = self._normalize_historical_bars(raw_bars, symbol_config["symbol"])
            frames.append(normalized)
            time.sleep(throttle_seconds)
        if not frames:
            return pd.DataFrame(columns=["date", "ticker", "open", "high", "low", "close", "volume"])
        return pd.concat(frames, ignore_index=True)

    def fetch_latest_snapshot(self, symbols: list[dict[str, Any]]) -> pd.DataFrame:
        rows = []
        for symbol_config in symbols:
            contract = build_contract_definition(symbol_config)
            snapshot = self.broker_client.request_market_snapshot(contract)
            rows.append(self._normalize_snapshot(snapshot, symbol_config["symbol"]))
        return pd.DataFrame(rows)

    def fetch_contract_metadata(self, symbol_config: dict[str, Any]) -> dict[str, Any]:
        return build_contract_definition(symbol_config)

    def _normalize_historical_bars(self, raw_bars: list[dict[str, Any]], ticker: str) -> pd.DataFrame:
        rows = []
        for bar in raw_bars:
            rows.append(
                {
                    "date": pd.to_datetime(bar["date"]).strftime("%Y-%m-%d"),
                    "ticker": ticker,
                    "open": float(bar["open"]),
                    "high": float(bar["high"]),
                    "low": float(bar["low"]),
                    "close": float(bar["close"]),
                    "volume": float(bar.get("volume", 0.0)),
                }
            )
        return pd.DataFrame(rows)

    def _normalize_snapshot(self, raw_snapshot: dict[str, Any], ticker: str) -> dict[str, Any]:
        return {
            "timestamp": pd.to_datetime(raw_snapshot["timestamp"]).strftime("%Y-%m-%d %H:%M:%S"),
            "ticker": ticker,
            "close": float(raw_snapshot.get("last", raw_snapshot.get("close", 0.0))),
            "volume": float(raw_snapshot.get("volume", 0.0)),
        }
