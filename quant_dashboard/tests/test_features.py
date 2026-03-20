from __future__ import annotations

from src.features.feature_engineer import engineer_features


def test_expected_features_exist(sample_multi_asset_frame, temp_config) -> None:
    features = engineer_features(sample_multi_asset_frame, temp_config["features"])
    assert {"return_1d", "rolling_mean_20", "momentum_10", "drawdown_20"}.issubset(features.columns)


def test_rolling_features_work_per_asset(sample_multi_asset_frame, temp_config) -> None:
    features = engineer_features(sample_multi_asset_frame, temp_config["features"])
    aaa = features[features["ticker"] == "AAA"].reset_index(drop=True)
    assert aaa.loc[4, "rolling_mean_5"] == aaa.loc[:4, "close"].mean()


def test_no_cross_asset_contamination(sample_multi_asset_frame, temp_config) -> None:
    features = engineer_features(sample_multi_asset_frame, temp_config["features"])
    aaa_first = features[features["ticker"] == "AAA"].iloc[0]["close"]
    bbb_first = features[features["ticker"] == "BBB"].iloc[0]["close"]
    assert aaa_first != bbb_first
