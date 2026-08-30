#data_service.py#


from pathlib import Path
from typing import Optional

import pandas as pd

from risk_engine import calculate_risk, get_risk_level


# Repository root: sih2026-26162/
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

FIRES_FILE = DATA_DIR / "classified_fires.csv"
INDUSTRIES_FILE = DATA_DIR / "industries.csv"

#temprary fix#
print("BASE_DIR =", BASE_DIR)
print("DATA_DIR =", DATA_DIR)
print("FIRES_FILE =", FIRES_FILE)
print("INDUSTRIES_FILE =", INDUSTRIES_FILE)
#temprary fix#

CLASSIFICATION_LABELS = {
    "INDUSTRIAL_FIRE": "Industrial Fire",
    "WILDFIRE": "Wildfire",
    "THERMAL_SOURCE": "Thermal Source",
    "UNKNOWN": "Unknown",
}


def _safe_float(value, default=None):
    try:
        if pd.isna(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def load_fires() -> pd.DataFrame:
    if not FIRES_FILE.exists():
        raise FileNotFoundError(
            f"Fire data not found: {FIRES_FILE}"
        )

    df = pd.read_csv(FIRES_FILE)

    if "acquisition_date" in df.columns:
        df["acquisition_date"] = pd.to_datetime(
            df["acquisition_date"],
            errors="coerce"
        )

    if (
        "distance_to_industry" not in df.columns
        and "distance_to_industry_km" in df.columns
    ):
        df["distance_to_industry"] = df["distance_to_industry_km"]

    if "classification" not in df.columns:
        df["classification"] = "UNKNOWN"

    df["classification_label"] = (
        df["classification"]
        .astype(str)
        .str.upper()
        .map(CLASSIFICATION_LABELS)
        .fillna("Unknown")
    )

    risk_scores = []
    risk_levels = []

    for _, row in df.iterrows():

        score, _ = calculate_risk(
            brightness=_safe_float(row.get("brightness"), 0) or 0,
            confidence=_safe_float(row.get("confidence"), 0) or 0,
            distance_km=_safe_float(row.get("distance_to_industry")),
            classification=str(row.get("classification", "UNKNOWN")),
        )

        risk_scores.append(score)
        risk_levels.append(get_risk_level(score))

    df["risk_score"] = risk_scores
    df["risk_level"] = risk_levels

    df["id"] = [
        f"FIRE-{index + 1:06d}"
        for index in range(len(df))
    ]

    print("\n====================")
    print("MAX SCORE:", df["risk_score"].max())
    print("TOP 10 SCORES:")
    print(
        df.sort_values(
            "risk_score",
            ascending=False
        )[
            [
                "risk_score",
                "risk_level",
                "classification",
                "brightness",
                "confidence",
                "distance_to_industry"
            ]
        ].head(10)
    )
    print("====================\n")

    return df
def load_industries() -> pd.DataFrame:
    if not INDUSTRIES_FILE.exists():
        raise FileNotFoundError(
            f"Industry data not found: {INDUSTRIES_FILE}"
        )

    df = pd.read_csv(INDUSTRIES_FILE)

    df["id"] = [
        f"IND-{index + 1:06d}"
        for index in range(len(df))
    ]

    return df

def get_fire_by_id(fire_id: str) -> Optional[pd.Series]:
    df = load_fires()
    result = df[df["id"] == fire_id]
    return None if result.empty else result.iloc[0]


def get_industry_by_id(industry_id: str) -> Optional[pd.Series]:
    df = load_industries()
    result = df[df["id"] == industry_id]
    return None if result.empty else result.iloc[0]
