from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class BrokerBase(ABC):
    """Abstract broker interface for future live broker integrations."""

    @abstractmethod
    def connect(self) -> bool:
        """Connect to the broker or data backend."""

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect cleanly."""

    @abstractmethod
    def submit_orders(self, orders: pd.DataFrame, market_snapshot: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Submit orders and return persisted orders and fills."""

    @abstractmethod
    def get_open_orders(self) -> pd.DataFrame:
        """Return open orders."""

    @abstractmethod
    def get_positions(self) -> pd.DataFrame:
        """Return latest positions."""

    @abstractmethod
    def get_account_state(self) -> pd.DataFrame:
        """Return latest account snapshot."""

    @abstractmethod
    def fetch_historical_data(self, symbols: list[dict], sync_config: dict) -> pd.DataFrame:
        """Fetch normalized historical data from the broker backend."""

    @abstractmethod
    def fetch_latest_snapshot(self, symbols: list[dict]) -> pd.DataFrame:
        """Fetch normalized latest market snapshots."""
