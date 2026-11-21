from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class TestCaseBase(BaseModel):
    name: str
    domain: str
    question: str
    expected_info: str
    must_contain: list[str]
    must_not_contain: list[str]
    reference_text: str


class TestCaseCreate(TestCaseBase):
    """POST /tests body: a TestCase without an id."""


class TestCaseOut(TestCaseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class ErrorBody(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorBody


class EvidenceItem(BaseModel):
    source: str
    snippet: str


class Checks(BaseModel):
    rules_passed: bool
    similarity: float
    judge_verdict: str


class VerificationResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    test_id: int
    answer: str
    status: str
    score: float
    reason: str
    evidence: list[EvidenceItem]
    checks: Checks


class RunCreate(BaseModel):
    version_label: str
    chatbot_url: str


class RunSummary(BaseModel):
    total: int
    verified: int
    failed: int
    pass_rate: float


class RunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    version_label: str
    chatbot_url: str
    status: str
    summary: RunSummary
    results: list[VerificationResult]
