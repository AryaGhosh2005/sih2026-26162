"""
data_service.py — High-performance data ingestion layer for AEGIS-FIRE.
Loads satellite thermal telemetry and OSM/reference industrial infrastructure.
"""

from pathlib import Path
from typing import Optional

import duckdb
import numpy as np
import pandas as pd

from risk_engine import get_risk_level

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

FIRES_FILE = DATA_DIR / "classified_fires.csv"
INDUSTRIES_FILE = DATA_DIR / "industries.csv"

CLASSIFICATION_LABELS = {
    "INDUSTRIAL_FIRE": "Industrial Fire",
    "WILDFIRE": "Wildfire",
    "THERMAL_SOURCE": "Thermal Source",
    "UNKNOWN": "Unknown",
}

_con = duckdb.connect(database=":memory:")


def load_fires() -> pd.DataFrame:
    """Loads and sanitizes classified fire detections with vectorized threat scores."""

    if not FIRES_FILE.exists():
        raise FileNotFoundError(f"Thermal detections not found at: {FIRES_FILE}")

    csv_path = str(FIRES_FILE).replace("\\", "/")
    df = _con.execute(
    f"SELECT * FROM read_csv_auto('{csv_path}')"
).fetch_df()

    if df is None or len(df) == 0:
        return pd.DataFrame(
            columns=[
            "id",
            "name",
            "latitude",
            "longitude",
            "type",
            ]
        )

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

    df["classification"] = df["classification"].astype(str).str.upper()

    df["classification_label"] = (
        df["classification"]
        .map(CLASSIFICATION_LABELS)
        .fillna("Unknown")
    )

    if "brightness" not in df.columns:
        df["brightness"] = 280.0

    if "confidence" not in df.columns:
        df["confidence"] = 50.0

    if "frp" not in df.columns:
        df["frp"] = 0.0

    if "distance_to_industry" not in df.columns:
        df["distance_to_industry"] = 999.0

    df["brightness"] = pd.to_numeric(
        df["brightness"],
        errors="coerce"
    ).fillna(280.0)

    df["confidence"] = pd.to_numeric(
        df["confidence"],
        errors="coerce"
    ).fillna(50.0)

    df["frp"] = pd.to_numeric(
        df["frp"],
        errors="coerce"
    ).fillna(0.0)

    df["distance_to_industry"] = pd.to_numeric(
        df["distance_to_industry"],
        errors="coerce"
    ).fillna(999.0)

    # Vectorized Risk Score Calculation
    brightness_score = (
        ((df["brightness"] - 280.0) / 100.0 * 40.0)
        .clip(0.0, 40.0)
    )

    confidence_score = (
        (df["confidence"] / 100.0 * 30.0)
        .clip(0.0, 30.0)
    )

    proximity_score = pd.Series(0.0, index=df.index)
    dist = df["distance_to_industry"]

    proximity_score[dist <= 2.0] = 30.0
    proximity_score[(dist > 2.0) & (dist <= 5.0)] = 22.0
    proximity_score[(dist > 5.0) & (dist <= 8.0)] = 14.0
    proximity_score[(dist > 8.0) & (dist <= 15.0)] = 7.0

    classification_bonus = pd.Series(0.0, index=df.index)
    classification_bonus[
        df["classification"] == "INDUSTRIAL_FIRE"
    ] = 30.0

    calculated_risk = (
        brightness_score
        + confidence_score
        + proximity_score
        + classification_bonus
    ).round().clip(0, 100).astype(int)

    if "risk_score" not in df.columns or df["risk_score"].isna().all():
        df["risk_score"] = calculated_risk
    else:
        df["risk_score"] = (
            pd.to_numeric(
                df["risk_score"],
                errors="coerce"
            )
            .fillna(calculated_risk)
            .astype(int)
        )

    df["risk_level"] = df["risk_score"].apply(get_risk_level)

    if "id" not in df.columns:
        df["id"] = [
            f"FIRE_{i + 1:05d}"
            for i in range(len(df))
        ]

    return df


def load_industries() -> pd.DataFrame:
    """Loads industrial facilities infrastructure database."""

    if not INDUSTRIES_FILE.exists():
        raise FileNotFoundError(
            f"Industrial database not found at: {INDUSTRIES_FILE}"
        )

    csv_path = str(INDUSTRIES_FILE).replace("\\", "/")

    df = _con.execute(
        f"SELECT * FROM read_csv_auto('{csv_path}')"
    ).fetch_df()

    df["latitude"] = (
        pd.to_numeric(
            df["latitude"],
            errors="coerce"
        ).fillna(0.0)
    )

    df["longitude"] = (
        pd.to_numeric(
            df["longitude"],
            errors="coerce"
        ).fillna(0.0)
    )

    if "id" not in df.columns:
        df["id"] = [
            f"IND_{i + 1:05d}"
            for i in range(len(df))
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