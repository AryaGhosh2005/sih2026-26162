import time
import requests
import pandas as pd
from io import StringIO
from config import FIRMS_MAP_KEY, SOURCE, DAY_RANGE, REGION_BBOX_FIRMS, REGION_BBOX_OSM, OVERPASS_MIRRORS


def fetch_fires() -> pd.DataFrame:
    """Fetch raw FIRMS hotspot data for the configured region."""
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{FIRMS_MAP_KEY}/{SOURCE}/{REGION_BBOX_FIRMS}/{DAY_RANGE}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return pd.read_csv(StringIO(resp.text))


def fetch_facilities() -> pd.DataFrame:
    """Fetch OSM industrial facility locations for the configured region."""
    query = f"""
    [out:json][timeout:90];
    (
      node["power"="plant"]({REGION_BBOX_OSM});
      way["power"="plant"]({REGION_BBOX_OSM});
      node["landuse"="industrial"]({REGION_BBOX_OSM});
      way["landuse"="industrial"]({REGION_BBOX_OSM});
      node["man_made"="works"]({REGION_BBOX_OSM});
      way["man_made"="works"]({REGION_BBOX_OSM});
    );
    out center;
    """
    headers = {
        "User-Agent": "hackathon-fire-classifier/1.0 (student project)",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = None
    for mirror in OVERPASS_MIRRORS:
        try:
            resp = requests.post(mirror, data={"data": query}, headers=headers, timeout=100)
            if resp.status_code == 200:
                data = resp.json()
                break
        except requests.exceptions.RequestException:
            time.sleep(2)
            continue

    if data is None:
        raise RuntimeError("All Overpass mirrors failed")

    facilities = []
    for el in data["elements"]:
        if el["type"] == "node":
            lat, lon = el["lat"], el["lon"]
        else:
            lat, lon = el["center"]["lat"], el["center"]["lon"]
        tags = el.get("tags", {})
        facilities.append({
            "latitude": lat,
            "longitude": lon,
            "name": tags.get("name", "unnamed"),
            "type": tags.get("power") or tags.get("landuse") or tags.get("man_made")
        })

    return pd.DataFrame(facilities)
