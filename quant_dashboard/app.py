from __future__ import annotations

from pathlib import Path

from dash import Dash

from src.analytics.reporting import run_pipeline
from src.dashboard.callbacks import register_callbacks
from src.dashboard.layout import build_layout
from src.utils.io import load_config
from src.utils.logger import get_logger


def create_app() -> Dash:
    """Create and configure the Dash application."""
    config = load_config()
    logs_dir = Path(config["project_root"]) / config["paths"]["logs_dir"]
    logger = get_logger("quant.dashboard", logs_dir, config["project"]["log_level"])
    logger.info("Starting dashboard bootstrap.")
    run_pipeline()
    app = Dash(
        __name__,
        use_pages=True,
        suppress_callback_exceptions=True,
        title=config["project"]["name"],
    )
    app.layout = build_layout()
    register_callbacks(app)
    logger.info("Dash app created successfully.")
    return app


app = create_app()
server = app.server


if __name__ == "__main__":
    app.run(debug=True)
