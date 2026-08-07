from datetime import datetime

# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import relationship

from app.database.base import Base


class Document(Base):

    __tablename__ = "documents"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    original_filename = Column(
        String,
        nullable=False
    )

    stored_filename = Column(
        String,
        nullable=False,
        unique=True
    )

    file_type = Column(
        String,
        nullable=False
    )

    file_path = Column(
        String,
        nullable=False
    )

    extracted_text = Column(
        Text,
        nullable=True
    )
    chunks = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    is_global = Column(
        Boolean,
        default=False,
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="documents"
    )