"""Public structural invariant checks over the registry."""

from __future__ import annotations

from .checks import (
    STANDARD_ANALOG_IDS,
    InvariantResult,
    all_invariants,
    check_each_has_carve_out,
    check_exemption_triggers_disjoint,
    check_typed_exemptions,
    check_enum_field_types,
    check_has_both_standards,
    check_nonempty_scope,
    check_nonempty_standard_text,
    check_standard_analogs_are_canary,
    check_standard_analogs_not_air_gapped,
    check_unique_ids,
    invariants_pass,
)

__all__ = [
    "InvariantResult",
    "all_invariants",
    "invariants_pass",
    "STANDARD_ANALOG_IDS",
    "check_unique_ids",
    "check_each_has_carve_out",
    "check_typed_exemptions",
    "check_exemption_triggers_disjoint",
    "check_nonempty_scope",
    "check_standard_analogs_not_air_gapped",
    "check_has_both_standards",
    "check_standard_analogs_are_canary",
    "check_enum_field_types",
    "check_nonempty_standard_text",
]
