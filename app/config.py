from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Admin
    admin_username: str = "admin"
    admin_password: str = "changeme"
    secret_key: str = "change-this-secret-key-in-production-min-32-chars"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # Storage
    originals_path: str = "./data/originals"
    media_path: str = "./data/media"
    zips_path: str = "./data/zips"
    db_path: str = "./data/db/gallery.db"

    # App
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False

    # Site defaults (overridden by DB settings at runtime)
    site_title: str = "Don Macaron Gallery"
    site_tagline: str = "Photography"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Ignore any extra keys in .env that aren't defined above
        # (e.g. HTTP_PORT used only by Docker Compose, not Python)
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
