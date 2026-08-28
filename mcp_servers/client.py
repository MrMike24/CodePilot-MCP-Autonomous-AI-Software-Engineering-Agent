from typing import Any, Callable
from backend.app.core.logging import logger
from mcp_servers.execution.server import ExecutionMCPServer, ExecutionResult
from mcp_servers.filesystem.server import FilesystemMCPServer
from mcp_servers.github.server import GitHubMCPServer


class MCPClientManager:
    """Unified MCP Client Manager orchestrating custom MCP servers (Filesystem, GitHub, Execution)."""

    def __init__(self, workspace_root: str | None = None):
        self.workspace_root = workspace_root
        self.fs_server = FilesystemMCPServer(workspace_root)
        self.github_server = GitHubMCPServer(workspace_root)
        self.execution_server = ExecutionMCPServer(workspace_root)
        self._registry: dict[str, Callable[..., Any]] = {}
        self._register_tools()

    def _register_tools(self) -> None:
        """Register all MCP server tools into unified client tool registry."""
        # Filesystem MCP Tools
        self._registry["list_directory"] = self.fs_server.list_directory
        self._registry["read_file"] = self.fs_server.read_file
        self._registry["create_file"] = self.fs_server.create_file
        self._registry["write_file"] = self.fs_server.write_file
        self._registry["search_files"] = self.fs_server.search_files
        self._registry["get_diff"] = self.fs_server.get_diff

        # GitHub MCP Tools
        self._registry["verify_authentication"] = self.github_server.verify_authentication
        self._registry["get_repository"] = self.github_server.get_repository
        self._registry["list_files"] = self.github_server.list_files
        self._registry["get_file"] = self.github_server.get_file
        self._registry["search_code"] = self.github_server.search_code
        self._registry["get_commit_history"] = self.github_server.get_commit_history
        self._registry["push_branch"] = self.github_server.push_branch
        self._registry["create_pull_request"] = self.github_server.create_pull_request
        self._registry["verify_pull_request"] = self.github_server.verify_pull_request

        # Execution MCP Tools
        self._registry["run_tests"] = self.execution_server.run_tests
        self._registry["run_linter"] = self.execution_server.run_linter
        self._registry["run_typecheck"] = self.execution_server.run_typecheck
        self._registry["run_security_scan"] = self.execution_server.run_security_scan

        logger.info(f"MCPClientManager initialized with {len(self._registry)} registered tools.")

    def list_tools(self) -> list[str]:
        """List names of available registered MCP tools."""
        return list(self._registry.keys())

    def execute_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Execute named MCP tool with provided arguments."""
        if tool_name not in self._registry:
            raise KeyError(f"MCP tool '{tool_name}' is not registered.")

        func = self._registry[tool_name]
        logger.info(f"MCP Client invoking tool '{tool_name}' with args {arguments}")
        try:
            result = func(**arguments)
            if isinstance(result, ExecutionResult):
                return result.model_dump()
            return result
        except Exception as e:
            logger.error(f"Error executing MCP tool '{tool_name}': {e}")
            return {"error": str(e), "status": "failed"}
