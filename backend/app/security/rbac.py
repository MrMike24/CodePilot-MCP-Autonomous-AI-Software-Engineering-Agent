from typing import Literal
from backend.app.core.logging import logger

Role = Literal["developer", "reviewer", "admin"]

ROLE_PERMISSIONS: dict[Role, set[str]] = {
    "developer": {
        "list_directory",
        "read_file",
        "create_file",
        "write_file",
        "search_files",
        "get_diff",
        "get_repository",
        "list_files",
        "get_file",
        "search_code",
        "get_issue",
        "list_issues",
        "get_pull_request",
        "create_branch",
        "get_commit_history",
        "run_tests",
        "run_linter",
        "run_typecheck",
        "run_security_scan",
    },
    "reviewer": {
        "list_directory",
        "read_file",
        "create_file",
        "write_file",
        "search_files",
        "get_diff",
        "get_repository",
        "list_files",
        "get_file",
        "search_code",
        "get_issue",
        "list_issues",
        "get_pull_request",
        "create_branch",
        "get_commit_history",
        "run_tests",
        "run_linter",
        "run_typecheck",
        "run_security_scan",
        "approve_pr",
        "reject_pr",
        "create_pull_request",
    },
    "admin": {
        "*",  # All tools permitted
    },
}


class SecurityPolicy:
    """RBAC security policy and tool authorization gatekeeper."""

    @staticmethod
    def check_tool_permission(user_role: Role, tool_name: str) -> bool:
        """Check if user role is authorized to execute specified tool."""
        allowed = ROLE_PERMISSIONS.get(user_role, set())
        if "*" in allowed or tool_name in allowed:
            return True

        logger.warning(f"RBAC Permission Denied: Role '{user_role}' attempted to execute unauthorized tool '{tool_name}'")
        return False
