from __future__ import annotations


EXECUTION_ASSUMPTIONS = {
    "signal_timing": "Signals are observed on date t.",
    "position_timing": "Approved target weights are executed with a one-day lag in backtests.",
    "fill_pricing": "Paper execution fills at the configured close price in local paper mode.",
    "transaction_costs": "Transaction costs are charged when executed weights or filled quantities change.",
}
