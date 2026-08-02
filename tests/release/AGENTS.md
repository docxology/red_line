# release tests - Test-folder guidance

This folder covers the `red_line.release` package: provenance digests, the release-input snapshot, manifest assembly and report interpretation, and two-pass artifact comparison. It does not cover the contract validators those functions call, which live under `tests/integration/`, nor the `scripts/` CLIs that wrap them.

## Test module inventory

| Module | What it exercises | Collected tests |
| --- | --- | --- |
| [test_provenance.py](test_provenance.py) | Chunked file digests, real-repository revision and dirtiness, honest render-toolchain location, and directory digest filtering. | 16 |
| [test_snapshot.py](test_snapshot.py) | Live analysis metrics, figure-registry binding and fallbacks, and snapshot writing. | 8 |
| [test_manifest.py](test_manifest.py) | Candidate-ledger binding, fail-closed report interpretation, publication-gate readiness, pre-render deferral versus decidable failure, manifest assembly, and the recorded renderer when one is and is not present. | 30 |
| [test_determinism.py](test_determinism.py) | Artifact hashing scope, PDF text comparison, drift classification, render invocation against a located toolchain, and two-pass comparison outcomes. | 26 |

## Helpers

| Surface | Signature or shape | Source | Notes |
| --- | --- | --- | --- |
| `_isolated_git_env` | `def _isolated_git_env(home: Path) -> dict[str, str]` | [test_provenance.py](test_provenance.py) | Builds a git environment pinned to `tmp_path` with `GIT_CONFIG_GLOBAL` and `GIT_CONFIG_SYSTEM` set to `/dev/null`, so the test never reads or writes the developer's git configuration. |
| `_artifact` | `def _artifact(root: Path, relative: str, payload: str) -> Path` | [test_determinism.py](test_determinism.py) | Writes one real artifact file, creating parents, inside a `tmp_path` output tree. |
| `ROOT` | `Path` | [test_manifest.py](test_manifest.py) | The real repository root, used only by `build_manifest` assertions that need the live tree. |

## No-mock policy

Use real files, real subprocesses, and real callables. Do not add `unittest.mock`, `MagicMock`, or `mocker.patch`; use `monkeypatch.setenv` and `monkeypatch.delenv` only for environment isolation. Three real-dependency techniques stand in for mocking here:

- **A real git repository.** `test_provenance.py` runs `git init`, commits, and then dirties a real repository under `tmp_path` to exercise `git_revision` and `git_dirty`. It is skipped when `git` is absent.
- **A real executable on `PATH`.** `test_determinism.py` writes an executable `uv` shell script under `tmp_path` (named `recording_uv` in the test, because it records each invocation to `$UV_INVOCATION_LOG`), points `PATH` at that directory, and lets `template_render_passes` invoke it for real. This is the same pattern as [test_figures.py](../test_figures.py). Pointing `PATH` at an empty directory instead proves the missing-`uv` path fails loudly.
- **A real render callable.** `compare_artifacts` takes an injected callable, so the two-pass paths are driven by an ordinary local function that records its invocations and mutates the tree, with no renderer and no sibling template checkout involved.

The rule is enforced rather than only stated: [test_no_substitutes.py](../test_no_substitutes.py) scans every `.py` file under `src/`, `tests/`, and `scripts/` for mocking-framework tokens, the replacing `monkeypatch` forms, and retired substitute branding, and carries planted-offence tests proving it detects each one.

## Coverage note on PDF drift

`classify_nondeterminism` is tested directly for all three outcomes. The PDF-metadata outcome is not reachable end-to-end through `compare_artifacts` in this suite: synthetic PDFs written under `tmp_path` carry no extractable text, so `pdf_texts_equal` is always `False` and the comparison lands on unclassified drift. Reaching that branch through `compare_artifacts` would require genuine rendered PDFs and a working `pdftotext`, which belongs to the render gate rather than the unit suite.

## Tests must not touch the working tree

Everything writes under `tmp_path`. The only reads against the real checkout are `build_manifest(ROOT, ...)` and `analysis_metrics()`.
