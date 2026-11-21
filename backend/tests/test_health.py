from fastapi.testclient import TestClient


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_cors_allows_only_the_frontend_origin(client: TestClient) -> None:
    allowed = client.get(
        "/api/health",
        headers={"Origin": "http://localhost:5173"},
    )
    assert allowed.headers["access-control-allow-origin"] == "http://localhost:5173"

    blocked = client.get(
        "/api/health",
        headers={"Origin": "http://localhost:9999"},
    )
    assert "access-control-allow-origin" not in blocked.headers
