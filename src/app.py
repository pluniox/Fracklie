"""Dash application factory (wires layout + callbacks)."""

from __future__ import annotations

from dash import Dash  # type: ignore

from src.dashboard.callbacks import register_callbacks
from src.dashboard.layout import create_layout
from src.utils.clean_data import load_clean_data


def create_app() -> Dash:
    dataframe = load_clean_data()

    app = Dash(__name__, suppress_callback_exceptions=True)
    app.title = "Fracklie - Dashboard"
    app.layout = create_layout(dataframe)
    register_callbacks(app, dataframe)
    return app
