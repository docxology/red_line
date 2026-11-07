# registry tests

This folder checks the live registry shape and provenance anchors. It keeps the author-attributed, first-person, non-exhaustive registry contract visible with direct assertions over `PERSONAL_RED_LINES`.

## Historical module inventory — 2026-10-21

| Module | What it exercises | Collected tests |
| --- | --- | --- |
| [test_lines.py](test_lines.py) | Registry shape counts, carve-outs, and standard-analog presence. | 4 |
| [test_provenance.py](test_provenance.py) | Author provenance, first-person standards, and non-exhaustive registry status. | 8 |

## Run

Use the project venv directly here. In the current managed environment, `uv run` tries to initialize the user-level uv cache, so the direct `.venv` entrypoint is the working form.

```bash
.venv/bin/python -m pytest tests/registry -q
```

## Coverage gate

The project gate lives in [pyproject.toml](../../pyproject.toml) as `--cov-fail-under=90` over `source = ["red_line"]`. These counts and the former `954`-test suite total are historical observations from `2026-10-21`, not current results. Use `.venv/bin/python -m pytest tests/registry --collect-only -q -o addopts=""` from the repository root for the current inventory; use the test command above for current execution evidence.

## Related

- [AGENTS.md](AGENTS.md)
- [registry package](../../src/red_line/registry/README.md)
