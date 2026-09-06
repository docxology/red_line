# Script contract

Every file in `scripts/` is a thin CLI over `src/red_line/`: argument parsing,
the `ROOT` constant, printing, and a single delegated call into a package
entrypoint. Business, data, figure, and analysis logic belongs in
`src/red_line/`, never here — a decision rule found in a script is misplaced
and should move into the package where it is importable and testable.

The one exception is `quality_gate.py`: sequencing the other scripts as
subprocesses is its purpose, not a domain concern. Even there the two
self-contained checks (figure-tree digest, wheel smoke) live in
`red_line.release` (`tree_digest`, `wheel_smoke`), not inline.

## Files

| Script | Calls into | Purpose |
| --- | --- | --- |
| `__init__.py` | — | Package marker keeping `from scripts import <name>` bound to this checkout |
| `build_canary.py` | `red_line.canary.issue_canary` | Generates the hash-based durability canary |
| `check_canary.py` | `red_line.canary.verify_canary` | Verifies the canary's integrity against the committed prior |
| `build_figures.py` | `red_line.figures.build_figures` | Builds the deterministic manuscript figures |
| `validate_source_claims.py` | `red_line.contracts.validate_source_claims` | Validates source claims against the ledger |
| `validate_claim_register.py` | `red_line.contracts.validate_claim_register` | Validates claim register entries against source |
| `validate_proposed_red_lines.py` | `red_line.contracts.validate_proposed_red_lines` | Validates proposed red-line entries |
| `validate_release_bindings.py` | `red_line.contracts.validate_release_bindings` | Validates release bindings |
| `validate_visual_bindings.py` | `red_line.contracts.validate_visual_bindings` | Validates visual bindings (figure captions, labels) |
| `build_release_data.py` | `red_line.release.write_snapshot` | Assembles release payload data |
| `build_release_manifest.py` | `red_line.release.build_manifest`, `release_ready` | Generates the release manifest |
| `compare_render_artifacts.py` | `red_line.release.compare_artifacts` | Compares render artifacts for drift detection |
| `quality_gate.py` | sibling scripts as subprocesses; `red_line.release.tree_digest`, `wheel_smoke` | Runs the full quality gate suite |

## Canonical commands

```bash
uv run pytest tests/ --cov=red_line --cov-fail-under=90
uv run python scripts/check_canary.py
uv run python scripts/build_figures.py
uv run python scripts/quality_gate.py
```

## Gotchas

- `__init__.py` is load-bearing. It keeps `scripts` a regular package so
  explicit imports (`from scripts import quality_gate`,
  `tests/canary/test_scripts.py`) resolve to this checkout instead of a
  same-named package from a sibling or render host on `sys.path`.
- Fail-closed argparse is pinned, not optional. `tests/test_script_clis.py`
  derives the entrypoint inventory from disk and requires every script to
  reject unknown flags and stray positionals with a non-zero exit and to
  answer `--help` without running.
- `build_figures.py` must run before the figure-dependent tests on a clean
  checkout; `quality_gate.py` performs that ordering itself.
- `check_canary.py` fails once the attestation is stale — that is the
  instrument working. Re-issue with `build_canary.py`, or pass `--as-of` for a
  pinned historical verification.
- The wheel smoke inside `quality_gate.py` requires `uv` on PATH; everything
  else runs from the editable install.
