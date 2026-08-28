from fastapi import APIRouter

from services.analytics_service import daily_trend, generate_summary
from services.data_service import load_fires


router = APIRouter(
    prefix="/api/v1/analytics",
    tags=["Analytics"],
)


@router.get("/summary")
def analytics_summary():
    return generate_summary(load_fires())


@router.get("/daily-trend")
def analytics_daily_trend():
    return {"data": daily_trend(load_fires())}
