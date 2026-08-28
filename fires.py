from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from schemas.fire import FireDetection, FireDetectionSummary
from services.data_service import get_fire_by_id, load_fires


router = APIRouter(
    prefix="/api/v1/fires",
    tags=["Fire Detection"],
)


@router.get("", response_model=list[FireDetectionSummary])
def get_fires(
    classification: Optional[str] = Query(default=None),
    satellite: Optional[str] = Query(default=None),
    min_brightness: Optional[float] = Query(default=None, ge=0),
    min_confidence: Optional[float] = Query(default=None, ge=0, le=100),
    max_distance: Optional[float] = Query(default=None, ge=0),
    risk_level: Optional[str] = Query(default=None),
):
    df = load_fires()

    if classification:
        df = df[df["classification"].astype(str).str.upper() == classification.upper()]

    if satellite:
        df = df[df["satellite"].astype(str).str.upper() == satellite.upper()]

    if min_brightness is not None:
        df = df[df["brightness"] >= min_brightness]

    if min_confidence is not None:
        df = df[df["confidence"] >= min_confidence]

    if max_distance is not None:
        df = df[df["distance_to_industry"] <= max_distance]

    if risk_level:
        df = df[df["risk_level"].str.upper() == risk_level.upper()]

    result = []

    for _, row in df.iterrows():
        distance = row.get("distance_to_industry")

        result.append({
            "id": row["id"],
            "latitude": float(row["latitude"]),
            "longitude": float(row["longitude"]),
            "classification": str(row["classification"]),
            "classification_label": row["classification_label"],
            "brightness": float(row["brightness"]),
            "confidence": float(row["confidence"]),
            "satellite": str(row["satellite"]),
            "risk_score": int(row["risk_score"]),
            "risk_level": str(row["risk_level"]),
            "distance_to_industry": (
                float(distance) if distance is not None else None
            ),
        })

    return result


@router.get("/{fire_id}", response_model=FireDetection)
def get_fire(fire_id: str):
    fire = get_fire_by_id(fire_id)

    if fire is None:
        raise HTTPException(
            status_code=404,
            detail="Fire detection not found",
        )

    distance = fire.get("distance_to_industry")

    return {
        "id": fire["id"],
        "latitude": float(fire["latitude"]),
        "longitude": float(fire["longitude"]),
        "brightness": float(fire["brightness"]),
        "confidence": float(fire["confidence"]),
        "satellite": str(fire["satellite"]),
        "classification": str(fire["classification"]),
        "classification_label": fire["classification_label"],
        "acquisition_date": fire.get("acquisition_date"),
        "distance_to_industry": (
            float(distance) if distance is not None and not __import__("pandas").isna(distance) else None
        ),
        "nearest_industry": fire.get("nearest_industry"),
        "industry_type": fire.get("industry_type"),
        "risk_score": int(fire["risk_score"]),
        "risk_level": str(fire["risk_level"]),
    }
