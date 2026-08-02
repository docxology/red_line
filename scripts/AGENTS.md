# Script contract

Every file in `scripts/` is a thin CLI over `src/`. Business logic belongs in
`src/red_line/`, not here.

## Files

- `__init__.py` — package marker
- `build_figures.py` — calls `red_line.figures.build_figures()` and prints the output paths
- `build_canary.py` — generates the hash-based durability canary
- `build_release_data.py` — assembles release payload data
- `build_release_manifest.py` — generates the release manifest
- `check_canary.py` — verifies the canary's integrity
- `compare_render_artifacts.py` — compares render artifacts for drift detection
- `quality_gate.py` — runs the full quality gate suite
- `validate_claim_register.py` — validates claim registry entries against source
- `validate_proposed_red_lines.py` — validates proposed red-line entries
- `validate_release_bindings.py` — validates release bindings
- `validate_source_claims.py` — validates source claims against the ledger
- `validate_visual_bindings.py` — validates visual bindings (figure captions, labels)

## Canonical commands

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90 --cov-report=term-missing
uv run python scripts/check_canary.py
uv run python scripts/build_figures.py
uv run python scripts/quality_gate.py
```
