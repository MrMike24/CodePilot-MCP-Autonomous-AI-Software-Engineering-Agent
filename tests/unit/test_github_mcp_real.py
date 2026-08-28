import pytest
import httpx
from unittest.mock import patch, MagicMock
from mcp_servers.github.server import GitHubMCPServer


@pytest.mark.unit
def test_github_auth_missing_token(tmp_path, monkeypatch):
    """Requirement 10.A: Detect missing GITHUB_TOKEN explicitly."""
    monkeypatch.setattr("backend.app.core.config.settings.GITHUB_TOKEN", None)
    gh = GitHubMCPServer(workspace_root=str(tmp_path))
    res = gh.verify_authentication()
    assert res["authenticated"] is False
    assert "GITHUB_TOKEN is not configured" in res["error"]


@pytest.mark.unit
def test_github_auth_invalid_token(tmp_path, monkeypatch):
    """Requirement 10.A: Detect invalid GITHUB_TOKEN via 401 response."""
    monkeypatch.setattr("backend.app.core.config.settings.GITHUB_TOKEN", "ghp_invalid_token_12345")
    gh = GitHubMCPServer(workspace_root=str(tmp_path))

    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.text = '{"message": "Bad credentials", "documentation_url": "https://docs.github.com/rest"}'

    with patch("httpx.Client.get", return_value=mock_resp):
        res = gh.verify_authentication()
        assert res["authenticated"] is False
        assert res["status_code"] == 401
        assert "Authentication failed" in res["error"]


@pytest.mark.unit
def test_github_repository_not_found(tmp_path, monkeypatch):
    """Requirement 10.B: Handle repository not found error."""
    monkeypatch.setattr("backend.app.core.config.settings.GITHUB_TOKEN", "ghp_valid_token_12345")
    gh = GitHubMCPServer(workspace_root=str(tmp_path))

    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_resp.text = '{"message": "Not Found"}'

    with patch("httpx.Client.get", return_value=mock_resp):
        with pytest.raises(ValueError, match="not found or inaccessible"):
            gh.get_repository("nonexistent-org", "nonexistent-repo")


@pytest.mark.unit
def test_github_pr_creation_failure_from_api(tmp_path, monkeypatch):
    """Requirement 10.D: Handle PR creation rejection from GitHub API."""
    monkeypatch.setattr("backend.app.core.config.settings.GITHUB_TOKEN", "ghp_valid_token_12345")
    gh = GitHubMCPServer(workspace_root=str(tmp_path))

    mock_post_resp = MagicMock()
    mock_post_resp.status_code = 422
    mock_post_resp.text = '{"message": "Validation Failed", "errors": [{"message": "No commits between main and branch"}]}'
    mock_post_resp.json.return_value = {
        "message": "Validation Failed",
        "errors": [{"message": "No commits between main and branch"}],
    }

    with patch("httpx.Client.post", return_value=mock_post_resp):
        with pytest.raises(ValueError, match="GitHub PR creation rejected by GitHub API"):
            gh.create_pull_request(
                title="Test PR",
                body="Test Body",
                head_branch="feature/branch",
                base_branch="main",
                owner="test-org",
                repo="test-repo",
            )


@pytest.mark.unit
def test_github_pr_verification_failure(tmp_path, monkeypatch):
    """Requirement 10.E: Fail if PR creation response cannot be verified via GET."""
    monkeypatch.setattr("backend.app.core.config.settings.GITHUB_TOKEN", "ghp_valid_token_12345")
    gh = GitHubMCPServer(workspace_root=str(tmp_path))

    # Mock successful POST creation
    mock_post_resp = MagicMock()
    mock_post_resp.status_code = 201
    mock_post_resp.json.return_value = {
        "number": 105,
        "html_url": "https://github.com/test-org/test-repo/pull/105",
        "head": {"sha": "abc123def456"},
    }

    # Mock failing GET verification (404)
    mock_get_resp = MagicMock()
    mock_get_resp.status_code = 404
    mock_get_resp.text = "Not Found"

    with patch("httpx.Client.post", return_value=mock_post_resp), patch("httpx.Client.get", return_value=mock_get_resp):
        with pytest.raises(ValueError, match="GitHub PR verification failed"):
            gh.create_pull_request(
                title="Test PR",
                body="Test Body",
                head_branch="feature/branch",
                base_branch="main",
                owner="test-org",
                repo="test-repo",
            )


@pytest.mark.unit
def test_github_pr_creation_and_verification_success(tmp_path, monkeypatch):
    """Requirement 10.F & 10.J: Return verified real PR data from GitHub API without fabricated numbers."""
    monkeypatch.setattr("backend.app.core.config.settings.GITHUB_TOKEN", "ghp_valid_token_12345")
    gh = GitHubMCPServer(workspace_root=str(tmp_path))

    # Mock POST creation
    mock_post_resp = MagicMock()
    mock_post_resp.status_code = 201
    mock_post_resp.json.return_value = {
        "number": 89,
        "html_url": "https://github.com/custom-owner/target-repo/pull/89",
        "head": {"sha": "e4d3c2b1a0987"},
    }

    # Mock GET verification
    mock_get_resp = MagicMock()
    mock_get_resp.status_code = 200
    mock_get_resp.json.return_value = {
        "number": 89,
        "html_url": "https://github.com/custom-owner/target-repo/pull/89",
        "title": "Add Rate Limiting to FastAPI Authentication",
        "state": "open",
    }

    with patch("httpx.Client.post", return_value=mock_post_resp), patch("httpx.Client.get", return_value=mock_get_resp):
        pr = gh.create_pull_request(
            title="Add Rate Limiting to FastAPI Authentication",
            body="Automated Rate Limiting implementation.",
            head_branch="codepilot/task-89",
            base_branch="main",
            owner="custom-owner",
            repo="target-repo",
        )

        assert pr["pr_number"] == 89
        assert pr["pr_url"] == "https://github.com/custom-owner/target-repo/pull/89"
        assert pr["is_simulated"] is False
        assert pr["verified"] is True
        assert pr["head_sha"] == "e4d3c2b1a0987"


@pytest.mark.unit
def test_push_branch_excludes_pycache_and_pyc(tmp_path, monkeypatch):
    """Requirement 6: Verify __pycache__ and *.pyc are strictly excluded from staging and commit."""
    import subprocess
    import os

    workspace = str(tmp_path)
    monkeypatch.setattr("backend.app.core.config.settings.GITHUB_TOKEN", None)
    gh = GitHubMCPServer(workspace_root=workspace)

    # Initialize git repo
    subprocess.run(["git", "init"], cwd=workspace, capture_output=True)
    subprocess.run(["git", "checkout", "-B", "main"], cwd=workspace, capture_output=True)

    # Create source files and pycache files
    os.makedirs(os.path.join(workspace, "app", "__pycache__"), exist_ok=True)
    os.makedirs(os.path.join(workspace, ".pytest_cache"), exist_ok=True)

    with open(os.path.join(workspace, "app", "main.py"), "w") as f:
        f.write("def hello(): return 'world'")

    with open(os.path.join(workspace, "app", "rate_limiter.py"), "w") as f:
        f.write("def rate_limit(): pass")

    with open(os.path.join(workspace, "app", "__pycache__", "main.cpython-313.pyc"), "wb") as f:
        f.write(b"compiled_bytecode_data")

    with open(os.path.join(workspace, ".pytest_cache", "cache.dat"), "w") as f:
        f.write("test_cache")

    # Run push_branch
    res = gh.push_branch("codepilot/test-feature-clean")

    # Verify committed files
    tracked = subprocess.run(["git", "ls-files"], cwd=workspace, capture_output=True, text=True).stdout.splitlines()

    assert "app/main.py" in tracked
    assert "app/rate_limiter.py" in tracked
    assert not any("__pycache__" in f for f in tracked)
    assert not any(f.endswith(".pyc") for f in tracked)
    assert not any(".pytest_cache" in f for f in tracked)

