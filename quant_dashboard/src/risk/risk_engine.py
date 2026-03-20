from __future__ import annotations

from typing import Any

import pandas as pd

from src.risk.rules import apply_risk_rules


def run_risk_checks(targets: pd.DataFrame, feature_frame: pd.DataFrame, risk_config: dict[str, Any]) -> pd.DataFrame:
    """Run pre-trade risk checks and return approved target weights."""
    return apply_risk_rules(targets, feature_frame, risk_config)
