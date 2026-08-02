# model tests - Test-folder guidance

This folder covers core model types and normalization helpers. It does not cover evaluator policy, review findings, or release-surface bindings.

## Test module inventory

| Module | What it exercises | Collected tests |
| --- | --- | --- |
| [test_action.py](test_action.py) | Action, context, evidence-record, and outside-scope semantics. | 9 |
| [test_enums.py](test_enums.py) | Deployment-tier oversight ordering. | 1 |
| [test_red_line.py](test_red_line.py) | Registry shape, carve-outs, normalization, and typed exemptions. | 10 |

## Helpers

| Surface | Signature or shape | Source | Notes |
| --- | --- | --- | --- |
| `complete_context` | `def complete_context(**overrides: str) -> ActionContext` | [helpers.py](../helpers.py) | Provides the real fully evidenced context used when constructing action-model values. |
| `action` | `def action(description: str, scope: frozenset[str], *, tier: DeploymentTier = DeploymentTier.HOSTED, ambiguous: bool = False, context: ActionContext | None = None) -> ProposedAction` | [helpers.py](../helpers.py) | Used where the model tests need a real action before asserting on context or evidence behavior. |

## No-mock policy

Use the real dataclasses and enums. Do not add `unittest.mock`, `MagicMock`, or `mocker.patch`; use `monkeypatch.setenv` only for environment isolation. The preferred pattern here is [test_action.py](test_action.py), which constructs real `EvidenceRecord`, `ActionContext`, and `ProposedAction` values and checks their validation behavior directly.

The rule is enforced rather than only stated: [test_no_substitutes.py](../test_no_substitutes.py) scans every `.py` file under `src/`, `tests/`, and `scripts/` for mocking-framework tokens, the replacing `monkeypatch` forms, and retired substitute branding, and carries planted-offence tests proving it detects each one.
