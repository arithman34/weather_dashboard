# Weather Dashboard

A full-stack weather tracking application. The backend is a FastAPI REST API with Celery background tasks that automatically fetch weather data every hour from [Open-Meteo](https://open-meteo.com/). The frontend is a Tkinter desktop app that consumes the API.

---

## Features

- Register and log in with JWT authentication
- Add locations by city and country code
- Automatic weather fetching every hour via Celery beat
- Manual weather fetch on demand
- Alert thresholds per location (min/max temperature)
- Weather history (up to 30 records per location)
- Welcome email on registration via Resend
- Full-screen Tkinter desktop frontend

---

## Project Structure

```
weather_dashboard/
├── .coveragerc
├── .dockerignore
├── .env.example
├── .gitignore
├── .vscode/
│   └── settings.json
├── alembic.ini
├── backend/
│   ├── __init__.py
│   ├── auth.py
│   ├── base.py
│   ├── celery_app.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── location.py
│   │   ├── user.py
│   │   └── weather.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── location.py
│   │   └── weather.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── location.py
│   │   ├── token.py
│   │   ├── user.py
│   │   └── weather.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── email.py
│   │   └── weather.py
│   └── tasks/
│       ├── __init__.py
│       ├── email.py
│       └── weather.py
├── docker-compose.yml
├── Dockerfile
├── entrypoint.sh
├── frontend/
│   ├── api.py
│   ├── components.py
│   ├── constants.py
│   ├── main.py
│   ├── page.py
│   ├── utils.py
│   └── views/
│       ├── dashboard.py
│       ├── edit_location.py
│       ├── login.py
│       ├── register.py
│       └── weather_history.py
├── LICENSE
├── migrations/
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions/
│       └── 5088cce11c00_initial_schema.py
├── pyproject.toml
├── pytest.ini
├── README.md
├── requirements.txt
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_auth.py
    ├── test_location.py
    ├── test_services.py
    ├── test_tasks.py
    └── test_weather.py
```

---

## Backend Setup

**Prerequisites:** Docker Desktop installed and running.

1. Create a `.env` file from the example and fill in your secrets:

    ```bash
    cp .env.example .env
    ```

    Then open `.env` and set `SECRET_KEY`, `RESEND_API_KEY`, and `FROM_EMAIL`.

2. Build and start all services:

    ```bash
    docker compose up --build
    ```

3. Run migrations (first time only):

    ```bash
    docker compose exec backend alembic upgrade head
    ```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

To stop:

```bash
docker compose down
```

---

## Frontend Setup

The frontend is a Tkinter desktop app and must always be run locally.

**Prerequisites:** Python 3.12+, backend running via Docker.

1. With your virtual environment active, run:

    ```bash
    python -m frontend.main
    ```

The app opens full-screen. Press `Escape` to close.

> `BASE_URL` in `frontend/api.py` defaults to `http://localhost:8000`. If your backend runs on a different port, update it there.

---

## Running Tests

Tests use a separate `weather_dashboard_test` database. Make sure the database service is running before executing the suite.

```bash
docker compose up db -d
pytest
```

Coverage reports are written to `htmlcov/`. Open `htmlcov/index.html` in a browser to view line-by-line coverage.

---

## Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | Async PostgreSQL URL (`postgresql+asyncpg://...`) |
| `SYNC_DATABASE_URL` | Sync PostgreSQL URL for Celery worker (`postgresql://...`) |
| `SECRET_KEY` | Secret used to sign JWTs |
| `REDIS_URL` | Redis connection URL |
| `RESEND_API_KEY` | API key from [resend.com](https://resend.com) |
| `FROM_EMAIL` | Sender address (use `onboarding@resend.dev` on the free tier) |

---

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI, Uvicorn |
| Database | PostgreSQL, SQLAlchemy (async), Alembic |
| Auth | JWT (python-jose), bcrypt (passlib) |
| Background tasks | Celery, Redis |
| Email | Resend |
| Weather data | Open-Meteo (no API key required) |
| Testing | pytest, pytest-asyncio, httpx, pytest-cov |
| Frontend | Tkinter, httpx |
| Containerisation | Docker, Docker Compose |
