from __future__ import annotations

from pathlib import Path

from src.brokers.ibkr_broker import IBKRBroker


class MockAccountClient:
    def connect(self, host: str, port: int, client_id: int) -> None:
        return None

    def disconnect(self) -> None:
        return None

    def request_account_summary(self) -> list[dict]:
        return [
            {"tag": "NetLiquidation", "value": "125000"},
            {"tag": "TotalCashValue", "value": "80000"},
            {"tag": "BuyingPower", "value": "150000"},
        ]

    def request_positions(self) -> list[dict]:
        return [{"symbol": "SPY", "position": 20, "marketPrice": 500.0, "marketValue": 10000.0, "unrealizedPnL": 100.0}]


def test_account_and_position_payloads_normalize(temp_config) -> None:
    broker = IBKRBroker(temp_config["ibkr"], Path(temp_config["project_root"]) / temp_config["paths"]["sqlite_path"], client_factory=MockAccountClient)
    broker.connect()
    account = broker.get_account_state()
    positions = broker.get_positions()
    assert "buying_power" in account.columns
    assert "ticker" in positions.columns
