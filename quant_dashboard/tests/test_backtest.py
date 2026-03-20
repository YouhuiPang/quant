from __future__ import annotations

from src.backtest.engine import run_backtest
from src.features.feature_engineer import engineer_features
from src.portfolio.position_targets import build_target_positions
from src.risk.risk_engine import run_risk_checks
from src.signals.signal_engine import generate_signals


def test_executed_weights_are_lagged_correctly(sample_multi_asset_frame, temp_config) -> None:
    features = engineer_features(sample_multi_asset_frame, temp_config["features"])
    signals = generate_signals(features, temp_config["strategy"])
    targets = build_target_positions(signals)
    approved = run_risk_checks(targets, features, temp_config["risk"])
    result = run_backtest(features, approved, temp_config)
    aaa = result.positions[result.positions["ticker"] == "AAA"].reset_index(drop=True)
    assert aaa.loc[0, "executed_weight"] == 0.0


def test_portfolio_aggregation_and_benchmark_exist(sample_multi_asset_frame, temp_config) -> None:
    features = engineer_features(sample_multi_asset_frame, temp_config["features"])
    signals = generate_signals(features, temp_config["strategy"])
    targets = build_target_positions(signals)
    approved = run_risk_checks(targets, features, temp_config["risk"])
    result = run_backtest(features, approved, temp_config)
    assert "portfolio_net_return" in result.portfolio_returns.columns
    assert "benchmark_return" in result.benchmark_returns.columns
