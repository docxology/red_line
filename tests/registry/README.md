# registry tests

This folder checks the live registry shape and provenance anchors. It keeps the author-attributed, first-person, non-exhaustive registry contract visible with direct assertions over `PERSONAL_RED_LINES`.

## Modules

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

The project gate lives in [pyproject.toml](../../pyproject.toml) as `--cov-fail-under=90` over `source = ["red_line"]`. The current full-suite measurement is `100.00%` with `878` passed tests on `2026-07-29`.

## Related

- [AGENTS.md](AGENTS.md)
- [registry package](../../src/red_line/registry/README.md)
