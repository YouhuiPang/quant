from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.brokers.ibkr_broker import IBKRBroker
from src.data.adapters.ibkr_historical_adapter import IBKRHistoricalDataAdapter
from src.data.adapters.ibkr_market_data_adapter import IBKRMarketDataAdapter
from src.data.preprocess import preprocess_price_data
from src.data.validator import validate_price_frame
from src.persistence.sqlite_store import SQLiteStateStore
from src.utils.config import load_config
from src.utils.helpers import ensure_directories
from src.utils.io import save_dataframe
from src.utils.logger import get_logger


def main() -> int:
    config = load_config()
    project_root = Path(config["project_root"])
    logs_dir = project_root / config["paths"]["logs_dir"]
    logger = get_logger("quant.ibkr.sync", logs_dir, config["project"]["log_level"])
    sqlite_path = project_root / config["paths"]["sqlite_path"]
    cache_path = project_root / config["paths"]["market_cache_path"]
    ensure_directories([cache_path.parent, sqlite_path.parent])

    broker = IBKRBroker(config["ibkr"], sqlite_path)
    store = SQLiteStateStore(sqlite_path)
    store.initialize()
    try:
        broker.connect()
        logger.info("Connected to IBKR endpoint for historical sync.")
        historical_adapter = IBKRHistoricalDataAdapter(broker.client)
        snapshot_adapter = IBKRMarketDataAdapter(broker.client)

        historical = historical_adapter.fetch_historical_data(config["data_sync"]["symbols"], config["data_sync"])
        if historical.empty:
            raise RuntimeError("IBKR historical sync returned no data.")
        historical = preprocess_price_data(historical)
        validate_price_frame(historical, config["data"])
        save_dataframe(historical, cache_path)

        if config["data_sync"].get("latest_snapshot_enabled", True):
            snapshots = snapshot_adapter.fetch_latest_snapshot(config["data_sync"]["symbols"])
            store.replace_table("market_snapshots", snapshots)
            save_dataframe(snapshots, project_root / config["paths"]["outputs_dir"] / "market_snapshots.csv")

        store.append_table(
            "broker_status",
            pd.DataFrame(
                [
                    {
                        "timestamp": pd.Timestamp.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                        "data_provider": "ibkr",
                        "broker_provider": config["runtime"]["broker_provider"],
                        "connection_status": "CONNECTED",
                        "runtime_mode": config["runtime"]["mode"],
                        "live_enabled": int(bool(config["ibkr"]["enable_live_orders"] and config["ibkr"]["confirm_live_orders"])),
                    }
                ]
            ),
        )
        logger.info("IBKR historical sync completed for %s rows.", len(historical))
        print("IBKR DATA SYNC COMPLETED")
        print({"rows": len(historical), "cache_path": str(cache_path)})
        return 0
    except Exception as exc:
        logger.exception("IBKR sync failed: %s", exc)
        print("IBKR DATA SYNC FAILED")
        print(str(exc))
        return 1
    finally:
        try:
            broker.disconnect()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
