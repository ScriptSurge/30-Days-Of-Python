"""
Example test file for authentication endpoints.

Run with: pytest app/tests/
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_login_placeholder():
    """Test login endpoint (placeholder)."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "password"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


# TODO: Add more tests as endpoints are implemented
