# AgentProbe verification engine (skeleton)

Pure-Python skeleton for the verification engine. It has no web framework, no
database, no external API calls, and no dependencies beyond pytest.

The API contract is in `docs/API_CONTRACT.md` at the repository root.
`verify()` returns a `VerificationResult` dict in that exact shape.

## Modules

| Module | Status | Responsibility |
| --- | --- | --- |
| `agentprobe_engine/__init__.py` | done | Exports `verify`. |
| `agentprobe_engine/rules.py` | fully implemented | Case-insensitive `must_contain` / `must_not_contain` checks. |
| `agentprobe_engine/similarity.py` | TODO | Return a 0.0-1.0 semantic similarity score. Placeholder returns `0.0`. |
| `agentprobe_engine/judge.py` | TODO | Return a judge verdict and reason. Placeholder returns `unknown` / `not implemented`. |
| `agentprobe_engine/classify.py` | TODO | Combine the checks into one of the five allowed statuses. Placeholder returns `unverified`. |
| `agentprobe_engine/verify.py` | done | Calls all four modules and builds the contract result. |

## Run the tests (Windows PowerShell)

```powershell
cd C:\Users\Gunavathi\agentprobe\engine
python -m pytest
```

Use `python -m pytest` (not just `pytest`) so the `engine/` directory is on
`sys.path` and `agentprobe_engine` imports resolve.

## What to implement next

1. `semantic_similarity(a, b)`: replace the `0.0` placeholder with a real
   offline scoring approach.
2. `llm_judge(question, expected, answer)`: implement offline judgment logic;
   do not call a real LLM or external API here.
3. `combine_checks(rules, similarity, judge)`: decide precedence for forbidden
   words, low similarity, partial matches, agreement, and judge disagreement.
   Never mark something `contradicted` just because text was not found.

Keep all signatures and return shapes unchanged so `verify()` continues to
satisfy the contract.
