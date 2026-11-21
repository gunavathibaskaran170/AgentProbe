"""LLM judge placeholder.

TODO: implement a judge that decides whether the answer is supported by the
expected information and explains why. Do not call any real LLM or external
API in this skeleton; return the fixed placeholder dict below instead.
"""

from __future__ import annotations


def llm_judge(question: str, expected: str, answer: str) -> dict:
    """Judge an answer against expected information for a question.

    TODO: return a dict with at least a ``verdict`` key (for example
    ``pass``/``fail``/``unclear``) and a ``reason`` string. Keep this function
    pure and offline. A real implementation can be dropped in later without
    changing verify()'s contract shape.
    """
    return {"verdict": "unknown", "reason": "not implemented"}
