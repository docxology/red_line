# hardening tests - Test-folder guidance

This folder covers adversarial constructor rejection, canary metadata corruption, digest determinism, invariant proof-of-detection, hostile scope declarations, and freshness boundaries. It does not cover broad release-surface bindings; those stay under `tests/integration/`.

## Test module inventory

| Module | What it exercises | Collected tests |
| --- | --- | --- |
| [test_canary.py](test_canary.py) | Malformed canary metadata and fail-closed verification. | 31 |
| [test_constructor_rejections.py](test_constructor_rejections.py) | Model and oversight constructor rejection on malformed inputs. | 50 |
| [test_digest.py](test_digest.py) | Digest determinism under reorder and content change. | 5 |
| [test_invariants.py](test_invariants.py) | Planted-bad invariant detection and normalization-aware failures. | 14 |
| [test_registry_anchors.py](test_registry_anchors.py) | Registry severity anchors and canonical tier-token checks. | 2 |
| [test_scope.py](test_scope.py) | Hostile scope declarations, normalization failures, and ambiguity stops. | 11 |
| [test_staleness.py](test_staleness.py) | Exact evidence and canary staleness boundaries. | 12 |

## Helpers

| Surface | Signature or shape | Source | Notes |
| --- | --- | --- | --- |
| `complete_context` | `def complete_context(**overrides: str) -> ActionContext` | [helpers.py](../helpers.py) | Used where hardening tests need a real default intake before corrupting or replacing parts of it. |
| `action` | `def action(description: str, scope: frozenset[str], *, tier: DeploymentTier = DeploymentTier.HOSTED, ambiguous: bool = False, context: ActionContext | None = None) -> ProposedAction` | [helpers.py](../helpers.py) | Builds the real action objects that are then stressed with hostile inputs. |
| `SHA_A`, `SHA_B`, `HOMOGLYPH_SURVEILLANCE` | module constants | [_shared.py](_shared.py) | Pinned digest literals plus the non-ASCII surveillance homoglyph used for hostile-input coverage. |
| `_corrupt`, `_line`, `_swap` | `def _corrupt(record, **changes)`, `def _line(line_id: str) -> RedLine`, `def _swap(bad_line: RedLine) -> tuple[RedLine, ...]` | [_shared.py](_shared.py) | Helpers for forging invalid frozen dataclass state and swapping one live line into the registry. |

## No-mock policy

Use real dataclasses and planted invalid state, not mocks. Do not add `unittest.mock`, `MagicMock`, or `mocker.patch`; use `monkeypatch.setenv` only for environment isolation. The preferred pattern here is [test_scope.py](test_scope.py), which creates a real action with `tests.helpers.action(...)`, then uses `_corrupt(...)` from [_shared.py](_shared.py) to plant hostile scope tokens before calling the real evaluator.

The rule is enforced rather than only stated: [test_no_substitutes.py](../test_no_substitutes.py) scans every `.py` file under `src/`, `tests/`, and `scripts/` for mocking-framework tokens, the replacing `monkeypatch` forms, and retired substitute branding, and carries planted-offence tests proving it detects each one.

## Invariants

This subtree was split out of a single 671-line module and grouped by adversarial concern. Add new tests to the matching concern module instead of rebuilding a new catch-all file.
