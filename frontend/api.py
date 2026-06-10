import httpx

BASE_URL = "http://localhost:8000"


def register(username: str, email: str, password: str) -> dict:
    response = httpx.post(
        f"{BASE_URL}/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )
    response.raise_for_status()
    return response.json()


def login(username: str, password: str) -> str:
    response = httpx.post(
        f"{BASE_URL}/auth/login",
        data={
            "username": username,
            "password": password,
        },
    )
    response.raise_for_status()
    return response.json()["access_token"]


def get_locations(token: str) -> list:
    response = httpx.get(f"{BASE_URL}/locations", headers={"Authorization": f"Bearer {token}"})
    response.raise_for_status()
    return response.json()


def create_location(token: str, city: str, country: str) -> dict:
    response = httpx.post(
        f"{BASE_URL}/locations",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "city": city,
            "country": country,
        },
    )
    response.raise_for_status()
    return response.json()


def delete_location(token: str, location_id: int) -> None:
    response = httpx.delete(f"{BASE_URL}/locations/{location_id}", headers={"Authorization": f"Bearer {token}"})
    response.raise_for_status()


def update_location(
    token: str,
    location_id: int,
    alert_threshold_max: float | None,
    alert_threshold_min: float | None,
    alert_enabled: bool,
) -> dict:
    response = httpx.put(
        f"{BASE_URL}/locations/{location_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "alert_threshold_max": alert_threshold_max,
            "alert_threshold_min": alert_threshold_min,
            "alert_enabled": alert_enabled,
        },
    )
    response.raise_for_status()
    return response.json()


def get_weather_history(token: str, location_id: int, limit: int = 30) -> list:
    response = httpx.get(
        f"{BASE_URL}/weather/{location_id}/history",
        headers={"Authorization": f"Bearer {token}"},
        params={"limit": limit},
    )
    response.raise_for_status()
    return response.json()


def get_latest_weather(token: str, location_id: int) -> dict:
    response = httpx.get(f"{BASE_URL}/weather/{location_id}", headers={"Authorization": f"Bearer {token}"})
    response.raise_for_status()
    return response.json()


def fetch_weather(token: str, location_id: int) -> None:
    response = httpx.get(f"{BASE_URL}/weather/{location_id}/fetch", headers={"Authorization": f"Bearer {token}"})
    response.raise_for_status()
