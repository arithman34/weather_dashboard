from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from backend.celery_app import celery
from backend.config import settings
from backend.models.location import LocationDB
from backend.models.weather import WeatherRecordDB
from backend.services.weather import fetch_current_weather, get_coordinates

engine = create_engine(settings.sync_database_url)
SessionLocal = sessionmaker(bind=engine)


@celery.task(name="backend.tasks.weather.fetch_all_weather")
def fetch_all_weather() -> None:
    """Scheduled task - fetches weather for every location in the DB."""
    with SessionLocal() as db:
        locations = db.execute(select(LocationDB)).scalars().all()
        for location in locations:
            fetch_weather_for_location.delay(location.id)


@celery.task(name="backend.tasks.weather.fetch_weather_for_location")
def fetch_weather_for_location(location_id: int) -> None:
    with SessionLocal() as db:
        result = db.execute(select(LocationDB).filter(LocationDB.id == location_id))
        location = result.scalar_one_or_none()

        if location is None:
            return

        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        recent = db.execute(
            select(WeatherRecordDB)
            .filter(WeatherRecordDB.location_id == location_id)
            .filter(WeatherRecordDB.recorded_at >= one_hour_ago)
        ).scalar_one_or_none()

        if recent is not None:
            return

        latitude, longitude = get_coordinates(location.city, location.country)
        weather_data = fetch_current_weather(latitude, longitude)

        record = WeatherRecordDB(
            location_id=location_id,
            temperature=weather_data["temperature"],
            feels_like=weather_data["feels_like"],
            humidity=weather_data["humidity"],
            wind_speed=weather_data["wind_speed"],
            description=weather_data["description"],
        )
        db.add(record)
        db.commit()
