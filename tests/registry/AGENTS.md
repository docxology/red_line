# registry tests - Test-folder guidance

This folder covers registry shape, standard-analog presence, and author provenance. It does not cover the deeper invariant battery or release bindings.

## Test module inventory

| Module | What it exercises | Collected tests |
| --- | --- | --- |
| [test_lines.py](test_lines.py) | Registry shape counts, carve-outs, and standard-analog presence. | 4 |
| [test_provenance.py](test_provenance.py) | Author provenance, first-person standards, and non-exhaustive registry status. | 8 |

## Helpers

| Surface | Signature or shape | Source | Notes |
| --- | --- | --- | --- |
| `tests.helpers.py` | not imported in this folder | [helpers.py](../helpers.py) | Registry tests read `PERSONAL_RED_LINES` directly instead of building action fixtures. |
| `tests/hardening/_shared.py` | not imported in this folder | [_shared.py](../hardening/_shared.py) | Registry tests stay on the live registry surface and do not use corruption helpers here. |

## No-mock policy

Use the live registry directly. Do not add `unittest.mock`, `MagicMock`, or `mocker.patch`; use `monkeypatch.setenv` only for environment isolation. The preferred pattern here is [test_provenance.py](test_provenance.py), which reads `PERSONAL_RED_LINES` directly and checks each line's `stated_by`, `stated_on`, and first-person standard text.

The rule is enforced rather than only stated: [test_no_substitutes.py](../test_no_substitutes.py) scans every `.py` file under `src/`, `tests/`, and `scripts/` for mocking-framework tokens, the replacing `monkeypatch` forms, and retired substitute branding, and carries planted-offence tests proving it detects each one.
