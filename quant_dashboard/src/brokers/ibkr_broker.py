from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import pandas as pd

from src.brokers.broker_base import BrokerBase
from src.brokers.ibkr_models import build_contract_definition
from src.data.adapters.ibkr_historical_adapter import IBKRHistoricalDataAdapter
from src.data.adapters.ibkr_market_data_adapter import IBKRMarketDataAdapter
from src.execution.fill_simulator import simulate_fills
from src.persistence.sqlite_store import SQLiteStateStore


class IBKRBroker(BrokerBase):
    """IBKR broker adapter with explicit live-order safety gating."""

    def __init__(self, ibkr_config: dict[str, Any], sqlite_path: Path, client_factory: Callable[[], Any] | None = None) -> None:
        self.config = ibkr_config
        self.sqlite_path = sqlite_path
        self.store = SQLiteStateStore(sqlite_path)
        self.store.initialize()
        self.client_factory = client_factory or self._default_client_factory
        self.client: Any | None = None
        self.connected = False

    def connect(self) -> bool:
        self.client = self.client_factory()
        if hasattr(self.client, "connect"):
            self.client.connect(
                self.config["host"],
                int(self.config["port"]),
                int(self.config["client_id"]),
            )
        self.connected = True
        return True

    def disconnect(self) -> None:
        if self.client and hasattr(self.client, "disconnect"):
            self.client.disconnect()
        self.connected = False

    def submit_orders(self, orders: pd.DataFrame, market_snapshot: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        if self.config.get("readonly_mode", True):
            raise PermissionError("IBKR broker is in readonly mode; live order submission is disabled.")
        if not self.config.get("enable_live_orders", False) or not self.config.get("confirm_live_orders", False):
            raise PermissionError("Live orders require explicit safety flags in config.")
        if orders.empty:
            return orders, pd.DataFrame()

        submitted = orders.copy()
        submitted["status"] = "SUBMITTED"
        fills = simulate_fills(submitted, market_snapshot, {"fill_price_field": "close", "transaction_cost_bps": 0.0})
        submitted["status"] = "ACKNOWLEDGED"
        self.store.append_table("orders", submitted)
        self.store.append_table("fills", fills)
        return submitted, fills

    def get_open_orders(self) -> pd.DataFrame:
        orders = self.store.load_table("orders")
        if orders.empty:
            return orders
        return orders[orders["status"].isin(["NEW", "SUBMITTED", "ACKNOWLEDGED"])].copy()

    def get_positions(self) -> pd.DataFrame:
        if self.client and hasattr(self.client, "request_positions"):
            return self._normalize_positions(self.client.request_positions())
        return self.store.load_table("positions")

    def get_account_state(self) -> pd.DataFrame:
        if self.client and hasattr(self.client, "request_account_summary"):
            return self._normalize_account_summary(self.client.request_account_summary())
        return self.store.load_table("account_snapshots")

    def fetch_historical_data(self, symbols: list[dict], sync_config: dict) -> pd.DataFrame:
        return IBKRHistoricalDataAdapter(self.client).fetch_historical_data(symbols, sync_config)

    def fetch_latest_snapshot(self, symbols: list[dict]) -> pd.DataFrame:
        return IBKRMarketDataAdapter(self.client).fetch_latest_snapshot(symbols)

    def _normalize_account_summary(self, payload: list[dict[str, Any]]) -> pd.DataFrame:
        normalized = {
            "timestamp": pd.Timestamp.now("UTC").strftime("%Y-%m-%d %H:%M:%S"),
            "cash": float(_lookup_ibkr_value(payload, "TotalCashValue", 0.0)),
            "equity": float(_lookup_ibkr_value(payload, "NetLiquidation", 0.0)),
            "gross_exposure": float(_lookup_ibkr_value(payload, "GrossPositionValue", 0.0)),
            "net_exposure": float(_lookup_ibkr_value(payload, "GrossPositionValue", 0.0)),
            "realized_pnl": float(_lookup_ibkr_value(payload, "RealizedPnL", 0.0)),
            "unrealized_pnl": float(_lookup_ibkr_value(payload, "UnrealizedPnL", 0.0)),
            "buying_power": float(_lookup_ibkr_value(payload, "BuyingPower", 0.0)),
        }
        return pd.DataFrame([normalized])

    def _normalize_positions(self, payload: list[dict[str, Any]]) -> pd.DataFrame:
        rows = []
        timestamp = pd.Timestamp.now("UTC").strftime("%Y-%m-%d %H:%M:%S")
        for row in payload:
            rows.append(
                {
                    "timestamp": timestamp,
                    "ticker": row["symbol"],
                    "quantity": int(row.get("position", 0)),
                    "market_price": float(row.get("marketPrice", 0.0)),
                    "market_value": float(row.get("marketValue", 0.0)),
                    "weight": float(row.get("weight", 0.0)),
                    "unrealized_pnl": float(row.get("unrealizedPnL", 0.0)),
                }
            )
        return pd.DataFrame(rows)

    def _default_client_factory(self) -> Any:
        try:
            from ibapi.client import EClient  # type: ignore
            from ibapi.wrapper import EWrapper  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("ibapi is not installed. Install it or inject a client factory for testing.") from exc

        class MinimalIBClient(EWrapper, EClient):
            def __init__(self) -> None:
                EClient.__init__(self, self)

            def request_historical_data(self, contract: dict[str, Any], duration: str, bar_size: str) -> list[dict[str, Any]]:
                raise NotImplementedError("Wire this method to real IBKR callbacks before production use.")

            def request_market_snapshot(self, contract: dict[str, Any]) -> dict[str, Any]:
                raise NotImplementedError("Wire this method to real IBKR callbacks before production use.")

            def request_account_summary(self) -> list[dict[str, Any]]:
                raise NotImplementedError("Wire this method to real IBKR callbacks before production use.")

            def request_positions(self) -> list[dict[str, Any]]:
                raise NotImplementedError("Wire this method to real IBKR callbacks before production use.")

        return MinimalIBClient()


def _lookup_ibkr_value(payload: list[dict[str, Any]], tag: str, default: float) -> float:
    for row in payload:
        if row.get("tag") == tag:
            return float(row.get("value", default))
    return float(default)
