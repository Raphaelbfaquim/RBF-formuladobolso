from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Aplicação
    APP_NAME: str = "FormuladoBolso"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # API
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Banco de Dados
    DATABASE_URL: str
    DATABASE_SYNC_URL: str

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    # CORS - aceita string ou lista
    CORS_ORIGINS: str | List[str] = "http://localhost:3000,http://localhost:8000"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Converter CORS_ORIGINS para lista se for string
        if isinstance(self.CORS_ORIGINS, str):
            if self.CORS_ORIGINS == "*":
                self.CORS_ORIGINS = ["*"]
            else:
                # Separar por vírgula se houver múltiplos valores
                self.CORS_ORIGINS = [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Permitir campos extras do .env


settings = Settings()

