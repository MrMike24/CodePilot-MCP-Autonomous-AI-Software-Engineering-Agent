import pytest
import httpx
from backend.app.main import app

@pytest.mark.asyncio
async def test_task_id_and_approval_integrity():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Create a real task
        create_res = await client.post(
            "/api/v1/tasks",
            json={
                "title": "Fix database connection pool timeout in user service",
                "description": "Add connection pool retry logic with exponential backoff and timeout handling.",
                "target_branch": "main",
            },
        )
        assert create_res.status_code == 201
        created_task = create_res.json()
        real_task_id = created_task["id"]
        assert len(real_task_id) > 10, "Task ID should be a valid UUID string"

        # 2. Task list returns the exact real task ID
        list_res = await client.get("/api/v1/tasks")
        assert list_res.status_code == 200
        tasks = list_res.json()
        matching_task = next((t for t in tasks if t["id"] == real_task_id), None)
        assert matching_task is not None, f"Task {real_task_id} not found in task list"
        assert matching_task["id"] == real_task_id

        # 3. Task detail endpoint returns the exact task ID
        detail_res = await client.get(f"/api/v1/tasks/{real_task_id}")
        assert detail_res.status_code == 200
        detail = detail_res.json()
        assert detail["id"] == real_task_id

        # 4. Unknown/stale task ID (such as task-8f92a10b) returns 404
        stale_res = await client.get("/api/v1/tasks/task-8f92a10b")
        assert stale_res.status_code == 404
        assert "not found" in stale_res.json()["detail"].lower()

        stale_approve_res = await client.post(
            "/api/v1/tasks/task-8f92a10b/approve",
            json={"approved": True, "comments": "Approve stale", "approved_by": "test_user"},
        )
        assert stale_approve_res.status_code == 404
        assert "not found" in stale_approve_res.json()["detail"].lower()

        # 5. Approval is rejected with HTTP 400 if task is NOT in WAITING_APPROVAL state
        # (Initially the task is CREATED / RUNNING, not yet WAITING_APPROVAL)
        if detail["status"] != "WAITING_APPROVAL":
            premature_approve_res = await client.post(
                f"/api/v1/tasks/{real_task_id}/approve",
                json={"approved": True, "comments": "Premature approval", "approved_by": "test_user"},
            )
            assert premature_approve_res.status_code == 400
            assert "WAITING_APPROVAL" in premature_approve_res.json()["detail"]

        # 6. Verify PR does not exist before approval
        assert detail.get("pull_request") is None
