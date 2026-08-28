import asyncio
import pytest
from unittest.mock import patch
from httpx import ASGITransport, AsyncClient
from backend.app.main import app
from backend.app.database.session import AsyncSessionLocal
from backend.app.services.task_service import TaskService
from backend.app.services.task_worker import run_agent_task_worker


@pytest.mark.asyncio
async def test_real_end_to_end_agent_pipeline_and_approval_gate():
    """Verify real end-to-end agent execution pipeline:

    Task Creation -> Background Worker -> Planning -> Code RAG -> Coder -> Sandbox Test -> Reviewer
    -> Pauses at WAITING_APPROVAL (PR blocked) -> Operator Approval -> PR Creation -> DELIVERED
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Create Engineering Task via REST API
        create_res = await client.post(
            "/api/v1/tasks",
            json={
                "title": "Fix HTTP 500 when email is empty in FastAPI user route",
                "description": "Fix the bug where the API returns HTTP 500 when the user submits an empty email address. Add regression tests.",
                "target_branch": "main",
            },
        )
        assert create_res.status_code == 201
        task_data = create_res.json()
        task_id = task_data["id"]
        assert task_data["status"] == "CREATED"

        # 2. Poll until background worker reaches WAITING_APPROVAL
        detail = None
        for _ in range(30):
            await asyncio.sleep(0.5)
            get_res = await client.get(f"/api/v1/tasks/{task_id}")
            assert get_res.status_code == 200
            detail = get_res.json()
            if detail["status"] in ["WAITING_APPROVAL", "COMPLETED", "FAILED"]:
                break

        assert detail is not None
        assert detail["status"] == "WAITING_APPROVAL"
        assert detail["runs"] is not None
        assert len(detail["runs"]) >= 1

        # Verify tool calls are serialized properly with arguments and result
        first_step = detail["runs"][0]["steps"][0]
        assert len(first_step["tool_calls"]) >= 1
        tc = first_step["tool_calls"][0]
        assert "tool_name" in tc
        assert "arguments" in tc
        assert "result" in tc

        # 3. Verify task paused at HUMAN APPROVAL GATE (WAITING_APPROVAL)
        async with AsyncSessionLocal() as db:
            service = TaskService(db)
            task = await service.get_task(task_id)
            assert task is not None
            assert task.status == "WAITING_APPROVAL"
            # Ensure PR was NOT created automatically before human approval!
            assert len(task.pull_requests) == 0

            # Verify step traces recorded in DB
            assert len(task.runs) >= 1
            steps = task.runs[0].steps
            agent_names = [s.agent_name for s in steps]
            assert "Planner" in agent_names
            assert "Code RAG" in agent_names
            assert "Coder" in agent_names
            assert "Execution" in agent_names
            assert "Reviewer" in agent_names

        # 4. Explicit Human Operator Approval via REST API
        with patch(
            "mcp_servers.github.server.GitHubMCPServer.create_pull_request",
            return_value={
                "pr_number": 42,
                "pr_url": "https://github.com/codepilot-org/demo_repository/pull/42",
                "head_branch": "codepilot/task-fix",
                "base_branch": "main",
                "status": "created",
                "is_simulated": False,
                "verified": True,
            },
        ):
            approve_res = await client.post(
                f"/api/v1/tasks/{task_id}/approve",
                json={
                    "approved": True,
                    "comments": "Approved by human operator after review of diff and test scorecard.",
                    "approved_by": "lead_engineer",
                },
            )
            assert approve_res.status_code == 200
            assert approve_res.json()["status"] == "APPROVED"

        # 5. Verify PR Creation and final status DELIVERED
        async with AsyncSessionLocal() as db:
            service = TaskService(db)
            task = await service.get_task(task_id)
            assert task is not None
            assert task.status == "DELIVERED"
            assert len(task.pull_requests) == 1
            pr = task.pull_requests[0]
            assert pr.pr_number == 42
            assert "codepilot-org" in pr.pr_url


@pytest.mark.asyncio
async def test_rate_limiting_autonomous_pipeline():
    """Verify rate-limiting engineering task through complete autonomous pipeline."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        create_res = await client.post(
            "/api/v1/tasks",
            json={
                "title": "Add Rate Limiting to FastAPI Authentication Endpoints",
                "description": "Implement rate limiting for authentication/login endpoints. Return HTTP 429 Too Many Requests when limit exceeded. Environment variable based configuration.",
                "target_branch": "main",
            },
        )
        assert create_res.status_code == 201
        task_id = create_res.json()["id"]

        detail = None
        for _ in range(30):
            await asyncio.sleep(0.5)
            get_res = await client.get(f"/api/v1/tasks/{task_id}")
            assert get_res.status_code == 200
            detail = get_res.json()
            if detail["status"] in ["WAITING_APPROVAL", "COMPLETED", "FAILED"]:
                break

        assert detail is not None
        assert detail["status"] == "WAITING_APPROVAL"
        assert detail["diff_summary"] is not None
        assert "rate_limiter" in detail["diff_summary"] or "rate_limit" in detail["diff_summary"]
        assert detail["review"] is not None
        if not detail["review"]["approved"]:
            print("\n=== REVIEW FINDINGS ===")
            print(detail["review"])
            print("=== EXECUTION RESULT ===")
            print(detail.get("execution_result"))
        assert detail["review"]["approved"] is True
        assert detail["pull_request"] is None  # Blocked before approval!
