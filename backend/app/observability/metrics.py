from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from backend.app.core.logging import logger

# Prometheus Metrics Definitions
AGENT_TASKS_TOTAL = Counter(
    "agent_tasks_total",
    "Total engineering tasks submitted to agent",
    ["status"],
)

AGENT_TASKS_SUCCESS_TOTAL = Counter(
    "agent_tasks_success_total",
    "Total engineering tasks completed successfully",
)

AGENT_TASKS_FAILED_TOTAL = Counter(
    "agent_tasks_failed_total",
    "Total engineering tasks failed",
)

AGENT_TOOL_CALLS_TOTAL = Counter(
    "agent_tool_calls_total",
    "Total MCP tool executions",
    ["tool", "status"],
)

AGENT_TOOL_FAILURES_TOTAL = Counter(
    "agent_tool_failures_total",
    "Total MCP tool execution failures",
    ["tool"],
)

AGENT_TASK_DURATION_SECONDS = Histogram(
    "agent_task_duration_seconds",
    "Total duration of agent task execution in seconds",
)

AGENT_TOOL_DURATION_SECONDS = Histogram(
    "agent_tool_duration_seconds",
    "Duration of individual MCP tool calls in seconds",
    ["tool"],
)

LLM_TOKENS_TOTAL = Counter(
    "llm_tokens_total",
    "Total tokens consumed across LLM requests",
    ["model"],
)

LLM_COST_TOTAL = Counter(
    "llm_cost_total",
    "Estimated total LLM cost in USD",
    ["model"],
)

DEBUG_ITERATIONS_TOTAL = Counter(
    "debug_iterations_total",
    "Total debug loop iterations executed",
)


def record_task_metrics(status: str, duration_sec: float) -> None:
    """Record task completion metrics."""
    AGENT_TASKS_TOTAL.labels(status=status).inc()
    AGENT_TASK_DURATION_SECONDS.observe(duration_sec)
    if status == "COMPLETED":
        AGENT_TASKS_SUCCESS_TOTAL.inc()
    elif status == "FAILED":
        AGENT_TASKS_FAILED_TOTAL.inc()


def record_tool_metrics(tool_name: str, status: str, duration_sec: float) -> None:
    """Record MCP tool call telemetry metrics."""
    AGENT_TOOL_CALLS_TOTAL.labels(tool=tool_name, status=status).inc()
    AGENT_TOOL_DURATION_SECONDS.labels(tool=tool_name).observe(duration_sec)
    if status == "failed":
        AGENT_TOOL_FAILURES_TOTAL.labels(tool=tool_name).inc()


def get_prometheus_metrics() -> tuple[bytes, str]:
    """Generate Prometheus exposition format payload."""
    return generate_latest(), CONTENT_TYPE_LATEST
