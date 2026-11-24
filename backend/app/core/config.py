"""Application configuration loaded from the environment."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings. Values come from the environment or a local .env file."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    database_url: str = "sqlite+aiosqlite:///./dev.db"

    jwt_secret: str = "change-me-in-dev"
    jwt_algorithm: str = "HS256"
    access_token_ttl_minutes: int = 15
    refresh_token_ttl_days: int = 14

    cookie_secure: bool = False

    # Password-reset email delivery (F-022). The link points at the frontend,
    # so the public site origin must be configured per environment.
    frontend_base_url: str = "http://127.0.0.1:5173"
    password_reset_ttl_minutes: int = 30
    password_reset_resend_seconds: int = 60

    # SMTP relay. Any provider (Resend, Mailgun, Postmark, Gmail) works; when
    # ``smtp_host`` is empty the API reports EMAIL_NOT_CONFIGURED instead of
    # pretending an email was sent.
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_from_name: str = "روتین کده"
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings instance."""
    return Settings()
