# release tests

This folder exercises the `red_line.release` package: how a source checkout and a rendered artifact tree become recorded evidence, and how that evidence fails closed when a report is missing, unreadable, or negative.

## Modules

| Module | What it exercises | Collected tests |
| --- | --- | --- |
| [test_provenance.py](test_provenance.py) | Chunked file digests, real-repository revision and dirtiness, honest render-toolchain location, and directory digest filtering. | 16 |
| [test_snapshot.py](test_snapshot.py) | Live analysis metrics, figure-registry binding and fallbacks, and snapshot writing. | 8 |
| [test_manifest.py](test_manifest.py) | Candidate-ledger binding, fail-closed report interpretation, publication-gate readiness, pre-render deferral versus decidable failure, manifest assembly, and the recorded renderer when one is and is not present. | 30 |
| [test_determinism.py](test_determinism.py) | Artifact hashing scope, PDF text comparison, drift classification, render invocation against a located toolchain, and two-pass comparison outcomes. | 26 |

## Run

Use the project venv directly here. In the current managed environment, `uv run` tries to initialize the user-level uv cache, so the direct `.venv` entrypoint is the working form.

```bash
.venv/bin/python -m pytest tests/release -q
```

## Coverage gate

The project gate lives in [pyproject.toml](../../pyproject.toml) as `--cov-fail-under=90` over `source = ["red_line"]`. This folder is written to hold `red_line/release/` at full statement and branch coverage; the current full-suite measurement is recorded in the repository [README.md](../../README.md).

## Related

- [AGENTS.md](AGENTS.md)
- [release package](../../src/red_line/release/README.md)
- [scripts](../../scripts/README.md)
