from __future__ import annotations

from pathlib import Path
import sqlite3

import pandas as pd

from src.utils.io import load_config, load_json, read_csv_if_exists


REQUIRED_OUTPUTS = [
    "signals.csv",
    "target_positions.csv",
    "approved_positions.csv",
    "positions.csv",
    "returns.csv",
    "portfolio_returns.csv",
    "trades.csv",
    "metrics.json",
    "benchmark_returns.csv",
    "risk_status.csv",
    "orders.csv",
    "fills.csv",
    "live_positions.csv",
    "account_snapshot.csv",
]

REQUIRED_METRIC_KEYS = [
    "total_return",
    "benchmark_total_return",
    "excess_return",
    "annualized_return",
    "annualized_volatility",
    "sharpe_ratio",
    "max_drawdown",
    "turnover",
    "number_of_trades",
    "win_rate",
]


def run_acceptance_checks() -> list[str]:
    """Return a list of acceptance failures. Empty means pass."""
    config = load_config()
    outputs_dir = Path(config["project_root"]) / config["paths"]["outputs_dir"]
    sqlite_path = Path(config["project_root"]) / config["paths"]["sqlite_path"]
    failures: list[str] = []

    for filename in REQUIRED_OUTPUTS:
        if not (outputs_dir / filename).exists():
            failures.append(f"Missing required output file: {filename}")

    if not sqlite_path.exists():
        failures.append("SQLite state store does not exist.")
    else:
        with sqlite3.connect(sqlite_path) as connection:
            tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", connection)["name"].tolist()
        for required_table in ["orders", "fills", "positions", "account_snapshots", "risk_events", "signals_state", "targets_state", "market_snapshots", "broker_status"]:
            if required_table not in tables:
                failures.append(f"Missing required sqlite table: {required_table}")

    metrics = load_json(outputs_dir / "metrics.json")
    for key in REQUIRED_METRIC_KEYS:
        if key not in metrics:
            failures.append(f"Missing required metric key: {key}")

    returns = read_csv_if_exists(outputs_dir / "returns.csv", parse_dates=["date"])
    portfolio_returns = read_csv_if_exists(outputs_dir / "portfolio_returns.csv", parse_dates=["date"])
    benchmark_returns = read_csv_if_exists(outputs_dir / "benchmark_returns.csv", parse_dates=["date"])
    trades = read_csv_if_exists(outputs_dir / "trades.csv", parse_dates=["entry_date", "exit_date"])
    approved_positions = read_csv_if_exists(outputs_dir / "approved_positions.csv", parse_dates=["timestamp"])
    positions = read_csv_if_exists(outputs_dir / "positions.csv", parse_dates=["date"])
    account_snapshot = read_csv_if_exists(outputs_dir / "account_snapshot.csv")
    orders = read_csv_if_exists(outputs_dir / "orders.csv")
    fills = read_csv_if_exists(outputs_dir / "fills.csv")
    market_snapshots = read_csv_if_exists(outputs_dir / "market_snapshots.csv")

    if not portfolio_returns.empty and not benchmark_returns.empty and len(portfolio_returns) != len(benchmark_returns):
        failures.append("Portfolio and benchmark return series lengths are inconsistent.")

    core_frames = {
        "returns": returns,
        "portfolio_returns": portfolio_returns,
        "benchmark_returns": benchmark_returns,
        "approved_positions": approved_positions,
        "positions": positions,
    }
    for name, frame in core_frames.items():
        if not frame.empty and frame.isnull().any().any():
            failures.append(f"NaN values detected in core output: {name}")

    if metrics.get("number_of_trades", 0) > 0 and trades.empty:
        failures.append("Trades file is empty despite non-zero recorded trade count.")

    if not account_snapshot.empty and account_snapshot.isnull().any().any():
        failures.append("Account snapshot contains null values.")

    if not orders.empty and not {"order_id", "ticker", "side", "quantity", "status"}.issubset(orders.columns):
        failures.append("Orders output is missing required columns.")

    if not fills.empty and not {"fill_id", "order_id", "ticker", "fill_price", "fill_quantity"}.issubset(fills.columns):
        failures.append("Fills output is missing required columns.")

    runtime = config["runtime"]
    ibkr = config["ibkr"]
    if runtime["broker_provider"] == "ibkr" and ibkr.get("enable_live_orders", False) and not ibkr.get("confirm_live_orders", False):
        failures.append("Unsafe live order configuration: enable_live_orders is true without confirm_live_orders.")
    if runtime["data_provider"] == "ibkr" and market_snapshots.empty and config["data_sync"].get("latest_snapshot_enabled", True):
        failures.append("IBKR provider mode requires latest snapshot data to exist.")

    return failures
