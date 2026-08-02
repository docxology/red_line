# invariants — Invariant editing guidance

This folder holds pure structural checks over the registry itself. The checks validate ids, scope, exemption structure, provenance, and serialization without evaluating an action.

## Public API inventory

| Name | Signature | Behavior | Source |
| --- | --- | --- | --- |
| `InvariantResult` | <code>class&nbsp;InvariantResult:</code> | One structural check outcome. | [checks.py](checks.py) |
| `check_unique_ids` | <code>def&nbsp;check_unique_ids(lines:&nbsp;tuple[RedLine,&nbsp;...])&nbsp;-&gt;&nbsp;list[InvariantResult]:</code> | Check that every registry line id is unique. | [checks.py](checks.py) |
| `check_each_has_carve_out` | <code>def&nbsp;check_each_has_carve_out(lines:&nbsp;tuple[RedLine,&nbsp;...])&nbsp;-&gt;&nbsp;list[InvariantResult]:</code> | Check that every line keeps a content-bearing carve-out clause. | [checks.py](checks.py) |
| `check_typed_exemptions` | <code>def&nbsp;check_typed_exemptions(lines:&nbsp;tuple[RedLine,&nbsp;...])&nbsp;-&gt;&nbsp;list[InvariantResult]:</code> | Check that every line keeps valid typed exemptions. | [checks.py](checks.py) |
| `check_nonempty_scope` | <code>def&nbsp;check_nonempty_scope(lines:&nbsp;tuple[RedLine,&nbsp;...])&nbsp;-&gt;&nbsp;list[InvariantResult]:</code> | Every line must have ≥1 scope keyword — a zero-scope line is unreachable. | [checks.py](checks.py) |
| `check_standard_analogs_not_air_gapped` | <code>def&nbsp;check_standard_analogs_not_air_gapped(lines:&nbsp;tuple[RedLine,&nbsp;...])&nbsp;-&gt;&nbsp;list[InvariantResult]:</code> | CANARY-grade (Standard-1/2 analog) lines may never permit air-gapped release. | [checks.py](checks.py) |
| `check_has_both_standards` | <code>def&nbsp;check_has_both_standards(lines:&nbsp;tuple[RedLine,&nbsp;...])&nbsp;-&gt;&nbsp;list[InvariantResult]:</code> | At least one Standard-1 analog (force) and one Standard-2 analog (profiling). | [checks.py](checks.py) |
| `check_standard_analogs_are_canary` | <code>def&nbsp;check_standard_analogs_are_canary(lines:&nbsp;tuple[RedLine,&nbsp;...])&nbsp;-&gt;&nbsp;list[InvariantResult]:</code> | The Standard-analog lines must keep CANARY severity — demotion is drift. | [checks.py](checks.py) |
| `check_enum_field_types` | <code>def&nbsp;check_enum_field_types(lines:&nbsp;tuple[RedLine,&nbsp;...])&nbsp;-&gt;&nbsp;list[InvariantResult]:</code> | max_tier / severity must be real enum members — dataclasses don't type-check. | [checks.py](checks.py) |
| `check_nonempty_standard_text` | <code>def&nbsp;check_nonempty_standard_text(lines:&nbsp;tuple[RedLine,&nbsp;...])&nbsp;-&gt;&nbsp;list[InvariantResult]:</code> | Run one structural invariant check and return its result record. | [checks.py](checks.py) |
| `check_provenance` | <code>def&nbsp;check_provenance(lines:&nbsp;tuple[RedLine,&nbsp;...])&nbsp;-&gt;&nbsp;list[InvariantResult]:</code> | Provenance dates and first-person commitments must remain explicit. | [checks.py](checks.py) |
| `check_unique_exemption_ids` | <code>def&nbsp;check_unique_exemption_ids(lines:&nbsp;tuple[RedLine,&nbsp;...])&nbsp;-&gt;&nbsp;list[InvariantResult]:</code> | Check that exemption ids stay unique across the registry. | [checks.py](checks.py) |
| `check_canonical_scope_tokens` | <code>def&nbsp;check_canonical_scope_tokens(lines:&nbsp;tuple[RedLine,&nbsp;...])&nbsp;-&gt;&nbsp;list[InvariantResult]:</code> | Registry and exemption scopes must use reviewed canonical spellings. | [checks.py](checks.py) |
| `check_exemption_triggers_disjoint` | <code>def&nbsp;check_exemption_triggers_disjoint(lines:&nbsp;tuple[RedLine,&nbsp;...])&nbsp;-&gt;&nbsp;list[InvariantResult]:</code> | No exemption trigger token may repeat its own line's prohibited scope. | [checks.py](checks.py) |
| `check_registry_serialization` | <code>def&nbsp;check_registry_serialization(lines:&nbsp;tuple[RedLine,&nbsp;...])&nbsp;-&gt;&nbsp;list[InvariantResult]:</code> | Canonical serialization must remain valid and JSON-stable. | [checks.py](checks.py) |
| `all_invariants` | <code>def&nbsp;all_invariants(lines:&nbsp;tuple[RedLine,&nbsp;...]&nbsp;=&nbsp;PERSONAL_RED_LINES)&nbsp;-&gt;&nbsp;list[InvariantResult]:</code> | Run every structural invariant and flatten the results. | [checks.py](checks.py) |
| `invariants_pass` | <code>def&nbsp;invariants_pass(lines:&nbsp;tuple[RedLine,&nbsp;...]&nbsp;=&nbsp;PERSONAL_RED_LINES)&nbsp;-&gt;&nbsp;bool:</code> | True iff every structural invariant passes on ``lines``. | [checks.py](checks.py) |

## Import direction

May import `model`, `registry`, and stdlib only. Keep this package below `analysis/` and above no release-surface code.

## Invariants

- The two standard-analog CANARY lines remain present, keep CANARY severity, and cannot allow `AIR_GAPPED` release.
- Checks stay pure and return `InvariantResult` records rather than raising on expected negative-control inputs.
- Detection power against planted-bad registries remains covered by tests; do not weaken fail cases to silence regressions.

## Tests

Tests for this folder live in:
- [../../../tests/invariants/test_checks.py](../../../tests/invariants/test_checks.py)
- [../../../tests/hardening/test_invariants.py](../../../tests/hardening/test_invariants.py)
- [../../../tests/hardening/test_registry_anchors.py](../../../tests/hardening/test_registry_anchors.py)
