import os

os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:postgres@localhost:5432/weather_dashboard_test"
os.environ["SYNC_DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/weather_dashboard_test"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["RESEND_API_KEY"] = "test-resend-key"
os.environ["FROM_EMAIL"] = "test@example.com"

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from unittest.mock import MagicMock, patch

from backend.base import Base
from backend.celery_app import celery as celery_app
from backend.database import get_db
from backend.main import app

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL environment variable is not set")

engine = create_async_engine(DATABASE_URL, poolclass=NullPool)
TestingAsyncSessionLocal = async_sessionmaker(engine, autocommit=False, autoflush=False, expire_on_commit=False)

celery_app.conf.update(task_always_eager=True, task_eager_propagates=False)


@pytest.fixture(autouse=True)
def mock_external_services():
    with patch("backend.services.email.resend.Emails.send"), \
         patch("backend.tasks.weather.get_coordinates", return_value=(51.5, -0.1)), \
         patch("backend.tasks.weather.fetch_current_weather", return_value={
             "temperature": 15.0, "feels_like": 13.0, "humidity": 70,
             "wind_speed": 10.0, "description": "Partly cloudy",
         }):
        yield


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture()
async def db():
    async with TestingAsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture()
async def client(db):
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture()
async def registered_user(client):
    await client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "password123",
        },
    )
    return {"username": "testuser", "password": "password123"}


@pytest_asyncio.fixture()
async def auth_headers(client, registered_user):
    response = await client.post(
        "/auth/login",
        data={
            "username": registered_user["username"],
            "password": registered_user["password"],
        },
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
