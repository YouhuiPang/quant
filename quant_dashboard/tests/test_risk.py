from __future__ import annotations

import pandas as pd

from src.risk.risk_engine import run_risk_checks


def _targets() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "timestamp": pd.to_datetime(["2024-01-01"] * 3),
            "ticker": ["AAA", "BBB", "CCC"],
            "signal": [1.0, 1.0, 1.0],
            "confidence": [0.9, 0.8, 0.5],
            "strategy_name": ["x"] * 3,
            "target_weight": [0.4, 0.4, 0.2],
        }
    )


def _features() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01"] * 3),
            "ticker": ["AAA", "BBB", "CCC"],
            "rolling_std_20": [0.02, 0.02, 0.09],
        }
    )


def test_max_asset_weight_rule_works(temp_config) -> None:
    approved = run_risk_checks(_targets(), _features(), temp_config["risk"])
    assert approved["approved_weight"].max() <= temp_config["risk"]["max_weight_per_asset"]


def test_blocked_allocations_carry_notes(temp_config) -> None:
    approved = run_risk_checks(_targets(), _features(), temp_config["risk"])
    blocked = approved[approved["ticker"] == "CCC"].iloc[0]
    assert blocked["risk_flag"] == "BLOCKED"
    assert blocked["risk_notes"]


def test_kill_switch_disables_allocations(temp_config) -> None:
    risk_config = {**temp_config["risk"], "kill_switch": True}
    approved = run_risk_checks(_targets(), _features(), risk_config)
    assert approved["approved_weight"].sum() == 0.0
