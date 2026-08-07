from pydantic import BaseModel


class UploadResponse(BaseModel):

    id: int

    original_filename: str

    stored_filename: str

    file_type: str

    is_global: bool

    class Config:
        from_attributes = True


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str