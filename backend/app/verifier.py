"""Placeholder verification logic.

The real engine will replace the body of verify_answer later. Keep this
signature and return shape exactly as defined in docs/API_CONTRACT.md.
"""

from __future__ import annotations


def verify_answer(test_case: dict, answer: str) -> dict:
    """Verify one chatbot answer against one test case.

    Placeholder rules (case-insensitive):
      - verified: every must_contain term is present and no must_not_contain
        term is present;
      - contradicted: at least one must_not_contain term is present;
      - unverified: otherwise.
    """
    answer_lower = answer.lower()
    must_contain = [str(term) for term in (test_case.get("must_contain") or [])]
    must_not_contain = [str(term) for term in (test_case.get("must_not_contain") or [])]

    missing = [term for term in must_contain if term.lower() not in answer_lower]
    forbidden = [term for term in must_not_contain if term.lower() in answer_lower]
    reference_text = str(test_case.get("reference_text") or "")

    if forbidden:
        status = "contradicted"
        score = 0.0
        reason = f"Answer contains forbidden term(s): {', '.join(forbidden)}."
        evidence = [{"source": "answer", "snippet": forbidden[0]}]
        checks = {
            "rules_passed": False,
            "similarity": 0.0,
            "judge_verdict": "fail",
        }
    elif missing:
        status = "unverified"
        found = len(must_contain) - len(missing)
        score = round(found / len(must_contain), 2) if must_contain else 0.0
        reason = f"Missing required term(s): {', '.join(missing)}."
        evidence = (
            [{"source": "reference_text", "snippet": reference_text}]
            if reference_text
            else []
        )
        checks = {
            "rules_passed": False,
            "similarity": score,
            "judge_verdict": "unreviewed",
        }
    else:
        status = "verified"
        score = 1.0
        reason = "All required terms found and no forbidden terms found."
        evidence = (
            [{"source": "reference_text", "snippet": reference_text}]
            if reference_text
            else []
        )
        checks = {
            "rules_passed": True,
            "similarity": 1.0,
            "judge_verdict": "pass",
        }

    return {
        "test_id": test_case["id"],
        "answer": answer,
        "status": status,
        "score": score,
        "reason": reason,
        "evidence": evidence,
        "checks": checks,
    }
