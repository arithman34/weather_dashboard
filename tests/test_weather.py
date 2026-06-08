from backend.models import WeatherRecordDB


async def _create_location(client, auth_headers):
    resp = await client.post("/locations", json={"city": "London", "country": "GB"}, headers=auth_headers)
    return resp.json()["id"]


async def test_get_latest_weather(client, auth_headers, db):
    location_id = await _create_location(client, auth_headers)

    record = WeatherRecordDB(location_id=location_id, temperature=20.0)
    db.add(record)
    await db.commit()

    response = await client.get(f"/weather/{location_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["temperature"] == 20.0


async def test_get_latest_weather_no_data(client, auth_headers):
    location_id = await _create_location(client, auth_headers)
    response = await client.get(f"/weather/{location_id}", headers=auth_headers)
    assert response.status_code == 404


async def test_get_weather_history(client, auth_headers, db):
    location_id = await _create_location(client, auth_headers)

    for temp in [15.0, 16.0, 17.0]:
        db.add(WeatherRecordDB(location_id=location_id, temperature=temp))
    await db.commit()

    response = await client.get(f"/weather/{location_id}/history", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 3


async def test_weather_requires_auth(client, auth_headers):
    location_id = await _create_location(client, auth_headers)
    response = await client.get(f"/weather/{location_id}")
    assert response.status_code == 401
