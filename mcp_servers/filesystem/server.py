import os
import re
from pathlib import Path
from typing import Any
from backend.app.core.config import settings
from backend.app.core.logging import logger


class FilesystemMCPServer:
    """Custom MCP Server for safe filesystem access within an isolated workspace boundary."""

    def __init__(self, workspace_root: str | None = None):
        root = workspace_root or settings.ALLOWED_HOST_WORKSPACE_ROOT
        self.workspace_root = Path(root).resolve()
        os.makedirs(self.workspace_root, exist_ok=True)
        self._initial_files: dict[str, str] = {}
        self._snapshot_files()
        try:
            import git
            if not (self.workspace_root / ".git").exists():
                git.Repo.init(self.workspace_root)
        except Exception:
            pass
        logger.info(f"FilesystemMCPServer initialized with workspace root: {self.workspace_root}")

    def _snapshot_files(self) -> None:
        """Capture initial snapshot of text files in workspace."""
        for root, dirs, files in os.walk(self.workspace_root):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in {"__pycache__", "node_modules", ".venv"}]
            for file in files:
                if file.startswith("."):
                    continue
                p = Path(root) / file
                rel = p.relative_to(self.workspace_root).as_posix()
                try:
                    self._initial_files[rel] = p.read_text(encoding="utf-8")
                except Exception:
                    pass

    def _resolve_path(self, relative_path: str) -> Path:
        """Resolve and validate target path stays strictly inside workspace root."""
        # Clean path input
        clean_rel = relative_path.lstrip("/\\")
        target = (self.workspace_root / clean_rel).resolve()

        # Strict boundary check
        try:
            target.relative_to(self.workspace_root)
        except ValueError:
            logger.warning(f"Path traversal blocked: {relative_path} -> {target}")
            raise PermissionError(f"Access denied: path '{relative_path}' is outside authorized workspace root.")

        # Prevent reading sensitive secret patterns
        filename = target.name.lower()
        if filename in {".env", ".git", "id_rsa", "credentials.json", "secrets.yaml"}:
            raise PermissionError(f"Access denied: file '{filename}' contains protected secrets.")

        return target

    def list_directory(self, path: str = ".") -> list[dict[str, Any]]:
        """List files and directories within target workspace path."""
        target_dir = self._resolve_path(path)
        if not target_dir.is_dir():
            raise NotADirectoryError(f"'{path}' is not a valid directory.")

        results = []
        for item in target_dir.iterdir():
            if item.name.startswith(".") or item.name in {"__pycache__", "node_modules", ".venv", "venv"}:
                continue
            results.append({
                "name": item.name,
                "path": item.relative_to(self.workspace_root).as_posix(),
                "is_dir": item.is_dir(),
                "size_bytes": item.stat().st_size if item.is_file() else 0,
            })
        return results

    def read_file(self, path: str) -> str:
        """Read content of a text file inside workspace."""
        file_path = self._resolve_path(path)
        if not file_path.is_file():
            raise FileNotFoundError(f"File '{path}' does not exist.")

        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

    def create_file(self, path: str, content: str = "") -> str:
        """Create a new file inside workspace."""
        file_path = self._resolve_path(path)
        os.makedirs(file_path.parent, exist_ok=True)

        if file_path.exists():
            raise FileExistsError(f"File '{path}' already exists. Use write_file to overwrite.")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"FilesystemMCP: Created file '{path}'")
        return file_path.relative_to(self.workspace_root).as_posix()

    def write_file(self, path: str, content: str) -> str:
        """Write content to an existing or new file inside workspace."""
        file_path = self._resolve_path(path)
        os.makedirs(file_path.parent, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"FilesystemMCP: Wrote content to file '{path}' ({len(content)} chars)")
        return file_path.relative_to(self.workspace_root).as_posix()

    def search_files(self, query: str, extension: str | None = None) -> list[dict[str, Any]]:
        """Search file contents for regex or substring pattern across workspace."""
        regex = re.compile(query, re.IGNORECASE)
        matches = []

        for root, dirs, files in os.walk(self.workspace_root):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in {"node_modules", "__pycache__", "venv"}]

            for file in files:
                if extension and not file.endswith(extension):
                    continue

                abs_file = Path(root) / file
                rel_file = str(abs_file.relative_to(self.workspace_root))

                try:
                    with open(abs_file, "r", encoding="utf-8", errors="ignore") as f:
                        for line_num, line in enumerate(f, 1):
                            if regex.search(line):
                                matches.append({
                                    "file": rel_file,
                                    "line_number": line_num,
                                    "line_content": line.strip(),
                                })
                except Exception:
                    continue

        return matches

    def get_diff(self) -> str:
        """Get workspace file diff summary."""
        try:
            import git
            repo = git.Repo(self.workspace_root, search_parent_directories=True)
            diff = repo.git.diff()
            untracked = repo.untracked_files
            untracked_content = []
            if untracked:
                for uf in untracked:
                    full_uf = os.path.join(repo.working_dir, uf)
                    try:
                        with open(full_uf, "r", encoding="utf-8") as f:
                            content = f.read()
                        untracked_content.append(f"--- /dev/null\n+++ b/{uf}\n" + content)
                    except Exception:
                        untracked_content.append(f"New file: {uf}")
            
            all_diff = ""
            if diff:
                all_diff += diff + "\n"
            if untracked_content:
                all_diff += "\n".join(untracked_content)
                
            if all_diff.strip():
                return all_diff
        except Exception:
            pass

        import difflib
        diff_chunks = []
        current_files: dict[str, str] = {}
        for root, dirs, files in os.walk(self.workspace_root):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in {"__pycache__", "node_modules", ".venv"}]
            for file in files:
                if file.startswith("."):
                    continue
                p = Path(root) / file
                rel = p.relative_to(self.workspace_root).as_posix()
                try:
                    current_files[rel] = p.read_text(encoding="utf-8")
                except Exception:
                    pass

        # Check modified & deleted files
        for rel, orig in self._initial_files.items():
            curr = current_files.get(rel)
            if curr is None:
                diff_chunks.append(f"--- a/{rel}\n+++ /dev/null\n(File deleted)")
            elif curr != orig:
                udiff = difflib.unified_diff(
                    orig.splitlines(keepends=True),
                    curr.splitlines(keepends=True),
                    fromfile=f"a/{rel}",
                    tofile=f"b/{rel}",
                )
                diff_chunks.append("".join(udiff))

        # Check newly created files
        for rel, curr in current_files.items():
            if rel not in self._initial_files:
                diff_chunks.append(f"--- /dev/null\n+++ b/{rel}\n" + curr)

        if diff_chunks:
            return "\n\n".join(diff_chunks)
        return "No changes detected."
