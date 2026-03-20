from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def sample_multi_asset_frame() -> pd.DataFrame:
    dates = pd.date_range("2024-01-01", periods=40, freq="B")
    rows: list[dict] = []
    for ticker, base in [("AAA", 100.0), ("BBB", 80.0)]:
        for idx, date in enumerate(dates):
            close = base + idx + (2 if ticker == "BBB" else 0)
            rows.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "ticker": ticker,
                    "open": close - 0.5,
                    "high": close + 1.0,
                    "low": close - 1.0,
                    "close": close,
                    "volume": 100000 + idx * 1000,
                }
            )
    return pd.DataFrame(rows)


@pytest.fixture
def temp_config(tmp_path: Path, sample_multi_asset_frame: pd.DataFrame) -> dict:
    raw_dir = tmp_path / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    sample_multi_asset_frame.to_csv(raw_dir / "prices.csv", index=False)
    return {
        "project": {"name": "Test Platform", "theme": "dark", "log_level": "INFO"},
        "runtime": {"mode": "paper", "data_provider": "csv", "broker_provider": "paper", "live_disabled": True},
        "paths": {
            "combined_prices": "data/raw/prices.csv",
            "processed_dir": "data/processed",
            "outputs_dir": "data/outputs",
            "state_dir": "data/state",
            "sqlite_path": "data/state/platform_state.db",
            "market_cache_path": "data/raw/prices.csv",
            "logs_dir": "logs",
        },
        "data": {"format": "combined_csv", "required_columns": ["date", "ticker", "open", "high", "low", "close", "volume"], "min_history_rows": 30},
        "features": {"ma_short_window": 5, "ma_long_window": 20, "momentum_window": 10, "drawdown_window": 20, "volatility_window": 20},
        "strategy": {"allow_short": False, "name": "test_strategy", "default_confidence": 0.75},
        "portfolio": {"method": "equal_weight_active", "max_gross_exposure": 1.0, "cash_when_flat": True, "lot_size": 1},
        "backtest": {"annualization_factor": 252, "transaction_cost_bps": 10, "initial_capital": 1.0, "execution_lag_days": 1, "fill_price_field": "close"},
        "benchmark": {"enabled": True, "method": "equal_weight_universe"},
        "risk": {"max_weight_per_asset": 0.35, "max_concurrent_positions": 2, "gross_exposure_limit": 1.0, "min_confidence_threshold": 0.55, "volatility_cap": 0.08, "kill_switch": False},
        "paper_execution": {"initial_cash": 100000.0, "order_type": "MKT", "fill_price_field": "close", "allow_partial_fills": False, "default_fill_ratio": 1.0, "transaction_cost_bps": 10},
        "ibkr": {
            "host": "127.0.0.1",
            "port": 7497,
            "client_id": 7,
            "account_id": "",
            "readonly_mode": True,
            "enable_live_orders": False,
            "confirm_live_orders": False,
            "use_ib_gateway": True,
            "market_data_type": 1,
        },
        "data_sync": {
            "symbols": [
                {"symbol": "AAA", "sec_type": "STK", "exchange": "SMART", "currency": "USD"},
                {"symbol": "BBB", "sec_type": "STK", "exchange": "SMART", "currency": "USD"},
            ],
            "bar_size": "1 day",
            "duration": "1 Y",
            "throttle_seconds": 0.0,
            "use_cache": True,
            "latest_snapshot_enabled": True,
        },
        "dashboard": {"default_date_window_days": 180, "chart_height": 380, "default_ticker": "ALL"},
        "project_root": str(tmp_path),
    }
