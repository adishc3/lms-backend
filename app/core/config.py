try:
    from pydantic import BaseSettings, ConfigDict
except Exception:
    from pydantic_settings import BaseSettings
    from pydantic import ConfigDict


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "mysql+pymysql://root:password@db:3306/lms"
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

    # Rate limiting defaults (in-memory, per-IP, suitable for single-process deployments)
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    REDIS_URL: str | None = None


settings = Settings()
