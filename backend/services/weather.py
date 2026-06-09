import httpx


def get_coordinates(city: str, country: str) -> tuple[float, float]:
    """Geocode a city/country to latitude and longitude using Open-Meteo's geocoding API."""
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city, "count": 1, "language": "en", "format": "json"}

    with httpx.Client() as client:
        response = client.get(url, params=params)
        response.raise_for_status()

    results = response.json().get("results")
    if not results:
        raise ValueError(f"Could not find coordinates for {city}, {country}")

    return results[0]["latitude"], results[0]["longitude"]


def fetch_current_weather(latitude: float, longitude: float) -> dict:
    """Fetch current weather from Open-Meteo for given coordinates."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": [
            "temperature_2m",
            "apparent_temperature",
            "relative_humidity_2m",
            "wind_speed_10m",
            "weather_code",
        ],
        "timezone": "auto",
    }

    with httpx.Client() as client:
        response = client.get(url, params=params)
        response.raise_for_status()

    current = response.json()["current"]

    return {
        "temperature": current["temperature_2m"],
        "feels_like": current["apparent_temperature"],
        "humidity": current["relative_humidity_2m"],
        "wind_speed": current["wind_speed_10m"],
        "description": _weather_code_to_description(current["weather_code"]),
    }


def _weather_code_to_description(code: int) -> str:
    """Convert WMO weather code to a human-readable description."""
    codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Icy fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Heavy drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        80: "Slight showers",
        81: "Moderate showers",
        82: "Heavy showers",
        95: "Thunderstorm",
        99: "Thunderstorm with hail",
    }
    return codes.get(code, "Unknown")
