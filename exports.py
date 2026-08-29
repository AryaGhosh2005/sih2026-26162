#exports.py#
import json

from fastapi import APIRouter
from fastapi.responses import Response

from data_service import load_fires


router = APIRouter(
    prefix="/api/v1/export",
    tags=["Export"],
)


@router.get("/csv")
def export_csv():
    csv_data = load_fires().to_csv(index=False)

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={
            "Content-Disposition": (
                "attachment; filename=thermal_anomalies.csv"
            )
        },
    )


@router.get("/geojson")
def export_geojson():
    df = load_fires()
    features = []

    for _, row in df.iterrows():
        properties = {}

        for column in df.columns:
            value = row[column]

            if hasattr(value, "isoformat"):
                value = value.isoformat()
            elif hasattr(value, "item"):
                value = value.item()

            properties[column] = value

        features.append({
            "type": "Feature",
            "properties": properties,
            "geometry": {
                "type": "Point",
                "coordinates": [
                    float(row["longitude"]),
                    float(row["latitude"]),
                ],
            },
        })

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
