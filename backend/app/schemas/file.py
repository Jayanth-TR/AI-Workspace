from pydantic import BaseModel


class FileGenerateRequest(BaseModel):
    prompt: str
    