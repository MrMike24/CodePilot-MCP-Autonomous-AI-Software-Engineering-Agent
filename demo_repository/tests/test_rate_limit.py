import os
import pytest
from fastapi.testclient import TestClient
from demo_repository.app.main import app
from demo_repository.app.rate_limiter import reset_rate_limits

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_limits():
    reset_rate_limits()
    yield
    reset_rate_limits()

def test_auth_login_success():
    response = client.post("/auth/login", json={"username": "admin", "password": "secret123"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_auth_login_invalid_credentials():
    response = client.post("/auth/login", json={"username": "admin", "password": "wrongpassword"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_rate_limiting_exceeded_returns_429():
    os.environ["RATE_LIMIT_MAX_REQUESTS"] = "3"
    os.environ["RATE_LIMIT_WINDOW_SECONDS"] = "60"
    reset_rate_limits()
    # Requests below limit (1, 2, 3)
    for _ in range(3):
        res = client.post("/auth/login", json={"username": "admin", "password": "secret123"})
        assert res.status_code == 200
    # 4th request must exceed rate limit and return HTTP 429
    res = client.post("/auth/login", json={"username": "admin", "password": "secret123"})
    assert res.status_code == 429
    assert "Rate limit exceeded" in res.json()["detail"]
    assert "Retry-After" in res.headers

def test_rate_limit_environment_configuration():
    os.environ["RATE_LIMIT_MAX_REQUESTS"] = "2"
    os.environ["RATE_LIMIT_WINDOW_SECONDS"] = "10"
    reset_rate_limits()
    # 1st request -> OK
    assert client.post("/auth/login", json={"username": "admin", "password": "secret123"}).status_code == 200
    # 2nd request -> OK
    assert client.post("/auth/login", json={"username": "admin", "password": "secret123"}).status_code == 200
    # 3rd request -> HTTP 429
    assert client.post("/auth/login", json={"username": "admin", "password": "secret123"}).status_code == 429
