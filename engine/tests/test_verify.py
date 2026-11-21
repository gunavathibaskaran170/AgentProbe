from agentprobe_engine.verify import verify

VALID_STATUSES = {
    "verified",
    "contradicted",
    "unsupported",
    "partially_verified",
    "unverified",
}

TEST_CASE = {
    "id": 1,
    "name": "Attendance rule",
    "domain": "education",
    "question": "What is the minimum attendance required?",
    "expected_info": "Minimum attendance is 75 percent.",
    "must_contain": ["75"],
    "must_not_contain": ["65", "60"],
    "reference_text": "Students need at least 75 percent attendance to sit exams.",
}


def test_verify_returns_contract_shape_and_valid_status() -> None:
    result = verify(TEST_CASE, "You need 75 percent attendance.")

    assert set(result) == {
        "test_id",
        "answer",
        "status",
        "score",
        "reason",
        "evidence",
        "checks",
    }
    assert result["test_id"] == 1
    assert result["answer"] == "You need 75 percent attendance."
    assert result["status"] in VALID_STATUSES
    assert isinstance(result["score"], float)
    assert 0.0 <= result["score"] <= 1.0
    assert isinstance(result["reason"], str) and result["reason"]
    assert isinstance(result["evidence"], list)
    assert all(set(item) == {"source", "snippet"} for item in result["evidence"])
    assert set(result["checks"]) == {
        "rules_passed",
        "similarity",
        "judge_verdict",
    }
    assert result["checks"]["similarity"] == 0.0
    assert result["checks"]["judge_verdict"] == "unknown"


def test_verify_reports_rule_failures_in_reason() -> None:
    result = verify(TEST_CASE, "You need 65 percent attendance.")

    assert result["checks"]["rules_passed"] is False
    assert "65" in result["reason"]
