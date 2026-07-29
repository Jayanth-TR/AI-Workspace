from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.core.config import settings
from app.database.base import Base
# pyrefly: ignore [missing-import]
from app.database.database import engine
from app.models import *
from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.message import router as message_router
from app.api.file import router as file_router
from app.api.knowledge import router as knowledge_router


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(message_router)
app.include_router(file_router)
app.include_router(knowledge_router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE document_chunks ADD COLUMN IF NOT EXISTS embedding TEXT;"))
            conn.commit()
    except Exception as e:
        print(f"Startup schema migration check: {e}")


@app.get("/")
def root():
    return {
        "message": "Welcome to AI workspace"
    }
