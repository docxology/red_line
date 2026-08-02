# Test folder contract

`tests/` exercises the public API, evaluator, registry, invariants, oversight,
canary, analysis, figures, and integration contracts. Tests are organised in
subdirectories by subsystem.

## Root-level test modules

- `test_figures.py` — figure determinism and registry metadata
- `test_figure_legibility.py` — printed text size and page-fit constraints
- `test_decision_surface_figures.py` — decision-surface figure contracts
- `test_new_composition_figures.py` — new-composition figure contracts
- `test_script_clis.py` — every read-only script passes on good input
- `test_standalone_contract.py` — the package works without sibling repos
- `test_publication_metadata.py` — publication metadata across config and package
- `test_no_substitutes.py` — no substitute/mock enforcement
- `test_hardening_contracts.py` — hardening contract enforcement
- `test_suite_inventory_binding.py` — suite inventory against source
- `test_witness_envelope.py` — witness envelope export contract

## Tests by subsystem

### `analysis/`
- `test_decision_surface.py` — decision surface invariants
- `test_monotonicity_sweep.py` — monotonicity sweep over declaration orders
- `test_outcome_coverage.py` — outcome coverage matrix
- `test_registry_metrics.py` — registry metric derivations

### `canary/`
- `test_hashing.py` — hash generation and verification
- `test_scripts.py` — canary script contracts
- `test_statement.py` — canary statement binding
- `test_verification.py` — canary verification protocol

### `evaluation/`
- `test_evaluator.py` — evaluate_action and status semantics
- `test_monotonicity.py` — monotonicity invariants

### `hardening/`
- `test_canary.py` — hardened canary contracts
- `test_constructor_rejections.py` — constructor rejection paths
- `test_digest.py` — digest computation and binding
- `test_invariants.py` — hardened invariant checks
- `test_registry_anchors.py` — registry anchor binding
- `test_scope.py` — scope validation contracts
- `test_staleness.py` — staleness detection

### `integration/`
- `test_beacon_binding.py` — beacon binding to source
- `test_contracts_branch_coverage.py` — branch coverage contracts
- `test_formalism_bindings.py` — formalism-prose bindings
- `test_manuscript_composition_binding.py` — manuscript composition binding
- `test_proposed_candidates_binding.py` — proposed-candidate binding
- `test_release_bindings.py` — release binding contracts
- `test_release_hardening.py` — release hardening
- `test_source_ledger_binding.py` — source-ledger binding
- `test_stemming_boundary_binding.py` — stemming boundary binding
- `test_trust_model.py` — trust model contracts
- `test_unbound_count_binding.py` — unbound count binding

### `invariants/`
- `test_checks.py` — structural invariant checks

### `model/`
- `test_action.py` — action model contracts
- `test_enums.py` — enumeration definitions
- `test_red_line.py` — RedLine model contracts

### `oversight/`
- `test_findings.py` — oversight finding contracts
- `test_transparency.py` — transparency reporting

### `registry/`
- `test_lines.py` — line registry contracts
- `test_provenance.py` — provenance records

### `release/`
- `test_determinism.py` — release determinism
- `test_manifest.py` — release manifest binding
- `test_provenance.py` — release provenance
- `test_snapshot.py` — release snapshot contracts

## Invariants

- No mocks. Use real records, temporary output roots, and planted-bad registries.
- Keep project coverage at or above the `90` floor in `pyproject.toml`.
- Import figure builders from `red_line.figures`, not from `scripts/`.

## Validation

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90 --cov-report=term-missing
```
