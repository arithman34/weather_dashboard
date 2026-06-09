from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    sync_database_url: str
    secret_key: str
    resend_api_key: str
    from_email: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    redis_url: str = "redis://localhost:6379/0"

    model_config = {"env_file": ".env"}


settings = Settings()
