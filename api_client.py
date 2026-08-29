import requests

API_URL = "http://127.0.0.1:8000"


def get_health():
    response = requests.get(
        f"{API_URL}/health",
        timeout=10
    )
    response.raise_for_status()
    return response.json()


def get_fires():
    response = requests.get(
        f"{API_URL}/api/fires",
        timeout=10
    )
    response.raise_for_status()
    return response.json()


def get_stats():
    response = requests.get(
        f"{API_URL}/api/stats",
        timeout=10
    )
    response.raise_for_status()
    return response.json()


def get_industries():
    response = requests.get(
        f"{API_URL}/api/industries",
        timeout=10
    )
    response.raise_for_status()
    return response.json()