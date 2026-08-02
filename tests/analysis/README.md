# analysis tests

This folder exercises the read-only analysis package through the live registry and the real evaluator. It binds computed reports back to actual registry structure instead of fixture stubs.

## Modules

| Module | What it exercises | Collected tests |
| --- | --- | --- |
| [test_monotonicity_sweep.py](test_monotonicity_sweep.py) | Exhaustive tier-lattice sweep over every live scope keyword. | 7 |
| [test_outcome_coverage.py](test_outcome_coverage.py) | Five-outcome reachability battery plus negative controls. | 16 |
| [test_registry_metrics.py](test_registry_metrics.py) | Registry composition metrics and proof-of-detection for planted defects. | 24 |
| [test_decision_surface.py](test_decision_surface.py) | Single-dimension evidence perturbation sweep and ANY/ALL trigger probe, with positive controls. | 18 |

## Run

Use the project venv directly here. In the current managed environment, `uv run` tries to initialize the user-level uv cache, so the direct `.venv` entrypoint is the working form.

```bash
.venv/bin/python -m pytest tests/analysis -q
```

## Coverage gate

The project gate lives in [pyproject.toml](../../pyproject.toml) as `--cov-fail-under=90` over `source = ["red_line"]`. The current full-suite measurement is `100.00%` with `878` passed tests on `2026-07-29`.

## Related

- [AGENTS.md](AGENTS.md)
- [analysis package](../../src/red_line/analysis/README.md)
