from __future__ import annotations

import pandas as pd


def build_portfolio_returns(asset_frame: pd.DataFrame) -> pd.DataFrame:
    """Aggregate weighted asset returns into a portfolio return stream."""
    portfolio = (
        asset_frame.groupby("date", as_index=False)
        .agg(
            portfolio_gross_return=("strategy_gross_return", "sum"),
            portfolio_net_return=("strategy_net_return", "sum"),
            turnover=("turnover", "sum"),
            transaction_cost=("transaction_cost", "sum"),
            active_positions=("executed_weight", lambda values: int((values > 0).sum())),
        )
        .sort_values("date")
    )
    portfolio["cumulative_strategy"] = (1.0 + portfolio["portfolio_net_return"]).cumprod()
    return portfolio
