from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.brokers.ibkr_broker import IBKRBroker
from src.utils.config import load_config


def main() -> int:
    config = load_config()
    sqlite_path = Path(config["project_root"]) / config["paths"]["sqlite_path"]
    broker = IBKRBroker(config["ibkr"], sqlite_path)
    try:
        broker.connect()
        print("IBKR CONNECTION TEST PASSED")
        print(
            {
                "host": config["ibkr"]["host"],
                "port": config["ibkr"]["port"],
                "client_id": config["ibkr"]["client_id"],
                "readonly_mode": config["ibkr"]["readonly_mode"],
            }
        )
        return 0
    except Exception as exc:
        print("IBKR CONNECTION TEST FAILED")
        print(str(exc))
        return 1
    finally:
        try:
            broker.disconnect()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
