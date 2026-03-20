from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.data.adapters.csv_adapter import CSVMarketDataAdapter
from src.data.preprocess import preprocess_price_data
from src.data.validator import validate_price_frame


def load_price_data(config: dict[str, Any]) -> pd.DataFrame:
    """Load normalized market data from the configured provider/cache."""
    project_root = Path(config["project_root"])
    runtime = config.get("runtime", {})
    provider = runtime.get("data_provider", "csv")
    if provider == "ibkr":
        csv_path = project_root / config["paths"]["market_cache_path"]
    else:
        csv_path = project_root / config["paths"]["combined_prices"]

    adapter = CSVMarketDataAdapter(csv_path)
    raw = adapter.fetch_historical_data(config["data_sync"]["symbols"], config["data_sync"])
    processed = preprocess_price_data(raw)
    validate_price_frame(processed, config["data"])
    return processed
