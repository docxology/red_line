# hardening tests

This folder holds the adversarial battery. It plants malformed states, stale dates, and hostile scope declarations against the real package surfaces and checks that they fail closed.

## Modules

| Module | What it exercises | Collected tests |
| --- | --- | --- |
| [test_canary.py](test_canary.py) | Malformed canary metadata and fail-closed verification. | 31 |
| [test_constructor_rejections.py](test_constructor_rejections.py) | Model and oversight constructor rejection on malformed inputs. | 50 |
| [test_digest.py](test_digest.py) | Digest determinism under reorder and content change. | 5 |
| [test_invariants.py](test_invariants.py) | Planted-bad invariant detection and normalization-aware failures. | 14 |
| [test_registry_anchors.py](test_registry_anchors.py) | Registry severity anchors and canonical tier-token checks. | 2 |
| [test_scope.py](test_scope.py) | Hostile scope declarations, normalization failures, and ambiguity stops. | 11 |
| [test_staleness.py](test_staleness.py) | Exact evidence and canary staleness boundaries. | 12 |

## Run

Use the project venv directly here. In the current managed environment, `uv run` tries to initialize the user-level uv cache, so the direct `.venv` entrypoint is the working form.

```bash
.venv/bin/python -m pytest tests/hardening -q
```

## Coverage gate

The project gate lives in [pyproject.toml](../../pyproject.toml) as `--cov-fail-under=90` over `source = ["red_line"]`. The current full-suite measurement is `100.00%` with `878` passed tests on `2026-07-29`.

## Related

- [AGENTS.md](AGENTS.md)
- [hardening.md](../../docs/hardening.md)
- [invariants package](../../src/red_line/invariants/README.md)
