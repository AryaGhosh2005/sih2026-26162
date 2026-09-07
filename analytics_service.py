#analytics_service.py#


import pandas as pd


def generate_summary(df: pd.DataFrame) -> dict:

    return {
        "total_detections": int(len(df)),

        "industrial_fires": int((df["classification"] == "INDUSTRIAL_FIRE").sum()),
        "wildfires": int((df["classification"] == "WILDFIRE").sum()),
        "thermal_sources": int((df["classification"] == "THERMAL_SOURCE").sum()),
        "unknown": int((df["classification"] == "UNKNOWN").sum()),

        "critical_risk": int((df["risk_level"] == "CRITICAL").sum()),
        "high_risk": int((df["risk_level"] == "HIGH").sum()),
        "moderate_risk": int((df["risk_level"] == "MODERATE").sum()),
        "low_risk": int((df["risk_level"] == "LOW").sum()),
    }


def daily_trend(df: pd.DataFrame) -> list:
    if "acquisition_date" not in df.columns:
        return []

    data = df.copy()

    data["acquisition_date"] = pd.to_datetime(
        data["acquisition_date"],
        errors="coerce"
    )

    data = data.dropna(subset=["acquisition_date"])

    if data.empty:
        return []

    grouped = (
        data.groupby(data["acquisition_date"].dt.date)
        .size()
        .reset_index(name="count")
    )

    grouped.columns = ["date", "count"]

    return [
        {
            "date": str(row["date"]),
            "count": int(row["count"])
        }
        for _, row in grouped.iterrows()
    ]