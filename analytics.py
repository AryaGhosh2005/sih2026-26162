#analytics.py#

from fastapi import APIRouter

from analytics_service import daily_trend, generate_summary
from data_service import load_fires


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

#temp#
@router.get("/summary")
def analytics_summary():

    df = load_fires()

    print("\n=== DEBUG RISK LEVELS ===")
    print(len(df))
    print(df["risk_level"].value_counts(dropna=False))

    return generate_summary(df)





@router.get("/debug/top-scores")
def top_scores():
    df = load_fires()

    return (
        df[
            [
                "risk_score",
                "risk_level",
                "classification",
                "brightness",
                "confidence",
                "distance_to_industry",
            ]
        ]
        .sort_values("risk_score", ascending=False)
        .head(20)
        .to_dict(orient="records")
    )