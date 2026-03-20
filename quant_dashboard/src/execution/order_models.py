from __future__ import annotations

from dataclasses import dataclass


@dataclass
class OrderModel:
    order_id: str
    timestamp: str
    ticker: str
    side: str
    quantity: int
    order_type: str
    status: str = "NEW"


@dataclass
class FillModel:
    fill_id: str
    order_id: str
    timestamp: str
    ticker: str
    fill_price: float
    fill_quantity: int
    transaction_cost: float
