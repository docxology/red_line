# Changelog

## 0.5.2 — 2026-11-09

- Keep companion repository identities on separate manuscript lines so print
  wrapping does not split the owner name mid-token.
- Require exact ASCII calendar review dates and Unicode scalar text before new
  native intake, registry, finding, or envelope custody; preserve valid Unicode
  canonical bytes and the existing evidence-date policy.
- Reject unbound findings with current-only decision traces instead of silently
  omitting the trace from schema 1; authentic historical schema-1 bytes are unchanged.
- Ignore commented-out figure geometry and XML font lookalikes, and honor trailing
  YAML comments on supported figure-height scalars without changing the print floor.
- Correct constructor/invariant guidance: RedLine construction and dataclasses.replace reject non-enum fields; the battery also detects corrupted records that bypass construction.
- Document existing restricted intake, replay diagnostics, evidence gates, and per-line decisions in their owning API inventories.
- Separate current repository citations from the verified 0.5.1 source archive and older historical identifiers; retain exact edition/object boundaries without a future DOI assertion.
- Remove incidental candidate counts, publication wording pins, and DOI allowlist assertions; retain native non-adoption, metadata validity, and disclosure controls. Align Ruff with the declared Python 3.11 floor.
- Observe Git revision, dirtiness, and tracked source without optional index writes; stat-only source changes remain clean and index bytes remain untouched.
- Keep registry content, refusal semantics, and canonical schemas unchanged; new reports retain the actual package producer version and historical evidence is not relabeled.

## 0.5.1 — 2026-11-08

- Documentation-only patch: use the current Line Set declaration, distinguish
  Copper resource accounting and Iron recorded recovery comparisons, and state
  access-controlled source boundaries without weakening refusal noncompensation.
- Delete incidental formalism prose and source-field copying assertions; retain
  native evaluator, pointer-tamper, staleness, and historical byte-custody controls.
- Synchronize current descriptive version metadata. Native evaluator semantics,
  registry identity, schemas, historical captures, and DOI identities are unchanged.
  No generated artifacts, deposit, or new release verification is asserted here.

## 0.5.0 — 2026-11-06

- Use native numbered section citations without duplicated prefixes or nested
  hand-written links in the manuscript roadmap and operating method.
- Emit figure registry schema 2.0 with authored `alt_text` and no retired `alt`
  field; native visual validation rejects stale schemas and retired fields.
- Remove `Exemption.satisfied`, `RedLine.satisfied_exemptions`, and
  `RedLine.carved_out`. Use dated `evaluate_action` assessments and their
  classifications/traces for action review; dated applicability remains a
  context-evidence predicate, not full action readiness or proof of an exemption.
- Preserve author policy, refusal noncompensation, typed-tier authority,
  evidence-first stops, and all six non-adopted candidates.
- Label the original four-instrument orientation as historical and direct
  current eight-color membership to the Line Set declaration. Separate candidate
  prospective examples from current token-silence and structural probes.
- Use American English in maintained prose, captions, guidance, and owned test
  identifiers; preserve historical records and source identities.
- Retire documentation-wording, figure-config source-copy, and static-count gates
  instead of re-pinning prose; label the dated inventories as history and use
  native pytest collection for the current runnable inventory.
- Distinguish the retained citation cohort from current family membership in
  skill and citation metadata notes; preserve published source identities.
- Refresh the generated dependency lock without changing declared constraints.
- Interpret non-object template-validation JSON as an explicit failed report,
  matching the render-report boundary instead of raising `AttributeError`.
- Cut over current package, manuscript, skill and citation metadata to 0.5.0;
  preserve issued canaries and historical release packets. No new DOI,
  independently published canary or current publication render is asserted.

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
- Preserve the executed render comparison across engine cleanup, with tracked
  source, renderer and final artifact bindings. Reject hash-only release evidence.
- Cite this version through the repository; retain the verified DOI only in
  historical references pending the author's reserve-first successor identifier.
- Distinguish candidate-version manifests from the repository's historical
  public availability; green readiness checks do not attest version publication.

See [the review dispositions](docs/review-20261020.md) and the dated
[candidate packet](docs/releases/v0.4.0.md) for historical verification results.
The existing DOI remains a historical identifier;
successor Zenodo versions follow the author's reserve-first procedure.

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
