from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth import get_current_user
from backend.database import get_db
from backend.models.location import LocationDB
from backend.models.user import UserDB
from backend.models.weather import WeatherRecordDB
from backend.schemas.weather import WeatherResponse
from backend.tasks.weather import fetch_weather_for_location

router = APIRouter(prefix="/weather", tags=["Weather"])


async def _get_owned_location(location_id: int, current_user: UserDB, db: AsyncSession) -> LocationDB:
    result = await db.execute(
        select(LocationDB).filter(LocationDB.id == location_id, LocationDB.user_id == current_user.id)
    )
    location = result.scalar_one_or_none()
    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return location


@router.get("/{location_id}", response_model=WeatherResponse)
async def get_latest_weather(
    location_id: int, db: AsyncSession = Depends(get_db), current_user: UserDB = Depends(get_current_user)
):
    await _get_owned_location(location_id, current_user, db)
    result = await db.execute(
        select(WeatherRecordDB)
        .filter(WeatherRecordDB.location_id == location_id)
        .order_by(WeatherRecordDB.recorded_at.desc())
        .limit(1)
    )
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=404, detail="No weather data available for this location")
    return record


@router.get("/{location_id}/history", response_model=list[WeatherResponse])
async def get_weather_history(
    location_id: int,
    limit: int = Query(default=30, ge=1, le=30, description="Number of days to return (1-30)"),
    db: AsyncSession = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    await _get_owned_location(location_id, current_user, db)

    result = await db.execute(
        select(WeatherRecordDB)
        .filter(WeatherRecordDB.location_id == location_id)
        .order_by(WeatherRecordDB.recorded_at.desc())
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{location_id}/fetch")
async def trigger_fetch(location_id: int):
    fetch_weather_for_location.delay(location_id)
    return {"message": "Weather fetch triggered"}
