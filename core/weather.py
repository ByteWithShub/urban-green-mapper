import requests


def get_current_weather(latitude: float, longitude: float) -> dict:
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "cloud_cover",
            "wind_speed_10m",
        ],
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    return response.json()["current"]