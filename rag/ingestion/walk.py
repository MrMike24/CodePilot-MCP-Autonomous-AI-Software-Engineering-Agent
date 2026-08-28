import os
from pathlib import Path
from typing import Generator
from backend.app.core.logging import logger

IGNORED_DIRS = {
    ".git", ".venv", "venv", "__pycache__", "node_modules", "build", "dist",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", ".idea", ".vscode", "coverage"
}

IGNORED_EXTENSIONS = {
    ".pyc", ".pyo", ".pyd", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg",
    ".zip", ".tar", ".gz", ".7z", ".pdf", ".db", ".sqlite", ".bin", ".exe", ".dll", ".so", ".dylib"
}

MAX_FILE_SIZE_BYTES = 500_000  # 500KB cap per file to ignore huge generated assets


class RepositoryWalker:
    """Walk repository files with strict exclusion rules for clean RAG ingestion."""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()

    def walk_source_files(self) -> Generator[tuple[Path, str], None, None]:
        """Yield (file_path, file_content) for all valid source files."""
        logger.info(f"Walking repository for RAG ingestion: {self.repo_path}")
        for root, dirs, files in os.walk(self.repo_path):
            # Exclude ignored directories in-place
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith(".")]

            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in IGNORED_EXTENSIONS:
                    continue

                full_path = Path(root) / file

                # File size safety check
                if full_path.stat().st_size > MAX_FILE_SIZE_BYTES:
                    continue

                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        if content.strip():
                            yield full_path, content
                except Exception as e:
                    logger.debug(f"Skipping unreadable file {full_path}: {e}")
