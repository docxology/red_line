# release tests

This folder exercises the `red_line.release` package: how a source checkout and a rendered artifact tree become recorded evidence, and how that evidence fails closed when a report is missing, unreadable, or negative.

## Historical module inventory — 2026-10-21

| Module | What it exercises | Collected tests |
| --- | --- | --- |
| [test_provenance.py](test_provenance.py) | Chunked file digests, real-repository revision and dirtiness, honest render-toolchain location, and directory digest filtering. | 17 |
| [test_snapshot.py](test_snapshot.py) | Live analysis metrics, figure-registry binding and fallbacks, and snapshot writing. | 8 |
| [test_manifest.py](test_manifest.py) | Candidate-ledger binding, fail-closed report interpretation, publication-gate readiness, pre-render deferral versus decidable failure, manifest assembly, and the recorded renderer when one is and is not present. | 32 |
| [test_determinism.py](test_determinism.py) | Artifact hashing scope, aggregate tree digesting, the wheel smoke guard, PDF text comparison, drift classification, render and full-pipeline CLI invocation, and two-pass comparison outcomes. | 62 |

## Run

Use the project venv directly here. In the current managed environment, `uv run` tries to initialize the user-level uv cache, so the direct `.venv` entrypoint is the working form.

```bash
.venv/bin/python -m pytest tests/release -q
```

## Coverage gate

The project gate lives in [pyproject.toml](../../pyproject.toml) as `--cov-fail-under=90` over `source = ["red_line"]`. These counts are a historical inventory from `2026-10-21`, not a current result. Use `.venv/bin/python -m pytest tests/release --collect-only -q -o addopts=""` from the repository root for the current inventory; execution and coverage evidence require running the tests.

## Related

- [AGENTS.md](AGENTS.md)
- [release package](../../src/red_line/release/README.md)
- [scripts](../../scripts/README.md)
