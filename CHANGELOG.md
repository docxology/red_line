# Changelog

## 0.4.0 — 2026-10-21

- Reject conflicting deployment-tier declarations before policy matching; derive
  oversight credentials only from the typed tier. Repair dead authored aliases
  with collision, chain and cycle validation, without heuristic stemming.
- Share dated evidence readiness across completeness, evaluator and safe
  applicability helpers. Preserve stale/contradicted duplicate history and
  retain the below-tier reason code alongside hard refusals.
- Bind new schema 2 findings to the reviewed registry, evaluator/package,
  restricted intake digest and structured per-line decision trace; support
  replay and preserve original unbound schema 1 report bytes.
- Separate envelope pointer agreement, schema/nonclaims contract, finding
  agreement diagnostics and trusted-prior archive digest checks.
- Expand finite compound-scope analysis and correct semantic, exemption-proof,
  monotonicity and archive-integrity claims. Registry content and canary remain
  unchanged; no substantive boundary amendment is inferred.
- Finish canonical manuscript documentation links and retain duplicate paths as
  redirects. Isolate renderer environments and repository-root provenance.

See [the review dispositions](docs/review-20261020.md) and the dated release
packet for current verification results. The existing DOI remains unchanged;
the new Zenodo version follows the author's reserve-first procedure.

## 0.3.0 — 2026-07-29

The envelope window: the canonical native report and the cross-instrument
report envelope plus its manuscript formalism.

### Canonical report and envelope

- `envelope.py` now exports `canonical_report` under `red-line.report/1.0` —
  the complete derivation of one `ReviewFinding`, with the set-aside
  authorization arm serialized as an explicit `null` rather than omitted —
  and `report_digest`, its SHA-256, following the house sorted-keys
  compact-separators convention.
- `envelope.py` exports the common report envelope under
  `line.report-envelope/1.0`, with the digest pointer, the review date, the
  registry version and content digest (the same deterministic hash the canary
  attests), the classification word in this line's own vocabulary as
  `native_status`, caller-supplied source snapshot references, and the
  instrument's non-claims in transportable form.
- `manuscript/08a_formalism.md` gained `def:report-envelope` and
  `prop:envelope-pointer`, bound by two new tests proven to bite via planted
  drifts, with the claim ledger and the fourteen suite-inventory sites moved.
- Strict release evidence went green for the first time under the
  engine-pipeline-last-then-strict sequence.

### Other

- `tests/README.md` gained a top-level module inventory table with exact test
  counts (11 modules, 273 collected).
- `scripts/AGENTS.md` corrected to list 13 scripts accurately.
- `tests/AGENTS.md` corrected to list 51 test files accurately (grouped by
  subsystem).
- All READMEs with sibling AGENTS.md now redirect to it.
- Bibliography audited; actually-cited entries restored.

### Gates

- Full suite: 878 passed, 100.00% coverage.
- Registry digest: `72835fd81d1f…` (canary-attested, unchanged).
- `quality_gate.py --render`: exit 0, "quality gate: passed" — first
  end-to-end pass under the reordered sequence.
