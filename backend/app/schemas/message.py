from pydantic import BaseModel, Field
from typing import Optional


class MessageCreate(BaseModel):
    content: Optional[str] = None
    message: Optional[str] = None
    mode: str = Field(default="chat", description="Mode: 'chat', 'web_search', or 'rag'")

    @property
    def text(self) -> str:
        if self.content is not None and self.content != "":
            return self.content
        if self.message is not None:
            return self.message
        return ""


# Alias for flexibility
ChatRequest = MessageCreate