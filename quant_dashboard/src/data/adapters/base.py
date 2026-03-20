from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import pandas as pd


class MarketDataAdapter(ABC):
    """Base interface for historical and latest market data providers."""

    @abstractmethod
    def fetch_historical_data(self, symbols: list[dict[str, Any]], sync_config: dict[str, Any]) -> pd.DataFrame:
        """Return normalized historical OHLCV data."""

    @abstractmethod
    def fetch_latest_snapshot(self, symbols: list[dict[str, Any]]) -> pd.DataFrame:
        """Return normalized latest market snapshots."""

    @abstractmethod
    def fetch_contract_metadata(self, symbol_config: dict[str, Any]) -> dict[str, Any]:
        """Return normalized contract metadata."""
