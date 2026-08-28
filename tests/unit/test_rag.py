from pathlib import Path
import pytest
from rag.parsing.splitter import CodeSplitter
from rag.retrieval.vector_store import CodeRAGStore


@pytest.mark.unit
def test_code_splitter_python_ast(tmp_path):
    splitter = CodeSplitter()
    code = """
def sample_func():
    return 42

class SampleClass:
    def method(self):
        pass
"""
    file_path = tmp_path / "sample.py"
    file_path.write_text(code)

    chunks = splitter.split_file(file_path, code, tmp_path)
    assert len(chunks) == 3
    symbols = [c.symbol_name for c in chunks]
    assert "sample_func" in symbols
    assert "SampleClass" in symbols


@pytest.mark.unit
def test_code_splitter_generic_fallback(tmp_path):
    splitter = CodeSplitter()
    md_content = "# Project Documentation\n\nThis is a sample markdown doc for CodePilot-MCP."
    file_path = tmp_path / "README.md"
    file_path.write_text(md_content)

    chunks = splitter.split_file(file_path, md_content, tmp_path)
    assert len(chunks) >= 1
    assert chunks[0].language == "md"
    assert chunks[0].symbol_type == "block"


@pytest.mark.unit
def test_code_rag_store_indexing_and_retrieval(tmp_path):
    # Setup test file
    code_dir = tmp_path / "app"
    code_dir.mkdir()
    (code_dir / "main.py").write_text("def validate_email(email):\n    if not email:\n        raise ValueError('Email empty')\n")

    rag = CodeRAGStore()
    count = rag.index_repository(str(tmp_path))
    assert count >= 1

    results = rag.retrieve_code("validate email empty", top_k=3)
    assert len(results) >= 1
    assert results[0]["symbol"] == "validate_email"
    assert results[0]["relevance_score"] > 0
