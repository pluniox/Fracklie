from __future__ import annotations

import pandas as pd
from dash import dcc, html  # type: ignore

from config import AGGLO_MAPPING, SURFACE_MAPPING


def carte_post(id_value: str, id_label: str, label_text: str) -> html.Div:
    return html.Div(
        className="kpi-card",
        children=[
            html.Div(label_text, className="kpi-label"),
            html.Div("0", id=id_value, className="kpi-value"),
            html.Div(
                id=id_label,
                style={"fontSize": "0.75rem", "color": "#a0a0b0", "marginTop": "4px"},
            ),
        ],
    )


def create_layout(dataframe: pd.DataFrame) -> html.Div:
    severities = sorted(dataframe["severity_label"].dropna().unique())

    return html.Div(
        className="container",
        children=[
            html.Div(
                className="header-container",
                children=[
                    html.Div(
                        className="app-title",
                        children=[
                            html.H1("ACCIDENTS ROUTIERS"),
                            html.P("Dashboard Analytique France 2022", className="app-subtitle"),
                        ],
                    ),
                ],
            ),
            html.Div(
                className="kpi-grid",
                children=[
                    carte_post("kpi-total-val", "kpi-total-sub", "TOTAL ACCIDENTS"),
                    carte_post("kpi-killed-val", "kpi-killed-sub", "DÉCÈS CRITIQUES"),
                    carte_post("kpi-injured-val", "kpi-injured-sub", "BLESSÉS"),
                    carte_post("kpi-urban-val", "kpi-urban-sub", "ZONE URBAINE"),
                ],
            ),
            html.Div(
                className="controls-panel",
                children=[
                    html.Div(
                        className="controls-grid",
                        children=[
                            html.Div(
                                [
                                    html.Label("📅 PÉRIODE"),
                                    dcc.DatePickerRange(
                                        id="date-range",
                                        min_date_allowed="2022-01-01",
                                        max_date_allowed="2022-12-31",
                                        initial_visible_month="2022-01-01",
                                        start_date="2022-01-01",
                                        end_date="2022-12-31",
                                        display_format="DD/MM/YYYY",
                                        className="dark-date-picker",
                                    ),
                                ],
                                className="control-item",
                            ),
                            html.Div(
                                [
                                    html.Label("⚠️ GRAVITÉ"),
                                    dcc.Dropdown(
                                        id="severity-filter",
                                        options=[{"label": label, "value": label} for label in severities],
                                        value=["Tue", "Blesse hospitalise", "Blesse leger"],
                                        multi=True,
                                        className="dark-dropdown",
                                    ),
                                ],
                                className="control-item",
                            ),
                            html.Div(
                                [
                                    html.Label("📍 ZONE"),
                                    dcc.Dropdown(
                                        id="agglo-filter",
                                        options=[
                                            {"label": label, "value": label}
                                            for label in AGGLO_MAPPING.values()
                                        ],
                                        value=["En agglomeration", "Hors agglomeration"],
                                        multi=True,
                                        placeholder="Sélectionner zone",
                                    ),
                                ],
                                className="control-item",
                            ),
                            html.Div(
                                [
                                    html.Label("🌧️ CHAUSSÉE"),
                                    dcc.Dropdown(
                                        id="surface-filter",
                                        options=[
                                            {"label": label, "value": label}
                                            for label in SURFACE_MAPPING.values()
                                        ],
                                        value=["Normale"],
                                        multi=True,
                                        placeholder="État chaussée",
                                    ),
                                ],
                                className="control-item",
                            ),
                        ],
                    )
                ],
            ),
            html.Div(
                className="charts-grid",
                children=[
                    html.Div(
                        dcc.Graph(id="density-map", config={"displayModeBar": False}),
                        className="chart-card span-8",
                    ),
                    html.Div(
                        dcc.Graph(id="kpi-pie", config={"displayModeBar": False}),
                        className="chart-card span-4",
                    ),
                    html.Div(
                        dcc.Graph(id="severity-graph", config={"displayModeBar": False}),
                        className="chart-card span-4",
                    ),
                    html.Div(
                        dcc.Graph(id="hourly-graph", config={"displayModeBar": False}),
                        className="chart-card span-4",
                    ),
                    html.Div(
                        dcc.Graph(id="surface-graph", config={"displayModeBar": False}),
                        className="chart-card span-4",
                    ),
                ],
            ),
        ],
    )

