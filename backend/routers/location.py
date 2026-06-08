from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.models.location import LocationDB
from backend.models.user import UserDB
from backend.schemas.location import LocationCreate, LocationResponse, LocationUpdate

router = APIRouter(prefix="/locations", tags=["Locations"])


@router.get("", response_model=list[LocationResponse])
def get_locations(db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    return db.query(LocationDB).filter(LocationDB.user_id == current_user.id).all()


@router.post("", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
def create_location(
    location_data: LocationCreate, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)
):
    location = LocationDB(
        user_id=current_user.id,
        city=location_data.city,
        country=location_data.country,
        alert_threshold_max=location_data.alert_threshold_max,
        alert_threshold_min=location_data.alert_threshold_min,
        alert_enabled=location_data.alert_enabled,
    )
    db.add(location)
    db.commit()
    db.refresh(location)
    return location


@router.put("/{location_id}", response_model=LocationResponse)
def update_location(
    location_id: int,
    update_data: LocationUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    location = db.query(LocationDB).filter(LocationDB.id == location_id, LocationDB.user_id == current_user.id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(location, field, value)

    db.commit()
    db.refresh(location)
    return location


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(location_id: int, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    location = db.query(LocationDB).filter(LocationDB.id == location_id, LocationDB.user_id == current_user.id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    db.delete(location)
    db.commit()
