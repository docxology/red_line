# integration tests - Test-folder guidance

This folder covers beacon bindings, contract-validator branch coverage, manuscript number binding, release-surface validation on the live tree, and trust-boundary attacks. It does not unit-test individual package helpers in isolation; those stay in the package-area folders. Fail-closed behavior of the `red_line.release` functions themselves moved to [../release/](../release/AGENTS.md); what stays here is the live-tree binding check and the contract regressions around it.

## Test module inventory

| Module | What it exercises | Collected tests |
| --- | --- | --- |
| [test_beacon_binding.py](test_beacon_binding.py) | README and beacon prose bindings to the live registry hash and line text. | 9 |
| [test_contracts_branch_coverage.py](test_contracts_branch_coverage.py) | Synthetic-tree branch coverage for the packaged validators. | 24 |
| [test_manuscript_composition_binding.py](test_manuscript_composition_binding.py) | Derived manuscript counts, reason-code prose bindings, and the applied-exemption id in the shared-token paragraph. | 11 |
| [test_proposed_candidates_binding.py](test_proposed_candidates_binding.py) | Executed evaluator silence on every non-adopted candidate scope, with a live-token positive control. | 50 |
| [test_source_ledger_binding.py](test_source_ledger_binding.py) | Source-ledger locator coverage and research-method table bindings. | 18 |
| [test_stemming_boundary_binding.py](test_stemming_boundary_binding.py) | The abstract's qualified stemming claim against scope normalization and the advisory hint path. | 5 |
| [test_unbound_count_binding.py](test_unbound_count_binding.py) | Every restated line count, the composition distributions, the truncated digest, and the new figure-caption numbers. | 22 |
| [test_release_bindings.py](test_release_bindings.py) | Live validator passes and release-manifest bindings on the source tree. | 7 |
| [test_release_hardening.py](test_release_hardening.py) | Candidate-ledger and source-claim binding regressions plus the figure-digest gate guard. | 3 |
| [test_trust_model.py](test_trust_model.py) | Evidence, canary, immutability, and fixture-backed trust-boundary attacks. | 21 |
| [test_formalism_bindings.py](test_formalism_bindings.py) | The formalism section's definitions and propositions re-derived from code, plus the auto-numbering structural gates. | 34 |

## Helpers

| Surface | Signature or shape | Source | Notes |
| --- | --- | --- | --- |
| `complete_context` | `def complete_context(**overrides: str) -> ActionContext` | [helpers.py](../helpers.py) | Used by trust-model tests that need a fully evidenced intake before modifying one evidence field. |
| `action` | `def action(description: str, scope: frozenset[str], *, tier: DeploymentTier = DeploymentTier.HOSTED, ambiguous: bool = False, context: ActionContext | None = None) -> ProposedAction` | [helpers.py](../helpers.py) | Builds real actions for the trust-model tests. |
| `tests/hardening/_shared.py` | not imported in this folder | [_shared.py](../hardening/_shared.py) | Integration tests build synthetic repo trees under `tmp_path` instead of corrupting in-memory dataclasses. |

## No-mock policy

Use real files under `tmp_path`, real JSON payloads, and the packaged validators. Do not add `unittest.mock`, `MagicMock`, or `mocker.patch`; use `monkeypatch.setenv` only for environment isolation. The preferred pattern here is [test_contracts_branch_coverage.py](test_contracts_branch_coverage.py), which writes synthetic repo trees under `tmp_path` and calls the real validator functions over those paths.

The rule is enforced rather than only stated: [test_no_substitutes.py](../test_no_substitutes.py) scans every `.py` file under `src/`, `tests/`, and `scripts/` for mocking-framework tokens, the replacing `monkeypatch` forms, and retired substitute branding, and carries planted-offence tests proving it detects each one.

## Invariants

Validator error strings are asserted by substring in this folder. Keep them stable unless the paired integration assertions are updated with intent.
