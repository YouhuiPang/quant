from __future__ import annotations

from src.features.feature_engineer import engineer_features
from src.signals.signal_engine import generate_signals


def test_signal_generation_logic_works(sample_multi_asset_frame, temp_config) -> None:
    features = engineer_features(sample_multi_asset_frame, temp_config["features"])
    signals = generate_signals(features, temp_config["strategy"])
    assert {"signal", "confidence", "strategy_name"}.issubset(signals.columns)


def test_confidence_field_populated(sample_multi_asset_frame, temp_config) -> None:
    features = engineer_features(sample_multi_asset_frame, temp_config["features"])
    signals = generate_signals(features, temp_config["strategy"])
    assert signals["confidence"].between(0, 1).all()


def test_multi_asset_signals_correct(sample_multi_asset_frame, temp_config) -> None:
    features = engineer_features(sample_multi_asset_frame, temp_config["features"])
    signals = generate_signals(features, temp_config["strategy"])
    assert set(signals["ticker"].unique()) == {"AAA", "BBB"}
