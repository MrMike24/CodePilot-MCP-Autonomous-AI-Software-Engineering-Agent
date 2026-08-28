import hashlib
import math
from typing import Protocol
from backend.app.core.config import settings
from backend.app.core.logging import logger

EMBEDDING_DIMENSION = 1536


class EmbeddingProvider(Protocol):
    def embed_text(self, text: str) -> list[float]:
        ...

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        ...


class LocalFeatureEmbeddingProvider:
    """Deterministic 1536-dimensional feature embedding generator for offline/demo/testing RAG."""

    def __init__(self, dimension: int = EMBEDDING_DIMENSION):
        self.dimension = dimension

    def embed_text(self, text: str) -> list[float]:
        vec = [0.0] * self.dimension
        words = text.lower().split()
        if not words:
            return vec

        for word in words:
            # Hash word to index
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dimension
            val = (h % 1000) / 1000.0
            vec[idx] += val

        # Normalize L2
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_text(t) for t in texts]


def get_embedding_provider() -> EmbeddingProvider:
    """Factory function returning active embedding provider."""
    return LocalFeatureEmbeddingProvider()
