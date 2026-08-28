import pytest
from mcp_servers.client import MCPClientManager
from mcp_servers.execution.server import ExecutionMCPServer
from mcp_servers.filesystem.server import FilesystemMCPServer
from mcp_servers.github.server import GitHubMCPServer


@pytest.mark.unit
def test_filesystem_mcp_operations(tmp_path):
    fs = FilesystemMCPServer(workspace_root=str(tmp_path))

    # Test file creation and read
    rel_path = fs.create_file("app/main.py", "print('hello')")
    assert rel_path == "app/main.py"

    content = fs.read_file("app/main.py")
    assert content == "print('hello')"

    # Test write file
    fs.write_file("app/main.py", "print('updated')")
    assert fs.read_file("app/main.py") == "print('updated')"

    # Test directory listing
    dir_list = fs.list_directory(".")
    assert len(dir_list) >= 1
    assert dir_list[0]["name"] == "app"


@pytest.mark.unit
def test_filesystem_mcp_security_path_traversal(tmp_path):
    fs = FilesystemMCPServer(workspace_root=str(tmp_path))

    # Test path traversal attack prevention
    with pytest.raises(PermissionError, match="Access denied"):
        fs.read_file("../../outside_workspace.txt")


@pytest.mark.unit
def test_filesystem_mcp_security_secret_blocking(tmp_path):
    fs = FilesystemMCPServer(workspace_root=str(tmp_path))

    # Attempting to access sensitive file names raises PermissionError
    with pytest.raises(PermissionError, match="protected secrets"):
        fs.read_file(".env")


@pytest.mark.unit
def test_github_mcp_missing_credentials_fails(tmp_path, monkeypatch):
    monkeypatch.setattr("backend.app.core.config.settings.GITHUB_TOKEN", None)
    gh = GitHubMCPServer(workspace_root=str(tmp_path))
    with pytest.raises(ValueError, match="GITHUB_TOKEN is not configured"):
        gh.create_pull_request(
            title="Fix Email Bug",
            body="Automated fix",
            head_branch="codepilot/fix",
        )


@pytest.mark.unit
def test_mcp_client_manager(tmp_path):
    client = MCPClientManager(workspace_root=str(tmp_path))
    tools = client.list_tools()
    assert "read_file" in tools
    assert "write_file" in tools
    assert "run_tests" in tools
    assert "create_pull_request" in tools

    # Execute tool via client
    client.execute_tool("create_file", {"path": "test.txt", "content": "mcp_client"})
    read_val = client.execute_tool("read_file", {"path": "test.txt"})
    assert read_val == "mcp_client"
