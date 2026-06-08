from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str = Field(
        ..., description="JWT access token for authentication", examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )
    token_type: str = Field(..., description="Type of the token (e.g., 'bearer')", examples=["bearer"])


class TokenData(BaseModel):
    username: str | None = Field(None, description="Username extracted from the token", examples=["john_doe"])
