import os
import json
from uuid import uuid4

from fastapi import UploadFile, HTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
# pyrefly: ignore [missing-import]
from sqlalchemy import select

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.user import User
from app.services.document_parser_service import DocumentParserService
from app.services.chunk_service import ChunkService
from app.services.embedding_service import EmbeddingService


parser_service = DocumentParserService()
chunk_service = ChunkService()
embedding_service = EmbeddingService()


class KnowledgeService:

    def upload_document(
        self,
        db: Session,
        file: UploadFile,
        current_user: User
    ):
        # Create upload folder
        os.makedirs(
            "uploaded_documents",
            exist_ok=True
        )

        # Get extension
        extension = file.filename.split(".")[-1].lower()

        # Validate file type
        allowed_types = ["pdf", "docx", "txt", "xlsx", "xls", "csv"]

        if extension not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="Only PDF, DOCX, TXT, XLSX, and CSV files are supported."
            )

        # Generate unique filename
        stored_filename = f"{uuid4()}.{extension}"

        # File path
        file_path = os.path.join(
            "uploaded_documents",
            stored_filename
        )

        # Save file
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        # Extract text
        extracted_text = parser_service.extract_text(
            file_path=file_path,
            file_type=extension
        )

        # Create chunks
        chunks = chunk_service.create_chunks(extracted_text)

        # Generate vector embeddings for chunks
        embeddings = embedding_service.generate_embeddings_batch(chunks) if chunks else []

        # Save document metadata
        document = Document(
            user_id=current_user.id,
            original_filename=file.filename,
            stored_filename=stored_filename,
            file_type=extension,
            file_path=file_path,
            extracted_text=extracted_text
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        # Save chunks with serialized embedding JSON
        for i, chunk_text in enumerate(chunks):
            emb_vector = embeddings[i] if i < len(embeddings) else []
            chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=i,
                content=chunk_text,
                embedding=json.dumps(emb_vector) if emb_vector else None
            )
            db.add(chunk)

        db.commit()
        db.refresh(document)

        return document

    def get_user_documents(self, db: Session, current_user: User):
        """Fetch all uploaded documents for the logged in user."""
        statement = (
            select(Document)
            .where(Document.user_id == current_user.id)
            .order_by(Document.created_at.desc())
        )
        return db.execute(statement).scalars().all()

    def delete_document(self, db: Session, document_id: int, current_user: User):
        """Delete an uploaded document and its chunks."""
        statement = select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
        doc = db.execute(statement).scalar_one_or_none()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if doc.file_path and os.path.exists(doc.file_path):
            try:
                os.remove(doc.file_path)
            except Exception:
                pass

        db.delete(doc)
        db.commit()
        return {"message": "Document deleted successfully"}