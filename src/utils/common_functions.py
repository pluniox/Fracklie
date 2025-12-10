from __future__ import annotations

from typing import Iterable, Optional, Sequence, Tuple

import pandas as pd


def filter_dataframe(
    df: pd.DataFrame,
    date_range: Optional[Tuple[str, str]] = None,
    severities: Optional[Sequence[str]] = None,
    agglo: Optional[Sequence[str]] = None,
    surfaces: Optional[Sequence[str]] = None,
    lighting_groups: Optional[Sequence[str]] = None,
) -> pd.DataFrame:
    filtered = df
    if date_range and all(date_range):
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        filtered = filtered[(filtered["date"] >= start) & (filtered["date"] <= end)]

    if severities:
        filtered = filtered[filtered["severity_label"].isin(severities)]

    if agglo:
        filtered = filtered[filtered["agg_label"].isin(agglo)]

    if surfaces:
        filtered = filtered[filtered["surface_label"].isin(surfaces)]

    if lighting_groups:
        filtered = filtered[filtered["lighting_group"].isin(lighting_groups)]

    return filtered


def dataframe_date_bounds(df: pd.DataFrame) -> Tuple[pd.Timestamp, pd.Timestamp]:
    return df["date"].min(), df["date"].max()
