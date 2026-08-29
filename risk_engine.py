#risk_engine.py#

from typing import Optional, Tuple


def calculate_brightness_score(brightness: float) -> float:
    score = ((brightness - 280) / 100) * 40
    return max(0, min(40, score))


def calculate_confidence_score(confidence: float) -> float:
    return max(0, min(30, (confidence / 100) * 30))


def calculate_proximity_score(distance_km: Optional[float]) -> float:
    if distance_km is None:
        return 0

    if distance_km <= 2:
        return 30
    if distance_km <= 5:
        return 22
    if distance_km <= 8:
        return 14
    if distance_km <= 15:
        return 7
    return 2


def calculate_classification_bonus(classification: str) -> float:
    return 20 if classification.upper() == "INDUSTRIAL_FIRE" else 0


def calculate_risk(
    brightness: float,
    confidence: float,
    distance_km: Optional[float],
    classification: str,
) -> Tuple[int, dict]:
    brightness_score = calculate_brightness_score(brightness)
    confidence_score = calculate_confidence_score(confidence)
    proximity_score = calculate_proximity_score(distance_km)
    classification_bonus = calculate_classification_bonus(classification)

    score = round(
        brightness_score
        + confidence_score
        + proximity_score
        + classification_bonus
    )
    score = max(0, min(100, score))

    breakdown = {
        "brightness_score": round(brightness_score, 2),
        "confidence_score": round(confidence_score, 2),
        "proximity_score": round(proximity_score, 2),
        "classification_bonus": round(classification_bonus, 2),
    }

    return score, breakdown


def get_risk_level(score: int) -> str:
    if score >= 65:
        return "CRITICAL"
    if score >= 50:
        return "HIGH"
    if score >= 35:
        return "MODERATE"
    return "LOW"


def get_recommendation(risk_level: str) -> str:
    recommendations = {
        "CRITICAL": "Immediate emergency response and industrial safety assessment required.",
        "HIGH": "Prioritize field verification and notify relevant authorities.",
        "MODERATE": "Monitor the anomaly and schedule verification.",
        "LOW": "Continue monitoring. No immediate intervention required.",
    }
    return recommendations.get(risk_level, "Continue monitoring.")
