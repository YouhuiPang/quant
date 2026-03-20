from __future__ import annotations

from src.data.loader import load_price_data


def test_switching_from_csv_to_ibkr_provider_works_via_config(temp_config) -> None:
    csv_frame = load_price_data(temp_config)
    temp_config["runtime"]["data_provider"] = "ibkr"
    ibkr_cache_frame = load_price_data(temp_config)
    assert len(csv_frame) == len(ibkr_cache_frame)
