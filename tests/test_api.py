from fastapi.testclient import TestClient
from demo_repository.app.main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Demo FastAPI Application"}


def test_create_user_success():
    response = client.post("/users", json={"username": "alice", "email": "alice@example.com"})
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"


def test_create_user_empty_email():
    response = client.post("/users", json={"username": "testuser", "email": ""})
    assert response.status_code == 400
    assert "Email cannot be empty" in response.json()["detail"]
