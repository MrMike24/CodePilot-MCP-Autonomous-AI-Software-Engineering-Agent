import pytest
import httpx
import asyncio
from unittest.mock import patch, MagicMock
from backend.app.main import app
from backend.app.database.session import AsyncSessionLocal
from backend.app.services.task_service import TaskService


@pytest.mark.integration
async def test_delivery_fails_gracefully_when_token_missing(monkeypatch):
    """Requirement 10.A & 10.I: Missing token transitions task to DELIVERY_FAILED and blocks DELIVERED status."""
    monkeypatch.setattr("backend.app.core.config.settings.GITHUB_TOKEN", None)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Create Task
        res = await client.post(
            "/api/v1/tasks",
            json={"title": "Test Delivery Failure", "description": "Ensure task does not become DELIVERED without valid GitHub token", "target_branch": "main"},
        )
        assert res.status_code == 201
        task_id = res.json()["id"]

        # Wait for WAITING_APPROVAL
        for _ in range(30):
            await asyncio.sleep(0.3)
            det = (await client.get(f"/api/v1/tasks/{task_id}")).json()
            if det["status"] in ["WAITING_APPROVAL", "COMPLETED", "FAILED"]:
                break

        assert det["status"] == "WAITING_APPROVAL"

        # Attempt Approval -> Should fail GitHub delivery with 400
        app_res = await client.post(
            f"/api/v1/tasks/{task_id}/approve",
            json={"approved": True, "comments": "Approved for delivery"},
        )
        assert app_res.status_code == 400
        assert "GITHUB_TOKEN is not configured" in app_res.json()["detail"]

        # Task must be in DELIVERY_FAILED status and NOT DELIVERED
        final_det = (await client.get(f"/api/v1/tasks/{task_id}")).json()
        assert final_det["status"] == "DELIVERY_FAILED"
        assert final_det["pull_request"] is None


@pytest.mark.integration
async def test_delivery_succeeds_with_verified_pr(monkeypatch):
    """Requirement 10.F, 10.G, 10.J: Successful real PR delivery stores real PR number & URL and transitions to DELIVERED."""
    monkeypatch.setattr("backend.app.core.config.settings.GITHUB_TOKEN", "ghp_mock_live_token_98765")
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Create Task
        res = await client.post(
            "/api/v1/tasks",
            json={"title": "Test Real PR Delivery", "description": "Ensure verified PR URL is persisted", "target_branch": "main"},
        )
        assert res.status_code == 201
        task_id = res.json()["id"]

        # Wait for WAITING_APPROVAL
        for _ in range(30):
            await asyncio.sleep(0.3)
            det = (await client.get(f"/api/v1/tasks/{task_id}")).json()
            if det["status"] in ["WAITING_APPROVAL", "COMPLETED", "FAILED"]:
                break

        assert det["status"] == "WAITING_APPROVAL"

        # Mock GitHub REST API POST and GET responses
        mock_post_resp = MagicMock()
        mock_post_resp.status_code = 201
        mock_post_resp.json.return_value = {
            "number": 1337,
            "html_url": "https://github.com/my-org/my-repo/pull/1337",
            "head": {"sha": "998877665544332211"},
        }

        mock_get_resp = MagicMock()
        mock_get_resp.status_code = 200
        mock_get_resp.json.return_value = {
            "number": 1337,
            "html_url": "https://github.com/my-org/my-repo/pull/1337",
            "title": "Test Real PR Delivery",
            "state": "open",
        }

        with patch("httpx.Client.post", return_value=mock_post_resp), patch("httpx.Client.get", return_value=mock_get_resp):
            app_res = await client.post(
                f"/api/v1/tasks/{task_id}/approve",
                json={"approved": True, "comments": "Approved for real delivery"},
            )
            assert app_res.status_code == 200

            # Verify Task is DELIVERED with exact PR number and URL
            final_det = (await client.get(f"/api/v1/tasks/{task_id}")).json()
            assert final_det["status"] == "DELIVERED"
            assert final_det["pull_request"] is not None
            assert final_det["pull_request"]["pr_number"] == 1337
            assert final_det["pull_request"]["pr_url"] == "https://github.com/my-org/my-repo/pull/1337"
