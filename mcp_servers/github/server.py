import os
import subprocess
from datetime import datetime, timezone
from typing import Any
import httpx
from backend.app.core.config import settings
from backend.app.core.logging import logger
from mcp_servers.filesystem.server import FilesystemMCPServer


class GitHubMCPServer:
    """Production GitHub MCP Server implementing real GitHub REST API operations and git management."""

    def __init__(self, workspace_root: str | None = None):
        self.workspace_root = workspace_root or settings.ALLOWED_HOST_WORKSPACE_ROOT
        self.fs = FilesystemMCPServer(self.workspace_root)
        self.token = settings.GITHUB_TOKEN
        self.base_url = "https://api.github.com"
        logger.info(f"GitHubMCPServer initialized (has_token={bool(self.token)})")

    def _get_headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token.strip()}"
        return headers

    def verify_authentication(self) -> dict[str, Any]:
        """Checks authentication against GitHub API without exposing token secret."""
        if not self.token or not self.token.strip():
            return {
                "authenticated": False,
                "error": "GITHUB_TOKEN is not configured in environment or .env file.",
            }
        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.get(f"{self.base_url}/user", headers=self._get_headers())
                if res.status_code == 200:
                    data = res.json()
                    return {
                        "authenticated": True,
                        "login": data.get("login"),
                        "name": data.get("name"),
                        "token_configured": True,
                    }
                else:
                    return {
                        "authenticated": False,
                        "status_code": res.status_code,
                        "error": f"GitHub Authentication failed ({res.status_code}): {res.text}",
                    }
        except Exception as e:
            return {
                "authenticated": False,
                "error": f"Failed to connect to GitHub API: {str(e)}",
            }

    def get_repository(self, owner: str = "codepilot-org", repo: str = "demo_repository") -> dict[str, Any]:
        """Retrieve real repository details from GitHub API."""
        if not self.token or not self.token.strip():
            raise ValueError("GitHub delivery unavailable: GITHUB_TOKEN is not configured.")
        with httpx.Client(timeout=10.0) as client:
            res = client.get(f"{self.base_url}/repos/{owner}/{repo}", headers=self._get_headers())
            if res.status_code != 200:
                raise ValueError(f"GitHub repository '{owner}/{repo}' not found or inaccessible ({res.status_code}): {res.text}")
            return res.json()

    def list_files(self, owner: str = "codepilot-org", repo: str = "demo_repository", path: str = ".") -> list[dict[str, Any]]:
        """List repository directory structure from workspace."""
        return self.fs.list_directory(path)

    def get_file(self, owner: str = "codepilot-org", repo: str = "demo_repository", path: str = "") -> str:
        """Get file contents from workspace."""
        return self.fs.read_file(path)

    def search_code(self, query: str) -> list[dict[str, Any]]:
        """Search code in repository workspace."""
        return self.fs.search_files(query)

    def get_commit_history(self, limit: int = 5) -> list[dict[str, Any]]:
        """Get local git commit history."""
        try:
            cmd = ["git", "log", f"-n{limit}", "--pretty=format:%H|%an|%ad|%s", "--date=iso"]
            res = subprocess.run(cmd, cwd=self.workspace_root, capture_output=True, text=True)
            if res.returncode != 0:
                return []
            commits = []
            for line in res.stdout.strip().splitlines():
                parts = line.split("|", 3)
                if len(parts) == 4:
                    commits.append({
                        "sha": parts[0],
                        "author": parts[1],
                        "date": parts[2],
                        "message": parts[3],
                    })
            return commits
        except Exception:
            return []

    def _ensure_gitignore(self) -> None:
        """Ensures that .gitignore exists and properly ignores cache, pyc, and temporary files."""
        gi_path = os.path.join(self.workspace_root, ".gitignore")
        required_patterns = [
            "__pycache__/",
            "*.py[cod]",
            "*.pyo",
            "*.pyd",
            ".pytest_cache/",
            ".coverage",
            ".venv",
            "*.sqlite",
            "*.db",
        ]
        existing = ""
        if os.path.exists(gi_path):
            with open(gi_path, "r", encoding="utf-8") as f:
                existing = f.read()

        missing = [p for p in required_patterns if p not in existing]
        if missing:
            with open(gi_path, "a", encoding="utf-8") as f:
                if existing and not existing.endswith("\n"):
                    f.write("\n")
                f.write("\n# Automated CodePilot Git Ignore Rules\n" + "\n".join(missing) + "\n")

    def push_branch(self, branch_name: str, remote_name: str = "origin") -> dict[str, Any]:
        """Pushes feature branch to remote git repository, ensuring cache files are strictly excluded."""
        try:
            self._ensure_gitignore()

            # 1. Check if git repo exists
            git_check = subprocess.run(["git", "status"], cwd=self.workspace_root, capture_output=True, text=True)
            if git_check.returncode != 0:
                subprocess.run(["git", "init"], cwd=self.workspace_root, capture_output=True)
                subprocess.run(["git", "checkout", "-B", "main"], cwd=self.workspace_root, capture_output=True)

            # 2. Switch/create branch
            subprocess.run(["git", "checkout", "-B", branch_name], cwd=self.workspace_root, capture_output=True)

            # 3. Explicitly remove any cached __pycache__ or .pytest_cache files from git tracking
            subprocess.run(["git", "rm", "-r", "--cached", "__pycache__"], cwd=self.workspace_root, capture_output=True)
            subprocess.run(["git", "rm", "-r", "--cached", ".pytest_cache"], cwd=self.workspace_root, capture_output=True)

            # 4. Stage files (honoring .gitignore)
            subprocess.run(["git", "add", "-A"], cwd=self.workspace_root, capture_output=True)

            # 5. Verify no .pyc or cache files are staged
            staged_check = subprocess.run(["git", "diff", "--name-only", "--cached"], cwd=self.workspace_root, capture_output=True, text=True)
            staged_files = staged_check.stdout.splitlines()
            for sf in staged_files:
                if "__pycache__" in sf or sf.endswith(".pyc") or sf.endswith(".pyo") or ".pytest_cache" in sf:
                    subprocess.run(["git", "rm", "--cached", sf], cwd=self.workspace_root, capture_output=True)

            # 6. Commit
            commit_res = subprocess.run(
                ["git", "commit", "-m", f"CodePilot-MCP automated implementation for {branch_name}"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
            )
            logger.info(f"git commit output: {commit_res.stdout.strip() or commit_res.stderr.strip()}")

            # 7. Push branch to GitHub using authenticated token URL
            target_owner = settings.GITHUB_DEFAULT_OWNER
            target_repo = settings.GITHUB_DEFAULT_REPO
            if self.token:
                auth_url = f"https://x-access-token:{self.token.strip()}@github.com/{target_owner}/{target_repo}.git"
                push_res = subprocess.run(
                    ["git", "push", "-u", "-f", auth_url, f"{branch_name}:{branch_name}"],
                    cwd=self.workspace_root,
                    capture_output=True,
                    text=True,
                )
                if push_res.returncode != 0:
                    logger.warning(f"git push output: {push_res.stderr or push_res.stdout}")
                    return {"pushed": False, "note": push_res.stderr or push_res.stdout}
                return {"pushed": True, "branch": branch_name}
            else:
                remotes = subprocess.run(["git", "remote"], cwd=self.workspace_root, capture_output=True, text=True)
                if remote_name in remotes.stdout.split():
                    push_res = subprocess.run(["git", "push", "-u", remote_name, branch_name], cwd=self.workspace_root, capture_output=True, text=True)
                    return {"pushed": push_res.returncode == 0, "branch": branch_name}
                return {"pushed": False, "note": f"Remote '{remote_name}' not configured in local git repository."}
        except Exception as e:
            logger.warning(f"Branch push notice: {e}")
            return {"pushed": False, "error": str(e)}

    def create_pull_request(
        self,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str = "main",
        owner: str | None = None,
        repo: str | None = None,
    ) -> dict[str, Any]:
        """Creates a real Pull Request on GitHub via API, performs post-creation verification, and returns verified PR data."""
        if not self.token or not self.token.strip():
            raise ValueError(
                "GitHub Delivery Failed: GITHUB_TOKEN is not configured in environment or .env. "
                "To create a real Pull Request, please set GITHUB_TOKEN."
            )

        target_owner = owner or settings.GITHUB_DEFAULT_OWNER
        target_repo = repo or settings.GITHUB_DEFAULT_REPO

        logger.info(f"GitHubMCP: Creating real PR on {target_owner}/{target_repo} ({head_branch} -> {base_branch})")

        # Push branch first if possible
        self.push_branch(head_branch)

        url = f"{self.base_url}/repos/{target_owner}/{target_repo}/pulls"
        payload = {
            "title": title,
            "body": body,
            "head": head_branch,
            "base": base_branch,
        }

        with httpx.Client(timeout=15.0) as client:
            res = client.post(url, json=payload, headers=self._get_headers())
            if res.status_code not in (200, 201):
                err_msg = res.text
                try:
                    err_json = res.json()
                    err_msg = err_json.get("message", res.text)
                    if "errors" in err_json:
                        err_msg += f" Details: {err_json['errors']}"
                except Exception:
                    pass
                raise ValueError(f"GitHub PR creation rejected by GitHub API ({res.status_code}): {err_msg}")

            data = res.json()
            pr_number = data.get("number")
            pr_url = data.get("html_url")
            head_sha = data.get("head", {}).get("sha", "")

            if not pr_number or not pr_url:
                raise ValueError(f"GitHub API returned invalid PR response missing number or html_url: {data}")

            # Explicit post-creation verification request (Requirement 7)
            verify_res = client.get(f"{url}/{pr_number}", headers=self._get_headers())
            if verify_res.status_code != 200:
                raise ValueError(f"GitHub PR verification failed: PR #{pr_number} could not be verified on GitHub API ({verify_res.status_code}).")

            verified_data = verify_res.json()
            logger.info(f"GitHubMCP: Successfully created and verified PR #{pr_number} at {verified_data.get('html_url')}")

            return {
                "pr_number": pr_number,
                "pr_url": verified_data.get("html_url", pr_url),
                "title": verified_data.get("title", title),
                "head_branch": head_branch,
                "base_branch": base_branch,
                "status": "created",
                "is_simulated": False,
                "head_sha": head_sha,
                "state": verified_data.get("state", "open"),
                "verified": True,
            }

    def verify_pull_request(self, owner: str, repo: str, pr_number: int) -> dict[str, Any]:
        """Explicitly fetches a PR from GitHub API to verify existence."""
        if not self.token or not self.token.strip():
            raise ValueError("GITHUB_TOKEN is not configured.")

        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        with httpx.Client(timeout=10.0) as client:
            res = client.get(url, headers=self._get_headers())
            if res.status_code != 200:
                return {
                    "verified": False,
                    "status_code": res.status_code,
                    "error": f"PR #{pr_number} not found on repository {owner}/{repo}: {res.text}",
                }
            data = res.json()
            return {
                "verified": True,
                "pr_number": data.get("number"),
                "html_url": data.get("html_url"),
                "state": data.get("state"),
                "title": data.get("title"),
            }
