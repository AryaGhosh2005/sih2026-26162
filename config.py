import os
from dotenv import load_dotenv

load_dotenv()

FIRMS_MAP_KEY = os.getenv("FIRMS_MAP_KEY")
SOURCE = "VIIRS_SNPP_NRT"
DAY_RANGE = 5

# south, west, north, east — WB/Jharkhand/Odisha industrial belt
REGION_BBOX_OSM = "19,82,25,89"
# west, south, east, north — same region, FIRMS order
REGION_BBOX_FIRMS = "82,19,89,25"

OVERPASS_MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]