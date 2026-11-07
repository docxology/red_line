# canary tests

This folder exercises registry hashing, canary issuance, verification, and the script entrypoints that expose them. It keeps the committed canary fixture tied to the real package APIs.

## Historical module inventory — 2026-10-21

| Module | What it exercises | Collected tests |
| --- | --- | --- |
| [test_hashing.py](test_hashing.py) | Deterministic registry and line digests, including the committed hash anchor. | 8 |
| [test_scripts.py](test_scripts.py) | CLI build/check behavior, real subprocess execution, and committed fixture parity. | 9 |
| [test_statement.py](test_statement.py) | Issued canary metadata, successor rationale, and added or removed line reporting. | 10 |
| [test_verification.py](test_verification.py) | Freshness, drift detection, aggregate-only statements, and canary-grade escalation. | 16 |

## Run

Use the project venv directly here. In the current managed environment, `uv run` tries to initialize the user-level uv cache, so the direct `.venv` entrypoint is the working form.

```bash
.venv/bin/python -m pytest tests/canary -q
```

## Coverage gate

The project gate lives in [pyproject.toml](../../pyproject.toml) as `--cov-fail-under=90` over `source = ["red_line"]`. These counts and the former `954`-test suite total are historical observations from `2026-10-21`, not current results. Use `.venv/bin/python -m pytest tests/canary --collect-only -q -o addopts=""` from the repository root for the current inventory; use the test command above for current execution evidence.

## Related

- [AGENTS.md](AGENTS.md)
- [canary package](../../src/red_line/canary/README.md)
- [canary_committed.json](../fixtures/canary_committed.json)
