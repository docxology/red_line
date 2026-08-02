# canary tests

This folder exercises registry hashing, canary issuance, verification, and the script entrypoints that expose them. It keeps the committed canary fixture tied to the real package APIs.

## Modules

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

The project gate lives in [pyproject.toml](../../pyproject.toml) as `--cov-fail-under=90` over `source = ["red_line"]`. The current full-suite measurement is `100.00%` with `878` passed tests on `2026-07-29`.

## Related

- [AGENTS.md](AGENTS.md)
- [canary package](../../src/red_line/canary/README.md)
- [canary_committed.json](../fixtures/canary_committed.json)
