import os
import json
from uuid import uuid4

from fastapi import UploadFile, HTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
# pyrefly: ignore [missing-import]
from sqlalchemy import select, or_

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.user import User
from app.services.document_parser_service import DocumentParserService
from app.services.chunk_service import ChunkService
from app.services.embedding_service import EmbeddingService
from app.services.vector_db_service import ChromaDBService


parser_service = DocumentParserService()
chunk_service = ChunkService()
embedding_service = EmbeddingService()
vector_db = ChromaDBService()


class KnowledgeService:

    def upload_document(
        self,
        db: Session,
        file: UploadFile,
        current_user: User,
        is_global: bool = False
    ):
        from app.core.config import settings
        
        if is_global and current_user.email != settings.ADMIN_EMAIL:
            raise HTTPException(
                status_code=403,
                detail="Only administrators can upload global company documents."
            )

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

        # Save file temporarily
        file_bytes = file.file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(file_bytes)

        # Extract text
        extracted_text = parser_service.extract_text(
            file_path=file_path,
            file_type=extension
        )

        # Create chunks
        chunks = chunk_service.create_chunks(extracted_text)

        # Generate vector embeddings for chunks
        embeddings = embedding_service.generate_embeddings_batch(chunks) if chunks else []

        from app.storage.supabase_client import upload_file_to_supabase, supabase_client
        from app.core.config import settings

        if supabase_client:
            supabase_path = f"documents/{current_user.id}/{stored_filename}"
            upload_file_to_supabase(settings.SUPABASE_BUCKET, supabase_path, file_bytes, file.content_type)
            if os.path.exists(file_path):
                os.remove(file_path)
            file_path = supabase_path

        # Save document metadata
        document = Document(
            user_id=current_user.id,
            original_filename=file.filename,
            stored_filename=stored_filename,
            file_type=extension,
            file_path=file_path,
            extracted_text=extracted_text,
            is_global=is_global
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        # Save chunks without serialized embedding JSON
        chunk_indices = []
        for i, chunk_text in enumerate(chunks):
            chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=i,
                content=chunk_text,
                embedding=None
            )
            db.add(chunk)
            chunk_indices.append(i)

        db.commit()
        db.refresh(document)
        
        # Add to Vector DB
        if chunks and embeddings:
            vector_db.add_embeddings(
                user_id=current_user.id,
                document_id=document.id,
                document_name=document.original_filename,
                chunks=chunks,
                embeddings=embeddings,
                chunk_indices=chunk_indices,
                is_global=is_global
            )

        return document

    def get_user_documents(self, db: Session, current_user: User):
        """Fetch all uploaded documents for the logged in user, plus global company documents."""
        statement = (
            select(Document)
            .where(or_(Document.user_id == current_user.id, Document.is_global == True))
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

        if doc.file_path:
            from app.storage.supabase_client import delete_file_from_supabase, supabase_client
            from app.core.config import settings
            if supabase_client and doc.file_path.startswith("documents/"):
                try:
                    delete_file_from_supabase(settings.SUPABASE_BUCKET, doc.file_path)
                except Exception:
                    pass
            elif os.path.exists(doc.file_path):
                try:
                    os.remove(doc.file_path)
                except Exception:
                    pass

        db.delete(doc)
        db.commit()
        
        # Also delete from Vector DB
        vector_db.delete_document(user_id=current_user.id, document_id=document_id)
        
        return {"message": "Document deleted successfully"}