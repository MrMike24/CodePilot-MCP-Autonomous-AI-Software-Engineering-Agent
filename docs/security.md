# Security Architecture & Constraints

Security is a foundational pillar of CodePilot-MCP. The agent is strictly constrained from executing arbitrary, destructive, or unauthorized host operations.

## Security Controls Overview

1. **Workspace Boundary Restrictions**:
   - All filesystem operations are managed by `FilesystemMCPServer`.
   - Target paths undergo canonical path resolution and strict boundary checks against `ALLOWED_HOST_WORKSPACE_ROOT`.
   - Path traversal attempts (`../`) raise `PermissionError`.

2. **Secret Filtering & Redaction**:
   - Access to sensitive files (`.env`, `.git`, `credentials.json`, `id_rsa`) is blocked at the MCP layer.
   - Structured JSON loggers sanitize log outputs, redacting API keys, passwords, and tokens.

3. **Sandboxed Code Execution**:
   - Code execution occurs inside Docker containers (`python:3.12-slim`).
   - Resource limits enforced: CPU caps, memory limits (512MB), timeouts (120s), and disabled network access (`--network none`).

4. **Human-in-the-Loop Approval Gates**:
   - The agent cannot automatically merge pull requests or push to protected branches.
   - Explicit human approval via the React web UI is required before PR creation.

5. **Role-Based Access Control (RBAC)**:
   - Tool permissions gated by role (`developer`, `reviewer`, `admin`).
