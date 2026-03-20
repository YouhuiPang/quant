from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.brokers.broker_base import BrokerBase
from src.execution.fill_simulator import simulate_fills
from src.persistence.snapshots import build_account_snapshot, build_position_snapshot
from src.persistence.sqlite_store import SQLiteStateStore


class PaperBroker(BrokerBase):
    """Paper broker that simulates immediate fills and persists state to SQLite."""

    def __init__(self, sqlite_path: Path, initial_cash: float, transaction_cost_bps: float = 10.0) -> None:
        self.store = SQLiteStateStore(sqlite_path)
        self.store.initialize()
        self.initial_cash = initial_cash
        self.transaction_cost_bps = transaction_cost_bps
        self.positions: dict[str, int] = {}
        self.average_costs: dict[str, float] = {}
        self.cash = initial_cash
        self.realized_pnl = 0.0
        self._load_latest_state()

    def connect(self) -> bool:
        return True

    def disconnect(self) -> None:
        return None

    def submit_orders(self, orders: pd.DataFrame, market_snapshot: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        if orders.empty:
            return orders, pd.DataFrame(columns=["fill_id", "order_id", "timestamp", "ticker", "fill_price", "fill_quantity", "transaction_cost"])

        submitted = orders.copy()
        submitted["status"] = "SUBMITTED"
        fills = simulate_fills(submitted, market_snapshot, {"fill_price_field": "close", "transaction_cost_bps": self.transaction_cost_bps})
        submitted["status"] = "FILLED"
        self.store.append_table("orders", submitted)
        self._apply_fills(submitted, fills)
        self.store.append_table("fills", fills)
        self._persist_snapshots(pd.to_datetime(submitted["timestamp"]).max(), market_snapshot)
        return submitted, fills

    def get_open_orders(self) -> pd.DataFrame:
        orders = self.store.load_table("orders")
        if orders.empty:
            return orders
        return orders[orders["status"] != "FILLED"].copy()

    def get_positions(self) -> pd.DataFrame:
        positions = self.store.load_table("positions")
        if positions.empty:
            return positions
        latest_timestamp = positions["timestamp"].max()
        return positions[positions["timestamp"] == latest_timestamp].copy()

    def get_account_state(self) -> pd.DataFrame:
        account = self.store.load_table("account_snapshots")
        if account.empty:
            return pd.DataFrame(
                [
                    {
                        "timestamp": pd.Timestamp.today().strftime("%Y-%m-%d"),
                        "cash": self.initial_cash,
                        "equity": self.initial_cash,
                        "gross_exposure": 0.0,
                        "net_exposure": 0.0,
                        "realized_pnl": 0.0,
                        "unrealized_pnl": 0.0,
                    }
                ]
            )
        latest_timestamp = account["timestamp"].max()
        return account[account["timestamp"] == latest_timestamp].copy()

    def fetch_historical_data(self, symbols: list[dict], sync_config: dict) -> pd.DataFrame:
        raise NotImplementedError("PaperBroker does not provide historical market data.")

    def fetch_latest_snapshot(self, symbols: list[dict]) -> pd.DataFrame:
        raise NotImplementedError("PaperBroker does not provide market data snapshots.")

    def _load_latest_state(self) -> None:
        positions = self.store.load_table("positions")
        account = self.store.load_table("account_snapshots")
        if not positions.empty:
            latest_positions = positions[positions["timestamp"] == positions["timestamp"].max()]
            self.positions = latest_positions.set_index("ticker")["quantity"].astype(int).to_dict()
            self.average_costs = latest_positions.set_index("ticker")["market_price"].astype(float).to_dict()
        if not account.empty:
            latest_account = account[account["timestamp"] == account["timestamp"].max()].iloc[-1]
            self.cash = float(latest_account["cash"])
            self.realized_pnl = float(latest_account["realized_pnl"])

    def _apply_fills(self, orders: pd.DataFrame, fills: pd.DataFrame) -> None:
        order_map = orders.set_index("order_id")["side"].to_dict()
        for row in fills.itertuples(index=False):
            side = -1 if order_map.get(row.order_id) == "SELL" else 1

            quantity = int(row.fill_quantity) * side
            fill_value = float(row.fill_price) * abs(int(row.fill_quantity))
            transaction_cost = float(row.transaction_cost)
            ticker = str(row.ticker)
            current_qty = int(self.positions.get(ticker, 0))
            current_avg_cost = float(self.average_costs.get(ticker, 0.0))

            if quantity > 0:
                new_qty = current_qty + quantity
                total_cost_basis = current_avg_cost * current_qty + fill_value + transaction_cost
                self.average_costs[ticker] = total_cost_basis / new_qty if new_qty else 0.0
                self.cash -= fill_value + transaction_cost
                self.positions[ticker] = new_qty
            else:
                sell_qty = abs(quantity)
                self.cash += fill_value - transaction_cost
                realized = sell_qty * (float(row.fill_price) - current_avg_cost) - transaction_cost
                self.realized_pnl += realized
                self.positions[ticker] = current_qty - sell_qty
                if self.positions[ticker] == 0:
                    self.average_costs[ticker] = 0.0

    def _persist_snapshots(self, timestamp: pd.Timestamp, market_snapshot: pd.DataFrame) -> None:
        price_map = market_snapshot.set_index("ticker")["close"].astype(float).to_dict()
        positions = build_position_snapshot(timestamp, self.positions, self.average_costs, price_map, self._estimate_equity(price_map))
        account = build_account_snapshot(timestamp, self.cash, positions, self.realized_pnl)
        self.store.append_table("positions", positions)
        self.store.append_table("account_snapshots", account)

    def _estimate_equity(self, latest_prices: dict[str, float]) -> float:
        market_value = sum(int(quantity) * float(latest_prices.get(ticker, 0.0)) for ticker, quantity in self.positions.items())
        return self.cash + market_value
