import pytest
import httpx
from unittest.mock import patch
from datetime import datetime, timezone
from backend.app.main import app
from backend.app.database.session import AsyncSessionLocal
from backend.app.services.task_service import TaskService


@pytest.mark.asyncio
async def test_trace_lifecycle_and_persistence_regression():
    """Verify trace event creation, persistence, API retrieval, and retention through full lifecycle."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Create a task
        create_res = await client.post(
            "/api/v1/tasks",
            json={
                "title": "Regression Test: Trace Persistence and Task Lifecycle",
                "description": "Ensure tool call traces are properly recorded, persisted, and retrieved across task lifecycle.",
                "target_branch": "main",
            },
        )
        assert create_res.status_code == 201
        task_data = create_res.json()
        task_id = task_data["id"]

        # 2. Wait for task to progress through pipeline and reach WAITING_APPROVAL
        for _ in range(30):
            import asyncio
            await asyncio.sleep(0.4)
            get_res = await client.get(f"/api/v1/tasks/{task_id}")
            assert get_res.status_code == 200
            detail = get_res.json()
            if detail["status"] in ["WAITING_APPROVAL", "COMPLETED", "FAILED"]:
                break

        assert detail["status"] == "WAITING_APPROVAL"

        # 3. Verify trace structure, task ID scoping, and persistence
        runs = detail.get("runs", [])
        assert len(runs) > 0, "Expected at least 1 agent run in task detail"

        all_tool_calls = []
        for run in runs:
            assert run["task_id"] == task_id
            for step in run.get("steps", []):
                for tc in step.get("tool_calls", []):
                    all_tool_calls.append(tc)
                    # Verify fields are non-empty and properly serialized
                    assert "tool_name" in tc and len(tc["tool_name"]) > 0
                    assert "arguments" in tc and isinstance(tc["arguments"], dict)
                    assert "result" in tc and isinstance(tc["result"], dict)
                    assert "timestamp" in tc and len(tc["timestamp"]) > 0
                    assert "duration_ms" in tc and isinstance(tc["duration_ms"], (int, float))
                    # Ensure no fake demo timestamps
                    assert "11:15:00" not in tc["timestamp"]

        assert len(all_tool_calls) >= 5, f"Expected >= 5 tool calls, found {len(all_tool_calls)}"

        # 4. Direct Database Check
        async with AsyncSessionLocal() as db:
            service = TaskService(db)
            db_task = await service.get_task(task_id)
            assert db_task is not None
            assert len(db_task.runs) > 0
            db_tools_count = sum(len(step.tool_calls) for run in db_task.runs for step in run.steps)
            assert db_tools_count == len(all_tool_calls)

        # 5. Approve Task and Verify Traces are Retained in DELIVERED state
        with patch(
            "mcp_servers.github.server.GitHubMCPServer.create_pull_request",
            return_value={
                "pr_number": 42,
                "pr_url": "https://github.com/codepilot-org/demo_repository/pull/42",
                "head_branch": "codepilot/task-trace",
                "base_branch": "main",
                "status": "created",
                "is_simulated": False,
                "verified": True,
            },
        ):
            app_res = await client.post(
                f"/api/v1/tasks/{task_id}/approve",
                json={
                    "approved": True,
                    "comments": "Approved via regression test suite.",
                    "approved_by": "lead_engineer",
                },
            )
            assert app_res.status_code == 200

        deliv_res = await client.get(f"/api/v1/tasks/{task_id}")
        assert deliv_res.status_code == 200
        deliv_data = deliv_res.json()
        assert deliv_data["status"] == "DELIVERED"

        # Verify all tool call traces are still intact after DELIVERED status
        deliv_runs = deliv_data.get("runs", [])
        assert len(deliv_runs) > 0
        deliv_tool_calls = sum(len(step.get("tool_calls", [])) for run in deliv_runs for step in run.get("steps", []))
        assert deliv_tool_calls == len(all_tool_calls)


@pytest.mark.asyncio
async def test_task_switching_and_isolated_traces():
    """Verify two distinct tasks have strictly isolated traces and do not bleed into each other."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Create Task A
        res_a = await client.post(
            "/api/v1/tasks",
            json={"title": "Task A: Unique Isolation Check", "description": "Desc A", "target_branch": "main"},
        )
        assert res_a.status_code == 201
        id_a = res_a.json()["id"]

        # Create Task B
        res_b = await client.post(
            "/api/v1/tasks",
            json={"title": "Task B: Unique Isolation Check", "description": "Desc B", "target_branch": "main"},
        )
        assert res_b.status_code == 201
        id_b = res_b.json()["id"]

        import asyncio
        # Wait for both to progress
        for _ in range(30):
            await asyncio.sleep(0.4)
            det_a = (await client.get(f"/api/v1/tasks/{id_a}")).json()
            det_b = (await client.get(f"/api/v1/tasks/{id_b}")).json()
            if det_a["status"] in ["WAITING_APPROVAL", "COMPLETED", "FAILED"] and det_b["status"] in ["WAITING_APPROVAL", "COMPLETED", "FAILED"]:
                break

        runs_a = det_a.get("runs", [])
        runs_b = det_b.get("runs", [])

        # Verify task_id scoping on all runs
        for r in runs_a:
            assert r["task_id"] == id_a
            assert r["task_id"] != id_b
        for r in runs_b:
            assert r["task_id"] == id_b
            assert r["task_id"] != id_a
