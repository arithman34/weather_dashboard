from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.models.location import LocationDB
from backend.models.user import UserDB
from backend.models.weather import WeatherRecordDB
from backend.schemas.weather import WeatherResponse

router = APIRouter(prefix="/weather", tags=["Weather"])


def _get_owned_location(location_id: int, current_user: UserDB, db: Session) -> LocationDB:
    location = (
        db.query(LocationDB)
        .filter(
            LocationDB.id == location_id,
            LocationDB.user_id == current_user.id,
        )
        .first()
    )
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location


@router.get("/{location_id}", response_model=WeatherResponse)
def get_latest_weather(
    location_id: int, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)
):
    _get_owned_location(location_id, current_user, db)

    record = (
        db.query(WeatherRecordDB)
        .filter(WeatherRecordDB.location_id == location_id)
        .order_by(WeatherRecordDB.recorded_at.desc())
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="No weather data available for this location")
    return record


@router.get("/{location_id}/history", response_model=list[WeatherResponse])
def get_weather_history(
    location_id: int,
    limit: int = Query(default=30, ge=1, le=60, description="Number of records to return (1-60)"),
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    _get_owned_location(location_id, current_user, db)

    return (
        db.query(WeatherRecordDB)
        .filter(WeatherRecordDB.location_id == location_id)
        .order_by(WeatherRecordDB.recorded_at.desc())
        .limit(limit)
        .all()
    )
