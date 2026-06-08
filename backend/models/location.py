from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.database import Base


class LocationDB(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)
    alert_threshold_max = Column(Float, nullable=True)
    alert_threshold_min = Column(Float, nullable=True)
    alert_enabled = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("UserDB", back_populates="locations")
    weather_records = relationship("WeatherRecordDB", back_populates="location", cascade="all, delete-orphan")
