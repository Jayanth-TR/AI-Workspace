from fastapi import APIRouter, Depends
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.message import MessageCreate
from app.services.message_service import MessageService


router = APIRouter(
    prefix="/chats",
    tags=["Messages"]
)

message_service = MessageService()


@router.post("/{chat_id}/messages")
def send_message(
    chat_id: int,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return message_service.send_message(
        db,
        chat_id,
        message_data,
        current_user
    )

@router.get("/{chat_id}/messages")
def get_messages(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return message_service.get_messages(
        db,
        chat_id,
        current_user
    )

@router.post("/messages")
def start_chat(
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return message_service.start_chat(
        db,
        message_data,
        current_user
    )