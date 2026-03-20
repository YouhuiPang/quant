from __future__ import annotations

from typing import Any

import pandas as pd


def build_trade_ledger(asset_frame: pd.DataFrame) -> pd.DataFrame:
    """Build a professional long-flat trade ledger from executed positions."""
    trade_rows: list[dict[str, Any]] = []

    for ticker, group in asset_frame.sort_values(["ticker", "date"]).groupby("ticker", sort=False):
        open_trade: dict[str, Any] | None = None

        for row in group.itertuples(index=False):
            current_position = float(row.executed_weight)
            if open_trade is None and current_position > 0:
                open_trade = {
                    "ticker": ticker,
                    "entry_date": pd.Timestamp(row.date),
                    "entry_price": float(row.close),
                    "entry_cost": float(row.transaction_cost),
                }
                continue

            if open_trade is not None and current_position == 0:
                entry_date = pd.Timestamp(open_trade["entry_date"])
                exit_date = pd.Timestamp(row.date)
                entry_price = float(open_trade["entry_price"])
                exit_price = float(row.close)
                total_cost = float(open_trade["entry_cost"]) + float(row.transaction_cost)
                gross_return = exit_price / entry_price - 1.0
                net_return = gross_return - total_cost

                trade_rows.append(
                    {
                        "ticker": ticker,
                        "entry_date": entry_date,
                        "exit_date": exit_date,
                        "entry_price": entry_price,
                        "exit_price": exit_price,
                        "direction": "LONG",
                        "holding_period": int((exit_date - entry_date).days),
                        "gross_return": gross_return,
                        "net_return": net_return,
                        "transaction_cost": total_cost,
                        "pnl": net_return,
                    }
                )
                open_trade = None

        if open_trade is not None:
            last_row = group.iloc[-1]
            exit_date = pd.Timestamp(last_row["date"])
            exit_price = float(last_row["close"])
            entry_date = pd.Timestamp(open_trade["entry_date"])
            entry_price = float(open_trade["entry_price"])
            total_cost = float(open_trade["entry_cost"]) + float(last_row["transaction_cost"])
            gross_return = exit_price / entry_price - 1.0
            net_return = gross_return - total_cost
            trade_rows.append(
                {
                    "ticker": ticker,
                    "entry_date": entry_date,
                    "exit_date": exit_date,
                    "entry_price": entry_price,
                    "exit_price": exit_price,
                    "direction": "LONG",
                    "holding_period": int((exit_date - entry_date).days),
                    "gross_return": gross_return,
                    "net_return": net_return,
                    "transaction_cost": total_cost,
                    "pnl": net_return,
                }
            )

    return pd.DataFrame(trade_rows)
