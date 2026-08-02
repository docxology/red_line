# invariants tests

This folder exercises the structural invariant battery against the live registry and against planted-bad variants. It proves that each check can fail for a known defect instead of passing vacuously.

## Modules

| Module | What it exercises | Collected tests |
| --- | --- | --- |
| [test_checks.py](test_checks.py) | Structural invariant results plus proof-of-detection on planted defects. | 18 |

## Run

Use the project venv directly here. In the current managed environment, `uv run` tries to initialize the user-level uv cache, so the direct `.venv` entrypoint is the working form.

```bash
.venv/bin/python -m pytest tests/invariants -q
```

## Coverage gate

The project gate lives in [pyproject.toml](../../pyproject.toml) as `--cov-fail-under=90` over `source = ["red_line"]`. The current full-suite measurement is `100.00%` with `878` passed tests on `2026-07-29`.

## Related

- [AGENTS.md](AGENTS.md)
- [invariants package](../../src/red_line/invariants/README.md)
