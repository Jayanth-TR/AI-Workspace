import logging
from app.core.config import settings
# pyrefly: ignore [missing-import]
from sqlalchemy import create_engine

logger = logging.getLogger(__name__)

db_url = settings.DATABASE_URL or "sqlite:///./ai_workspace.db"

if db_url.startswith("sqlite"):
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    try:
        engine = create_engine(db_url, echo=False)
        with engine.connect() as conn:
            pass
    except Exception as e:
        logger.warning(f"Database connection to {db_url} failed ({e}). Falling back to SQLite database.")
        fallback_url = "sqlite:///./ai_workspace.db"
        engine = create_engine(
            fallback_url,
            connect_args={"check_same_thread": False},
            echo=False
        )