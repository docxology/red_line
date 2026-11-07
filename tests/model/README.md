# model tests

This folder exercises the core data model: dataclasses, enums, normalization helpers, and evidence-record validation. It keeps the domain foundation tied to the real package types.

## Historical module inventory — 2026-10-21

| Module | What it exercises | Collected tests |
| --- | --- | --- |
| [test_action.py](test_action.py) | Action, context, evidence-record, and outside-scope semantics. | 11 |
| [test_enums.py](test_enums.py) | Deployment-tier oversight ordering. | 1 |
| [test_red_line.py](test_red_line.py) | Registry shape, carve-outs, normalization, and typed exemptions. | 24 |

## Run

Use the project venv directly here. In the current managed environment, `uv run` tries to initialize the user-level uv cache, so the direct `.venv` entrypoint is the working form.

```bash
.venv/bin/python -m pytest tests/model -q
```

## Coverage gate

The project gate lives in [pyproject.toml](../../pyproject.toml) as `--cov-fail-under=90` over `source = ["red_line"]`. These counts and the former `954`-test suite total are historical observations from `2026-10-21`, not current results. Use `.venv/bin/python -m pytest tests/model --collect-only -q -o addopts=""` from the repository root for the current inventory; use the test command above for current execution evidence.

## Related

- [AGENTS.md](AGENTS.md)
- [model package](../../src/red_line/model/README.md)
