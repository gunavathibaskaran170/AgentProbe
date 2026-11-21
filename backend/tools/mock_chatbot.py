"""Tiny fake chatbot for manual end-to-end tests.

Run from backend/ with:
    python tools/mock_chatbot.py

It listens on http://127.0.0.1:9000 and answers POST /chat with a fixed
answer per question. The "passing mark" answer is deliberately wrong.
"""

from __future__ import annotations

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="AgentProbe mock chatbot")

ANSWERS: dict[str, str] = {
    "What is the minimum attendance required?": (
        "Students need at least 75 percent attendance to sit exams."
    ),
    # Deliberately wrong: an expected answer of "40 percent" is contradicted.
    "What is the passing mark?": "You need 65 percent to pass.",
}

DEFAULT_ANSWER = "I am not sure about that."


class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
def chat(payload: ChatRequest) -> dict[str, str]:
    return {"answer": ANSWERS.get(payload.message, DEFAULT_ANSWER)}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9000)
