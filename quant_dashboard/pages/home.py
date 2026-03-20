from __future__ import annotations

from dash import html, register_page

from src.dashboard.components import section_header


register_page(__name__, path="/", name="Home", order=0)


layout = html.Div(
    [
        section_header("Platform Overview", "Current strategy, benchmark, account, and risk snapshot."),
        html.Div(id="home-summary-cards", style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(220px, 1fr))", "gap": "18px"}),
        html.Div(id="home-latest-status", style={"marginTop": "20px", "opacity": 0.8, "fontSize": "14px"}),
    ]
)
