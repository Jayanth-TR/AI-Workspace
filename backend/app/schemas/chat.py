from pydantic import BaseModel
from app.schemas.message import ChatRequest, MessageCreate


class ChatCreate(BaseModel):
    title: str


__all__ = ["ChatCreate", "ChatRequest", "MessageCreate"]