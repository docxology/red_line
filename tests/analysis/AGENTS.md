# analysis tests - Test-folder guidance

This folder covers analysis reports and their derived counts. It does not cover manuscript prose bindings or release-surface validation; those live under `tests/integration/`.

## Test module inventory

| Module | What it exercises | Collected tests |
| --- | --- | --- |
| [test_monotonicity_sweep.py](test_monotonicity_sweep.py) | Exhaustive tier-lattice sweep over every live scope keyword. | 7 |
| [test_outcome_coverage.py](test_outcome_coverage.py) | Five-outcome reachability battery plus negative controls. | 16 |
| [test_registry_metrics.py](test_registry_metrics.py) | Registry composition metrics and proof-of-detection for planted defects. | 24 |
| [test_decision_surface.py](test_decision_surface.py) | Single-dimension evidence perturbation sweep and ANY/ALL trigger probe, with positive controls. | 18 |

## Helpers

| Surface | Signature or shape | Source | Notes |
| --- | --- | --- | --- |
| `tests.helpers.py` | not imported in this folder | [helpers.py](../helpers.py) | These analysis tests call the live analysis APIs directly instead of routing through helper-built actions. |
| `tests/hardening/_shared.py` | not imported in this folder | [_shared.py](../hardening/_shared.py) | Hardening-only corruption helpers stay out of the analysis battery. |

## No-mock policy

Use the live registry and the real analysis functions. Do not add `unittest.mock`, `MagicMock`, or `mocker.patch`; use `monkeypatch.setenv` only for environment isolation. The preferred pattern here is [test_outcome_coverage.py](test_outcome_coverage.py), which runs `run_outcome_coverage()` against `PERSONAL_RED_LINES` and checks the returned classifications and reason codes directly.

The rule is enforced rather than only stated: [test_no_substitutes.py](../test_no_substitutes.py) scans every `.py` file under `src/`, `tests/`, and `scripts/` for mocking-framework tokens, the replacing `monkeypatch` forms, and retired substitute branding, and carries planted-offence tests proving it detects each one.
