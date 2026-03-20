from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.analytics.reporting import load_dashboard_bundle, run_pipeline
from src.brokers.paper_broker import PaperBroker
from src.execution.execution_engine import create_orders_from_targets
from src.execution.trade_ledger import build_execution_trade_ledger
from src.utils.config import load_config
from src.utils.io import save_dataframe


def main() -> int:
    config = load_config()
    bundle = run_pipeline()
    sqlite_path = Path(config["project_root"]) / config["paths"]["sqlite_path"]
    outputs_dir = Path(config["project_root"]) / config["paths"]["outputs_dir"]
    broker = PaperBroker(
        sqlite_path=sqlite_path,
        initial_cash=float(config["paper_execution"]["initial_cash"]),
        transaction_cost_bps=float(config["paper_execution"]["transaction_cost_bps"]),
    )

    latest_timestamp = bundle.approved_targets["timestamp"].max()
    approved_latest = bundle.approved_targets[bundle.approved_targets["timestamp"] == latest_timestamp].copy()
    market_snapshot = bundle.enriched[bundle.enriched["date"] == pd.to_datetime(latest_timestamp)].copy()
    current_positions = broker.get_positions()
    account_state = broker.get_account_state()
    execution_config = {**config["paper_execution"], **config["portfolio"]}
    orders = create_orders_from_targets(approved_latest, current_positions, account_state, market_snapshot, execution_config)
    submitted_orders, fills = broker.submit_orders(orders, market_snapshot)
    execution_trades = build_execution_trade_ledger(fills)

    save_dataframe(submitted_orders, outputs_dir / "orders.csv")
    save_dataframe(fills, outputs_dir / "fills.csv")
    save_dataframe(execution_trades, outputs_dir / "execution_trade_ledger.csv")
    save_dataframe(broker.get_positions(), outputs_dir / "live_positions.csv")
    save_dataframe(broker.get_account_state(), outputs_dir / "account_snapshot.csv")

    print(f"PAPER SESSION COMPLETED | orders={len(submitted_orders)} | fills={len(fills)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
