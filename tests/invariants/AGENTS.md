# invariants tests - Test-folder guidance

This folder covers the invariant battery itself. It does not cover the broader adversarial helpers and boundary-date checks that sit under `tests/hardening/`.

## Test module inventory

| Module | What it exercises | Collected tests |
| --- | --- | --- |
| [test_checks.py](test_checks.py) | Structural invariant results plus proof-of-detection on planted defects. | 18 |

## Helpers

| Surface | Signature or shape | Source | Notes |
| --- | --- | --- | --- |
| `tests.helpers.py` | not imported in this folder | [helpers.py](../helpers.py) | Invariant tests mutate the live registry surface directly instead of building `ProposedAction` fixtures. |
| local `_corrupt` | `def _corrupt(record, **changes)` | [test_checks.py](test_checks.py) | This folder carries its own tiny corruption helper alongside the planted-bad registry cases. |

## No-mock policy

Use the live registry and planted-bad dataclass replacements. Do not add `unittest.mock`, `MagicMock`, or `mocker.patch`; use `monkeypatch.setenv` only for environment isolation. The preferred pattern here is [test_checks.py](test_checks.py), which uses `dataclasses.replace(...)` and a local `_corrupt(...)` helper to force known defects through the real invariant battery.

The rule is enforced rather than only stated: [test_no_substitutes.py](../test_no_substitutes.py) scans every `.py` file under `src/`, `tests/`, and `scripts/` for mocking-framework tokens, the replacing `monkeypatch` forms, and retired substitute branding, and carries planted-offence tests proving it detects each one.
