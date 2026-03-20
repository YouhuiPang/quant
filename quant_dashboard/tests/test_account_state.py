from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.brokers.paper_broker import PaperBroker


def test_cash_equity_update_after_fills(tmp_path: Path) -> None:
    broker = PaperBroker(tmp_path / "state.db", 100000.0)
    orders = pd.DataFrame([{"order_id": "1", "timestamp": "2024-01-01", "ticker": "AAA", "side": "BUY", "quantity": 10, "order_type": "MKT", "status": "NEW"}])
    market = pd.DataFrame([{"ticker": "AAA", "close": 100.0}])
    broker.submit_orders(orders, market)
    account = broker.get_account_state().iloc[-1]
    assert account["cash"] < 100000.0
    assert account["equity"] > 0


def test_exposures_update_correctly(tmp_path: Path) -> None:
    broker = PaperBroker(tmp_path / "state.db", 100000.0)
    orders = pd.DataFrame([{"order_id": "1", "timestamp": "2024-01-01", "ticker": "AAA", "side": "BUY", "quantity": 10, "order_type": "MKT", "status": "NEW"}])
    market = pd.DataFrame([{"ticker": "AAA", "close": 100.0}])
    broker.submit_orders(orders, market)
    account = broker.get_account_state().iloc[-1]
    assert account["gross_exposure"] >= 0
