async def test_create_location(client, auth_headers):
    response = await client.post(
        "/locations",
        json={
            "city": "London",
            "country": "GB",
            "alert_threshold_max": 35.0,
            "alert_threshold_min": -5.0,
            "alert_enabled": True,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["city"] == "London"
    assert data["alert_enabled"] is True


async def test_get_locations(client, auth_headers):
    await client.post("/locations", json={"city": "London", "country": "GB"}, headers=auth_headers)

    response = await client.get("/locations", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_update_location(client, auth_headers):
    create_resp = await client.post("/locations", json={"city": "London", "country": "GB"}, headers=auth_headers)
    location_id = create_resp.json()["id"]

    response = await client.put(
        f"/locations/{location_id}",
        json={
            "alert_threshold_max": 30.0,
            "alert_enabled": True,
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["alert_threshold_max"] == 30.0


async def test_delete_location(client, auth_headers):
    create_resp = await client.post("/locations", json={"city": "London", "country": "GB"}, headers=auth_headers)
    location_id = create_resp.json()["id"]

    response = await client.delete(f"/locations/{location_id}", headers=auth_headers)
    assert response.status_code == 204


async def test_get_locations_requires_auth(client):
    response = await client.get("/locations")
    assert response.status_code == 401


async def test_cannot_access_other_users_location(client, auth_headers):
    create_resp = await client.post("/locations", json={"city": "London", "country": "GB"}, headers=auth_headers)
    location_id = create_resp.json()["id"]

    await client.post(
        "/auth/register", json={"username": "user2", "email": "user2@example.com", "password": "password123"}
    )
    login_resp = await client.post("/auth/login", data={"username": "user2", "password": "password123"})
    headers2 = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    response = await client.delete(f"/locations/{location_id}", headers=headers2)
    assert response.status_code == 404
