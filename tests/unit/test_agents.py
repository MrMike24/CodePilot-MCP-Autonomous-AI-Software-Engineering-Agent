import pytest
from backend.app.agents.coder import CoderAgent
from backend.app.agents.debugger import DebuggerAgent
from backend.app.agents.planner import PlannerAgent
from backend.app.agents.reviewer import ReviewerAgent
from backend.app.agents.workflow import AgentOrchestrator
from mcp_servers.client import MCPClientManager
from rag.retrieval.vector_store import CodeRAGStore


@pytest.mark.unit
def test_planner_agent(tmp_path):
    rag = CodeRAGStore()
    planner = PlannerAgent(rag)

    state = {
        "task_id": "test-1",
        "task_title": "Fix HTTP 500 when email is empty",
        "task_description": "Fix empty email validation bug",
        "workspace_root": str(tmp_path),
    }

    res = planner.run(state)
    assert "plan" in res
    plan = res["plan"]
    assert plan.summary != ""
    assert len(plan.subtasks) >= 3
    assert plan.risks != []


@pytest.mark.unit
def test_debugger_agent_max_iterations(tmp_path):
    client = MCPClientManager(str(tmp_path))
    debugger = DebuggerAgent(client)

    state = {
        "debug_iterations": 4,  # Next will reach 5
        "execution_result": {"stdout": "FAILED", "stderr": "Error", "exit_code": 1},
        "workspace_root": str(tmp_path),
    }

    res = debugger.run(state)
    assert res["debug_iterations"] == 5
    assert res["status"] == "FAILED"
    assert "errors" in res


@pytest.mark.unit
def test_reviewer_agent(tmp_path):
    reviewer = ReviewerAgent()

    state = {
        "execution_result": {"exit_code": 0, "tests_passed": 2, "tests_failed": 0},
        "diff_summary": "diff --git a/app.py b/app.py\n+fixed code",
    }

    res = reviewer.run(state)
    assert res["review"].approved is True
    assert res["review"].confidence > 0.90
    assert res["status"] == "WAITING_APPROVAL"


@pytest.mark.unit
def test_agent_orchestrator_full_run(tmp_path):
    # Prepare minimal workspace
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "main.py").write_text('def create_user(user):\n    if not user.email:\n        raise Exception("Database error")\n')
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_api.py").write_text('def test_create_user_empty_email():\n    assert True\n')

    orchestrator = AgentOrchestrator(str(tmp_path))
    final_state = orchestrator.run_task({
        "task_id": "eval-1",
        "task_title": "Fix HTTP 500 when email is empty",
        "task_description": "Fix empty email validation bug",
        "workspace_root": str(tmp_path),
        "target_branch": "main",
        "feature_branch": "codepilot/fix-email",
        "debug_iterations": 0,
    })

    assert final_state["status"] in {"COMPLETED", "WAITING_APPROVAL", "IMPLEMENTATION_COMPLETE"}
    assert final_state.get("plan") is not None
