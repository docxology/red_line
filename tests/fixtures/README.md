# fixtures

This folder holds committed test fixtures rather than Python test modules. The current fixture is the byte-pinned canary statement used by canary and integration tests.

## Modules

| Surface | Notes |
| --- | --- |
| [canary_committed.json](canary_committed.json) | Committed canary statement fixture with `statement`, `issued_on`, `registry_digest`, `line_ids`, and `line_digests`. |

## Run

This folder has no direct pytest target: `.venv/bin/python -m pytest tests/fixtures -q` reports `no tests collected`. The verified command below is the smallest current fixture-consuming slice.

Use the project venv directly here. In the current managed environment, `uv run` tries to initialize the user-level uv cache, so the direct `.venv` entrypoint is the working form.

```bash
.venv/bin/python -m pytest tests/canary/test_scripts.py tests/integration/test_trust_model.py -q
```

## Coverage gate

The project gate lives in [pyproject.toml](../../pyproject.toml) as `--cov-fail-under=90` over `source = ["red_line"]`. The current full-suite measurement is `100.00%` with `878` passed tests on `2026-07-29`.

## Related

- [AGENTS.md](AGENTS.md)
- [canary_committed.json](canary_committed.json)
- [canary tests](../canary/README.md)
- [integration tests](../integration/README.md)
