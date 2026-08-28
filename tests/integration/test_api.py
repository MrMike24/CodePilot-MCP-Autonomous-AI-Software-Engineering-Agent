import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.database.session import init_db
from backend.app.main import app


@pytest.fixture(autouse=True)
async def setup_database():
    await init_db()


@pytest.mark.integration
async def test_health_check_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/v1/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "online"
        assert data["project"] == "CodePilot-MCP"
        assert "database" in data


@pytest.mark.integration
async def test_task_creation_and_listing():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create Task
        res = await client.post(
            "/api/v1/tasks",
            json={"title": "Integration Task", "description": "Test FastAPI Endpoint"},
        )
        assert res.status_code == 201
        data = res.json()
        assert data["title"] == "Integration Task"
        assert data["status"] in ["CREATED", "PENDING", "PLANNING", "WAITING_APPROVAL"]

        # List Tasks
        list_res = await client.get("/api/v1/tasks")
        assert list_res.status_code == 200
        tasks = list_res.json()
        assert len(tasks) >= 1
        assert any(t["id"] == data["id"] for t in tasks)
