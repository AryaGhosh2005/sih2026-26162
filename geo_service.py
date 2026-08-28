import math


def haversine_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    """Return great-circle distance between two points in kilometres."""
    radius = 6371.0

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1)
        * math.cos(phi2)
        * math.sin(delta_lambda / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius * c


def find_nearest_industry(latitude, longitude, industries):
    if industries.empty:
        return None

    best = None
    best_distance = float("inf")

    for _, industry in industries.iterrows():
        distance = haversine_distance(
            latitude,
            longitude,
            float(industry["latitude"]),
            float(industry["longitude"]),
        )

        if distance < best_distance:
            best_distance = distance
            best = industry

    if best is None:
        return None

    return {
        "industry": best,
        "distance_km": round(best_distance, 3),
    }
