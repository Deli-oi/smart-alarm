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
    fish_voice_id: str = "59b8d12e87724010a34190047391be4f"  # "F1", clear British; alt Alok b7204d4e40ef4a548c7c8547b7f73492
    api_token: str = "change-me"  # shared secret the iPhone app sends
    github_user: str = ""
    github_token: str = ""
    timezone: str = "America/New_York"
    debug: bool = False
    token_enc_key: str = ""  # Fernet key for stored OAuth tokens; keep it out of the database host
    store: str = "mongo"  # "memory" runs without Atlas, for local dev and UI testing
    cors_origins: str = "*"  # comma separated; bearer token still guards every data route
    ics_url: str = ""  # Google Calendar "secret address in iCal format"
    gmail_user: str = ""
    gmail_app_password: str = ""  # a Google app password, not the account password


@lru_cache
def get_settings() -> Settings:
    return Settings()
