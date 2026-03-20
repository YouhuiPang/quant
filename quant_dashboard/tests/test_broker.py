from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.brokers.paper_broker import PaperBroker


def test_paper_broker_stores_submitted_orders(tmp_path: Path) -> None:
    broker = PaperBroker(tmp_path / "state.db", 100000.0)
    orders = pd.DataFrame([{"order_id": "1", "timestamp": "2024-01-01", "ticker": "AAA", "side": "BUY", "quantity": 10, "order_type": "MKT", "status": "NEW"}])
    market = pd.DataFrame([{"ticker": "AAA", "close": 100.0}])
    broker.submit_orders(orders, market)
    assert not broker.store.load_table("orders").empty


def test_get_open_orders_and_account_state(tmp_path: Path) -> None:
    broker = PaperBroker(tmp_path / "state.db", 100000.0)
    assert broker.get_open_orders().empty
    assert not broker.get_account_state().empty
