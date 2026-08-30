from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class FireDetectionBase(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    # NOTE: was `gt=0`. classifier.py fills missing brightness with 0
    # (fires_df["brightness"].fillna(0)), so a strict >0 constraint
    # crashed response validation for any such fire. Relaxed to >=0.
    brightness: float = Field(..., ge=0)
    confidence: float = Field(..., ge=0, le=100)
    satellite: str = Field(..., min_length=1, max_length=50)
    classification: str = Field(..., min_length=1, max_length=50)
    acquisition_date: Optional[datetime] = None
    distance_to_industry: Optional[float] = Field(default=None, ge=0)
    nearest_industry: Optional[str] = None
    industry_type: Optional[str] = None


class FireDetectionCreate(FireDetectionBase):
    pass


class FireDetection(FireDetectionBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    classification_label: Optional[str] = None
    risk_score: int = Field(..., ge=0, le=100)
    risk_level: str


class FireDetectionSummary(BaseModel):
    id: str
    latitude: float
    longitude: float
    classification: str
    classification_label: Optional[str]
    brightness: float
    confidence: float
    satellite: str
    acquisition_date: Optional[datetime] = None
    risk_score: int
    risk_level: str
    distance_to_industry: Optional[float]