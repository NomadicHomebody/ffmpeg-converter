from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Manages application settings and loads them from a .env file."""
    API_KEY: str | None = None
    MAX_CONCURRENT_JOBS: int = 4

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
