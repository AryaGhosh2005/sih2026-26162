from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class IndustryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    industry_type: Optional[str] = None
    risk_category: Optional[str] = None


class Industry(IndustryBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
