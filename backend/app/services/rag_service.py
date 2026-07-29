import json
import logging
from typing import List, Dict, Any, Optional
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
# pyrefly: ignore [missing-import]
from sqlalchemy import select

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.user import User
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.services.file_service import FileService

logger = logging.getLogger(__name__)

embedding_service = EmbeddingService()
llm_service = LLMService()
file_service = FileService()


class RAGService:
    """Service for handling Knowledge Base / RAG queries using semantic vector search, LLM synthesis, and file generation."""

    def process_query(
        self,
        query: str,
        db: Optional[Session] = None,
        current_user: Optional[User] = None
    ) -> str:
        """Process RAG query by retrieving relevant chunks from user documents and synthesizing answer or generating files."""
        clean_query = query.strip() if query else ""
        if not clean_query:
            return "Please provide a valid question to query your Knowledge Base."

        # Query document chunks from database
        chunks_with_docs = []
        if db and current_user:
            statement = (
                select(DocumentChunk, Document)
                .join(Document, DocumentChunk.document_id == Document.id)
                .where(Document.user_id == current_user.id)
            )
            chunks_with_docs = db.execute(statement).all()
        elif db:
            statement = (
                select(DocumentChunk, Document)
                .join(Document, DocumentChunk.document_id == Document.id)
            )
            chunks_with_docs = db.execute(statement).all()

        if not chunks_with_docs:
            return (
                "📚 **Knowledge Base Empty**: No documents found in your Knowledge Base. "
                "Please upload documents (.pdf, .docx, or .txt) in the Knowledge Assistant section to enable RAG answers."
            )

        # Generate vector embedding for user query
        query_embedding = embedding_service.generate_embedding(clean_query)

        # Calculate similarity score for each chunk
        scored_chunks: List[Dict[str, Any]] = []
        for chunk, doc in chunks_with_docs:
            if not chunk.content:
                continue

            sim_score = 0.0
            if query_embedding and chunk.embedding:
                try:
                    chunk_vector = json.loads(chunk.embedding)
                    sim_score = embedding_service.cosine_similarity(query_embedding, chunk_vector)
                except Exception as e:
                    logger.warning(f"Failed to parse chunk embedding: {e}")
                    sim_score = 0.0

            # Fallback keyword match score if embedding fails or is absent
            if sim_score == 0.0:
                query_words = set(clean_query.lower().split())
                content_words = set(chunk.content.lower().split())
                common = query_words.intersection(content_words)
                if common:
                    sim_score = 0.05 * len(common)

            scored_chunks.append({
                "score": sim_score,
                "content": chunk.content,
                "document_name": doc.original_filename
            })

        # Sort chunks by relevance score in descending order
        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        top_chunks = [c for c in scored_chunks[:5] if c["score"] > 0.0]

        if not top_chunks:
            return f"No relevant content found in your Knowledge Base matching: *\"{clean_query}\"*."

        # Format Context and Source References
        context_blocks: List[str] = []
        source_docs = set()
        for idx, item in enumerate(top_chunks, 1):
            context_blocks.append(f"[{idx}] Source Document: {item['document_name']}\nContent: {item['content']}")
            source_docs.add(item['document_name'])

        formatted_context = "\n\n".join(context_blocks)

        # Synthesize Answer via LLM with structured Markdown instructions
        prompt = (
            f"User Question: {clean_query}\n\n"
            f"Retrieved Knowledge Base Context:\n{formatted_context}\n\n"
            f"Instructions:\n"
            f"1. Answer the user's question clearly, thoroughly, and accurately using ONLY the provided Knowledge Base context above.\n"
            f"2. Format your output into clean Markdown sections with headers (e.g., ## Overview, ## Key Solutions & Services, ## Key Features).\n"
            f"3. Use bullet points (- ) and bold formatting for important terms and highlights.\n"
            f"4. If the provided context does not contain enough information to answer the question, state that clearly."
        )

        try:
            ai_response = llm_service.generate_response([
                {"role": "system", "content": "You are a professional Knowledge Base AI assistant answering questions based on user uploaded documents with clean, beautifully formatted markdown output."},
                {"role": "user", "content": prompt}
            ])

            # Check if user explicitly requested file generation (Excel, PDF, Word)
            is_file_request = False
            req_type_data = llm_service.detect_request_type(clean_query)
            if isinstance(req_type_data, dict) and req_type_data.get("type") == "file":
                is_file_request = True
            elif any(kw in clean_query.lower() for kw in ["excel", "xlsx", "csv", "spreadsheet", "generate file", "create file", "export pdf", "generate pdf"]):
                is_file_request = True

            generated_file_ref = ""
            if is_file_request:
                try:
                    ft_data = llm_service.detect_file_type(clean_query)
                    target_ext = ft_data.get("file_type", "xlsx").strip().lower()

                    file_prompt = (
                        f"User File Request: {clean_query}\n\n"
                        f"Retrieved Knowledge Base Context:\n{formatted_context}\n\n"
                        f"Extract all relevant data from the Knowledge Base context to generate the requested file content."
                    )

                    file_result = None
                    if target_ext == "xlsx":
                        excel_data = llm_service.generate_excel_data(file_prompt)
                        if excel_data:
                            file_result = file_service.create_excel(excel_data)
                    elif target_ext == "docx":
                        docx_content = llm_service.generate_document_content(file_prompt)
                        file_result = file_service.create_word(docx_content)
                    elif target_ext == "pdf":
                        pdf_content = llm_service.generate_document_content(file_prompt)
                        file_result = file_service.create_pdf(pdf_content)

                    if file_result and "filename" in file_result:
                        generated_file_ref = f"\n\nsandbox:/{file_result['filename']}"
                except Exception as fe:
                    logger.error(f"Failed to generate file in RAGService: {fe}")

            sources_markdown = "\n".join([f"- 📄 `{doc}`" for doc in source_docs])
            return f"{ai_response.strip()}{generated_file_ref}\n\n---\n### 📄 **Source Documents**\n{sources_markdown}"

        except Exception as e:
            logger.error(f"Failed to generate RAG response: {e}", exc_info=True)
            sources_markdown = "\n".join([f"- 📄 `{doc}`" for doc in source_docs])
            return (
                f"Retrieved relevant content from your documents, but failed to synthesize response.\n\n"
                f"### 📄 **Source Documents**\n{sources_markdown}"
            )
