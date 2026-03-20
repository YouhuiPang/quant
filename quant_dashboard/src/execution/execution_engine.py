from __future__ import annotations

import pandas as pd

from src.execution.order_router import generate_orders


def create_orders_from_targets(
    approved_targets: pd.DataFrame,
    current_positions: pd.DataFrame,
    account_state: pd.DataFrame,
    market_snapshot: pd.DataFrame,
    execution_config: dict,
) -> pd.DataFrame:
    """Create orders required to move from current holdings to approved targets."""
    return generate_orders(approved_targets, current_positions, account_state, market_snapshot, execution_config)
