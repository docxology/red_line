# analysis tests

This folder exercises the read-only analysis package through the live registry and the real evaluator. It binds computed reports back to actual registry structure instead of fixture stubs.

## Historical module inventory — 2026-10-21

| Module | What it exercises | Collected tests |
| --- | --- | --- |
| [test_monotonicity_sweep.py](test_monotonicity_sweep.py) | Exhaustive tier-lattice sweep over every live scope keyword. | 10 |
| [test_outcome_coverage.py](test_outcome_coverage.py) | Five-outcome reachability battery plus negative controls. | 16 |
| [test_registry_metrics.py](test_registry_metrics.py) | Registry composition metrics and proof-of-detection for planted defects. | 24 |
| [test_decision_surface.py](test_decision_surface.py) | Single-dimension evidence perturbation sweep and ANY/ALL trigger probe, with positive controls. | 18 |

## Run

Use the project venv directly here. In the current managed environment, `uv run` tries to initialize the user-level uv cache, so the direct `.venv` entrypoint is the working form.

```bash
.venv/bin/python -m pytest tests/analysis -q
```

## Coverage gate

The project gate lives in [pyproject.toml](../../pyproject.toml) as `--cov-fail-under=90` over `source = ["red_line"]`. These counts and the former `954`-test suite total are historical observations from `2026-10-21`, not current results. Use `.venv/bin/python -m pytest tests/analysis --collect-only -q -o addopts=""` from the repository root for the current inventory; use the test command above for current execution evidence.

## Related

- [AGENTS.md](AGENTS.md)
- [analysis package](../../src/red_line/analysis/README.md)
