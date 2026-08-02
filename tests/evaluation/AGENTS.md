# evaluation tests - Test-folder guidance

This folder covers `evaluate_action()` and tier monotonicity over real actions. It does not cover review finding rendering or transparency aggregation; those live under `tests/oversight/`.

## Test module inventory

| Module | What it exercises | Collected tests |
| --- | --- | --- |
| [test_evaluator.py](test_evaluator.py) | Classification, carve-outs, aliases, stale evidence, and intake-blocking behavior. | 14 |
| [test_monotonicity.py](test_monotonicity.py) | Tier-floor monotonicity and regression coverage for the pre-fix inversion bug. | 6 |

## Helpers

| Surface | Signature or shape | Source | Notes |
| --- | --- | --- | --- |
| `complete_context` | `def complete_context(**overrides: str) -> ActionContext` | [helpers.py](../helpers.py) | Builds the fully evidenced default context used by helper-created actions. |
| `action` | `def action(description: str, scope: frozenset[str], *, tier: DeploymentTier = DeploymentTier.HOSTED, ambiguous: bool = False, context: ActionContext | None = None) -> ProposedAction` | [helpers.py](../helpers.py) | Creates the real `ProposedAction` values that these tests pass into `evaluate_action()`. |

## No-mock policy

Use real `ProposedAction` instances and the live registry. Do not add `unittest.mock`, `MagicMock`, or `mocker.patch`; use `monkeypatch.setenv` only for environment isolation. The preferred pattern here is [test_evaluator.py](test_evaluator.py), which builds actions with `tests.helpers.action(...)` and asserts on the real `ActionAssessment` returned by `evaluate_action()`.

The rule is enforced rather than only stated: [test_no_substitutes.py](../test_no_substitutes.py) scans every `.py` file under `src/`, `tests/`, and `scripts/` for mocking-framework tokens, the replacing `monkeypatch` forms, and retired substitute branding, and carries planted-offence tests proving it detects each one.
