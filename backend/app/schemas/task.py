from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field


class RepositoryCreate(BaseModel):
    name: str = Field(..., example="demo_repository")
    url: str | None = Field(default=None, example="https://github.com/example/demo_repository")
    default_branch: str = Field(default="main")
    local_path: str = Field(..., example="c:/Users/pramu/Downloads/MCP/demo_repository")


class RepositoryResponse(RepositoryCreate):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskCreate(BaseModel):
    title: str = Field(..., example="Fix HTTP 500 when email is empty")
    description: str = Field(..., example="Fix the bug where the API returns HTTP 500 when the user submits an empty email address. Add regression tests.")
    repository_id: str | None = Field(default=None)
    repository_path: str | None = Field(default=None)
    target_branch: str = Field(default="main")


class TaskPlanSubtask(BaseModel):
    id: int
    title: str
    description: str
    target_files: list[str]


class TaskPlan(BaseModel):
    """Structured plan output from Planner Agent."""
    summary: str
    subtasks: list[TaskPlanSubtask]
    relevant_files: list[str]
    required_tools: list[str]
    risks: list[str]
    test_strategy: str


class ReviewFinding(BaseModel):
    file: str
    line: int | None = None
    issue: str
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]


class ReviewResult(BaseModel):
    """Structured result output from Reviewer Agent."""
    approved: bool
    confidence: float = Field(ge=0.0, le=1.0)
    findings: list[ReviewFinding]
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    recommendations: list[str]
    tests_status: str


class ApprovalRequest(BaseModel):
    approved: bool
    comments: str | None = None
    approved_by: str = Field(default="human_operator")


class ToolCallTrace(BaseModel):
    id: str
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict, validation_alias="arguments_json")
    result: dict[str, Any] = Field(default_factory=dict, validation_alias="result_json")
    status: str
    duration_ms: float
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AgentStepTrace(BaseModel):
    id: str
    agent_name: str
    step_name: str
    status: str
    log_output: str | None = None
    timestamp: datetime
    tool_calls: list[ToolCallTrace] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class AgentRunTrace(BaseModel):
    id: str
    task_id: str
    status: str
    error_message: str | None = None
    start_time: datetime
    end_time: datetime | None = None
    total_tokens: int
    estimated_cost: float
    steps: list[AgentStepTrace] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    repository_id: str
    status: str
    target_branch: str
    feature_branch: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskDetailResponse(TaskResponse):
    repository: RepositoryResponse | None = None
    runs: list[AgentRunTrace] = Field(default_factory=list)
    review: ReviewResult | None = None
    diff_summary: str | None = None
    execution_result: dict[str, Any] | None = None
    pull_request: dict[str, Any] | None = None
