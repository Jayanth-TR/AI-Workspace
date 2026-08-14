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
from app.services.vector_db_service import ChromaDBService

logger = logging.getLogger(__name__)

embedding_service = EmbeddingService()
llm_service = LLMService()
file_service = FileService()
vector_db = ChromaDBService()


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

        if not current_user:
            return "You must be logged in to query the Knowledge Base."
            
        # Generate vector embedding for user query
        query_embedding = embedding_service.generate_embedding(clean_query)
        if not query_embedding:
            return "Failed to generate embedding for query."

        # Search ChromaDB
        scored_chunks = vector_db.search_embeddings(
            query_embedding=query_embedding,
            user_id=current_user.id,
            top_k=5
        )

        # Enforce similarity threshold to discard irrelevant chunks (score >= 0.35)
        RELEVANCE_THRESHOLD = 0.35
        top_chunks = [c for c in scored_chunks if c.get("score", 0.0) >= RELEVANCE_THRESHOLD]

        if not top_chunks:
            # Fallback to general LLM answer if no relevant documents match
            try:
                fallback_response = llm_service.generate_response([
                    {"role": "system", "content": "You are a helpful AI assistant. The user queried the Knowledge Base, but no relevant content matching their question was found in their uploaded documents. Briefly inform the user that their uploaded documents do not contain relevant information for this query, and then provide a clear, accurate answer using general knowledge."},
                    {"role": "user", "content": clean_query}
                ])
                return f"ℹ️ *Note: No relevant information was found in your uploaded Knowledge Base documents for this query. Answering based on general AI knowledge:*\n\n{fallback_response.strip()}"
            except Exception as fe:
                logger.error(f"Fallback response generation failed: {fe}")
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
            f"1. Answer the user's question clearly, thoroughly, and accurately using the provided Knowledge Base context above.\n"
            f"2. If the context is relevant, prioritize it. If the context is missing specific details, state what the documents cover and answer using general knowledge clearly.\n"
            f"3. Do NOT make up false definitions or hallucinate acronym meanings from unrelated document text.\n"
            f"4. Format your output into clean Markdown sections with headers (e.g., ## Overview, ## Key Solutions & Services, ## Key Features).\n"
            f"5. Use bullet points (- ) and bold formatting for important terms and highlights."
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
