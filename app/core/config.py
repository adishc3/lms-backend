from pathlib import Path

from pydantic_settings import BaseSettings
from pydantic import ConfigDict

_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = _BACKEND_DIR / ".env"


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=str(ENV_FILE), extra="ignore")

    DATABASE_URL: str | None = None
    SECRET_KEY: str = "change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_USE_TLS: bool = False
    SMTP_USE_SSL: bool = False
    EMAIL_FROM: str = "noreply@example.com"
    EMAIL_ENABLED: bool = False

    AI_ENABLED: bool = False
    AI_PROVIDER_URL: str | None = None
    AI_API_KEY: str | None = None
    AI_DEFAULT_MODEL: str = "gpt-3.5-turbo"
    AI_TEMPERATURE: float = 0.5
    AI_TIMEOUT_SECONDS: int = 30

    TRUSTED_HOSTS: str = "localhost,127.0.0.1,testserver"
    FORCE_HTTPS: bool = False
    GZIP_MIN_SIZE: int = 1000

    UPLOAD_FOLDER: str = "static/uploads"
    UPLOAD_MAX_SIZE: int = 20_000_000

    # Cloudinary configuration
    CLOUDINARY_CLOUD_NAME: str | None = None
    CLOUDINARY_API_KEY: str | None = None
    CLOUDINARY_API_SECRET: str | None = None

    # Single sign-on / enterprise integration
    SSO_PROVIDER: str | None = None
    SSO_CLIENT_ID: str | None = None
    SSO_CLIENT_SECRET: str | None = None
    SSO_METADATA_URL: str | None = None

    # Localization / internationalization
    SUPPORTED_LOCALES: str = "en,es"
    DEFAULT_LOCALE: str = "en"

    # Rate limiting defaults (in-memory, per-IP, suitable for single-process deployments)
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    REDIS_URL: str | None = None

    # CORS - comma-separated list of allowed origins
    CORS_ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:5174,http://localhost:3000,https://learnatwill.vercel.app,https://learnatwill-9vr69ji77-adishc3s-projects.vercel.app"


def _parse_env_list(value: str | None, fallback: list[str]) -> list[str]:
    if value:
        return [item.strip() for item in value.split(",") if item.strip()]
    return fallback


settings = Settings()

if not settings.DATABASE_URL:
    settings.DATABASE_URL = "mysql+pymysql://root:password@db:3306/lms"

ALLOWED_ORIGINS: list[str] = [origin.strip() for origin in settings.CORS_ALLOWED_ORIGINS.split(",") if origin.strip()]


def get_settings() -> Settings:
    return settings
