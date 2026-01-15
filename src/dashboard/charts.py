from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.dashboard.theme import THEME, apply_polish


def blank_figure(title: str) -> go.Figure:
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
    return apply_polish(fig)


def severity_histogram(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return blank_figure("Gravité par environnement")
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
        labels={"severity_label": "Gravité", "accidents": "", "agg_label": "Zone"},
        title="GRAVITÉ PAR ZONE",
        color_discrete_sequence=[THEME["neon_colors"][0], THEME["neon_colors"][3]],
    )
    fig.update_layout(
        legend_title_text="",
        legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1),
    )
    return apply_polish(fig)


def surface_histogram(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return blank_figure("État de la chaussée")
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
        color_discrete_sequence=THEME["neon_colors"],
    )
    fig.update_layout(showlegend=False, xaxis_tickangle=-20)
    return apply_polish(fig)


def density_map(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return blank_figure("Carte de densité")
    fig = px.density_mapbox(
        df,
        lat="lat",
        lon="long",
        z=None,
        radius=10,
        hover_data={"agg_label": True, "severity_label": True},
        mapbox_style="carto-darkmatter",
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


def hourly_bar(df: pd.DataFrame) -> go.Figure:
    working = df.dropna(subset=["hour"])
    if working.empty:
        return blank_figure("Distribution Horaire")
    grouped = working.groupby("hour").size().reset_index(name="accidents").sort_values("hour")
    fig = px.bar(
        grouped,
        x="hour",
        y="accidents",
        labels={"hour": "Heure", "accidents": ""},
        title="DISTRIBUTION HORAIRE",
    )
    fig.update_traces(marker_color=THEME["neon_colors"][2])
    fig.update_xaxes(dtick=2)
    return apply_polish(fig)


def lighting_pie(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return blank_figure("Conditions d'éclairage")
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
        hole=0.6,
    )
    fig.update_traces(textposition="inside", textinfo="percent")
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="v", yanchor="top", y=0.5, xanchor="left", x=1.1),
    )
    return apply_polish(fig)

