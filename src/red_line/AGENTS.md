# red_line — Package-root guidance

This folder is the package root for `red_line`. It re-exports the public API from subpackages, keeps `version.py` as the package-version authority, and holds one top-level domain module, `envelope.py` (the common report envelope).

## Public API inventory

| Name | Signature | Behavior | Source |
| --- | --- | --- | --- |
| `canonical_report` | `def canonical_report(finding: ReviewFinding) -> str` | Complete deterministic JSON of one review finding (`red-line.report/1.0`); the absent-authorization arm serializes as an explicit `null`. | [envelope.py](envelope.py) |
| `report_digest` | `def report_digest(finding: ReviewFinding) -> str` | SHA-256 hex over `canonical_report`; the pointer an envelope carries. | [envelope.py](envelope.py) |
| `ReportEnvelope` | frozen dataclass, ten fields | The common `line.report-envelope/1.0` witness record; fail-closed `__post_init__`. | [envelope.py](envelope.py) |
| `finding_envelope` | `def finding_envelope(finding, subject_id="", source_snapshot_refs=(), lines=PERSONAL_RED_LINES) -> ReportEnvelope` | Wraps a finding in the envelope, pointing at — never reinterpreting — its canonical form; validates inputs fail-closed. | [envelope.py](envelope.py) |
| `canonical_envelope` | `def canonical_envelope(envelope: ReportEnvelope) -> str` | Stable JSON of an envelope for archiving beside its report. | [envelope.py](envelope.py) |
| `envelope_matches_finding` | `def envelope_matches_finding(envelope, finding, lines=PERSONAL_RED_LINES) -> bool` | Archived-pair read-back check over digest, review date, status word, and registry digest. | [envelope.py](envelope.py) |
| `REPORT_SCHEMA` / `ENVELOPE_SCHEMA` / `RED_LINE_ID` / `SCOPE_AND_NONCLAIMS` | constants | Schema strings, the instrument identity, and the transportable non-claims; siblings align by publishing the same envelope schema string, never by import. | [envelope.py](envelope.py) |

## Subpackages

| Subpackage | Owns | Guidance |
| --- | --- | --- |
| `model/` | Actions, contexts, evidence records, and enums. | [model/AGENTS.md](model/AGENTS.md) |
| `registry/` | The live personal red-line set. | [registry/AGENTS.md](registry/AGENTS.md) |
| `evaluation/` | The evaluator that classifies a proposed action. | [evaluation/AGENTS.md](evaluation/AGENTS.md) |
| `oversight/` | Review findings and transparency reporting. | [oversight/AGENTS.md](oversight/AGENTS.md) |
| `invariants/` | Structural checks over the registry and model. | [invariants/AGENTS.md](invariants/AGENTS.md) |
| `canary/` | Registry hashing, canary issuance, and verification. | [canary/AGENTS.md](canary/AGENTS.md) |
| `analysis/` | Derived metrics over the registry and evaluator. | [analysis/AGENTS.md](analysis/AGENTS.md) |
| `figures/` | Deterministic figure generation and the figure registry. | [figures/AGENTS.md](figures/AGENTS.md) |
| `contracts/` | Release-binding validators returning `list[str]`. | [contracts/AGENTS.md](contracts/AGENTS.md) |
| `release/` | Provenance digests, input snapshot, manifest, and render determinism. | [release/AGENTS.md](release/AGENTS.md) |

## Import direction

Keep root-package code to re-exports and package metadata. Domain modules may import sibling subpackages; `version.py` stays dependency-free.

## Invariants

- `version.py` remains the package-version authority consumed by packaging metadata.
- The root package stays a re-export surface; do not move business logic into `__init__.py`.
- Public API changes here should stay synchronized with the subpackage definitions they expose.

## Tests

Tests for this folder live in:
- [../../tests/test_witness_envelope.py](../../tests/test_witness_envelope.py)
- [../../tests/evaluation/test_evaluator.py](../../tests/evaluation/test_evaluator.py)
- [../../tests/hardening/test_digest.py](../../tests/hardening/test_digest.py)
- [../../tests/integration/test_release_bindings.py](../../tests/integration/test_release_bindings.py)
