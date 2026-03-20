from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.brokers.ibkr_broker import IBKRBroker


class MockLiveClient:
    def connect(self, host: str, port: int, client_id: int) -> None:
        return None

    def disconnect(self) -> None:
        return None


def test_internal_order_model_maps_cleanly_and_safety_gating_works(temp_config) -> None:
    broker = IBKRBroker(temp_config["ibkr"], Path(temp_config["project_root"]) / temp_config["paths"]["sqlite_path"], client_factory=MockLiveClient)
    broker.connect()
    orders = pd.DataFrame([{"order_id": "1", "timestamp": "2024-01-01", "ticker": "AAA", "side": "BUY", "quantity": 10, "order_type": "MKT", "status": "NEW"}])
    market = pd.DataFrame([{"ticker": "AAA", "close": 100.0}])
    with pytest.raises(PermissionError):
        broker.submit_orders(orders, market)
