from app.core.config import settings
# pyrefly: ignore [missing-import]
from sqlalchemy import create_engine

engine = create_engine(
    settings.DATABASE_URL,
    echo= True
)