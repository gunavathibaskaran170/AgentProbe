from typing import Any

from fastapi.testclient import TestClient

TEST_CASE: dict[str, Any] = {
    "name": "Attendance rule",
    "domain": "education",
    "question": "What is the minimum attendance required?",
    "expected_info": "Minimum attendance is 75 percent.",
    "must_contain": ["75"],
    "must_not_contain": ["65", "60"],
    "reference_text": "Students need at least 75 percent attendance to sit exams.",
}


def test_list_tests_is_empty_initially(client: TestClient) -> None:
    response = client.get("/api/tests")

    assert response.status_code == 200
    assert response.json() == []


def test_create_test_returns_201_with_full_test_case(client: TestClient) -> None:
    response = client.post("/api/tests", json=TEST_CASE)

    assert response.status_code == 201
    body = response.json()
    assert body == {**TEST_CASE, "id": 1}
    assert isinstance(body["must_contain"], list)
    assert isinstance(body["must_not_contain"], list)


def test_created_test_appears_in_list(client: TestClient) -> None:
    created = client.post("/api/tests", json=TEST_CASE)
    assert created.status_code == 201

    response = client.get("/api/tests")

    assert response.status_code == 200
    assert response.json() == [created.json()]


def test_validation_error_uses_contract_shape(client: TestClient) -> None:
    payload = {key: value for key, value in TEST_CASE.items() if key != "question"}

    response = client.post("/api/tests", json=payload)

    assert response.status_code == 422
    body = response.json()
    assert set(body) == {"error"}
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert isinstance(body["error"]["message"], str)
    assert body["error"]["message"]
