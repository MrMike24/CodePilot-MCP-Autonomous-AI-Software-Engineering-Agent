from typing import Any, TypedDict
from backend.app.schemas.task import ReviewResult, TaskPlan

MAX_DEBUG_ITERATIONS = 5


class AgentState(TypedDict, total=False):
    """Strongly typed LangGraph agent state container."""

    task_id: str
    task_title: str
    task_description: str
    workspace_root: str
    target_branch: str
    feature_branch: str

    plan: TaskPlan | None
    retrieved_context: list[dict[str, Any]]
    changes_made: list[str]
    diff_summary: str | None
    execution_result: dict[str, Any] | None
    debug_iterations: int

    review: ReviewResult | None
    approval_status: str  # PENDING, APPROVED, REJECTED
    pr_result: dict[str, Any] | None

    status: str
    tool_history: list[dict[str, Any]]
    errors: list[str]
