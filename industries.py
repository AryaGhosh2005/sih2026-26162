#industries.py#

from fastapi import APIRouter, HTTPException

from industry import Industry
from data_service import get_industry_by_id, load_industries


router = APIRouter(
    prefix="/api/v1/industries",
    tags=["Industries"],
)


@router.get("", response_model=list[Industry])
def get_industries():
    df = load_industries()
    result = []

    for _, row in df.iterrows():
        result.append({
            "id": row["id"],
            "name": row.get(
                "name",
                row.get("industry_name", "Unknown"),
            ),
            "latitude": float(row["latitude"]),
            "longitude": float(row["longitude"]),
            "industry_type": row.get("industry_type"),
            "risk_category": row.get("risk_category"),
        })

    return result


@router.get("/{industry_id}", response_model=Industry)
def get_industry(industry_id: str):
    industry = get_industry_by_id(industry_id)

    if industry is None:
        raise HTTPException(
            status_code=404,
            detail="Industry not found",
        )

    return {
        "id": industry["id"],
        "name": industry.get(
            "name",
            industry.get("industry_name", "Unknown"),
        ),
        "latitude": float(industry["latitude"]),
        "longitude": float(industry["longitude"]),
        "industry_type": industry.get("industry_type"),
        "risk_category": industry.get("risk_category"),
    }
