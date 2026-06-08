from backend.models import WeatherRecordDB


def _create_location(client, auth_headers):
    resp = client.post("/locations", json={"city": "London", "country": "GB"}, headers=auth_headers)
    return resp.json()["id"]


def test_get_latest_weather(client, auth_headers, db):
    location_id = _create_location(client, auth_headers)

    record = WeatherRecordDB(location_id=location_id, temperature=20.0)
    db.add(record)
    db.commit()

    response = client.get(f"/weather/{location_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["temperature"] == 20.0


def test_get_latest_weather_no_data(client, auth_headers):
    location_id = _create_location(client, auth_headers)
    response = client.get(f"/weather/{location_id}", headers=auth_headers)
    assert response.status_code == 404


def test_get_weather_history(client, auth_headers, db):
    location_id = _create_location(client, auth_headers)

    for temp in [15.0, 16.0, 17.0]:
        db.add(WeatherRecordDB(location_id=location_id, temperature=temp))
    db.commit()

    response = client.get(f"/weather/{location_id}/history", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_weather_requires_auth(client, auth_headers):
    location_id = _create_location(client, auth_headers)
    response = client.get(f"/weather/{location_id}")
    assert response.status_code == 401
