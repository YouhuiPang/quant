from __future__ import annotations

import pandas as pd


def build_benchmark_returns(feature_frame: pd.DataFrame) -> pd.DataFrame:
    """Create an equal-weight buy-and-hold benchmark across the loaded universe."""
    benchmark = (
        feature_frame.groupby("date", as_index=False)
        .agg(benchmark_return=("return_1d", "mean"))
        .sort_values("date")
    )
    benchmark["cumulative_benchmark"] = (1.0 + benchmark["benchmark_return"].fillna(0.0)).cumprod()
    return benchmark
