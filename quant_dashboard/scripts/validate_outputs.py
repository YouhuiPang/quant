from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.acceptance_checks import run_acceptance_checks


def main() -> int:
    failures = run_acceptance_checks()
    if failures:
        print("ACCEPTANCE CHECKS FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("ACCEPTANCE CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
