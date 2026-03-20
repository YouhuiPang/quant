from __future__ import annotations

from typing import Any

import pandas as pd


def build_position_snapshot(
    timestamp: pd.Timestamp,
    positions: dict[str, int],
    average_costs: dict[str, float],
    latest_prices: dict[str, float],
    equity: float,
) -> pd.DataFrame:
    """Build a position snapshot frame from holdings and latest prices."""
    rows: list[dict[str, Any]] = []
    for ticker, quantity in sorted(positions.items()):
        if quantity == 0:
            continue
        market_price = float(latest_prices.get(ticker, 0.0))
        market_value = quantity * market_price
        avg_cost = float(average_costs.get(ticker, market_price))
        unrealized_pnl = quantity * (market_price - avg_cost)
        weight = market_value / equity if equity else 0.0
        rows.append(
            {
                "timestamp": timestamp.strftime("%Y-%m-%d"),
                "ticker": ticker,
                "quantity": int(quantity),
                "market_price": market_price,
                "market_value": market_value,
                "weight": weight,
                "unrealized_pnl": unrealized_pnl,
            }
        )
    return pd.DataFrame(rows)


def build_account_snapshot(
    timestamp: pd.Timestamp,
    cash: float,
    positions_frame: pd.DataFrame,
    realized_pnl: float,
) -> pd.DataFrame:
    """Build a one-row account snapshot."""
    market_value = float(positions_frame["market_value"].sum()) if not positions_frame.empty else 0.0
    unrealized_pnl = float(positions_frame["unrealized_pnl"].sum()) if not positions_frame.empty else 0.0
    equity = cash + market_value
    return pd.DataFrame(
        [
            {
                "timestamp": timestamp.strftime("%Y-%m-%d"),
                "cash": cash,
                "equity": equity,
                "gross_exposure": market_value / equity if equity else 0.0,
                "net_exposure": market_value / equity if equity else 0.0,
                "realized_pnl": realized_pnl,
                "unrealized_pnl": unrealized_pnl,
            }
        ]
    )
