import os
import sys
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

# Confidence mapping: VIIRS gives categorical l/n/h, schema wants a float
CONFIDENCE_MAP = {"l": 30.0, "n": 60.0, "h": 90.0}


def _to_radians(df: pd.DataFrame, lat_col: str, lon_col: str):
    return np.radians(df[[lat_col, lon_col]].values)


def add_distance_feature(fires_df: pd.DataFrame, facilities_df: pd.DataFrame) -> pd.DataFrame:
    fires_df = fires_df.copy()
    facility_coords = _to_radians(facilities_df, "latitude", "longitude")
    tree = cKDTree(facility_coords)
    fire_coords = _to_radians(fires_df, "latitude", "longitude")

    distances, indices = tree.query(fire_coords, k=1)
    EARTH_RADIUS_KM = 6371
    fires_df["distance_to_industry"] = distances * EARTH_RADIUS_KM
    fires_df["nearest_industry"] = facilities_df.iloc[indices]["name"].values
    fires_df["industry_type"] = facilities_df.iloc[indices]["type"].values
    return fires_df


def add_persistence_feature(fires_df: pd.DataFrame) -> pd.DataFrame:
    fires_df = fires_df.copy()
    fires_df["grid_lat"] = (fires_df["latitude"] / 0.01).round() * 0.01
    fires_df["grid_lon"] = (fires_df["longitude"] / 0.01).round() * 0.01

    persistence = (
        fires_df.groupby(["grid_lat", "grid_lon"])["acq_date"]
        .nunique()
        .reset_index()
        .rename(columns={"acq_date": "persistence_days"})
    )
    return fires_df.merge(persistence, on=["grid_lat", "grid_lon"], how="left")


def _classify_row(row) -> str:
    dist = row["distance_to_industry"]
    persistence = row["persistence_days"]
    frp = row["frp"]

    if dist <= 1.0 and persistence >= 2:
        return "INDUSTRIAL_FIRE"
    if dist <= 3.0 and persistence >= 3:
        return "INDUSTRIAL_FIRE"
    if dist > 10.0 and persistence <= 1 and frp > 5:
        return "WILDFIRE"
    if persistence >= 2 and dist > 3.0:
        return "THERMAL_SOURCE"
    return "UNKNOWN"


def classify(fires_df: pd.DataFrame, facilities_df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes raw FIRMS + OSM data, returns a DataFrame matching the
    Universal Data Contract schema:
    latitude, longitude, brightness, acquisition_date, satellite,
    classification, confidence, distance_to_industry
    — plus nearest_industry / industry_type, which app.py optionally
    reads via .get() for its event detail panel.
    """
    df = add_distance_feature(fires_df, facilities_df)
    df = add_persistence_feature(df)
    df["classification"] = df.apply(_classify_row, axis=1)
    df["confidence"] = df["confidence"].map(CONFIDENCE_MAP).fillna(50.0)

    result = pd.DataFrame({
        "latitude": df["latitude"],
        "longitude": df["longitude"],
        "brightness": df["bright_ti4"],
        "acquisition_date": df["acq_date"],   # FIRMS already returns YYYY-MM-DD
        "satellite": df["satellite"],
        "classification": df["classification"],
        "confidence": df["confidence"],
        "distance_to_industry": df["distance_to_industry"].round(2),
        "nearest_industry": df["nearest_industry"],
        "industry_type": df["industry_type"]
    })
    return result


if __name__ == "__main__":
    from data_fetcher import fetch_fires, fetch_facilities

    output_dir = sys.argv[1] if len(sys.argv) > 1 else "data"
    os.makedirs(output_dir, exist_ok=True)

    print("Fetching FIRMS hotspot data...")
    raw_fires = fetch_fires()
    print(f"  {len(raw_fires)} raw hotspots fetched")

    print("Fetching OSM industrial facilities...")
    facilities = fetch_facilities()
    print(f"  {len(facilities)} facilities fetched")

    print("Classifying...")
    classified = classify(raw_fires, facilities)

    fires_path = os.path.join(output_dir, "classified_fires.csv")
    industries_path = os.path.join(output_dir, "industries.csv")

    classified.to_csv(fires_path, index=False)
    facilities.to_csv(industries_path, index=False)

    print(f"Saved {len(classified)} classified fires to {fires_path}")
    print(f"Saved {len(facilities)} facilities to {industries_path}")