from __future__ import annotations

from functools import lru_cache
from typing import Dict, Optional

import pandas as pd

from config import (
    AGGLO_MAPPING,
    CLEANED_DATA_DIR,
    CLEANED_FILE,
    LIGHT_MAPPING,
    RAW_DATA_DIR,
    RAW_FILENAMES,
    SEVERITY_LABELS,
    SEVERITY_ORDER,
    SURFACE_MAPPING,
)
from src.utils.get_data import download_data


def _safe_float(value: object) -> Optional[float]:
    if pd.isna(value):
        return None
    text = str(value).strip().replace(",", ".")
    if text in {"", "-1", "None", "nan"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _extract_hour(hrmn_value: object) -> Optional[int]:
    if pd.isna(hrmn_value):
        return None
    text = str(hrmn_value).split(".")[0].zfill(4)
    if not text.isdigit():
        return None
    try:
        return int(text[:2])
    except ValueError:
        return None


def _lighting_group(lum: Optional[int]) -> str:
    if lum is None or pd.isna(lum):
        return "Non renseigne"
    if lum == 5:
        return "Eclairage public"
    if lum in (3, 4):
        return "Sans eclairage public"
    if lum in (1, 2):
        return "Lumiere naturelle"
    return "Non renseigne"


def _worst_severity(usagers: pd.DataFrame) -> pd.DataFrame:
    working = usagers.copy()
    working["severity_rank"] = working["grav"].map(SEVERITY_ORDER).fillna(-1)
    idx = working.groupby("Num_Acc")["severity_rank"].idxmax()
    result = working.loc[idx, ["Num_Acc", "grav"]].rename(columns={"grav": "severity_code"})
    result["severity_label"] = result["severity_code"].map(SEVERITY_LABELS).fillna("Gravite inconnue")
    result["victim_count"] = usagers.groupby("Num_Acc")["grav"].size().reindex(result["Num_Acc"]).values
    return result


def clean_data(force: bool = False) -> pd.DataFrame:
    download_data(force=force)
    CLEANED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    caracteristiques_path = RAW_DATA_DIR / RAW_FILENAMES["caracteristiques"]
    lieux_path = RAW_DATA_DIR / RAW_FILENAMES["lieux"]
    usagers_path = RAW_DATA_DIR / RAW_FILENAMES["usagers"]

    caracteristiques = pd.read_csv(
        caracteristiques_path,
        sep=";",
        dtype={"hrmn": str},
        low_memory=False,
    )
    caracteristiques["agg"] = pd.to_numeric(caracteristiques["agg"], errors="coerce")
    caracteristiques["lum"] = pd.to_numeric(caracteristiques["lum"], errors="coerce")
    caracteristiques = caracteristiques.rename(columns={"Accident_Id": "Num_Acc"})
    caracteristiques["lat"] = caracteristiques["lat"].apply(_safe_float)
    caracteristiques["long"] = caracteristiques["long"].apply(_safe_float)
    caracteristiques["date"] = pd.to_datetime(
        dict(year=caracteristiques["an"], month=caracteristiques["mois"], day=caracteristiques["jour"]),
        errors="coerce",
    )
    caracteristiques["hour"] = caracteristiques["hrmn"].apply(_extract_hour)
    caracteristiques["agg_label"] = caracteristiques["agg"].map(AGGLO_MAPPING).fillna("Non renseigne")
    caracteristiques["lighting_label"] = caracteristiques["lum"].map(LIGHT_MAPPING).fillna("Non renseigne")
    caracteristiques["lighting_group"] = caracteristiques["lum"].apply(_lighting_group)

    lieux = pd.read_csv(lieux_path, sep=";", low_memory=False)
    lieux["surf"] = pd.to_numeric(lieux["surf"], errors="coerce")
    lieux = lieux[["Num_Acc", "surf"]]
    lieux["surface_label"] = lieux["surf"].map(SURFACE_MAPPING).fillna("Non renseigne")

    usagers = pd.read_csv(usagers_path, sep=";", low_memory=False)
    usagers["grav"] = pd.to_numeric(usagers["grav"], errors="coerce")
    severity = _worst_severity(usagers)

    merged = (
        caracteristiques.merge(lieux, on="Num_Acc", how="left")
        .merge(severity, on="Num_Acc", how="left")
    )

    merged = merged[
        [
            "Num_Acc",
            "date",
            "hour",
            "agg",
            "agg_label",
            "lat",
            "long",
            "surf",
            "surface_label",
            "lum",
            "lighting_label",
            "lighting_group",
            "severity_code",
            "severity_label",
            "victim_count",
        ]
    ]

    merged = merged.dropna(subset=["lat", "long"])
    merged.to_csv(CLEANED_FILE, index=False)
    return merged


@lru_cache
def load_clean_data() -> pd.DataFrame:
    if not CLEANED_FILE.exists():
        return clean_data(force=False)
    return pd.read_csv(CLEANED_FILE, parse_dates=["date"])


if __name__ == "__main__":
    clean_data(force=False)
