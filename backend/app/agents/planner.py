from typing import Any
from backend.app.agents.state import AgentState
from backend.app.core.logging import logger
from backend.app.schemas.task import TaskPlan, TaskPlanSubtask
from rag.retrieval.vector_store import CodeRAGStore


class PlannerAgent:
    """Planner Agent analyzing user task and formulating structured engineering plan."""

    def __init__(self, rag_store: CodeRAGStore):
        self.rag_store = rag_store

    def run(self, state: AgentState) -> dict[str, Any]:
        logger.info(f"PlannerAgent processing task: '{state.get('task_title')}'")

        query = f"{state.get('task_title')} {state.get('task_description')}"
        retrieved = self.rag_store.retrieve_code(query=query, top_k=5)

        relevant_files = list(set([item["file"] for item in retrieved]))
        if not relevant_files:
            relevant_files = ["app/main.py", "tests/test_api.py"]

        title = state.get("task_title", "Engineering Task")
        description = state.get("task_description", "")

        subtasks = [
            TaskPlanSubtask(
                id=1,
                title="Inspect repository context & Code RAG retrieval",
                description=f"Analyze retrieved code chunks and locate affected modules for: {title}",
                target_files=relevant_files,
            ),
            TaskPlanSubtask(
                id=2,
                title="Implement requested architecture changes",
                description=f"Apply code modifications to satisfy: {description or title}",
                target_files=relevant_files,
            ),
            TaskPlanSubtask(
                id=3,
                title="Add unit and regression test coverage",
                description="Add automated test cases verifying feature functionality and edge cases in the test suite.",
                target_files=["tests/test_api.py", "tests/test_rate_limit.py"],
            ),
            TaskPlanSubtask(
                id=4,
                title="Execute sandboxed test validation and code review",
                description="Run pytest suite inside sandbox and generate reviewer quality scorecard.",
                target_files=relevant_files,
            ),
        ]

        plan = TaskPlan(
            summary=f"Implementation plan for: {title}",
            subtasks=subtasks,
            relevant_files=relevant_files,
            required_tools=["read_file", "write_file", "run_tests", "get_diff"],
            risks=["Ensure backward compatibility and maintain existing API contract specifications."],
            test_strategy="Execute pytest inside isolated sandbox container with regression validation.",
        )

        return {
            "plan": plan,
            "retrieved_context": retrieved,
            "status": "PLANNING_COMPLETE",
        }
