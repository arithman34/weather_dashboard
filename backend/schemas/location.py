from datetime import datetime

from pydantic import BaseModel, Field


class LocationCreate(BaseModel):
    city: str = Field(..., description="City name for the location", examples=["London", "New York"])
    country: str = Field(..., description="Country name for the location", examples=["UK", "USA"])
    alert_threshold_max: float | None = Field(
        None, description="Maximum temperature threshold for alerts", examples=[30.0]
    )
    alert_threshold_min: float | None = Field(
        None, description="Minimum temperature threshold for alerts", examples=[0.0]
    )
    alert_enabled: bool = Field(False, description="Whether alerts are enabled for this location", examples=[True])


class LocationUpdate(BaseModel):
    alert_threshold_max: float | None = Field(
        None, description="Maximum temperature threshold for alerts", examples=[30.0]
    )
    alert_threshold_min: float | None = Field(
        None, description="Minimum temperature threshold for alerts", examples=[0.0]
    )
    alert_enabled: bool | None = Field(
        None, description="Whether alerts are enabled for this location", examples=[True]
    )


class LocationResponse(BaseModel):
    id: int = Field(..., description="Unique identifier for the location", examples=[1])
    user_id: int = Field(..., description="Identifier of the user who owns this location", examples=[1])
    city: str = Field(..., description="City name for the location", examples=["London"])
    country: str = Field(..., description="Country name for the location", examples=["UK"])
    alert_threshold_max: float | None = Field(
        None, description="Maximum temperature threshold for alerts", examples=[30.0]
    )
    alert_threshold_min: float | None = Field(
        None, description="Minimum temperature threshold for alerts", examples=[0.0]
    )
    alert_enabled: bool = Field(..., description="Whether alerts are enabled for this location", examples=[True])
    created_at: datetime = Field(
        ..., description="Timestamp when the location was created", examples=["2026-01-01T00:00:00Z"]
    )

    model_config = {"from_attributes": True}
