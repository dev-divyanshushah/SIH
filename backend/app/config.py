from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./persist_air.db"
    SECRET_KEY: str = "persist-air-dev-secret"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    ML_SERVICE_URL: str = "http://localhost:8001"
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"

settings = Settings()
