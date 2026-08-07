import os
import logging
from typing import List, Dict, Any, Optional
# pyrefly: ignore [missing-import]
import chromadb

logger = logging.getLogger(__name__)

class ChromaDBService:
    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "ai_workspace_knowledge"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        
        try:
            # Initialize persistent client
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"} # Use cosine similarity matching
            )
            logger.info(f"Initialized ChromaDB at {self.persist_directory} with collection {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise e
            
    def add_embeddings(self, 
                      user_id: int,
                      document_id: int, 
                      document_name: str,
                      chunks: List[str], 
                      embeddings: List[List[float]],
                      chunk_indices: List[int],
                      is_global: bool = False):
        """Adds document chunks and their embeddings to ChromaDB."""
        if not self.collection:
            logger.error("ChromaDB collection is not initialized.")
            return False
            
        if not chunks or not embeddings or len(chunks) != len(embeddings):
            logger.warning("Invalid chunks or embeddings provided to ChromaDB.")
            return False
            
        try:
            ids = []
            metadatas = []
            documents = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"user_{user_id}_doc_{document_id}_chunk_{chunk_indices[i]}"
                ids.append(chunk_id)
                documents.append(chunk)
                metadatas.append({
                    "user_id": user_id,
                    "document_id": document_id,
                    "document_name": document_name,
                    "chunk_index": chunk_indices[i],
                    "is_global": is_global
                })
                
            self.collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            return True
        except Exception as e:
            logger.error(f"Failed to add embeddings to ChromaDB: {e}")
            return False
            
    def search_embeddings(self, query_embedding: List[float], user_id: int, top_k: int = 5) -> List[Dict[str, Any]]:
        """Searches ChromaDB for the most similar chunks for a specific user."""
        if not self.collection:
            logger.error("ChromaDB collection is not initialized.")
            return []
            
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where={
                    "$or": [
                        {"user_id": user_id},
                        {"is_global": True}
                    ]
                },
                include=["documents", "metadatas", "distances"]
            )
            
            scored_chunks = []
            if results and results['documents'] and len(results['documents']) > 0:
                docs = results['documents'][0]
                metadatas = results['metadatas'][0]
                distances = results['distances'][0] if 'distances' in results and results['distances'] else []
                
                for i in range(len(docs)):
                    # ChromaDB distance for cosine is (1 - cosine_similarity).
                    sim_score = 1.0 - distances[i] if distances and i < len(distances) else 0.0
                    
                    scored_chunks.append({
                        "score": sim_score,
                        "content": docs[i],
                        "document_name": metadatas[i].get("document_name", "Unknown Document")
                    })
                    
            # Sort by score descending
            scored_chunks.sort(key=lambda x: x["score"], reverse=True)
            return scored_chunks
            
        except Exception as e:
            logger.error(f"Failed to search ChromaDB: {e}")
            return []
            
    def delete_document(self, user_id: int, document_id: int):
        """Deletes all chunks for a specific document from ChromaDB."""
        if not self.collection:
            return False
            
        try:
            # We must use where clause to delete based on metadata
            self.collection.delete(
                where={
                    "$and": [
                        {"user_id": user_id},
                        {"document_id": document_id}
                    ]
                }
            )
            return True
        except Exception as e:
            logger.error(f"Failed to delete document from ChromaDB: {e}")
            return False
