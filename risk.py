from pydantic import BaseModel, Field


class RiskBreakdown(BaseModel):
    brightness_score: float = Field(..., ge=0, le=40)
    confidence_score: float = Field(..., ge=0, le=30)
    proximity_score: float = Field(..., ge=0, le=30)
    classification_bonus: float = Field(..., ge=0, le=5)


class RiskResponse(BaseModel):
    fire_id: str
    risk_score: int = Field(..., ge=0, le=100)
    risk_level: str
    breakdown: RiskBreakdown
    recommendation: str
