# AgentProbe: Project Brief

AgentProbe tests AI chatbots. It sends test questions to a chatbot, checks
each answer against expected information, and reports what is wrong.

## MVP scope (do NOT build beyond this)

1. Store test cases
2. Run them against a chatbot over HTTP
3. Verify each answer
4. Store results and show a report
   Domain for now: EDUCATION only.

## Verification statuses (only these five)

verified, contradicted, unsupported, partially_verified, unverified
Never mark a claim "contradicted" just because it cannot be found.

## Folders

backend/ (FastAPI), engine/ (pure Python), frontend/ (React).
Each agent edits ONLY its own folder. docs/ is read-only for agents.

## Rules for every agent

- Follow docs/API_CONTRACT.md exactly. If it is unclear, ask. Never change it.
- No secrets in code. Keep it simple. Ask before adding any library.
- Write tests for what you build.
