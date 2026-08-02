# data - Data-folder guidance

This folder holds the hand-maintained machine-readable contracts that bind release claims, source citations, and non-adopted candidate lines back to the live tree.

## Data inventory

| File | Schema | What it binds | Validator | Asserting tests |
| --- | --- | --- | --- | --- |
| [claim_register.json](claim_register.json) | `1.0` | Ten release claims, four claim classes, four verification modes, and their documentation rows in `docs/claim-register.md`. | [`validate_claim_register`](../src/red_line/contracts/claim_register.py) | [test_release_bindings.py](../tests/integration/test_release_bindings.py), [test_contracts_branch_coverage.py](../tests/integration/test_contracts_branch_coverage.py) |
| [proposed_red_lines.json](proposed_red_lines.json) | `1.0` | Six non-adopted candidate lines, `registry_effect = none`, and the decision rows in `docs/PROPOSED_RED_LINES.md`. | [`validate_proposed_red_lines`](../src/red_line/contracts/proposed_red_lines.py) | [test_release_bindings.py](../tests/integration/test_release_bindings.py), [test_release_hardening.py](../tests/integration/test_release_hardening.py) |
| [source_claims.json](source_claims.json) | `1.0` | Forty-five bibliography-backed source records, manuscript citation bindings, and three source-driven figure bindings. | [`validate_source_claims`](../src/red_line/contracts/source_claims.py) | [test_release_bindings.py](../tests/integration/test_release_bindings.py), [test_contracts_branch_coverage.py](../tests/integration/test_contracts_branch_coverage.py), [test_release_hardening.py](../tests/integration/test_release_hardening.py) |
| [formalism_claim_ledger.json](formalism_claim_ledger.json) | `1.0` | Every formalism-block label declared in `manuscript/08a_formalism.md` plus the package's evidence-freshness window, so the render engine's evidence registry resolves a `[@def:…]`/`[@prop:…]` cross-reference instead of reporting it as an unsupported bibliography citation. | none (read by the render engine's evidence registry) | [test_formalism_bindings.py](../tests/integration/test_formalism_bindings.py) |

## Invariants

- These files are hand-maintained contracts, not generated output. `formalism_claim_ledger.json` is the one exception in kind: its rows are hand-written but every one is re-derived from the manuscript and the package by [test_formalism_bindings.py](../tests/integration/test_formalism_bindings.py), so it cannot drift from the blocks it declares.
- Editing one file without updating the validator that reads it and the prose surface it binds will break the gate.
- `source_claims.json` is also read by [`validate_visual_bindings`](../src/red_line/contracts/visual_bindings.py) when figure `source_ids` are present.

## Related

- [contracts README](../src/red_line/contracts/README.md)
- [claim-register.md](../docs/claim-register.md)
- [PROPOSED_RED_LINES.md](../docs/PROPOSED_RED_LINES.md)
- [research-method.md](../docs/research-method.md)
