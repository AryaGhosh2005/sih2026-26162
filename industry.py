#industry.py#

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class IndustryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    industry_type: Optional[str] = Field(default=None, max_length=100)
    risk_category: Optional[str] = Field(default=None, max_length=50)


class IndustryCreate(IndustryBase):
    """Schema used when creating an industry."""
    pass


class IndustryUpdate(BaseModel):
    """Schema used when partially updating an industry."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    industry_type: Optional[str] = Field(default=None, max_length=100)
    risk_category: Optional[str] = Field(default=None, max_length=50)


class Industry(IndustryBase):
    """Schema returned by the API."""
    model_config = ConfigDict(from_attributes=True)

    id: str