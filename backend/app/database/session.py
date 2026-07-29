# pyrefly: ignore [missing-import]
from sqlalchemy.orm import sessionmaker
from app.database.database import engine

SessionLocal = sessionmaker(
    bind= engine, 
    autoflush=False,
    autocommit=False

)

