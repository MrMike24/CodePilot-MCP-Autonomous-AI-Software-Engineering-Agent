import pytest
from backend.app.security.rbac import SecurityPolicy


@pytest.mark.security
def test_security_policy_rbac():
    # Developer role permissions
    assert SecurityPolicy.check_tool_permission("developer", "read_file") is True
    assert SecurityPolicy.check_tool_permission("developer", "run_tests") is True
    assert SecurityPolicy.check_tool_permission("developer", "approve_pr") is False

    # Reviewer role permissions
    assert SecurityPolicy.check_tool_permission("reviewer", "read_file") is True
    assert SecurityPolicy.check_tool_permission("reviewer", "approve_pr") is True
    assert SecurityPolicy.check_tool_permission("reviewer", "create_pull_request") is True

    # Admin role permissions
    assert SecurityPolicy.check_tool_permission("admin", "any_random_tool") is True
