from __future__ import annotations

from dash import dcc, html, page_container, page_registry

from src.dashboard.styles import APP_STYLE, COLORS, CONTENT_STYLE, LINK_STYLE, NAV_STYLE


def build_layout() -> html.Div:
    """Create the shared multipage application shell."""
    ordered_pages = sorted(page_registry.values(), key=lambda page: page["order"])
    nav_links = [dcc.Link(page["name"], href=page["relative_path"], style=LINK_STYLE) for page in ordered_pages]

    return html.Div(
        [
            dcc.Location(id="url"),
            dcc.Download(id="download-trades"),
            dcc.Download(id="download-metrics"),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div("Quant Research Dashboard v2", style={"fontSize": "22px", "fontWeight": 700}),
                            html.Div(
                                "Multi-asset research, portfolio backtesting, benchmark analysis, and trade monitoring",
                                style={"fontSize": "13px", "color": COLORS["muted"], "marginTop": "4px"},
                            ),
                        ]
                    ),
                    html.Div(nav_links, style={"display": "flex", "gap": "10px", "flexWrap": "wrap"}),
                ],
                style={
                    **NAV_STYLE,
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "center",
                    "gap": "24px",
                },
            ),
            html.Div(page_container, style=CONTENT_STYLE),
        ],
        style=APP_STYLE,
    )
