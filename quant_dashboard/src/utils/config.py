from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from src.utils.validation import validate_config


def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).resolve().parents[2]


def load_config(config_path: str | Path | None = None) -> dict[str, Any]:
    """Load and validate configuration."""
    resolved_path = Path(config_path) if config_path else project_root() / "config" / "config.yaml"
    with resolved_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    validate_config(config)
    config["project_root"] = str(project_root())
    return config
