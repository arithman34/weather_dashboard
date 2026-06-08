def test_register_success(client):
    response = client.post(
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


def test_register_duplicate_username(client, registered_user):
    response = client.post(
        "/auth/register",
        json={
            "username": registered_user["username"],
            "email": "other@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 400


def test_register_duplicate_email(client, registered_user):
    response = client.post(
        "/auth/register",
        json={
            "username": "otherusername",
            "email": "testuser@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 400


def test_register_short_password(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "shortpwduser",
            "email": "shortpwd@example.com",
            "password": "abc",
        },
    )
    assert response.status_code == 422


def test_login_success(client, registered_user):
    response = client.post(
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


def test_login_wrong_password(client, registered_user):
    response = client.post(
        "/auth/login",
        data={
            "username": registered_user["username"],
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401


def test_login_unknown_user(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "nobody",
            "password": "password123",
        },
    )
    assert response.status_code == 401
