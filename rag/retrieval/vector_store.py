import math
from typing import Any
from backend.app.core.config import settings
from backend.app.core.logging import logger
from rag.embeddings.provider import EMBEDDING_DIMENSION, get_embedding_provider
from rag.ingestion.walk import RepositoryWalker
from rag.parsing.splitter import CodeChunk, CodeSplitter


def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


class CodeRAGStore:
    """Hybrid Code-aware Retrieval Store managing index building and vector retrieval."""

    def __init__(self, collection_name: str = settings.QDRANT_COLLECTION_NAME):
        self.collection_name = collection_name
        self.embedding_provider = get_embedding_provider()
        self.splitter = CodeSplitter()
        # In-memory vector cache for resilient zero-dependency execution
        self._index: list[dict[str, Any]] = []

    def index_repository(self, repo_path: str) -> int:
        """Walk repository, split into chunks, embed, and store vectors."""
        walker = RepositoryWalker(repo_path)
        chunks: list[CodeChunk] = []

        for file_path, content in walker.walk_source_files():
            file_chunks = self.splitter.split_file(file_path, content, walker.repo_path)
            chunks.extend(file_chunks)

        if not chunks:
            logger.warning(f"No code chunks extracted from {repo_path}")
            return 0

        logger.info(f"Ingesting {len(chunks)} code chunks into CodeRAGStore...")
        self._index.clear()

        for chunk in chunks:
            vector = self.embedding_provider.embed_text(f"{chunk.symbol_name} {chunk.content}")
            self._index.append({
                "chunk_id": chunk.chunk_id,
                "file_path": chunk.file_path,
                "symbol_name": chunk.symbol_name,
                "symbol_type": chunk.symbol_type,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "content": chunk.content,
                "vector": vector,
                "metadata": chunk.metadata,
            })

        logger.info(f"RAG Indexing complete. Total indexed chunks: {len(self._index)}")
        return len(self._index)

    def retrieve_code(self, query: str, top_k: int = 5, file_filter: str | None = None) -> list[dict[str, Any]]:
        """Perform semantic hybrid code retrieval."""
        if not self._index:
            logger.info("RAG Index is empty. Auto-indexing demo repository...")
            self.index_repository(settings.ALLOWED_HOST_WORKSPACE_ROOT)

        import re
        query_vec = self.embedding_provider.embed_text(query)
        query_words = set(re.findall(r"\w+", query.lower()))

        scored_results = []
        for item in self._index:
            if file_filter and file_filter not in item["file_path"]:
                continue

            # Vector similarity score
            vec_score = cosine_similarity(query_vec, item["vector"])

            # Keyword relevance score (hybrid search)
            content_words = set(re.findall(r"\w+", item["content"].lower()))
            keyword_score = len(query_words.intersection(content_words)) / max(1, len(query_words))

            # Hybrid score combination
            final_score = (0.7 * max(0.0, vec_score)) + (0.3 * keyword_score)
            if final_score <= 0 and (keyword_score > 0 or vec_score > 0):
                final_score = 0.05

            scored_results.append({
                "file": item["file_path"],
                "symbol": item["symbol_name"],
                "symbol_type": item["symbol_type"],
                "line_range": f"L{item['start_line']}-L{item['end_line']}",
                "relevance_score": round(float(final_score), 4),
                "snippet": item["content"],
                "metadata": item["metadata"],
            })

        # Sort by relevance descending
        scored_results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored_results[:top_k]
