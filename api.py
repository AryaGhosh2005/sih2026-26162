from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

from data_fetcher import fetch_fires, fetch_facilities
from classifier import classify

app = FastAPI(title="Industrial Fire Classification API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_cache = {"fires_df": None, "facilities_df": None}


def _load_data(force_refresh: bool = False) -> pd.DataFrame:
    if _cache["fires_df"] is None or force_refresh:
        raw_fires = fetch_fires()
        facilities = fetch_facilities()
        classified = classify(raw_fires, facilities)

        _cache["fires_df"] = classified
        _cache["facilities_df"] = facilities

    return _cache["fires_df"]


@app.get("/")
def root():
    return {"status": "ok", "message": "Industrial Fire Classification API is running"}


@app.get("/api/fires")
def get_fires():
    try:
        df = _load_data()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch/classify data: {e}")
    return {"fires": df.to_dict(orient="records")}


@app.get("/api/stats")
def get_stats():
    try:
        df = _load_data()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch/classify data: {e}")

    counts = df["classification"].value_counts().to_dict()
    return {
        "total_fires": int(len(df)),
        "industrial_fires": int(counts.get("INDUSTRIAL_FIRE", 0)),
        "wildfires": int(counts.get("WILDFIRE", 0)),
        "thermal_sources": int(counts.get("THERMAL_SOURCE", 0)),
        "unknown": int(counts.get("UNKNOWN", 0)),
        "avg_confidence": round(float(df["confidence"].mean()), 2)
    }


@app.get("/api/industries")
def get_industries():
    try:
        _load_data()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch/classify data: {e}")
    return {"industries": _cache["facilities_df"].to_dict(orient="records")}


@app.post("/api/refresh")
def refresh():
    try:
        df = _load_data(force_refresh=True)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to refresh data: {e}")
    return {"status": "refreshed", "total_fires": int(len(df))}