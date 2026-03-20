from __future__ import annotations

import pytest

from src.utils.io import load_config
from src.utils.validation import validate_config


def test_config_loads() -> None:
    config = load_config()
    assert "paths" in config
    assert "paper_execution" in config


def test_missing_critical_config_keys_raise_useful_errors() -> None:
    with pytest.raises(ValueError, match="Config missing required top-level keys"):
        validate_config({"project": {}})
