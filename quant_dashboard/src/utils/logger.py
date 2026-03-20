from __future__ import annotations

import logging
from pathlib import Path

from src.utils.helpers import ensure_directories


def get_logger(name: str, logs_dir: Path, level: str = "INFO") -> logging.Logger:
    """Build a file and console logger for the local platform."""
    ensure_directories([logs_dir])
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    file_handler = logging.FileHandler(logs_dir / "quant_dashboard.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logger.level)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logger.level)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False
    return logger
