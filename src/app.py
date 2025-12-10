"""Dash application for the road safety dashboard."""
from __future__ import annotations

from typing import List

import dash
from dash import Dash, Input, Output, dcc, html
import plotly.express as px

from config import AGGLO_MAPPING, SURFACE_MAPPING
from src.utils.clean_data import load_clean_data
from src.utils.common_functions import dataframe_date_bounds, filter_dataframe


DATAFRAME = load_clean_data()
DATE_MIN, DATE_MAX = dataframe_date_bounds(DATAFRAME)
CARD_STYLE = {
    "backgroundColor": "white",
    "padding": "12px",
    "border": "1px solid #e0e0e0",
    "borderRadius": "8px",
    "boxShadow": "0 1px 2px rgba(0,0,0,0.05)",
}


def _blank_figure(title: str) -> px.scatter:
    fig = px.scatter()
    fig.update_layout(
        title=title,
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[
            {
                "text": "Aucune donnee pour cette selection",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 14},
            }
        ],
    )
    return fig


def _severity_histogram(df: pd.DataFrame) -> px.bar:
    if df.empty:
        return _blank_figure("Gravite par environnement")
    grouped = (
        df.groupby(["severity_label", "agg_label"])
        .size()
        .reset_index(name="accidents")
        .sort_values("accidents", ascending=False)
    )
    fig = px.bar(
        grouped,
        x="severity_label",
        y="accidents",
        color="agg_label",
        barmode="group",
        labels={"severity_label": "Gravite", "accidents": "Nombre d'accidents", "agg_label": "Zone"},
        title="Gravite des accidents par environnement",
        color_discrete_sequence=px.colors.sequential.Viridis,
    )
    fig.update_layout(legend_title_text="Zone")
    return fig


def _surface_histogram(df: pd.DataFrame) -> px.bar:
    if df.empty:
        return _blank_figure("Etat de la chaussee")
    grouped = (
        df.groupby("surface_label")
        .size()
        .reset_index(name="accidents")
        .sort_values("accidents", ascending=False)
    )
    fig = px.bar(
        grouped,
        x="surface_label",
        y="accidents",
        labels={"surface_label": "Etat de la chaussee", "accidents": "Nombre d'accidents"},
        title="Etat de la chaussee lors des accidents",
        color="surface_label",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_layout(showlegend=False, xaxis_tickangle=-20)
    return fig


def _density_map(df: pd.DataFrame) -> px.density_mapbox:
    if df.empty:
        return _blank_figure("Carte de densite des accidents")
    fig = px.density_mapbox(
        df,
        lat="lat",
        lon="long",
        z=None,
        radius=8,
        hover_data={"agg_label": True, "severity_label": True, "surface_label": True},
        mapbox_style="open-street-map",
        zoom=4.5,
        center={"lat": 46.6, "lon": 2.5},
        title="Carte de densite des accidents corporels (2022)",
    )
    return fig


def _hourly_bar(df: pd.DataFrame) -> px.bar:
    working = df.dropna(subset=["hour"])
    if working.empty:
        return _blank_figure("Accidents par heure")
    grouped = (
        working.groupby("hour")
        .size()
        .reset_index(name="accidents")
        .sort_values("hour")
    )
    fig = px.bar(
        grouped,
        x="hour",
        y="accidents",
        labels={"hour": "Heure de l'accident", "accidents": "Nombre d'accidents"},
        title="Distribution horaire des accidents",
    )
    fig.update_xaxes(dtick=1)
    return fig


def _lighting_pie(df: pd.DataFrame) -> px.pie:
    if df.empty:
        return _blank_figure("Accidents par eclairage")
    grouped = (
        df.groupby("lighting_group")
        .size()
        .reset_index(name="accidents")
        .sort_values("accidents", ascending=False)
    )
    fig = px.pie(
        grouped,
        values="accidents",
        names="lighting_group",
        title="Eclairage lors des accidents",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    return fig


def _layout_controls() -> html.Div:
    return html.Div(
        children=[
            html.Div(
                [
                    html.Label("Plage de dates"),
                    dcc.DatePickerRange(
                        id="date-range",
                        min_date_allowed=DATE_MIN,
                        max_date_allowed=DATE_MAX,
                        start_date=DATE_MIN,
                        end_date=DATE_MAX,
                        display_format="DD/MM/YYYY",
                    ),
                ],
                className="control-item",
            ),
            html.Div(
                [
                    html.Label("Gravite"),
                    dcc.Dropdown(
                        id="severity-filter",
                        options=[{"label": label, "value": label} for label in sorted(DATAFRAME["severity_label"].dropna().unique())],
                        value=["Tue", "Blesse hospitalise", "Blesse leger"],
                        multi=True,
                        placeholder="Choisir la gravite",
                    ),
                ],
                className="control-item",
            ),
            html.Div(
                [
                    html.Label("Zone (agglo / hors agglo)"),
                    dcc.Checklist(
                        id="agglo-filter",
                        options=[{"label": label, "value": label} for label in AGGLO_MAPPING.values()],
                        value=["En agglomeration", "Hors agglomeration"],
                        inline=True,
                    ),
                ],
                className="control-item",
            ),
            html.Div(
                [
                    html.Label("Etat de la chaussee"),
                    dcc.Dropdown(
                        id="surface-filter",
                        options=[{"label": label, "value": label} for label in SURFACE_MAPPING.values()],
                        multi=True,
                        placeholder="Etat de la route",
                    ),
                ],
                className="control-item",
            ),
            html.Div(
                [
                    html.Label("Eclairage"),
                    dcc.Checklist(
                        id="lighting-filter",
                        options=[
                            {"label": "Eclairage public", "value": "Eclairage public"},
                            {"label": "Sans eclairage public", "value": "Sans eclairage public"},
                            {"label": "Lumiere naturelle", "value": "Lumiere naturelle"},
                            {"label": "Non renseigne", "value": "Non renseigne"},
                        ],
                        value=["Eclairage public", "Sans eclairage public", "Lumiere naturelle", "Non renseigne"],
                        inline=True,
                    ),
                ],
                className="control-item",
            ),
        ],
        style={
            "display": "grid",
            "gridTemplateColumns": "repeat(auto-fit, minmax(240px, 1fr))",
            "gap": "12px",
            "margin": "16px 0",
            "padding": "12px",
            "border": "1px solid #e0e0e0",
            "borderRadius": "8px",
            "backgroundColor": "#f9f9f9",
        },
    )


def _layout_graphs() -> html.Div:
    return html.Div(
        children=[
            html.Div(dcc.Graph(id="severity-env-graph"), style=CARD_STYLE),
            html.Div(dcc.Graph(id="surface-graph"), style=CARD_STYLE),
            html.Div(
                dcc.Graph(id="density-map"),
                style={**CARD_STYLE, "gridColumn": "span 2"},
            ),
            html.Div(dcc.Graph(id="hourly-graph"), style=CARD_STYLE),
            html.Div(dcc.Graph(id="lighting-pie"), style=CARD_STYLE),
        ],
        style={
            "display": "grid",
            "gridTemplateColumns": "repeat(auto-fit, minmax(360px, 1fr))",
            "gap": "16px",
        },
    )


def _register_callbacks(app: Dash) -> None:
    @app.callback(
        Output("severity-env-graph", "figure"),
        Output("surface-graph", "figure"),
        Output("density-map", "figure"),
        Output("hourly-graph", "figure"),
        Output("lighting-pie", "figure"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input("severity-filter", "value"),
        Input("agglo-filter", "value"),
        Input("surface-filter", "value"),
        Input("lighting-filter", "value"),
    )
    def update_figures(
        start_date: str,
        end_date: str,
        severity_values: List[str],
        agglo_values: List[str],
        surface_values: List[str],
        lighting_values: List[str],
    ):
        filtered = filter_dataframe(
            DATAFRAME,
            date_range=(start_date, end_date),
            severities=severity_values,
            agglo=agglo_values,
            surfaces=surface_values,
            lighting_groups=lighting_values,
        )
        return (
            _severity_histogram(filtered),
            _surface_histogram(filtered),
            _density_map(filtered),
            _hourly_bar(filtered),
            _lighting_pie(filtered),
        )


def create_app() -> Dash:
    app = Dash(__name__, suppress_callback_exceptions=True)
    app.title = "Accidents corporels 2022"
    app.layout = html.Div(
        id="page-container",
        children=[
            html.Header(
                [
                    html.H1("Accidents corporels de la route - France 2022"),
                    html.P(
                        "Visualisation basee sur les donnees ouvertes du Ministere de l'Interieur "
                        "disponibles sur data.gouv.fr."
                    ),
                ]
            ),
            _layout_controls(),
            _layout_graphs(),
            html.Footer(
                "Sources : data.gouv.fr - Bases annuelles des accidents corporels de la circulation."
            ),
        ],
        style={
            "maxWidth": "1200px",
            "margin": "0 auto",
            "fontFamily": "Arial, sans-serif",
            "padding": "16px",
        },
    )
    _register_callbacks(app)
    return app
