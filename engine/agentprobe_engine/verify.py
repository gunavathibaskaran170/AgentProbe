"""End-to-end verification entry point.

This composes the four engine modules and returns a dict in the exact
VerificationResult shape defined in docs/API_CONTRACT.md.
"""

from __future__ import annotations

from .classify import combine_checks
from .judge import llm_judge
from .rules import check_rules
from .similarity import semantic_similarity

VALID_STATUSES = frozenset(
    {
        "verified",
        "contradicted",
        "unsupported",
        "partially_verified",
        "unverified",
    }
)

PLACEHOLDER_SCORES = {
    "verified": 1.0,
    "partially_verified": 0.5,
    "contradicted": 0.0,
    "unsupported": 0.0,
    "unverified": 0.0,
}


def verify(test_case: dict, answer: str, config: dict | None = None) -> dict:
    """Verify one chatbot answer against one contract TestCase.

    Args:
        test_case: Contract TestCase dict, including ``id``.
        answer: The chatbot answer string.
        config: Reserved for future engine configuration. The placeholders
            ignore it, but the signature matches the contract.

    Returns:
        A VerificationResult dict with exactly: ``test_id``, ``answer``,
        ``status``, ``score``, ``reason``, ``evidence`` and ``checks``.
    """
    rules = check_rules(test_case, answer)

    expected = str(test_case.get("expected_info") or "")
    similarity = semantic_similarity(expected, answer)
    judge = llm_judge(
        str(test_case.get("question") or ""),
        expected,
        answer,
    )

    status = combine_checks(rules, similarity, judge)
    if status not in VALID_STATUSES:
        status = "unverified"

    reference_text = str(test_case.get("reference_text") or "")
    evidence = (
        [{"source": "reference_text", "snippet": reference_text}]
        if reference_text
        else []
    )

    reason_parts: list[str] = []
    if rules["missing"]:
        reason_parts.append("Missing required term(s): " + ", ".join(rules["missing"]) + ".")
    if rules["forbidden_found"]:
        reason_parts.append(
            "Forbidden term(s) found: " + ", ".join(rules["forbidden_found"]) + "."
        )
    if not reason_parts:
        reason_parts.append("Rule checks passed; similarity and judge checks are placeholders.")

    return {
        "test_id": test_case["id"],
        "answer": answer,
        "status": status,
        "score": PLACEHOLDER_SCORES[status],
        "reason": " ".join(reason_parts),
        "evidence": evidence,
        "checks": {
            "rules_passed": rules["passed"],
            "similarity": similarity,
            "judge_verdict": judge.get("verdict", "unknown"),
        },
    }
