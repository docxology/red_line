# contracts — Contracts editing guidance

This folder contains the shipped release-binding validators. Each validator inspects project surfaces and returns `list[str]` errors without printing, exiting, or mutating project state.

## Public API inventory

| Name | Signature | Behavior | Source |
| --- | --- | --- | --- |
| `validate_claim_register` | <code>def&nbsp;validate_claim_register(root:&nbsp;Path)&nbsp;-&gt;&nbsp;list[str]:</code> | Validate the claim register JSON and its documentation row bindings. | [claim_register.py](claim_register.py) |
| `validate_proposed_red_lines` | <code>def&nbsp;validate_proposed_red_lines(root:&nbsp;Path)&nbsp;-&gt;&nbsp;list[str]:</code> | Validate the candidate red-line ledger and its decision table bindings. | [proposed_red_lines.py](proposed_red_lines.py) |
| `validate_release_bindings` | <code>def&nbsp;validate_release_bindings(root:&nbsp;Path,&nbsp;*,&nbsp;require_rendered:&nbsp;bool&nbsp;=&nbsp;False)&nbsp;-&gt;&nbsp;list[str]:</code> | Validate source bindings, optionally requiring rendered surfaces. | [release_bindings.py](release_bindings.py) |
| `validate_source_claims` | <code>def&nbsp;validate_source_claims(root:&nbsp;Path)&nbsp;-&gt;&nbsp;list[str]:</code> | Validate the source ledger against bibliography and manuscript citations. | [source_claims.py](source_claims.py) |
| `validate_visual_bindings` | <code>def&nbsp;validate_visual_bindings(root:&nbsp;Path)&nbsp;-&gt;&nbsp;list[str]:</code> | Validate the bound project surfaces and return a list of error strings. | [visual_bindings.py](visual_bindings.py) |

## Import direction

May import stdlib, the root package, `canary/`, and `figures/`. Older policy packages must not import `contracts/`, and validators must not depend on `scripts/`.

## Invariants

- Error strings are asserted by integration tests; do not reword them casually.
- Validators stay pure in interface: return `list[str]`, no side effects, no CLI behavior.
- Rendered-surface checks remain optional behind `require_rendered` where the source tree can be valid without `output/`.

## Tests

Tests for this folder live in:
- [../../../tests/integration/test_release_bindings.py](../../../tests/integration/test_release_bindings.py)
- [../../../tests/integration/test_contracts_branch_coverage.py](../../../tests/integration/test_contracts_branch_coverage.py)
- [../../../tests/test_hardening_contracts.py](../../../tests/test_hardening_contracts.py)
