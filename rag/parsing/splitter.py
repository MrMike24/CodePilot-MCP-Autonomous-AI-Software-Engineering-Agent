import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from backend.app.core.logging import logger


@dataclass
class CodeChunk:
    chunk_id: str
    file_path: str
    language: str
    symbol_name: str
    symbol_type: str  # function, class, module
    start_line: int
    end_line: int
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


class CodeSplitter:
    """Language-aware code splitter parsing Python AST into function and class chunks."""

    def split_file(self, file_path: Path, content: str, repo_root: Path) -> list[CodeChunk]:
        rel_path = str(file_path.relative_to(repo_root))
        ext = file_path.suffix.lower()

        if ext == ".py":
            return self._split_python_ast(rel_path, content)
        else:
            return self._split_generic_sliding_window(rel_path, content, ext)

    def _split_python_ast(self, rel_path: str, content: str) -> list[CodeChunk]:
        chunks: list[CodeChunk] = []
        lines = content.splitlines()

        try:
            tree = ast.parse(content)
        except SyntaxError:
            # Fallback to sliding window if file has syntax errors
            return self._split_generic_sliding_window(rel_path, content, ".py")

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                start_line = getattr(node, "lineno", 1)
                end_line = getattr(node, "end_lineno", len(lines))
                symbol_name = node.name
                symbol_type = "class" if isinstance(node, ast.ClassDef) else "function"

                snippet = "\n".join(lines[start_line - 1 : end_line])
                chunk_id = f"{rel_path}:{symbol_name}:{start_line}"

                chunks.append(
                    CodeChunk(
                        chunk_id=chunk_id,
                        file_path=rel_path,
                        language="python",
                        symbol_name=symbol_name,
                        symbol_type=symbol_type,
                        start_line=start_line,
                        end_line=end_line,
                        content=snippet,
                        metadata={
                            "file_path": rel_path,
                            "symbol_name": symbol_name,
                            "symbol_type": symbol_type,
                            "start_line": start_line,
                            "end_line": end_line,
                        },
                    )
                )

        # Module level overview if no symbols were extracted
        if not chunks:
            chunks = self._split_generic_sliding_window(rel_path, content, ".py")

        return chunks

    def _split_generic_sliding_window(
        self, rel_path: str, content: str, ext: str, window_lines: int = 40, overlap: int = 10
    ) -> list[CodeChunk]:
        chunks: list[CodeChunk] = []
        lines = content.splitlines()
        if not lines:
            return chunks

        step = max(1, window_lines - overlap)
        for i in range(0, len(lines), step):
            window = lines[i : i + window_lines]
            start_line = i + 1
            end_line = i + len(window)
            snippet = "\n".join(window)
            chunk_id = f"{rel_path}:block:{start_line}"

            chunks.append(
                CodeChunk(
                    chunk_id=chunk_id,
                    file_path=rel_path,
                    language=ext.lstrip("."),
                    symbol_name="module_block",
                    symbol_type="block",
                    start_line=start_line,
                    end_line=end_line,
                    content=snippet,
                    metadata={
                        "file_path": rel_path,
                        "symbol_name": "module_block",
                        "symbol_type": "block",
                        "start_line": start_line,
                        "end_line": end_line,
                    },
                )
            )

        return chunks
