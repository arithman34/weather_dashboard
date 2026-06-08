from datetime import datetime

from pydantic import BaseModel, Field


class WeatherResponse(BaseModel):
    id: int = Field(..., description="Unique identifier for the weather record", examples=[1])
    location_id: int = Field(
        ..., description="Identifier of the location associated with this weather record", examples=[1]
    )
    temperature: float = Field(..., description="Current temperature in Celsius", examples=[22.5])
    feels_like: float | None = Field(None, description="Feels like temperature in Celsius", examples=[21.0])
    humidity: int | None = Field(None, description="Current humidity percentage", examples=[60])
    wind_speed: float | None = Field(None, description="Current wind speed in m/s", examples=[5.0])
    description: str | None = Field(None, description="Weather description (e.g., 'clear sky')", examples=["clear sky"])
    recorded_at: datetime = Field(
        ..., description="Timestamp when the weather data was recorded", examples=["2026-01-01T00:00:00Z"]
    )

    model_config = {"from_attributes": True}
