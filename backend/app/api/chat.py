from fastapi import APIRouter, Depends, HTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.chat import ChatCreate
from app.services.chat_service import ChatService


router = APIRouter(
    prefix="/chats",
    tags=["Chats"]
)

chat_service = ChatService()


@router.post("/")
def create_chat(
    chat_data: ChatCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return chat_service.create_chat(
        db,
        chat_data,
        current_user
    )

@router.get("/")
def get_chats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return chat_service.get_user_chats(
        db,
        current_user
    )

@router.delete("/{chat_id}")
def delete_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    success = chat_service.delete_chat(
        db,
        chat_id,
        current_user
    )
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Chat not found or unauthorized"
        )
    return {"message": "Chat deleted successfully"}