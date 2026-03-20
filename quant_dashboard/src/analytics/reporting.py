from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from src.backtest.engine import BacktestResult, run_backtest
from src.data.loader import load_price_data
from src.features.feature_engineer import engineer_features
from src.persistence.sqlite_store import SQLiteStateStore
from src.persistence.snapshots import build_account_snapshot
from src.portfolio.position_targets import build_target_positions
from src.risk.risk_engine import run_risk_checks
from src.risk.risk_state import summarize_risk_state
from src.signals.signal_engine import generate_signals
from src.utils.helpers import ensure_directories
from src.utils.io import load_json, read_csv_if_exists, save_dataframe, save_json
from src.utils.config import load_config
from src.utils.logger import get_logger


@dataclass
class DashboardBundle:
    enriched: pd.DataFrame
    signals: pd.DataFrame
    targets: pd.DataFrame
    approved_targets: pd.DataFrame
    positions: pd.DataFrame
    asset_returns: pd.DataFrame
    portfolio_returns: pd.DataFrame
    benchmark_returns: pd.DataFrame
    trades: pd.DataFrame
    metrics: dict[str, Any]
    asset_summary: pd.DataFrame
    risk_summary: pd.DataFrame
    state: dict[str, pd.DataFrame]
    config: dict[str, Any]


def run_pipeline(config_path: str | Path | None = None) -> DashboardBundle:
    """Run the local research pipeline and persist outputs for the Dash app."""
    config = load_config(config_path)
    project_root = Path(config["project_root"])
    processed_dir = project_root / config["paths"]["processed_dir"]
    outputs_dir = project_root / config["paths"]["outputs_dir"]
    logs_dir = project_root / config["paths"]["logs_dir"]
    state_dir = project_root / config["paths"]["state_dir"]
    sqlite_path = project_root / config["paths"]["sqlite_path"]
    ensure_directories([processed_dir, outputs_dir, logs_dir, state_dir])
    logger = get_logger("quant.pipeline", logs_dir, config["project"]["log_level"])
    store = SQLiteStateStore(sqlite_path)
    store.initialize()
    _initialize_state_if_empty(store, config, prices_timestamp=None)

    logger.info("Pipeline started.")
    prices = load_price_data(config)
    _initialize_state_if_empty(store, config, prices_timestamp=pd.to_datetime(prices["date"]).max())
    logger.info("Loaded market data for %s tickers and %s rows.", prices["ticker"].nunique(), len(prices))
    feature_frame = engineer_features(prices, config["features"])
    logger.info("Feature engineering complete.")
    signal_frame = generate_signals(feature_frame, config["strategy"])
    logger.info("Signal generation complete.")
    target_frame = build_target_positions(signal_frame)
    logger.info("Portfolio target generation complete.")
    approved_targets = run_risk_checks(target_frame, feature_frame, config["risk"])
    logger.info("Risk checks complete.")
    backtest_result = run_backtest(feature_frame, approved_targets, config)
    logger.info("Backtest completed.")
    risk_summary = summarize_risk_state(approved_targets)
    _persist_outputs(backtest_result, signal_frame, target_frame, approved_targets, risk_summary, processed_dir, outputs_dir)
    _persist_state(store, signal_frame, approved_targets, risk_summary, config)
    logger.info("Output persistence completed.")

    return DashboardBundle(
        enriched=backtest_result.enriched_frame,
        signals=backtest_result.signals,
        targets=target_frame,
        approved_targets=approved_targets,
        positions=backtest_result.positions,
        asset_returns=backtest_result.asset_returns,
        portfolio_returns=backtest_result.portfolio_returns,
        benchmark_returns=backtest_result.benchmark_returns,
        trades=backtest_result.trades,
        metrics=backtest_result.metrics,
        asset_summary=backtest_result.asset_summary,
        risk_summary=risk_summary,
        state=_load_state_frames(store),
        config=config,
    )


def load_dashboard_bundle(config_path: str | Path | None = None) -> DashboardBundle:
    """Load the latest persisted pipeline outputs for dashboard rendering."""
    config = load_config(config_path)
    project_root = Path(config["project_root"])
    processed_dir = project_root / config["paths"]["processed_dir"]
    outputs_dir = project_root / config["paths"]["outputs_dir"]

    enriched = read_csv_if_exists(processed_dir / "feature_frame.csv", parse_dates=["date"])
    signals = read_csv_if_exists(outputs_dir / "signals.csv", parse_dates=["date"])
    targets = read_csv_if_exists(outputs_dir / "target_positions.csv", parse_dates=["timestamp"])
    approved_targets = read_csv_if_exists(outputs_dir / "approved_positions.csv", parse_dates=["timestamp"])
    positions = read_csv_if_exists(outputs_dir / "positions.csv", parse_dates=["date"])
    asset_returns = read_csv_if_exists(outputs_dir / "returns.csv", parse_dates=["date"])
    portfolio_returns = read_csv_if_exists(outputs_dir / "portfolio_returns.csv", parse_dates=["date"])
    benchmark_returns = read_csv_if_exists(outputs_dir / "benchmark_returns.csv", parse_dates=["date"])
    trades = read_csv_if_exists(outputs_dir / "trades.csv", parse_dates=["entry_date", "exit_date"])
    metrics = load_json(outputs_dir / "metrics.json")
    asset_summary = read_csv_if_exists(outputs_dir / "asset_summary.csv")
    risk_summary = read_csv_if_exists(outputs_dir / "risk_status.csv", parse_dates=["timestamp"])
    store = SQLiteStateStore(project_root / config["paths"]["sqlite_path"])
    store.initialize()

    if enriched.empty or portfolio_returns.empty:
        return run_pipeline(config_path)

    return DashboardBundle(
        enriched=enriched,
        signals=signals,
        targets=targets,
        approved_targets=approved_targets,
        positions=positions,
        asset_returns=asset_returns,
        portfolio_returns=portfolio_returns,
        benchmark_returns=benchmark_returns,
        trades=trades,
        metrics=metrics,
        asset_summary=asset_summary,
        risk_summary=risk_summary,
        state=_load_state_frames(store),
        config=config,
    )


def latest_snapshot(bundle: DashboardBundle) -> dict[str, Any]:
    """Create a concise latest snapshot for dashboard summary cards."""
    latest_portfolio = bundle.portfolio_returns.sort_values("date").iloc[-1]
    latest_signals = bundle.positions[bundle.positions["date"] == bundle.positions["date"].max()]
    latest_account = bundle.state["account"]
    latest_account_row = latest_account.iloc[-1] if not latest_account.empty else None
    latest_risk = bundle.risk_summary
    latest_risk_text = "OK"
    if not latest_risk.empty and (latest_risk["risk_flag"] != "APPROVED").any():
        latest_risk_text = "Flags Present"
    broker_status = bundle.state["broker_status"]
    latest_status = broker_status.iloc[-1] if not broker_status.empty else None
    market_snapshots = bundle.state["market_snapshots"]
    latest_market_snapshot = market_snapshots.iloc[-1] if not market_snapshots.empty else None

    return {
        "latest_date": pd.Timestamp(latest_portfolio["date"]).strftime("%Y-%m-%d"),
        "active_positions": int((latest_signals["executed_weight"] > 0).sum()),
        "latest_portfolio_return": float(latest_portfolio["portfolio_net_return"]),
        "latest_benchmark_return": float(latest_portfolio["benchmark_return"]),
        "strategy_total_return": float(bundle.metrics["total_return"]),
        "benchmark_total_return": float(bundle.metrics["benchmark_total_return"]),
        "cash": float(latest_account_row["cash"]) if latest_account_row is not None else 0.0,
        "equity": float(latest_account_row["equity"]) if latest_account_row is not None else 0.0,
        "risk_status": latest_risk_text,
        "data_provider": latest_status["data_provider"] if latest_status is not None else bundle.config["runtime"]["data_provider"],
        "broker_provider": latest_status["broker_provider"] if latest_status is not None else bundle.config["runtime"]["broker_provider"],
        "connection_status": latest_status["connection_status"] if latest_status is not None else "LOCAL_CACHE",
        "latest_market_snapshot": latest_market_snapshot["timestamp"] if latest_market_snapshot is not None else "N/A",
    }


def _persist_outputs(
    result: BacktestResult,
    signals: pd.DataFrame,
    targets: pd.DataFrame,
    approved_targets: pd.DataFrame,
    risk_summary: pd.DataFrame,
    processed_dir: Path,
    outputs_dir: Path,
) -> None:
    save_dataframe(result.enriched_frame, processed_dir / "feature_frame.csv")
    save_dataframe(signals.rename(columns={"timestamp": "date"}), outputs_dir / "signals.csv")
    save_dataframe(targets, outputs_dir / "target_positions.csv")
    save_dataframe(approved_targets, outputs_dir / "approved_positions.csv")
    save_dataframe(result.positions, outputs_dir / "positions.csv")
    save_dataframe(result.asset_returns, outputs_dir / "returns.csv")
    save_dataframe(result.portfolio_returns, outputs_dir / "portfolio_returns.csv")
    save_dataframe(result.benchmark_returns, outputs_dir / "benchmark_returns.csv")
    save_dataframe(result.trades, outputs_dir / "trades.csv")
    save_dataframe(result.asset_summary, outputs_dir / "asset_summary.csv")
    save_dataframe(risk_summary, outputs_dir / "risk_status.csv")
    save_json(result.metrics, outputs_dir / "metrics.json")


def _persist_state(store: SQLiteStateStore, signals: pd.DataFrame, approved_targets: pd.DataFrame, risk_summary: pd.DataFrame, config: dict[str, Any]) -> None:
    store.append_table("signals_state", signals.assign(timestamp=lambda frame: pd.to_datetime(frame["timestamp"]).dt.strftime("%Y-%m-%d")))
    store.append_table(
        "targets_state",
        approved_targets.assign(timestamp=lambda frame: pd.to_datetime(frame["timestamp"]).dt.strftime("%Y-%m-%d"))[
            ["timestamp", "ticker", "target_weight", "approved_weight", "risk_flag", "risk_notes"]
        ],
    )
    store.append_table(
        "risk_events",
        risk_summary.assign(timestamp=lambda frame: pd.to_datetime(frame["timestamp"]).dt.strftime("%Y-%m-%d"))[
            ["timestamp", "ticker", "target_weight", "approved_weight", "risk_flag", "risk_notes"]
        ],
    )
    store.append_table(
        "broker_status",
        pd.DataFrame(
            [
                {
                    "timestamp": pd.Timestamp.now("UTC").strftime("%Y-%m-%d %H:%M:%S"),
                    "data_provider": config["runtime"]["data_provider"],
                    "broker_provider": config["runtime"]["broker_provider"],
                    "connection_status": "LOCAL_CACHE" if config["runtime"]["data_provider"] == "csv" else "CACHE_READY",
                    "runtime_mode": config["runtime"]["mode"],
                    "live_enabled": int(bool(config["ibkr"]["enable_live_orders"] and config["ibkr"]["confirm_live_orders"])),
                }
            ]
        ),
    )


def _load_state_frames(store: SQLiteStateStore) -> dict[str, pd.DataFrame]:
    return {
        "orders": store.load_table("orders"),
        "fills": store.load_table("fills"),
        "positions": store.load_table("positions"),
        "account": store.load_table("account_snapshots"),
        "risk_events": store.load_table("risk_events"),
        "signals": store.load_table("signals_state"),
        "targets": store.load_table("targets_state"),
        "market_snapshots": store.load_table("market_snapshots"),
        "broker_status": store.load_table("broker_status"),
    }


def _initialize_state_if_empty(store: SQLiteStateStore, config: dict[str, Any], prices_timestamp: pd.Timestamp | None) -> None:
    account = store.load_table("account_snapshots")
    if not account.empty:
        return
    timestamp = prices_timestamp if prices_timestamp is not None else pd.Timestamp.today().normalize()
    initial_cash = float(config["paper_execution"]["initial_cash"])
    empty_positions = pd.DataFrame(columns=["timestamp", "ticker", "quantity", "market_price", "market_value", "weight", "unrealized_pnl"])
    account_snapshot = build_account_snapshot(timestamp, initial_cash, empty_positions, 0.0)
    store.append_table("account_snapshots", account_snapshot)
