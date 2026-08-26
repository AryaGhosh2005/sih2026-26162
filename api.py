"""
api.py
FastAPI backend for serving classified fire data and statistics.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
from typing import List, Dict, Any

# --- Initialize FastAPI ---
CLASS_LABELS = {
    "INDUSTRIAL_FIRE": "Industrial Fire",
    "WILDFIRE": "Wildfire",
    "THERMAL_SOURCE": "Thermal Source",
    "UNKNOWN": "Unknown"
}

app = FastAPI(
    title="Thermal Anomaly Detection API",
    description="API for serving classified fire data and industrial facilities",
    version="1.0.0"
)

# --- Enable CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for MVP (restrict in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Loading Functions ---
def load_fires_data():
    """Load classified fires data from CSV"""
    try:
        df = pd.read_csv("data/classified_fires.csv")
        # Convert date to string for JSON serialization
        if "acquisition_date" in df.columns:
            df["acquisition_date"] = pd.to_datetime(df["acquisition_date"]).dt.strftime("%Y-%m-%d")
        return df
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="classified_fires.csv not found. Run classifier.py first.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")

def load_industries_data():
    """Load industries data from CSV"""
    try:
        return pd.read_csv("data/industries.csv")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="industries.csv not found. Run data_generator.py first.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading industries: {str(e)}")

# --- API Endpoints ---

@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "message": "Thermal Anomaly Detection API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": [
            "/api/fires",
            "/api/stats",
            "/api/industries",
            "/health"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    # Check if data files exist
    fires_exists = os.path.exists("data/classified_fires.csv")
    industries_exists = os.path.exists("data/industries.csv")
    
    return {
        "status": "healthy" if fires_exists and industries_exists else "degraded",
        "files": {
            "classified_fires.csv": fires_exists,
            "industries.csv": industries_exists
        },
        "timestamp": pd.Timestamp.now().isoformat()
    }

@app.get("/api/fires")
async def get_fires():
    """
    Get all classified fires.
    Returns a list of fire objects with classification details.
    """
    df = load_fires_data()
    
    # Convert to dictionary (JSON-friendly)
    result = df.to_dict(orient="records")
    
    # Clean up NaN values
    for record in result:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None
    
    return {"fires": result}

@app.get("/api/stats")
async def get_stats():
    """
    Get statistics about classified fires.
    Returns counts by type and average confidence.
    """
    df = load_fires_data()
    
    total = len(df)
    
    # Count by classification
    industrial = len(df[df["classification"] == "INDUSTRIAL_FIRE"])
    wildfire = len(df[df["classification"] == "WILDFIRE"])
    thermal = len(df[df["classification"] == "THERMAL_SOURCE"])
    
    # Average confidence (if column exists, else random placeholder)
    if "confidence" in df.columns:
        avg_confidence = round(df["confidence"].mean(), 1)
    else:
        avg_confidence = 87.5  # placeholder
    
    # Daily trend data
    if "acquisition_date" in df.columns:
        daily_counts = df.groupby("acquisition_date").size().reset_index(name="count")
        daily_trend = daily_counts.to_dict(orient="records")
    else:
        daily_trend = []
    
    # Breakdown by satellite
    if "satellite" in df.columns:
        satellite_counts = df.groupby("satellite").size().reset_index(name="count")
        by_satellite = satellite_counts.to_dict(orient="records")
    else:
        by_satellite = []
    
    return {
        "total_fires": total,
        "industrial_fires": industrial,
        "wildfires": wildfire,
        "thermal_sources": thermal,
        "avg_confidence": avg_confidence,
        "by_satellite": by_satellite,
        "daily_trend": daily_trend
    }

@app.get("/api/industries")
async def get_industries():
    """
    Get all industrial facilities.
    Returns a list of industrial sites with names, coordinates, and types.
    """
    df = load_industries_data()
    
    result = df.to_dict(orient="records")
    
    return {"industries": result}

# --- Optional: Filtered endpoint for query parameters ---
@app.get("/api/fires/filter")
async def filter_fires(
    classification: str = None,
    satellite: str = None,
    min_brightness: float = None,
    max_brightness: float = None
):
    """
    Filter fires by classification, satellite, or brightness range.
    """
    df = load_fires_data()
    
    if classification:
        df = df[df["classification"] == classification]
    
    if satellite:
        df = df[df["satellite"] == satellite]
    
    if min_brightness:
        df = df[df["brightness"] >= min_brightness]
    
    if max_brightness:
        df = df[df["brightness"] <= max_brightness]
    
    result = df.to_dict(orient="records")
    
    # Clean NaN values
    for record in result:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None
    
    return {
        "filtered": result,
        "count": len(result)
    }

# --- Run with: uvicorn api:app --reload --port 8000 ---

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)