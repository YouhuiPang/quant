from __future__ import annotations

import pandas as pd

from src.execution.execution_engine import create_orders_from_targets


def test_target_to_order_mapping_works() -> None:
    approved = pd.DataFrame(
        {"timestamp": pd.to_datetime(["2024-01-01"]), "ticker": ["AAA"], "approved_weight": [0.5]}
    )
    positions = pd.DataFrame(columns=["ticker", "quantity"])
    account = pd.DataFrame([{"equity": 100000.0}])
    market = pd.DataFrame([{"ticker": "AAA", "close": 100.0}])
    orders = create_orders_from_targets(approved, positions, account, market, {"order_type": "MKT", "lot_size": 1, "initial_cash": 100000.0})
    assert not orders.empty
    assert orders.iloc[0]["side"] == "BUY"


def test_orders_generated_only_when_needed() -> None:
    approved = pd.DataFrame({"timestamp": pd.to_datetime(["2024-01-01"]), "ticker": ["AAA"], "approved_weight": [0.5]})
    positions = pd.DataFrame([{"ticker": "AAA", "quantity": 500}])
    account = pd.DataFrame([{"equity": 100000.0}])
    market = pd.DataFrame([{"ticker": "AAA", "close": 100.0}])
    orders = create_orders_from_targets(approved, positions, account, market, {"order_type": "MKT", "lot_size": 1, "initial_cash": 100000.0})
    assert orders.empty
