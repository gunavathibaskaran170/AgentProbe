from __future__ import annotations

import httpx
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.errors import chatbot_unreachable, not_found
from app.models import Result, Run, TestCase
from app.schemas import (
    RunCreate,
    RunOut,
    RunSummary,
    VerificationResult,
)
from app.verifier import verify_answer

router = APIRouter(tags=["runs"])

CHATBOT_TIMEOUT_SECONDS = 30.0


def _ask_chatbot(chatbot_url: str, question: str) -> str:
    """Send one question and return the chatbot's answer string."""
    try:
        response = httpx.post(
            chatbot_url,
            json={"message": question},
            timeout=CHATBOT_TIMEOUT_SECONDS,
        )
    except httpx.HTTPError as exc:
        raise chatbot_unreachable(
            f"Could not reach chatbot at {chatbot_url}"
        ) from exc

    if not 200 <= response.status_code < 300:
        raise chatbot_unreachable(
            f"Chatbot at {chatbot_url} returned HTTP {response.status_code}"
        )

    try:
        data = response.json()
        answer = data["answer"]
        if not isinstance(answer, str):
            raise ValueError("answer must be a string")
    except (KeyError, TypeError, ValueError) as exc:
        raise chatbot_unreachable(
            f"Chatbot at {chatbot_url} returned an invalid response"
        ) from exc

    return answer


def _run_out(run: Run) -> RunOut:
    results = sorted(run.results, key=lambda item: item.test_id)
    total = len(results)
    verified = sum(1 for item in results if item.status == "verified")
    summary = RunSummary(
        total=total,
        verified=verified,
        failed=total - verified,
        pass_rate=round(verified / total, 2) if total else 0.0,
    )
    return RunOut(
        id=run.id,
        version_label=run.version_label,
        chatbot_url=run.chatbot_url,
        status=run.status,
        summary=summary,
        results=[VerificationResult.model_validate(item) for item in results],
    )


@router.post("/runs", response_model=RunOut, status_code=status.HTTP_201_CREATED)
def create_run(payload: RunCreate, db: Session = Depends(get_db)) -> RunOut:
    test_cases = db.query(TestCase).order_by(TestCase.id).all()

    # Complete every external call and verification before writing anything,
    # so a chatbot failure never leaves a partial run behind.
    verification_results: list[dict] = []
    for test_case in test_cases:
        answer = _ask_chatbot(payload.chatbot_url, test_case.question)
        verification_results.append(
            verify_answer(
                {
                    "id": test_case.id,
                    "name": test_case.name,
                    "domain": test_case.domain,
                    "question": test_case.question,
                    "expected_info": test_case.expected_info,
                    "must_contain": test_case.must_contain,
                    "must_not_contain": test_case.must_not_contain,
                    "reference_text": test_case.reference_text,
                },
                answer,
            )
        )

    run = Run(
        version_label=payload.version_label,
        chatbot_url=payload.chatbot_url,
        status="completed",
    )
    for verification in verification_results:
        run.results.append(Result(**verification))

    db.add(run)
    db.commit()
    db.refresh(run)
    return _run_out(run)


@router.get("/runs/{run_id}", response_model=RunOut)
def get_run(run_id: int, db: Session = Depends(get_db)) -> RunOut:
    run = db.query(Run).filter(Run.id == run_id).first()
    if run is None:
        raise not_found(f"Run {run_id} not found")
    return _run_out(run)
