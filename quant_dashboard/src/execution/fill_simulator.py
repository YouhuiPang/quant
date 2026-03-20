from __future__ import annotations

import uuid

import pandas as pd


def simulate_fills(orders: pd.DataFrame, market_snapshot: pd.DataFrame, execution_config: dict) -> pd.DataFrame:
    """Simulate full fills at the configured market price field."""
    if orders.empty:
        return pd.DataFrame(columns=["fill_id", "order_id", "timestamp", "ticker", "fill_price", "fill_quantity", "transaction_cost"])

    fill_price_field = execution_config.get("fill_price_field", "close")
    cost_bps = float(execution_config.get("transaction_cost_bps", 0.0))
    price_map = market_snapshot.set_index("ticker")[fill_price_field].to_dict()

    fills = orders.copy()
    fills["fill_id"] = [uuid.uuid4().hex for _ in range(len(fills))]
    fills["fill_price"] = fills["ticker"].map(price_map).astype(float)
    fills["fill_quantity"] = fills["quantity"].astype(int)
    fills["transaction_cost"] = fills["fill_price"] * fills["fill_quantity"] * cost_bps / 10_000.0
    return fills[["fill_id", "order_id", "timestamp", "ticker", "fill_price", "fill_quantity", "transaction_cost"]]
