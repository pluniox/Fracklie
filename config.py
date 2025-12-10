"""Global configuration for the road safety dashboard project."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
CLEANED_DATA_DIR = DATA_DIR / "cleaned"

DATA_URLS = {
    "caracteristiques": (
        "https://static.data.gouv.fr/resources/"
        "bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-"
        "routiere-annees-de-2005-a-2021/20231005-093927/carcteristiques-2022.csv"
    ),
    "lieux": (
        "https://static.data.gouv.fr/resources/"
        "bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-"
        "routiere-annees-de-2005-a-2021/20231005-094112/lieux-2022.csv"
    ),
    "usagers": (
        "https://static.data.gouv.fr/resources/"
        "bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-"
        "routiere-annees-de-2005-a-2021/20231005-094229/usagers-2022.csv"
    ),
}

RAW_FILENAMES = {
    "caracteristiques": "caracteristiques_2022.csv",
    "lieux": "lieux_2022.csv",
    "usagers": "usagers_2022.csv",
}

CLEANED_FILE = CLEANED_DATA_DIR / "accidents_cleaned.csv"

SEVERITY_LABELS = {
    2: "Tue",
    3: "Blesse hospitalise",
    4: "Blesse leger",
    1: "Indemne",
}

SEVERITY_ORDER = {2: 3, 3: 2, 4: 1, 1: 0}

AGGLO_MAPPING = {
    1: "Hors agglomeration",
    2: "En agglomeration",
    3: "Autre",
}

SURFACE_MAPPING = {
    1: "Normale",
    2: "Mouillee",
    3: "Flaques",
    4: "Inondee",
    5: "Enneigee",
    6: "Boue",
    7: "Verglas",
    8: "Corps gras",
    9: "Autre",
}

LIGHT_MAPPING = {
    1: "Plein jour",
    2: "Crepuscule ou aube",
    3: "Nuit sans eclairage public",
    4: "Nuit avec eclairage public non allume",
    5: "Nuit avec eclairage public allume",
}
