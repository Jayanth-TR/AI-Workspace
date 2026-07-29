# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
# pyrefly: ignore [missing-import]
from sqlalchemy import select, delete
from app.models.chat import Chat
from app.models.user import User
from app.schemas.chat import ChatCreate


class ChatService:

    def create_chat(
        self,
        db: Session,
        chat_data: ChatCreate,
        current_user: User
    ):
        chat = Chat(
            title=chat_data.title,
            user_id=current_user.id
        )

        db.add(chat)
        db.commit()
        db.refresh(chat)

        return chat

    def get_user_chats(
        self,
        db: Session,
        current_user: User
    ):
        statement = (
            select(Chat)
            .where(Chat.user_id == current_user.id)
            .order_by(Chat.created_at.desc())
        )

        chats = db.execute(
            statement
        ).scalars().all()

        return chats

    def delete_chat(
        self,
        db: Session,
        chat_id: int,
        current_user: User
    ):
        statement = (
            select(Chat)
            .where(Chat.id == chat_id, Chat.user_id == current_user.id)
        )
        chat = db.execute(statement).scalar_one_or_none()
        if not chat:
            return False

        # Cascade delete message records first
        from app.models.message import Message
        db.execute(
            delete(Message)
            .where(Message.chat_id == chat_id)
        )

        db.delete(chat)
        db.commit()
        return True
