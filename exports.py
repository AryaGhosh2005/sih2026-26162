import json
import pandas as pd

from fastapi import APIRouter, Response

from services.data_service import load_fires


router = APIRouter(
    prefix="/api/v1/export",
    tags=["Export"],
)


@router.get("/geojson")
def export_geojson():
    df = load_fires()

    features = []

    for _, row in df.iterrows():
        properties = {}

        for column in df.columns:
            value = row[column]

            if pd.isna(value):
                value = None

            elif hasattr(value, "isoformat"):
                value = value.isoformat()

            elif hasattr(value, "item"):
                value = value.item()

            properties[column] = value

        features.append(
            {
                "type": "Feature",
                "properties": properties,
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        float(row["longitude"]),
                        float(row["latitude"]),
                    ],
                },
            }
        )

    geojson = {
        "type": "FeatureCollection",
        "features": features,
    }

    return Response(
        content=json.dumps(
            geojson,
            indent=2,
            default=str,
        ),
        media_type="application/geo+json",
        headers={
            "Content-Disposition": (
                "attachment; filename=thermal_anomalies.geojson"
            )
        },
    )
