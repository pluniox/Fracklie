from __future__ import annotations

from typing import Any

import plotly.graph_objects as go

THEME: dict[str, Any] = {
    "template": "plotly_dark",
    "bg_color": "rgba(0,0,0,0)",
    "text_color": "#ffffff",
    "neon_colors": ["#2E93fA", "#66DA26", "#00E396", "#E91E63", "#FF9800", "#FEB019"],
    "font_family": "Inter, sans-serif",
}


def apply_polish(fig: go.Figure) -> go.Figure:
    """Applies consistent styling across all figures."""
    fig.update_layout(
        template=THEME["template"],
        paper_bgcolor=THEME["bg_color"],
        plot_bgcolor=THEME["bg_color"],
        font={"color": THEME["text_color"], "family": THEME["font_family"], "size": 12},
        margin={"t": 50, "l": 10, "r": 10, "b": 10},
        title_font={"size": 16, "family": THEME["font_family"]},
        xaxis={"showgrid": False, "zeroline": False, "showticklabels": True},
        yaxis={"showgrid": False, "zeroline": False, "showticklabels": True},
        hoverlabel={
            "bgcolor": "#05050f",
            "bordercolor": "#2E93fA",
            "font_family": THEME["font_family"],
        },
    )
    return fig

