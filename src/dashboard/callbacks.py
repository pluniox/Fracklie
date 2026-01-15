from __future__ import annotations

import pandas as pd
from dash import Dash, Input, Output  # type: ignore

from src.dashboard.charts import (
    density_map,
    hourly_bar,
    lighting_pie,
    severity_histogram,
    surface_histogram,
)
from src.utils.common_functions import filter_dataframe


def register_callbacks(app: Dash, dataframe: pd.DataFrame) -> None:
    @app.callback(
        Output("kpi-total-val", "children"),
        Output("kpi-total-sub", "children"),
        Output("kpi-killed-val", "children"),
        Output("kpi-killed-sub", "children"),
        Output("kpi-injured-val", "children"),
        Output("kpi-injured-sub", "children"),
        Output("kpi-urban-val", "children"),
        Output("kpi-urban-sub", "children"),
        Output("density-map", "figure"),
        Output("kpi-pie", "figure"),
        Output("severity-graph", "figure"),
        Output("hourly-graph", "figure"),
        Output("surface-graph", "figure"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input("severity-filter", "value"),
        Input("agglo-filter", "value"),
        Input("surface-filter", "value"),
    )
    def update_dashboard(start, end, sev, agg, surf):
        sev = sev or []
        agg = agg or []
        surf = surf or []

        filtered = filter_dataframe(
            dataframe,
            date_range=(start, end),
            severities=sev,
            agglo=agg,
            surfaces=surf,
            lighting_groups=None,
        )

        total = len(filtered)

        killed = int((filtered["severity_label"] == "Tue").sum())
        killed_pct = (killed / total * 100) if total > 0 else 0

        injured = int(
            filtered["severity_label"].isin(["Blesse hospitalise", "Blesse leger"]).sum()
        )
        injured_pct = (injured / total * 100) if total > 0 else 0

        urban = int((filtered["agg_label"] == "En agglomeration").sum())
        urban_pct = (urban / total * 100) if total > 0 else 0

        kpi_total = f"{total:,}".replace(",", " ")
        kpi_total_sub = "Accidents"

        kpi_killed = f"{killed:,}".replace(",", " ")
        kpi_killed_sub = f"{killed_pct:.1f}% Total"

        kpi_injured = f"{injured:,}".replace(",", " ")
        kpi_injured_sub = f"{injured_pct:.1f}% Total"

        kpi_urban = f"{urban:,}".replace(",", " ")
        kpi_urban_sub = f"{urban_pct:.1f}% Total"

        map_fig = density_map(filtered)
        pie_fig = lighting_pie(filtered)
        sev_fig = severity_histogram(filtered)
        hour_fig = hourly_bar(filtered)
        surf_fig = surface_histogram(filtered)

        return (
            kpi_total,
            kpi_total_sub,
            kpi_killed,
            kpi_killed_sub,
            kpi_injured,
            kpi_injured_sub,
            kpi_urban,
            kpi_urban_sub,
            map_fig,
            pie_fig,
            sev_fig,
            hour_fig,
            surf_fig,
        )

