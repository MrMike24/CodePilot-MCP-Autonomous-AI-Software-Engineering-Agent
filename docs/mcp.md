# Model Context Protocol (MCP) Integration

CodePilot-MCP utilizes the Model Context Protocol (MCP) as its foundational tool interaction standard. All interactions with external services, filesystems, and execution environments are handled via specialized MCP servers.

## Custom MCP Server Architecture

### 1. Filesystem MCP Server (`mcp_servers/filesystem/server.py`)
Provides safe file workspace operations:
- `list_directory`: Workspace folder navigation.
- `read_file`: Safe text file content reading.
- `create_file`: File creation.
- `write_file`: File modification.
- `search_files`: Regex or keyword content search.
- `get_diff`: Workspace git diff extraction.

**Security Constraints**:
- Path canonicalization prevents directory traversal attacks (`../`).
- Access to sensitive files (`.env`, `.git`, `credentials.json`) is blocked with `PermissionError`.

### 2. GitHub MCP Server (`mcp_servers/github/server.py`)
Provides repository management and PR operations:
- `get_repository`, `list_files`, `get_file`, `search_code`.
- `get_issue`, `list_issues`, `get_pull_request`.
- `create_branch`, `get_commit_history`.
- `create_pull_request`: Supports dry-run simulation when `DEMO_MODE=true`, allowing local offline demonstration without needing GitHub API tokens.

### 3. Execution MCP Server (`mcp_servers/execution/server.py`)
Provides sandboxed tool execution:
- `run_tests`: Pytest suite execution in container/process sandbox.
- `run_linter`: Ruff code linter.
- `run_typecheck`: MyPy static type checking.
- `run_security_scan`: Security rule scanning.

Returns structured `ExecutionResult`:
```json
{
  "command": "python -m pytest tests -v",
  "exit_code": 0,
  "stdout": "...",
  "stderr": "...",
  "duration": 1.85,
  "timed_out": false,
  "tests_passed": 1,
  "tests_failed": 0
}
```
