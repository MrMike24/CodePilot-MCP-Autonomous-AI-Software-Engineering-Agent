# Code-Aware RAG Pipeline Architecture

CodePilot-MCP features a dedicated Code-Aware RAG (Retrieval-Augmented Generation) pipeline built for high-precision source code understanding.

## Ingestion & Parsing Workflow

1. **Repository Ingestion (`rag/ingestion/walk.py`)**:
   - Recursively walks repository source trees.
   - Applies exclusion filters to skip `.git`, `node_modules`, `venv`, build directories, binary assets, and files exceeding 500KB.

2. **Language-Aware AST Splitting (`rag/parsing/splitter.py`)**:
   - Parses Python source files using standard `ast` tree parsing.
   - Extracts top-level classes and functions as discrete `CodeChunk` units.
   - Preserves rich metadata: file path, symbol name, symbol type, start line, end line, and line range snippet.
   - Falls back to sliding-window block splitting for generic non-Python files.

3. **Embedding Vector Provider (`rag/embeddings/provider.py`)**:
   - Uses normalized 1536-dimensional feature vectors.
   - Ensures deterministic vector indexing for local/demo execution without remote model dependency failures.

4. **Vector Store & Hybrid Retrieval (`rag/retrieval/vector_store.py`)**:
   - Integrates with Qdrant vector database.
   - Hybrid scoring formula combining vector cosine similarity (70%) and keyword relevance (30%):
     $$\text{Score} = 0.7 \times \text{CosineSim}(\vec{q}, \vec{v}) + 0.3 \times \text{KeywordMatch}(q, t)$$
   - Returns top $k$ relevant code snippets with file path, symbol, line range, score, and snippet text.
