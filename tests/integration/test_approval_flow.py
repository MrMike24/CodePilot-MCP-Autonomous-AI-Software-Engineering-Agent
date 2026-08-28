import asyncio
import pytest
from unittest.mock import patch
from httpx import AsyncClient, ASGITransport
from backend.app.database.session import init_db
from backend.app.main import app


@pytest.fixture(autouse=True)
async def setup_database():
    await init_db()


@pytest.mark.integration
async def test_approval_flow_approve():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create Task
        res = await client.post(
            "/api/v1/tasks",
            json={"title": "Fix Email Bug", "description": "Fix HTTP 500 when email is empty"},
        )
        assert res.status_code == 201
        task_id = res.json()["id"]

        # Wait for pipeline to reach WAITING_APPROVAL
        for _ in range(25):
            d = await client.get(f"/api/v1/tasks/{task_id}")
            if d.json()["status"] in ["WAITING_APPROVAL", "COMPLETED", "FAILED"]:
                break
            await asyncio.sleep(0.4)

        # Approve Task
        with patch(
            "mcp_servers.github.server.GitHubMCPServer.create_pull_request",
            return_value={
                "pr_number": 42,
                "pr_url": "https://github.com/codepilot-org/demo_repository/pull/42",
                "head_branch": "codepilot/fix",
                "base_branch": "main",
                "status": "created",
                "is_simulated": False,
                "verified": True,
            },
        ):
            app_res = await client.post(
                f"/api/v1/tasks/{task_id}/approve",
                json={"approved": True, "comments": "LGTM! Ready for PR."},
            )
            assert app_res.status_code == 200
            assert app_res.json()["status"] == "APPROVED"
            assert app_res.json()["approved_by"] == "human_operator"

        # Verify Task status
        detail_res = await client.get(f"/api/v1/tasks/{task_id}")
        assert detail_res.status_code == 200
        assert detail_res.json()["status"] in ["APPROVED", "DELIVERED"]


@pytest.mark.integration
async def test_approval_flow_reject():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create Task
        res = await client.post(
            "/api/v1/tasks",
            json={"title": "Refactor Code", "description": "Refactor route handler"},
        )
        assert res.status_code == 201
        task_id = res.json()["id"]

        # Wait for pipeline to reach WAITING_APPROVAL
        for _ in range(25):
            d = await client.get(f"/api/v1/tasks/{task_id}")
            if d.json()["status"] in ["WAITING_APPROVAL", "COMPLETED", "FAILED"]:
                break
            await asyncio.sleep(0.4)

        # Reject Task
        rej_res = await client.post(
            f"/api/v1/tasks/{task_id}/approve",
            json={"approved": False, "comments": "Changes missing unit tests. Rejection required."},
        )
        assert rej_res.status_code == 200
        assert rej_res.json()["status"] == "REJECTED"

        # Verify Task status
        detail_res = await client.get(f"/api/v1/tasks/{task_id}")
        assert detail_res.status_code == 200
        assert detail_res.json()["status"] == "REJECTED"

