"""Deterministic rule checks for a test case and answer.

This module is fully implemented. Checks are case-insensitive substring
matches, and missing/empty term lists are handled safely.
"""

from __future__ import annotations


def check_rules(test_case: dict, answer: str) -> dict:
    """Check required and forbidden terms against an answer.

    Args:
        test_case: A contract TestCase dict. ``must_contain`` and
            ``must_not_contain`` may be missing, ``None``, or empty.
        answer: The chatbot answer to check.

    Returns:
        ``{"passed": bool, "missing": [...], "forbidden_found": [...]}``.
        Returned terms keep their original casing from the test case.
    """
    case = test_case or {}
    answer_lower = str(answer or "").lower()

    must_contain = case.get("must_contain") or []
    must_not_contain = case.get("must_not_contain") or []

    missing = [
        str(term)
        for term in must_contain
        if str(term).lower() not in answer_lower
    ]
    forbidden_found = [
        str(term)
        for term in must_not_contain
        if str(term).lower() in answer_lower
    ]

    return {
        "passed": not missing and not forbidden_found,
        "missing": missing,
        "forbidden_found": forbidden_found,
    }
