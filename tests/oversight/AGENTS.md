# oversight tests - Test-folder guidance

This folder covers review-finding creation, finding rendering, authorizations, provenance fields, and transparency aggregation. It does not cover the underlying evaluator classifications themselves; those stay under `tests/evaluation/`.

## Test module inventory

| Module | What it exercises | Collected tests |
| --- | --- | --- |
| [test_findings.py](test_findings.py) | Review findings, rendered text, authorizations, provenance fields, and stale-review behavior. | 16 |
| [test_transparency.py](test_transparency.py) | Classification, authorization, and blocked-count aggregation. | 2 |

## Helpers

| Surface | Signature or shape | Source | Notes |
| --- | --- | --- | --- |
| `action` | `def action(description: str, scope: frozenset[str], *, tier: DeploymentTier = DeploymentTier.HOSTED, ambiguous: bool = False, context: ActionContext | None = None) -> ProposedAction` | [helpers.py](../helpers.py) | Builds the real action records reviewed by `review_engagement()`. |
| `complete_context` | available through `tests.helpers.py` but not imported here | [helpers.py](../helpers.py) | This folder mostly relies on helper-built actions rather than direct context construction. |

## No-mock policy

Use real `ReviewAuthorization`, `ReviewFinding`, and evaluator results. Do not add `unittest.mock`, `MagicMock`, or `mocker.patch`; use `monkeypatch.setenv` only for environment isolation. The preferred pattern here is [test_findings.py](test_findings.py), which creates real actions with `tests.helpers.action(...)` and passes them through the real `review_engagement()` function.

The rule is enforced rather than only stated: [test_no_substitutes.py](../test_no_substitutes.py) scans every `.py` file under `src/`, `tests/`, and `scripts/` for mocking-framework tokens, the replacing `monkeypatch` forms, and retired substitute branding, and carries planted-offence tests proving it detects each one.
