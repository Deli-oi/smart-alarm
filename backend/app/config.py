from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Backend settings, read from environment variables or backend/.env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "smart_alarm"
    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-5-5"
    fish_api_key: str = ""
    api_token: str = "change-me"  # shared secret the iPhone app sends
    timezone: str = "America/New_York"


@lru_cache
def get_settings() -> Settings:
    return Settings()
