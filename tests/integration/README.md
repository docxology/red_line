# integration tests

This folder binds code, docs, data, manuscript sections, fixtures, and release helpers together. It exercises the packaged validators against the live tree and against synthetic repo slices built under `tmp_path`.

## Modules

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

## Run

Use the project venv directly here. In the current managed environment, `uv run` tries to initialize the user-level uv cache, so the direct `.venv` entrypoint is the working form.

```bash
.venv/bin/python -m pytest tests/integration -q
```

## Coverage gate

The project gate lives in [pyproject.toml](../../pyproject.toml) as `--cov-fail-under=90` over `source = ["red_line"]`. The current full-suite measurement is `100.00%` with `878` passed tests on `2026-07-29`.

## Related

- [AGENTS.md](AGENTS.md)
- [contracts package](../../src/red_line/contracts/README.md)
- [VERIFY.md](../../docs/VERIFY.md)
