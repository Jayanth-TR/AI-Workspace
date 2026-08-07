from typing import List
from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    HTTPException
)

# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from app.dependencies import (
    get_db,
    get_current_user
)

from app.models.user import User
from app.schemas.knowledge import UploadResponse, QueryRequest, QueryResponse
from app.services.knowledge_service import KnowledgeService
from app.services.rag_service import RAGService


router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge"]
)

knowledge_service = KnowledgeService()
rag_service = RAGService()


@router.post(
    "/upload",
    response_model=UploadResponse
)
def upload_document(
    file: UploadFile = File(...),
    is_global: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return knowledge_service.upload_document(
        db,
        file,
        current_user,
        is_global
    )


@router.post(
    "/query",
    response_model=QueryResponse
)
def query_knowledge_base(
    request: QueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    answer = rag_service.process_query(
        query=request.query,
        db=db,
        current_user=current_user
    )
    return {"answer": answer}


@router.get(
    "/documents",
    response_model=List[UploadResponse]
)
def get_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return knowledge_service.get_user_documents(db, current_user)


@router.delete(
    "/documents/{document_id}"
)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return knowledge_service.delete_document(db, document_id, current_user)