from __future__ import annotations

from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient

from app import routes
from app.db import SessionLocal
from app.models import Result, Run

CHATBOT_URL = "http://localhost:9000/chat"


def _create_test_case(
    client: TestClient,
    *,
    name: str,
    question: str,
    must_contain: list[str],
    must_not_contain: list[str],
) -> dict[str, Any]:
    response = client.post(
        "/api/tests",
        json={
            "name": name,
            "domain": "education",
            "question": question,
            "expected_info": "See reference text.",
            "must_contain": must_contain,
            "must_not_contain": must_not_contain,
            "reference_text": "Reference text for this question.",
        },
    )
    assert response.status_code == 201
    return response.json()


def _install_fake_chatbot(
    monkeypatch: pytest.MonkeyPatch,
    answers: dict[str, str],
) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []

    def fake_post(url: str, *, json: dict[str, str], timeout: float) -> httpx.Response:
        calls.append({"url": url, "json": json, "timeout": timeout})
        return httpx.Response(200, json={"answer": answers[json["message"]]})

    monkeypatch.setattr(routes.runs.httpx, "post", fake_post)
    return calls


def test_create_run_uses_contract_shapes_and_summary(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    first = _create_test_case(
        client,
        name="Attendance rule",
        question="What is the minimum attendance required?",
        must_contain=["75"],
        must_not_contain=["65", "60"],
    )
    second = _create_test_case(
        client,
        name="Passing mark",
        question="What is the passing mark?",
        must_contain=["40"],
        must_not_contain=["65"],
    )
    calls = _install_fake_chatbot(
        monkeypatch,
        {
            first["question"]: "You need 75 percent attendance.",
            second["question"]: "You need 65 percent to pass.",
        },
    )

    response = client.post(
        "/api/runs",
        json={"version_label": "bot_v1", "chatbot_url": CHATBOT_URL},
    )

    assert response.status_code == 201
    body = response.json()
    assert set(body) == {"id", "version_label", "chatbot_url", "status", "summary", "results"}
    assert body["version_label"] == "bot_v1"
    assert body["chatbot_url"] == CHATBOT_URL
    assert body["status"] == "completed"
    assert body["summary"] == {
        "total": 2,
        "verified": 1,
        "failed": 1,
        "pass_rate": 0.5,
    }

    results = body["results"]
    assert [item["test_id"] for item in results] == [first["id"], second["id"]]
    assert [item["status"] for item in results] == ["verified", "contradicted"]
    assert [item["answer"] for item in results] == [
        "You need 75 percent attendance.",
        "You need 65 percent to pass.",
    ]
    for item in results:
        assert set(item) == {
            "test_id", "answer", "status", "score", "reason", "evidence", "checks",
        }
        assert 0.0 <= item["score"] <= 1.0
        assert item["evidence"]
        assert all(set(evidence) == {"source", "snippet"} for evidence in item["evidence"])
        assert set(item["checks"]) == {"rules_passed", "similarity", "judge_verdict"}

    assert calls == [
        {
            "url": CHATBOT_URL,
            "json": {"message": "What is the minimum attendance required?"},
            "timeout": 30.0,
        },
        {
            "url": CHATBOT_URL,
            "json": {"message": "What is the passing mark?"},
            "timeout": 30.0,
        },
    ]


def test_get_run_returns_saved_run(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    test_case = _create_test_case(
        client,
        name="Attendance rule",
        question="What is the minimum attendance required?",
        must_contain=["75"],
        must_not_contain=["65"],
    )
    _install_fake_chatbot(
        monkeypatch,
        {test_case["question"]: "Attendance is 75 percent."},
    )
    created = client.post(
        "/api/runs",
        json={"version_label": "bot_v2", "chatbot_url": CHATBOT_URL},
    )
    assert created.status_code == 201

    response = client.get(f"/api/runs/{created.json()['id']}")

    assert response.status_code == 200
    assert response.json() == created.json()


def test_get_missing_run_uses_not_found_error_shape(client: TestClient) -> None:
    response = client.get("/api/runs/999")

    assert response.status_code == 404
    assert response.json() == {
        "error": {"code": "NOT_FOUND", "message": "Run 999 not found"}
    }


def test_chatbot_unreachable_saves_nothing(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    _create_test_case(
        client,
        name="Attendance rule",
        question="What is the minimum attendance required?",
        must_contain=["75"],
        must_not_contain=[],
    )

    def failing_post(url: str, *, json: dict[str, str], timeout: float) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    monkeypatch.setattr(routes.runs.httpx, "post", failing_post)

    response = client.post(
        "/api/runs",
        json={"version_label": "bot_v1", "chatbot_url": CHATBOT_URL},
    )

    assert response.status_code == 502
    assert response.json()["error"]["code"] == "CHATBOT_UNREACHABLE"
    with SessionLocal() as db:
        assert db.query(Run).count() == 0
        assert db.query(Result).count() == 0


def test_bad_chatbot_data_saves_nothing(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    _create_test_case(
        client,
        name="Attendance rule",
        question="What is the minimum attendance required?",
        must_contain=["75"],
        must_not_contain=[],
    )

    def bad_data_post(url: str, *, json: dict[str, str], timeout: float) -> httpx.Response:
        return httpx.Response(200, json={"unexpected": "shape"})

    monkeypatch.setattr(routes.runs.httpx, "post", bad_data_post)

    response = client.post(
        "/api/runs",
        json={"version_label": "bot_v1", "chatbot_url": CHATBOT_URL},
    )

    assert response.status_code == 502
    assert response.json()["error"]["code"] == "CHATBOT_UNREACHABLE"
    with SessionLocal() as db:
        assert db.query(Run).count() == 0


def test_chatbot_http_error_saves_nothing(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    _create_test_case(
        client,
        name="Attendance rule",
        question="What is the minimum attendance required?",
        must_contain=["75"],
        must_not_contain=[],
    )

    def error_post(url: str, *, json: dict[str, str], timeout: float) -> httpx.Response:
        return httpx.Response(500, request=httpx.Request("POST", url))

    monkeypatch.setattr(routes.runs.httpx, "post", error_post)

    response = client.post(
        "/api/runs",
        json={"version_label": "bot_v1", "chatbot_url": CHATBOT_URL},
    )

    assert response.status_code == 502
    assert response.json()["error"]["code"] == "CHATBOT_UNREACHABLE"
    with SessionLocal() as db:
        assert db.query(Run).count() == 0


def test_run_without_test_cases_has_zero_summary(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, Any]] = []

    def should_not_be_called(
        url: str,
        *,
        json: dict[str, str],
        timeout: float,
    ) -> httpx.Response:
        calls.append({"url": url, "json": json})
        return httpx.Response(200, json={"answer": "unused"})

    monkeypatch.setattr(routes.runs.httpx, "post", should_not_be_called)

    response = client.post(
        "/api/runs",
        json={"version_label": "empty_bot", "chatbot_url": CHATBOT_URL},
    )

    assert response.status_code == 201
    assert response.json()["summary"] == {
        "total": 0,
        "verified": 0,
        "failed": 0,
        "pass_rate": 0.0,
    }
    assert response.json()["results"] == []
    assert calls == []
