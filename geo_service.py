#geo_service.py#
import math
import numpy as np
from scipy.spatial import KDTree


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

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return radius * c


def build_industry_tree(industries):
    """
    Build KDTree once and reuse it.
    """

    if industries.empty:
        return None, None

    coords = np.column_stack(
        (
            industries["latitude"],
            industries["longitude"]
        )
    )

    tree = KDTree(coords)

    return tree, industries.reset_index(drop=True)


def find_nearest_industry(
    latitude,
    longitude,
    tree,
    industries
):
    """
    Fast nearest industry lookup using KDTree.
    """

    if tree is None:
        return None

    _, index = tree.query(
        [latitude, longitude]
    )

    industry = industries.iloc[index]

    distance = haversine_distance(
        latitude,
        longitude,
        float(industry["latitude"]),
        float(industry["longitude"])
    )

    return {
        "industry": industry,
        "distance_km": round(distance, 3),
    }