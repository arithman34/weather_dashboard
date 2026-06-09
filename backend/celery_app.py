from celery import Celery

from backend.config import settings

celery = Celery(
    "weather_dashboard",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["backend.tasks.weather", "backend.tasks.email"],
)

celery.conf.beat_schedule = {
    "fetch-weather-every-hour": {
        "task": "backend.tasks.weather.fetch_all_weather",
        "schedule": 3600.0,
    }
}
