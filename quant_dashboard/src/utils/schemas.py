from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class SignalRecord:
    timestamp: str
    ticker: str
    signal: float
    confidence: float
    strategy_name: str


@dataclass
class TargetPositionRecord:
    timestamp: str
    ticker: str
    target_weight: float


@dataclass
class ApprovedTargetRecord:
    timestamp: str
    ticker: str
    approved_weight: float
    risk_flag: str
    risk_notes: str


@dataclass
class OrderRecord:
    order_id: str
    timestamp: str
    ticker: str
    side: str
    quantity: int
    order_type: str
    status: str


@dataclass
class FillRecord:
    fill_id: str
    order_id: str
    timestamp: str
    ticker: str
    fill_price: float
    fill_quantity: int
    transaction_cost: float


@dataclass
class PositionSnapshotRecord:
    timestamp: str
    ticker: str
    quantity: int
    market_price: float
    market_value: float
    weight: float
    unrealized_pnl: float


@dataclass
class AccountSnapshotRecord:
    timestamp: str
    cash: float
    equity: float
    gross_exposure: float
    net_exposure: float
    realized_pnl: float
    unrealized_pnl: float


def record_to_dict(record: Any) -> dict[str, Any]:
    """Convert dataclass records to dictionaries."""
    return asdict(record)
