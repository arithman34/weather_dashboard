from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    username: str = Field(
        ..., min_length=3, max_length=50, description="Unique username for the user", examples=["john_doe"]
    )
    email: EmailStr = Field(..., description="User's email address", examples=["john@example.com"])
    password: str = Field(..., description="Password for the user account", examples=["password123"])

    @field_validator("password")
    @classmethod
    def password_min_length(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        return value


class UserResponse(BaseModel):
    id: int = Field(..., description="Unique identifier for the user", examples=[1])
    username: str = Field(..., description="Unique username for the user", examples=["john_doe"])
    email: str = Field(..., description="User's email address", examples=["john@example.com"])
    is_active: bool = Field(..., description="Whether the user account is active", examples=[True])
    created_at: datetime = Field(
        ..., description="Timestamp when the user account was created", examples=["2026-01-01T12:00:00Z"]
    )

    model_config = {"from_attributes": True}
