async def test_register_success(client):
    response = await client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepass",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "hashed_password" not in data


async def test_register_duplicate_username(client, registered_user):
    response = await client.post(
        "/auth/register",
        json={
            "username": registered_user["username"],
            "email": "other@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 400


async def test_register_duplicate_email(client, registered_user):
    response = await client.post(
        "/auth/register",
        json={
            "username": "otherusername",
            "email": "testuser@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 400


async def test_register_short_password(client):
    response = await client.post(
        "/auth/register",
        json={
            "username": "shortpwduser",
            "email": "shortpwd@example.com",
            "password": "abc",
        },
    )
    assert response.status_code == 422


async def test_login_success(client, registered_user):
    response = await client.post(
        "/auth/login",
        data={
            "username": registered_user["username"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password(client, registered_user):
    response = await client.post(
        "/auth/login",
        data={
            "username": registered_user["username"],
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401


async def test_login_unknown_user(client):
    response = await client.post(
        "/auth/login",
        data={
            "username": "nobody",
            "password": "password123",
        },
    )
    assert response.status_code == 401


async def test_protected_route_no_token(client):
    response = await client.get("/locations")
    assert response.status_code == 401


async def test_protected_route_invalid_token(client):
    response = await client.get("/locations", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401


async def test_hash_and_verify_password():
    from backend.auth import hash_password, verify_password

    hashed = hash_password("mysecretpassword")
    assert hashed != "mysecretpassword"
    assert verify_password("mysecretpassword", hashed) is True
    assert verify_password("wrongpassword", hashed) is False


async def test_create_access_token():
    from backend.auth import create_access_token

    token = create_access_token({"sub": "testuser"})
    assert isinstance(token, str)
    assert len(token) > 0
