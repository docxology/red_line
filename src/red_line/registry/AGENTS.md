# registry — Registry editing guidance

This folder is the beacon authority: provenance constants plus the live `PERSONAL_RED_LINES` tuple. It defines the substantive boundary the rest of the package reads.

## Public API inventory

| Name | Signature | Behavior | Source |
| --- | --- | --- | --- |
| none | n/a | This folder exports structure, constants, or re-exports rather than defining public functions or classes directly. | n/a |

## Import direction

May import `model.enums` and `model.red_line` only. Higher layers may depend on the registry; the registry should not depend on evaluator, oversight, figures, or contracts code.

## Invariants

- The live registry remains first-person and dated through `RedLine.stated_by` and `RedLine.stated_on`.
- The two standard-analog CANARY lines stay present and cannot take an `AIR_GAPPED` ceiling.
- Scope tokens and exemption triggers stay canonical so normalization does not silently rewrite policy.

## Tests

Tests for this folder live in:
- [../../../tests/registry/test_lines.py](../../../tests/registry/test_lines.py)
- [../../../tests/registry/test_provenance.py](../../../tests/registry/test_provenance.py)
- [../../../tests/hardening/test_registry_anchors.py](../../../tests/hardening/test_registry_anchors.py)
- [../../../tests/invariants/test_checks.py](../../../tests/invariants/test_checks.py)
