# fixtures - Test-fixture guidance

This folder stores committed fixture data consumed by tests elsewhere in the suite. It does not define standalone test modules, helper functions, or generated output.

## Test module inventory

| Module | What it exercises | Collected tests |
| --- | --- | --- |
| none | This folder defines no Python test modules. | 0 |

## Helpers

| Surface | Signature or shape | Source | Notes |
| --- | --- | --- | --- |
| `tests.helpers.py` | not imported in this folder | [helpers.py](../helpers.py) | Fixture files are consumed by other tests; they do not call helper constructors here. |
| `tests/hardening/_shared.py` | not imported in this folder | [_shared.py](../hardening/_shared.py) | Hardening helpers do not participate in this data-only fixture folder. |

## No-mock policy

Keep fixtures as real committed bytes. Do not replace them with `unittest.mock`, `MagicMock`, or `mocker.patch`; use `monkeypatch.setenv` only for environment isolation in the consuming tests. The preferred pattern is [test_scripts.py](../canary/test_scripts.py), which compares real script output to [canary_committed.json](canary_committed.json).

The rule is enforced rather than only stated: [test_no_substitutes.py](../test_no_substitutes.py) scans every `.py` file under `src/`, `tests/`, and `scripts/` for mocking-framework tokens, the replacing `monkeypatch` forms, and retired substitute branding, and carries planted-offence tests proving it detects each one.
