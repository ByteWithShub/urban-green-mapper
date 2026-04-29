import time
import requests


def geocode_location(query: str) -> tuple[float, float, float, float]:
    """
    Convert a Canadian place name into a bounding box using Nominatim.

    Returns:
        bbox as west, south, east, north
    """
    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": f"{query}, Canada",
        "format": "json",
        "limit": 1,
        "addressdetails": 1,
    }

    headers = {
        "User-Agent": "UrbanGreenSpaceMapper/1.0 student-research-project"
    }

    response = requests.get(url, params=params, headers=headers, timeout=20)
    response.raise_for_status()

    data = response.json()

    if not data:
        raise ValueError(f"No location found for: {query}")

    # Nominatim bbox: south, north, west, east
    south, north, west, east = map(float, data[0]["boundingbox"])

    time.sleep(1)

    return west, south, east, north