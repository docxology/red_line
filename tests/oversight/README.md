# oversight tests

This folder exercises review findings and transparency reports over real actions. It binds the oversight layer to the evaluator and keeps review metadata typed and dated.

## Modules

| Module | What it exercises | Collected tests |
| --- | --- | --- |
| [test_findings.py](test_findings.py) | Review findings, rendered text, authorizations, provenance fields, and stale-review behavior. | 19 |
| [test_transparency.py](test_transparency.py) | Classification, authorization, and blocked-count aggregation. | 2 |

## Run

Use the project venv directly here. In the current managed environment, `uv run` tries to initialize the user-level uv cache, so the direct `.venv` entrypoint is the working form.

```bash
.venv/bin/python -m pytest tests/oversight -q
```

## Coverage gate

The project gate lives in [pyproject.toml](../../pyproject.toml) as `--cov-fail-under=90` over `source = ["red_line"]`. The suite inventory is synchronized with `953` collected tests on `2026-10-21`. Execution and coverage results belong in the release packet.

## Related

- [AGENTS.md](AGENTS.md)
- [oversight package](../../src/red_line/oversight/README.md)
