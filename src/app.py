from __future__ import annotations

from typing import List, Tuple

import dash
from dash import Dash, Input, Output, dcc, html # type: ignore
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from config import AGGLO_MAPPING, SURFACE_MAPPING
from src.utils.clean_data import load_clean_data
from src.utils.common_functions import dataframe_date_bounds, filter_dataframe

DATAFRAME = load_clean_data()
DATE_MIN, DATE_MAX = dataframe_date_bounds(DATAFRAME)

# --- POLISHED THEME CONFIGURATION ---
THEME = {
    "template": "plotly_dark",
    "bg_color": "rgba(0,0,0,0)",
    "text_color": "#ffffff",
    # NEON PALETTE: Blue, Green, Cyan, Pink, Orange
    "neon_colors": ["#2E93fA", "#66DA26", "#00E396", "#E91E63", "#FF9800", "#FEB019"],
    "font_family": "Inter, sans-serif"
}

def _apply_polish(fig):
    """Applies the final Polish: No grids, dark template, Inter font, transparent bg."""
    fig.update_layout(
        template=THEME["template"],
        paper_bgcolor=THEME["bg_color"],
        plot_bgcolor=THEME["bg_color"],
        font={"color": THEME["text_color"], "family": THEME["font_family"], "size": 12},
        margin={"t": 50, "l": 10, "r": 10, "b": 10}, # Tight margins
        title_font={"size": 16, "family": THEME["font_family"]},
        xaxis={"showgrid": False, "zeroline": False, "showticklabels": True},
        yaxis={"showgrid": False, "zeroline": False, "showticklabels": True},
        hoverlabel={
            "bgcolor": "#05050f",
            "bordercolor": "#2E93fA",
            "font_family": THEME["font_family"]
        }
    )
    return fig

def _blank_figure(title: str):
    fig = px.scatter()
    fig.update_layout(
        title=title,
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[
            {
                "text": "Pas de données",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 14, "color": "#a0a0b0"},
            }
        ],
    )
    return _apply_polish(fig)


def _severity_histogram(df: pd.DataFrame):
    if df.empty:
        return _blank_figure("Gravité par environnement")
    grouped = (
        df.groupby(["severity_label", "agg_label"])
        .size()
        .reset_index(name="accidents")
        .sort_values("accidents", ascending=False)
    )
    # Using a gradient palette for severity if possible, or just neon
    fig = px.bar(
        grouped,
        x="severity_label",
        y="accidents",
        color="agg_label",
        barmode="group",
        labels={"severity_label": "Gravité", "accidents": "", "agg_label": "Zone"},
        title="GRAVITÉ PAR ZONE",
        color_discrete_sequence=[THEME["neon_colors"][0], THEME["neon_colors"][3]] # Blue vs Pink
    )
    fig.update_layout(legend_title_text="", legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1))
    return _apply_polish(fig)


def _surface_histogram(df: pd.DataFrame):
    if df.empty:
        return _blank_figure("État de la chaussée")
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
        labels={"surface_label": "Chaussée", "accidents": ""},
        title="IMPACT MÉTÉO (CHAUSSÉE)",
        color="surface_label",
        color_discrete_sequence=THEME["neon_colors"]
    )
    fig.update_layout(showlegend=False, xaxis_tickangle=-20)
    return _apply_polish(fig)


def _density_map(df: pd.DataFrame):
    if df.empty:
        return _blank_figure("Carte de densité")
    fig = px.density_mapbox(
        df,
        lat="lat",
        lon="long",
        z=None,
        radius=10,
        hover_data={"agg_label": True, "severity_label": True},
        mapbox_style="carto-darkmatter", # Matches Pure Dark perfectly
        zoom=5,
        center={"lat": 46.6, "lon": 2.5},
        title="CARTE DE CHALEUR",
    )
    fig.update_layout(
        template=THEME["template"],
        paper_bgcolor=THEME["bg_color"],
        mapbox_zoom=4.8,
        margin={"t": 40, "l": 0, "r": 0, "b": 0},
        font={"color": THEME["text_color"], "family": THEME["font_family"]},
        title_font={"size": 16},
    )
    return fig


def _hourly_bar(df: pd.DataFrame):
    working = df.dropna(subset=["hour"])
    if working.empty:
        return _blank_figure("Distribution Horaire")
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
        labels={"hour": "Heure", "accidents": ""},
        title="DISTRIBUTION HORAIRE",
    )
    fig.update_traces(marker_color=THEME["neon_colors"][2]) # Neon Green/Cyan
    fig.update_xaxes(dtick=2)
    return _apply_polish(fig)


def _lighting_pie(df: pd.DataFrame):
    if df.empty:
        return _blank_figure("Conditions d'éclairage")
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
        title="ÉCLAIRAGE",
        color_discrete_sequence=THEME["neon_colors"],
        hole=0.6
    )
    fig.update_traces(textposition='inside', textinfo='percent')
    fig.update_layout(showlegend=True, legend=dict(orientation="v", yanchor="top", y=0.5, xanchor="left", x=1.1))
    return _apply_polish(fig)


def _kpi_card(id_value: str, id_label: str, label_text: str):
    return html.Div(
        className="kpi-card",
        children=[
            html.Div(label_text, className="kpi-label"),
            html.Div("0", id=id_value, className="kpi-value"),
            html.Div(id=id_label, style={"fontSize": "0.75rem", "color": "#a0a0b0", "marginTop": "4px"})
        ]
    )

def create_layout() -> html.Div:
    return html.Div(
        className="container",
        children=[
            # Header
            html.Div(
                className="header-container",
                children=[
                    html.Div(
                        className="app-title",
                        children=[
                            html.H1("ACCIDENTS ROUTIERS"),
                            html.P("Dashboard Analytique France 2022", className="app-subtitle")
                        ]
                    ),
                ]
            ),

            # KPI Grid
            html.Div(
                className="kpi-grid",
                children=[
                    _kpi_card("kpi-total-val", "kpi-total-sub", "TOTAL ACCIDENTS"),
                    _kpi_card("kpi-killed-val", "kpi-killed-sub", "DÉCÈS CRITIQUES"),
                    _kpi_card("kpi-injured-val", "kpi-injured-sub", "BLESSÉS"),
                    _kpi_card("kpi-urban-val", "kpi-urban-sub", "ZONE URBAINE"),
                ]
            ),

            # Controls
            html.Div(
                className="controls-panel",
                children=[
                    html.Div(
                        className="controls-grid",
                        children=[
                            html.Div([
                                html.Label("📅 PÉRIODE"),
                                dcc.DatePickerRange(
                                    id="date-range",
                                    min_date_allowed="2022-01-01",
                                    max_date_allowed="2022-12-31",
                                    initial_visible_month="2022-01-01",
                                    start_date="2022-01-01",
                                    end_date="2022-12-31",
                                    display_format="DD/MM/YYYY",
                                    className="dark-date-picker"
                                )
                            ], className="control-item"),
                            
                            html.Div([
                                html.Label("⚠️ GRAVITÉ"),
                                dcc.Dropdown(
                                    id="severity-filter",
                                    options=[{"label": l, "value": l} for l in sorted(DATAFRAME["severity_label"].dropna().unique())],
                                    value=["Tue", "Blesse hospitalise", "Blesse leger"],
                                    multi=True,
                                    className="dark-dropdown"
                                )
                            ], className="control-item"),
                            
                            html.Div([
                                html.Label("📍 ZONE"),
                                dcc.Dropdown(
                                    id="agglo-filter",
                                    options=[{"label": l, "value": l} for l in AGGLO_MAPPING.values()],
                                    value=["En agglomeration", "Hors agglomeration"],
                                    multi=True,
                                    placeholder="Sélectionner zone"
                                )
                            ], className="control-item"),

                            html.Div([
                                html.Label("🌧️ CHAUSSÉE"),
                                dcc.Dropdown(
                                    id="surface-filter",
                                    options=[{"label": l, "value": l} for l in SURFACE_MAPPING.values()],
                                    value=["Normale"],
                                    multi=True,
                                    placeholder="État chaussée"
                                )
                            ], className="control-item"),
                        ]
                    )
                ]
            ),

            # Charts Grid
            html.Div(
                className="charts-grid",
                children=[
                    html.Div(dcc.Graph(id="density-map", config={"displayModeBar": False}), className="chart-card span-8"),
                    html.Div(dcc.Graph(id="kpi-pie", config={"displayModeBar": False}), className="chart-card span-4"),
                    html.Div(dcc.Graph(id="severity-graph", config={"displayModeBar": False}), className="chart-card span-4"),
                    html.Div(dcc.Graph(id="hourly-graph", config={"displayModeBar": False}), className="chart-card span-4"),
                    html.Div(dcc.Graph(id="surface-graph", config={"displayModeBar": False}), className="chart-card span-4"),
                ]
            ),
        ]
    )

def _register_callbacks(app: Dash):
    @app.callback(
        # KPIs
        Output("kpi-total-val", "children"),
        Output("kpi-total-sub", "children"),
        Output("kpi-killed-val", "children"),
        Output("kpi-killed-sub", "children"),
        Output("kpi-injured-val", "children"),
        Output("kpi-injured-sub", "children"),
        Output("kpi-urban-val", "children"),
        Output("kpi-urban-sub", "children"),
        # Charts
        Output("density-map", "figure"),
        Output("kpi-pie", "figure"),
        Output("severity-graph", "figure"),
        Output("hourly-graph", "figure"),
        Output("surface-graph", "figure"),
        # Inputs
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input("severity-filter", "value"),
        Input("agglo-filter", "value"),
        Input("surface-filter", "value"),
    )
    def update_dashboard(start, end, sev, agg, surf):
        # Default empty lists if None
        sev = sev or []
        agg = agg or []
        surf = surf or []

        filtered = filter_dataframe(
            DATAFRAME,
            date_range=(start, end),
            severities=sev,
            agglo=agg,
            surfaces=surf,
            lighting_groups=None
        )
        
        # --- KPI Calculations ---
        total = len(filtered)
        
        killed_df = filtered[filtered["severity_label"] == "Tue"]
        killed = len(killed_df)
        killed_pct = (killed / total * 100) if total > 0 else 0
        
        injured_df = filtered[filtered["severity_label"].isin(["Blesse hospitalise", "Blesse leger"])]
        injured = len(injured_df)
        injured_pct = (injured / total * 100) if total > 0 else 0
        
        urban_df = filtered[filtered["agg_label"] == "En agglomeration"]
        urban = len(urban_df)
        urban_pct = (urban / total * 100) if total > 0 else 0
        
        kpi_total = f"{total:,}".replace(",", " ")
        kpi_total_sub = "Accidents"
        
        kpi_killed = f"{killed:,}".replace(",", " ")
        kpi_killed_sub = f"{killed_pct:.1f}% Total"
        
        kpi_injured = f"{injured:,}".replace(",", " ")
        kpi_injured_sub = f"{injured_pct:.1f}% Total"
        
        kpi_urban = f"{urban:,}".replace(",", " ")
        kpi_urban_sub = f"{urban_pct:.1f}% Total"

        # --- Charts ---
        map_fig = _density_map(filtered)
        pie_fig = _lighting_pie(filtered)
        sev_fig = _severity_histogram(filtered)
        hour_fig = _hourly_bar(filtered)
        surf_fig = _surface_histogram(filtered)
        
        return (
            kpi_total, kpi_total_sub,
            kpi_killed, kpi_killed_sub,
            kpi_injured, kpi_injured_sub,
            kpi_urban, kpi_urban_sub,
            map_fig, pie_fig, sev_fig, hour_fig, surf_fig
        )


def create_app() -> Dash:
    app = Dash(__name__, suppress_callback_exceptions=True)
    app.title = "Fracklie - Dashboard"
    app.layout = create_layout()
    _register_callbacks(app)
    return app
