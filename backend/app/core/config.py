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

    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: str = ""

    FRONTEND_URL: str = "http://localhost:5173"
    ADMIN_EMAIL: str = "admin@company.com"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

# Configure DATABASE_URL for AWS RDS PostgreSQL & local fallbacks
if not settings.DATABASE_URL:
    settings.DATABASE_URL = "sqlite:///./ai_workspace.db"
elif settings.DATABASE_URL.startswith("postgres://"):
    settings.DATABASE_URL = settings.DATABASE_URL.replace("postgres://", "postgresql://", 1)