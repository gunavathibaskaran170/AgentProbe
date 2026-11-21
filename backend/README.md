# AgentProbe backend

FastAPI backend for AgentProbe. It stores test cases, runs them against a
chatbot over HTTP, verifies the answers, and stores a report.

The API contract lives in `docs/API_CONTRACT.md` at the repository root.
All endpoints are mounted under `/api`.

## Requirements

- Python 3.11 or newer
- Packages listed in `backend/requirements.txt` (FastAPI, uvicorn, SQLAlchemy,
  httpx, pytest). Pydantic is installed as a FastAPI dependency.

No secrets are stored in code. The only setting is the database URL, read from
the `AGENTPROBE_DATABASE_URL` environment variable with a safe default.

## Install (Windows PowerShell)

```powershell
cd C:\Users\Gunavathi\agentprobe\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks the activation script in your environment, run this once
first:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

If the packages are already installed globally, the venv steps are optional
and you can use `python` directly.

## Database

The SQLite database `backend/agentprobe.db` is created automatically when the
API starts. All tables are created on startup; no migration tool is used.

To use a different database file, set the environment variable before starting
the server (use forward slashes in the SQLite URL):

```powershell
$env:AGENTPROBE_DATABASE_URL = "sqlite:///C:/Users/Gunavathi/agentprobe/backend/other.db"
```

## Run the API

```powershell
cd C:\Users\Gunavathi\agentprobe\backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- Health check: `http://127.0.0.1:8000/api/health` -> `{"status":"ok"}`
- Interactive docs: `http://127.0.0.1:8000/docs`
- CORS allows only `http://localhost:5173`.

## Run the tests

```powershell
cd C:\Users\Gunavathi\agentprobe\backend
python -m pytest tests -q
```

Tests point `AGENTPROBE_DATABASE_URL` at a temporary directory before the app
is imported, so they never touch `backend/agentprobe.db`. The chatbot call is
mocked, so no mock chatbot needs to be running.

## Mock chatbot (local development only)

`tools/mock_chatbot.py` is a tiny FastAPI app that listens on port 9000 and
answers `POST /chat` with a fixed answer per question. The "passing mark"
answer is deliberately wrong so you can see a `contradicted` result.

Start it in its own terminal:

```powershell
cd C:\Users\Gunavathi\agentprobe\backend
python tools/mock_chatbot.py
```

Example request body:

```json
{"message": "What is the minimum attendance required?"}
```

Example response body:

```json
{"answer": "Students need at least 75 percent attendance to sit exams."}
```

Known questions:

| Question | Answer |
| --- | --- |
| `What is the minimum attendance required?` | `Students need at least 75 percent attendance to sit exams.` |
| `What is the passing mark?` | `You need 65 percent to pass.` (deliberately wrong) |

Any other question gets `I am not sure about that.`

## Manual end-to-end test

1. Start the mock chatbot (terminal 1, command above).
2. Start the API (terminal 2, command above).
3. Open `http://127.0.0.1:8000/docs`.
4. Call `POST /api/tests` twice with these bodies:

```json
{"name":"Attendance rule","domain":"education","question":"What is the minimum attendance required?","expected_info":"Minimum attendance is 75 percent.","must_contain":["75"],"must_not_contain":["65","60"],"reference_text":"Students need at least 75 percent attendance to sit exams."}
```

```json
{"name":"Passing mark","domain":"education","question":"What is the passing mark?","expected_info":"The passing mark is 40 percent.","must_contain":["40"],"must_not_contain":["65"],"reference_text":"Students need at least 40 percent to pass."}
```

5. Call `POST /api/runs` with:

```json
{"version_label":"bot_v1","chatbot_url":"http://127.0.0.1:9000/chat"}
```

Expected summary:

```json
{"total":2,"verified":1,"failed":1,"pass_rate":0.5}
```

6. Call `GET /api/runs/1` to see the stored report.

POST `/api/runs` sends `{"message": question}` to the chatbot with a 30-second
timeout. If the chatbot cannot be reached or returns invalid data, the API
returns `CHATBOT_UNREACHABLE` (HTTP 502) and saves nothing.

## Verification

Verification currently uses a placeholder in `app/verifier.py`:

- `verified` when every `must_contain` term appears and no `must_not_contain`
  term appears in the answer;
- `contradicted` when a `must_not_contain` term appears;
- `unverified` otherwise.

Matching is case-insensitive substring matching. The real engine will replace
only the body of `verify_answer(test_case: dict, answer: str) -> dict`.

## Errors

Errors always use this shape:

```json
{"error": {"code": "NOT_FOUND", "message": "Run 999 not found"}}
```

Codes: `NOT_FOUND` (404), `VALIDATION_ERROR` (422),
`CHATBOT_UNREACHABLE` (502), `INTERNAL_ERROR` (500).

## Layout

```
backend/
  app/
    main.py            FastAPI app, CORS, routers, error handlers
    db.py              engine, session, Base, startup table creation
    models.py          TestCase, Run, Result tables
    schemas.py         Pydantic models matching the contract
    errors.py          error helpers
    verifier.py        placeholder verify_answer()
    routes/
      health.py
      tests.py
      runs.py
  tools/
    mock_chatbot.py    local fake chatbot on port 9000
  tests/
    test_health.py
    test_tests_api.py
    test_runs_api.py
    conftest.py        temporary database setup
  requirements.txt
  README.md
```
