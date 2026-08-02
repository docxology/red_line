# evaluation tests

This folder exercises the core evaluator over real `ProposedAction` instances. It keeps classification, carve-out, alias, freshness, and tier-floor behavior tied to the live registry.

## Modules

| Module | What it exercises | Collected tests |
| --- | --- | --- |
| [test_evaluator.py](test_evaluator.py) | Classification, carve-outs, aliases, stale evidence, and intake-blocking behavior. | 14 |
| [test_monotonicity.py](test_monotonicity.py) | Tier-floor monotonicity and regression coverage for the pre-fix inversion bug. | 6 |

## Run

Use the project venv directly here. In the current managed environment, `uv run` tries to initialize the user-level uv cache, so the direct `.venv` entrypoint is the working form.

```bash
.venv/bin/python -m pytest tests/evaluation -q
```

## Coverage gate

The project gate lives in [pyproject.toml](../../pyproject.toml) as `--cov-fail-under=90` over `source = ["red_line"]`. The current full-suite measurement is `100.00%` with `878` passed tests on `2026-07-29`.

## Related

- [AGENTS.md](AGENTS.md)
- [evaluation package](../../src/red_line/evaluation/README.md)
