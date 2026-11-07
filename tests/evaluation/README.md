# evaluation tests

This folder exercises the core evaluator over real `ProposedAction` instances. It keeps classification, carve-out, alias, freshness, and tier-floor behavior tied to the live registry.

## Historical module inventory — 2026-10-21

| Module | What it exercises | Collected tests |
| --- | --- | --- |
| [test_evaluator.py](test_evaluator.py) | Classification, carve-outs, aliases, stale evidence, and intake-blocking behavior. | 19 |
| [test_monotonicity.py](test_monotonicity.py) | Tier-floor monotonicity and regression coverage for the pre-fix inversion bug. | 6 |

## Run

Use the project venv directly here. In the current managed environment, `uv run` tries to initialize the user-level uv cache, so the direct `.venv` entrypoint is the working form.

```bash
.venv/bin/python -m pytest tests/evaluation -q
```

## Coverage gate

The project gate lives in [pyproject.toml](../../pyproject.toml) as `--cov-fail-under=90` over `source = ["red_line"]`. These counts and the former `954`-test suite total are historical observations from `2026-10-21`, not current results. Use `.venv/bin/python -m pytest tests/evaluation --collect-only -q -o addopts=""` from the repository root for the current inventory; use the test command above for current execution evidence.

## Related

- [AGENTS.md](AGENTS.md)
- [evaluation package](../../src/red_line/evaluation/README.md)
