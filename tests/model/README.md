# model tests

This folder exercises the core data model: dataclasses, enums, normalization helpers, and evidence-record validation. It keeps the domain foundation tied to the real package types.

## Modules

| Module | What it exercises | Collected tests |
| --- | --- | --- |
| [test_action.py](test_action.py) | Action, context, evidence-record, and outside-scope semantics. | 9 |
| [test_enums.py](test_enums.py) | Deployment-tier oversight ordering. | 1 |
| [test_red_line.py](test_red_line.py) | Registry shape, carve-outs, normalization, and typed exemptions. | 10 |

## Run

Use the project venv directly here. In the current managed environment, `uv run` tries to initialize the user-level uv cache, so the direct `.venv` entrypoint is the working form.

```bash
.venv/bin/python -m pytest tests/model -q
```

## Coverage gate

The project gate lives in [pyproject.toml](../../pyproject.toml) as `--cov-fail-under=90` over `source = ["red_line"]`. The current full-suite measurement is `100.00%` with `878` passed tests on `2026-07-29`.

## Related

- [AGENTS.md](AGENTS.md)
- [model package](../../src/red_line/model/README.md)
