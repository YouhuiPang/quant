from __future__ import annotations

import pandas as pd
import pytest

from src.data.loader import load_price_data


def test_valid_multi_asset_data_loading(temp_config: dict) -> None:
    frame = load_price_data(temp_config)
    assert set(frame["ticker"].unique()) == {"AAA", "BBB"}


def test_missing_columns_errors(temp_config: dict, tmp_path) -> None:
    bad = pd.DataFrame({"date": ["2024-01-01"], "ticker": ["AAA"], "close": [100.0]})
    path = tmp_path / "data" / "raw"
    path.mkdir(parents=True, exist_ok=True)
    bad.to_csv(path / "prices.csv", index=False)
    temp_config["project_root"] = str(tmp_path)
    with pytest.raises(ValueError, match="Missing required columns"):
        load_price_data(temp_config)


def test_duplicate_date_handling(temp_config: dict, sample_multi_asset_frame: pd.DataFrame, tmp_path) -> None:
    duplicated = pd.concat([sample_multi_asset_frame, sample_multi_asset_frame.iloc[[0]]], ignore_index=True)
    path = tmp_path / "data" / "raw"
    path.mkdir(parents=True, exist_ok=True)
    duplicated.to_csv(path / "prices.csv", index=False)
    temp_config["project_root"] = str(tmp_path)
    with pytest.raises(ValueError, match="Duplicate ticker/date rows detected"):
        load_price_data(temp_config)
