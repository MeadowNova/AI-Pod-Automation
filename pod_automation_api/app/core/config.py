from typing import List, Optional, Union, Annotated
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "POD AI Automation API"
    DESCRIPTION: str = "API for Etsy POD sellers automation platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # CORS
    BACKEND_CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"

    @property
    def CORS_ORIGINS(self) -> List[str]:
        """
        Get the CORS origins as a list.
        """
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",") if origin.strip()]

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    # JWT
    JWT_SECRET: str = "CHANGE_ME_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Etsy API
    ETSY_CLIENT_ID: str = ""
    ETSY_CLIENT_SECRET: str = ""
    ETSY_REDIRECT_URI: str = "http://localhost:8000/api/v1/etsy/callback"

    # Stripe
    STRIPE_API_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # AI Model
    AI_MODEL_HOST: str = "http://localhost:11434"
    AI_MODEL_NAME: str = "qwen3:8b"

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra="ignore"
    )


settings = Settings()
