# AgentProbe API Contract (v1)

Base URL: http://localhost:8000/api
All bodies are JSON.

## Error format

{ "error": { "code": "NOT_FOUND", "message": "Test case 12 not found" } }
Codes: NOT_FOUND, VALIDATION_ERROR, CHATBOT_UNREACHABLE, INTERNAL_ERROR

## TestCase

{
"id": 1,
"name": "Attendance rule",
"domain": "education",
"question": "What is the minimum attendance required?",
"expected_info": "Minimum attendance is 75 percent.",
"must_contain": ["75"],
"must_not_contain": ["65", "60"],
"reference_text": "Students need at least 75 percent attendance to sit exams."
}

## VerificationResult

{
"test_id": 1,
"answer": "You need 65 percent attendance.",
"status": "contradicted",
"score": 0.12,
"reason": "Answer says 65 but reference says 75.",
"evidence": [ { "source": "reference_text", "snippet": "at least 75 percent" } ],
"checks": { "rules_passed": false, "similarity": 0.31, "judge_verdict": "fail" }
}
status is one of: verified, contradicted, unsupported, partially_verified, unverified
score is a number from 0.0 to 1.0

## Endpoints

GET /health -> { "status": "ok" }
GET /tests -> [TestCase]
POST /tests body: TestCase without id -> 201 TestCase
POST /runs body: { "version_label": "bot_v1", "chatbot_url": "http://localhost:9000/chat" }
-> 201 Run
GET /runs/{id} -> Run

## Run

{
"id": 1,
"version_label": "bot_v1",
"chatbot_url": "http://localhost:9000/chat",
"status": "completed",
"summary": { "total": 10, "verified": 7, "failed": 3, "pass_rate": 0.7 },
"results": [ VerificationResult ]
}

## Chatbot being tested (external)

AgentProbe sends: POST {chatbot_url} { "message": "..." }
It expects: { "answer": "..." }

## Engine interface (Python)

verify(test_case: dict, answer: str, config: dict | None = None) -> dict
Returns a VerificationResult dict exactly as defined above.
