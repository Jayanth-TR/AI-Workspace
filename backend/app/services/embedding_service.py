import json
import math
import logging
from typing import List, Optional
from openai import OpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating vector embeddings and computing vector similarity."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or getattr(settings, "OPENAI_API_KEY", "")
        self.client: Optional[OpenAI] = None
        if self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client in EmbeddingService: {e}")

    def generate_embedding(self, text: str, model: str = "text-embedding-3-small") -> List[float]:
        """Generate vector embedding for a single text prompt."""
        clean_text = text.strip() if text else ""
        if not clean_text or not self.client:
            return []

        try:
            res = self.client.embeddings.create(
                input=clean_text,
                model=model
            )
            return res.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return []

    def generate_embeddings_batch(self, texts: List[str], model: str = "text-embedding-3-small") -> List[List[float]]:
        """Generate vector embeddings for a batch of text chunks."""
        clean_texts = [t.strip() for t in texts if t and t.strip()]
        if not clean_texts or not self.client:
            return [[] for _ in texts]

        try:
            res = self.client.embeddings.create(
                input=clean_texts,
                model=model
            )
            return [item.embedding for item in res.data]
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            return [self.generate_embedding(t, model=model) for t in clean_texts]

    def cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """Compute cosine similarity between two vector embeddings."""
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))

        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0

        return dot_product / (norm_a * norm_b)
