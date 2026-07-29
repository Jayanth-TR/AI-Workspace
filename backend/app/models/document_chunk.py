from datetime import datetime

# pyrefly: ignore [missing-import]
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Text,
    DateTime
)

# pyrefly: ignore [missing-import]
from sqlalchemy.orm import relationship

from app.database.base import Base


class DocumentChunk(Base):

    __tablename__ = "document_chunks"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    document_id = Column(
        Integer,
        ForeignKey("documents.id"),
        nullable=False
    )

    chunk_index = Column(
        Integer,
        nullable=False
    )

    content = Column(
        Text,
        nullable=False
    )

    embedding = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    document = relationship(
        "Document",
        back_populates="chunks"
    )