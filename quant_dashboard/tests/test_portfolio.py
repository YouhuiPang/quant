from __future__ import annotations

import pandas as pd

from src.portfolio.position_targets import build_target_positions
from src.risk.risk_engine import run_risk_checks


def test_equal_weight_allocation_works() -> None:
    signals = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(["2024-01-01"] * 3),
            "ticker": ["AAA", "BBB", "CCC"],
            "signal": [1.0, 1.0, 0.0],
            "confidence": [0.8, 0.9, 0.2],
            "strategy_name": ["x"] * 3,
        }
    )
    targets = build_target_positions(signals)
    assert targets.loc[targets["ticker"] == "AAA", "target_weight"].iloc[0] == 0.5
    assert targets.loc[targets["ticker"] == "BBB", "target_weight"].iloc[0] == 0.5


def test_no_active_signal_leads_to_zero_allocation() -> None:
    signals = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(["2024-01-01"]),
            "ticker": ["AAA"],
            "signal": [0.0],
            "confidence": [0.2],
            "strategy_name": ["x"],
        }
    )
    targets = build_target_positions(signals)
    assert targets["target_weight"].iloc[0] == 0.0


def test_target_weights_sum_sensibly(sample_multi_asset_frame, temp_config) -> None:
    feature_frame = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01"] * 3),
            "ticker": ["AAA", "BBB", "CCC"],
            "rolling_std_20": [0.02, 0.02, 0.02],
        }
    )
    signals = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(["2024-01-01"] * 3),
            "ticker": ["AAA", "BBB", "CCC"],
            "signal": [1.0, 1.0, 1.0],
            "confidence": [0.8, 0.9, 0.85],
            "strategy_name": ["x"] * 3,
        }
    )
    targets = build_target_positions(signals)
    approved = run_risk_checks(targets, feature_frame, temp_config["risk"])
    assert approved["approved_weight"].sum() <= 1.0
