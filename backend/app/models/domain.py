from datetime import datetime, timezone
from typing import Any
import uuid
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.session import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def generate_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="developer")  # developer, reviewer, admin
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class Repository(Base):
    __tablename__ = "repositories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(512), nullable=True)
    default_branch: Mapped[str] = mapped_column(String(100), default="main")
    local_path: Mapped[str] = mapped_column(String(512), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="repository", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    repository_id: Mapped[str] = mapped_column(String(36), ForeignKey("repositories.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PENDING")
    target_branch: Mapped[str] = mapped_column(String(100), default="main")
    feature_branch: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    repository: Mapped["Repository"] = relationship("Repository", back_populates="tasks")
    runs: Mapped[list["AgentRun"]] = relationship("AgentRun", back_populates="task", cascade="all, delete-orphan")
    execution_results: Mapped[list["ExecutionResultModel"]] = relationship("ExecutionResultModel", back_populates="task")
    reviews: Mapped[list["ReviewModel"]] = relationship("ReviewModel", back_populates="task")
    approvals: Mapped[list["ApprovalModel"]] = relationship("ApprovalModel", back_populates="task")
    pull_requests: Mapped[list["PullRequestModel"]] = relationship("PullRequestModel", back_populates="task")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("tasks.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="RUNNING")  # RUNNING, COMPLETED, FAILED, PAUSED
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    estimated_cost: Mapped[float] = mapped_column(Float, default=0.0)

    task: Mapped["Task"] = relationship("Task", back_populates="runs")
    steps: Mapped[list["AgentStep"]] = relationship("AgentStep", back_populates="run", cascade="all, delete-orphan")


class AgentStep(Base):
    __tablename__ = "agent_steps"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("agent_runs.id"), nullable=False)
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    step_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="IN_PROGRESS")
    log_output: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    run: Mapped["AgentRun"] = relationship("AgentRun", back_populates="steps")
    tool_calls: Mapped[list["ToolCallModel"]] = relationship("ToolCallModel", back_populates="step", cascade="all, delete-orphan")


class ToolCallModel(Base):
    __tablename__ = "tool_calls"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    step_id: Mapped[str] = mapped_column(String(36), ForeignKey("agent_steps.id"), nullable=False)
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False)
    arguments_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    result_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(50), default="SUCCESS")
    duration_ms: Mapped[float] = mapped_column(Float, default=0.0)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    step: Mapped["AgentStep"] = relationship("AgentStep", back_populates="tool_calls")

    @property
    def arguments(self) -> dict[str, Any]:
        return self.arguments_json or {}

    @property
    def result(self) -> dict[str, Any]:
        return self.result_json or {}


class ExecutionResultModel(Base):
    __tablename__ = "execution_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("tasks.id"), nullable=False)
    command: Mapped[str] = mapped_column(String(512), nullable=False)
    exit_code: Mapped[int] = mapped_column(Integer, nullable=False)
    stdout: Mapped[str] = mapped_column(Text, default="")
    stderr: Mapped[str] = mapped_column(Text, default="")
    tests_passed: Mapped[int] = mapped_column(Integer, default=0)
    tests_failed: Mapped[int] = mapped_column(Integer, default=0)
    duration: Mapped[float] = mapped_column(Float, default=0.0)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    task: Mapped["Task"] = relationship("Task", back_populates="execution_results")


class ReviewModel(Base):
    __tablename__ = "reviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("tasks.id"), nullable=False)
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    findings_json: Mapped[list[Any]] = mapped_column(JSON, default=list)
    severity: Mapped[str] = mapped_column(String(50), default="LOW")
    recommendations_json: Mapped[list[Any]] = mapped_column(JSON, default=list)
    tests_status: Mapped[str] = mapped_column(String(100), default="UNKNOWN")
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    task: Mapped["Task"] = relationship("Task", back_populates="reviews")


class ApprovalModel(Base):
    __tablename__ = "approvals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("tasks.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # APPROVED, REJECTED
    approved_by: Mapped[str] = mapped_column(String(100), default="human_operator")
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    task: Mapped["Task"] = relationship("Task", back_populates="approvals")


class PullRequestModel(Base):
    __tablename__ = "pull_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("tasks.id"), nullable=False)
    pr_number: Mapped[int] = mapped_column(Integer, nullable=False)
    pr_url: Mapped[str] = mapped_column(String(512), nullable=False)
    branch_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_simulated: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(50), default="OPEN")
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    task: Mapped["Task"] = relationship("Task", back_populates="pull_requests")


class CostRecord(Base):
    __tablename__ = "cost_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("tasks.id"), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource: Mapped[str] = mapped_column(String(255), nullable=False)
    details_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
