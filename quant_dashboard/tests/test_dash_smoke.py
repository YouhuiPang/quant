from __future__ import annotations

from dash import page_registry

from app import create_app


def test_dash_app_can_instantiate() -> None:
    app = create_app()
    assert app.title


def test_key_pages_load_without_import_failure() -> None:
    app = create_app()
    assert app.layout is not None
    assert len(page_registry) >= 8
