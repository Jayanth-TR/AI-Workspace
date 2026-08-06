import os
# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "AI Workspace API"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    SECRET_KEY: str = "qwerttrewq"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    DATABASE_URL: str = ""

    OPENAI_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

# Fix DATABASE_URL for Render & cloud deployments
if not settings.DATABASE_URL or "localhost" in settings.DATABASE_URL and not os.getenv("DATABASE_URL"):
    settings.DATABASE_URL = "sqlite:///./ai_workspace.db"
elif settings.DATABASE_URL.startswith("postgres://"):
    settings.DATABASE_URL = settings.DATABASE_URL.replace("postgres://", "postgresql://", 1)