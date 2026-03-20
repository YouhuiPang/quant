from __future__ import annotations

import uuid

import pandas as pd


def generate_orders(
    approved_targets: pd.DataFrame,
    current_positions: pd.DataFrame,
    account_state: pd.DataFrame,
    market_snapshot: pd.DataFrame,
    execution_config: dict,
) -> pd.DataFrame:
    """Generate delta orders from approved target weights and current holdings."""
    if approved_targets.empty:
        return pd.DataFrame(columns=["order_id", "timestamp", "ticker", "side", "quantity", "order_type", "status"])

    timestamp = pd.to_datetime(approved_targets["timestamp"]).max().strftime("%Y-%m-%d")
    equity = float(account_state.iloc[-1]["equity"]) if not account_state.empty else float(execution_config.get("initial_cash", 100000.0))
    lot_size = int(execution_config.get("lot_size", 1))
    price_map = market_snapshot.set_index("ticker")["close"].to_dict()
    current_map = current_positions.set_index("ticker")["quantity"].to_dict() if not current_positions.empty else {}

    rows: list[dict] = []
    for row in approved_targets.itertuples(index=False):
        approved_weight = float(row.approved_weight)
        price = float(price_map.get(row.ticker, 0.0))
        if price <= 0:
            continue
        target_qty = int((approved_weight * equity) / price)
        if lot_size > 1:
            target_qty = target_qty - (target_qty % lot_size)
        current_qty = int(current_map.get(row.ticker, 0))
        delta = target_qty - current_qty
        if delta == 0:
            continue
        rows.append(
            {
                "order_id": uuid.uuid4().hex,
                "timestamp": timestamp,
                "ticker": row.ticker,
                "side": "BUY" if delta > 0 else "SELL",
                "quantity": abs(delta),
                "order_type": execution_config.get("order_type", "MKT"),
                "status": "NEW",
            }
        )
    columns = ["order_id", "timestamp", "ticker", "side", "quantity", "order_type", "status"]
    return pd.DataFrame(rows, columns=columns)
