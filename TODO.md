# Red Line — open release backlog

This file contains only work that remains open after the private hardening and
release-preflight pass. The current private release gate is recorded in
`output/reports/release_manifest.json`.

## P1 — author-controlled candidate lifecycle

The six candidates remain explicitly non-adopted in
`docs/PROPOSED_RED_LINES.md`; no candidate may be added to
`PERSONAL_RED_LINES` automatically.

- [ ] If the author later reopens any candidate for adoption, record the
  decision, scope boundary, typed exemptions and `any`/`all` semantics,
  required evidence, false-positive controls, and positive/negative evaluator
  cases before any registry change.
- [ ] If a candidate is adopted, bump the package/version metadata, update all
  prose/hash/count/ledger surfaces, issue a dated rationaled successor canary,
  regenerate artifacts, and rerun every release gate.

## P2 — independent publication gate

- [ ] Publish the current canary statement and registry hash to an independently
  held public or append-only surface; record its exact URL, commit, timestamp,
  or equivalent witness locator in `docs/VERIFY.md` and the release manifest.
- [ ] Obtain an independent reviewer who compares the source registry, installed
  package, rendered PDF/HTML, claim ledger, release manifest, and prior canary;
  preserve the review record with the release evidence.
- [ ] Verify before publication that the external witness and reviewer are
  genuinely independent of the same writable checkout.
- [ ] Retain the explicit boundary on every publication surface: this is
  personal auditability, not enforcement, legal compliance, semantic safety
  classification, or external certification.

## P3 — post-expansion release-evidence refresh

Successive passes through 2026-07-27 — the analysis expansion, the hardening
pass, the thin-orchestrator split, the substitution audit, the legibility and
composition pass, and the script-CLI fail-closed pass below — moved the tested
tree to 765 tests with sixteen generated figures. The release evidence must
describe that current tree, not an earlier snapshot.

- [x] Strict release evidence regenerated (2026-07-29): with the sidecar
  window committed path-selectively, the full engine core pipeline run for
  this project ends `all_passed: true` (the analysis stage re-runs
  `compare_render_artifacts.py`, so `render_determinism.json` is fresh and
  the artifact manifest is coherent with the tree), and
  `build_release_manifest.py --strict` then exits 0 — `source_dirty: false`,
  `template_dirty: false` (a single untracked file in the template checkout
  was the last blocker; strict fails on any template dirt by design). The
  868-test, seventeen-figure tree now has a green strict manifest.
- [x] `quality_gate.py --render` reordered (2026-07-29, second window). The
  measured defect: its `compare_render_artifacts.py` step re-renders through
  the engine AFTER the engine's artifact manifest was captured, the engine's
  PDF is not byte-stable across renders, so the render passes flipped the
  engine validation report to "Artifact manifest: FAIL" before
  `build_release_manifest.py --strict` read it — the gate failed at its own
  last step from every starting state. The fix changes what the gate
  attests, deliberately: after the comparison, `release.template_full_pipeline`
  runs the engine's full core pipeline as the FINAL tree-producing step —
  the engine's one entrypoint that regenerates the artifact manifest
  alongside the artifacts — and only then does the strict manifest read the
  tree. Determinism is still attested by the comparison's two passes; the
  strict verdict now describes the pipeline's tree rather than a
  render-drifted one. Strict continues to require a committed sidecar tree
  and a clean template checkout, by design. Measured after the reorder
  (2026-07-29, committed tree, clean template): the whole
  `quality_gate.py --render` run exits 0 and prints "quality gate: passed" —
  the first end-to-end pass the gate has ever had.
- [x] Commit the expansion pass in the sidecar repo path-selectively
  (`-- working/red_line`), per the established pathspec discipline
  (2026-07-22: expansion + audit-fix commits, scope-verified via
  `git show --name-status`).

## Log

- 2026-08-01 — autonomous intelligence & visualization assessment pass.
  **Made.** (1) Reconciled `tests/test_figures.py:54` to the in-flight
  `manuscript/config.yaml` geometry (`left=0.42in` → `left=0.33in`, the value
  `red_line.figures.legibility` actually parses); the tree was 1-failing at 877
  before the reconciliation and is 878 passing + 100.00% coverage after. (2)
  Corrected a docstring claim drift in `src/red_line/model/action.py`:
  `ProposedAction.ambiguous` said it "forces at least REQUIRES_MODIFICATION
  when a line is implicated," but the evaluator (and
  `tests/evaluation/test_evaluator.py:122`, `tests/oversight/test_findings.py`)
  pins ambiguous to the intake-gate stop `INSUFFICIENT_INFORMATION`; the doc
  now says what the code does. **Verified.** Full `quality_gate.py --as-of
  2026-07-17` passed (figures build + five validators + ruff check + 878 pytest
  at ≥90% cov + canary + figure-byte-determinism + wheel smoke);
  `scripts/check_canary.py` intact; all 18 figures build deterministically, all
  18 are embedded in `manuscript/*.md` with zero orphans/dangling refs, and
  every derived figure number (16 exemption rows, 36/34 monotonicity slots over
  108 evals, 45 sensitivity runs, 58 trigger runs, 45 sources/44 ledger rows,
  canary digest `72835fd8…f5aad7`) matches prose. **Major — now fixed.** The
  test review-epoch time-bomb in `tests/helpers.py` (hardcoded
  `recorded_on="2026-07-15"` with ~40 behavioral tests relying on the default
  today-`as_of`) was migrated: `complete_context` now dates evidence at
  `date.today()`, and every explicit-past review date that consumed helper
  evidence was moved to a fresh date (`test_transparency.py`,
  `test_findings.py`, `test_trust_model.py`, `test_evaluator.py`,
  `test_scope.py`, `test_constructor_rejections.py`,
  `test_proposed_candidates_binding.py` `PROBE_AS_OF`,
  `test_stemming_boundary_binding.py` `REVIEWED_ON`,
  `test_witness_envelope.py` `AS_OF`). The witness-envelope module's
  analysis-battery cases stay pinned at their own fixed `BATTERY_AS_OF`
  (deterministic figures/prose), so a single date can never silently go stale
  for either source; the staleness-boundary test in `test_staleness.py` now
  derives `recorded` from the actual fixture evidence date instead of a
  hard-coded literal. Verified: 878 passed, 100.00% coverage, ruff clean,
  figures still byte-deterministic, `quality_gate.py` passes.
  **Minor (historical, not live).** `CHANGELOG.md` 0.3.0 records "877 passed" —
  the release-time count before the in-flight 878th test. `ruff format --check`
  is not a configured gate here (no `[tool.ruff.format]`; the tree
  deliberately writes non-ruff-format multi-line expressions) and no `mypy`
  config exists, so neither was enforced.
  **Also reconciled** (same pass): `CHANGELOG.md` 0.3.0 gate numbers were the
  last lagging surface of the in-flight inventory update — its "877 passed"
  and "50 test files" contradicted the sibling `tests/README.md` (which already
  read "878 collected"/"878 passed tests") and `tests/AGENTS.md` (51 files on
  disk). Both CHANGELOG numbers updated to 878 / 51 to match the current tree.
  No test binds the CHANGELOG, so no suite impact.

- 2026-07-29 (second window) — the envelope stated formally.
  `manuscript/08a_formalism.md` gains "The report envelope":
  `def:report-envelope` (the ten fields in order, bound to
  `dataclasses.fields(ReportEnvelope)`; `native_status` one instrument's
  word, never cross-line comparable; the `red-line.report/1.0` pointer with
  the absent authorization arm as explicit `null`) and
  `prop:envelope-pointer` (live agreement, every checked-field edit
  visible), with a binding-table row, two new claim-ledger citation rows
  (`data/formalism_claim_ledger.json`, 24 → 26 claims), and two new binding
  tests in `tests/integration/test_formalism_bindings.py` — each proven to
  bite by planting a drift in the real manuscript ("ten fields" → "nine
  fields"; "any checked field" → "some checked field") and watching exactly
  the named test fail before byte-identical restoration. The suite-inventory
  bindings moved with the two new tests (868 → 870 across the fourteen
  bound README/AGENTS sites). Measured at close (my own runs): 870 passed,
  100.00% coverage, re-rendered with zero undefined references, engine
  validation `all_passed: true` after a full core-pipeline pass, strict
  release manifest green under the pipeline-last-then-strict sequence.
  Version deliberately stays 0.3.0: the envelope surface itself shipped in
  the previous entry, and this window adds prose and tests over it.

- 2026-07-29 — common report envelope layer (line-set design review response).
  **What shipped.** "The Space Between the Lines" (an external reviewer,
  2026-07-29) proposed one common report envelope per line, pointing at the
  complete native report without reinterpreting it. Red Line now exports that
  contract: `src/red_line/envelope.py` adds `canonical_report`
  (`red-line.report/1.0`, the complete `ReviewFinding` derivation with the
  absent-authorization arm serialized as an explicit `null`), `report_digest`
  (SHA-256), and the envelope surface (`line.report-envelope/1.0`,
  `RED_LINE_ID`, transportable `SCOPE_AND_NONCLAIMS`, `ReportEnvelope`,
  `finding_envelope`, `canonical_envelope`, `envelope_matches_finding`), all
  re-exported from the package root. `tests/test_witness_envelope.py` (17
  tests) drives real `review_engagement` findings — including the analysis
  battery reaching all five classifications — through the envelope, pins
  determinism, field-roster completeness against `dataclasses.fields`,
  tamper detection on every checked field via `dataclasses.replace`,
  fail-closed inputs, and that the non-claims travel inside the record. A
  planted defect (envelope silently dropping its boundary sentences) turned
  the named non-claims test red before restoration was shasum-verified. The
  suite is 868 collected/passed tests at 100.00% total coverage;
  `envelope.py` alone measures 100.00% statement and branch. Decision record:
  `docs/correspondence.md`. The shared witness register the review proposes
  is deliberately **not** built here — it is a separate work. Manuscript
  formalism for the envelope is deferred to the next manuscript window
  (formal edits require a re-render and manifest pass), and the version stays
  `0.3.0` under an unreleased-style log entry for the same reason: additive
  code and docs, no bound version surface touched.
- 2026-07-27 — script-CLI fail-closed pass (adversarial verification).
  **Seven of eleven scripts could not fail on a bad argument.** `build_figures.py`
  and the five `validate_*.py` wrappers parsed no arguments at all, so
  `scripts/validate_source_claims.py --definitely-not-a-flag` printed
  `source/claim ledger: valid` and exited 0. `check_canary.py` was the severe
  case: it called `parse_args([] if argv is None else argv)`, and `None` is
  exactly what the `__main__` path passes, so the real command line was
  discarded wholesale — `--as-of 2099-01-01` and `--prior /nonexistent.json`
  both exited 0 with "canary intact". That flag is threaded from
  `quality_gate.py --as-of`, so the gate's *deterministic* freshness check was
  silently evaluating against today instead. Every script now parses its
  arguments and exits 2 on an unrecognized one; `check_canary.py` passes `argv`
  straight through. The in-process tests had always passed an explicit list, so
  they exercised a path that worked while the production entrypoint did not —
  `tests/test_script_clis.py` (48 tests) therefore drives every script as a real
  subprocess, and pins `--as-of` and `--prior` to observable behaviour rather
  than to a help string. Both original bugs were re-injected and confirmed to
  turn the new gate red (7 and 3 failures respectively).
  **A prose list that no gate read.** `docs/development.md` said the suite had
  "two root-level modules" and named two, while seven were on disk; the existing
  inventory binding reads only `tests/**/AGENTS.md` and `tests/**/README.md`, so
  the guide was outside every check. The list is now recomputed from disk by
  `test_the_development_guide_lists_every_root_level_test_module`, proven to go
  red on a removed entry.
  **A mechanism sentence that named the wrong exemption.**
  `manuscript/09a_registry_composition.md` said the shared token `handoff` is
  cleared on `dual-use-ablation` by its *methods-publication* exemption. It is
  not: that exemption's trigger tokens are `methods`, `paper`, and `benchmark`,
  and a declared scope of exactly `handoff` reaches none of them. The evaluator
  reports applying `retained-oversight`, which triggers on the hosted tier. The
  surrounding counts were all bound to derived metrics; this sentence sat
  between them and was not, which is how a plausible-but-wrong mechanism
  survived. The id is now re-derived from the assessment's own reason strings
  by `test_the_named_applied_exemption_is_the_one_the_evaluator_reports`, which
  also rejects naming any exemption the evaluator did not apply; restoring the
  original wording turns it red.
  **Two more surfaces that contradicted their own file or its sibling.**
  `docs/visualization-briefs.md` opened by correctly calling five figures
  analysis-derived and then, in its own module table, said `plates_analysis.py`
  owns "three plates" and named three — the two plates added in the previous
  pass never reached the table. Per-module ownership is now recomputed from
  `GENERATORS.__module__` by
  `test_visualization_brief_module_table_matches_generator_ownership`. And
  `README.md` still said "Three separate works are being developed beside it"
  after `manuscript/02b_line_set_orientation.md` and the sidecar line-set map
  had both been updated to name `line_set` the fifth work; the README now
  carries the same acknowledgement, including the no-dependency clause and the
  fact that the *set* remains four lines. Suite 714 → 765 passed at 100.00% statement and branch
  coverage over `src/red_line/` (2596 statements, 888 branches, zero missed,
  zero partial); figure set unchanged at sixteen, byte-identical across two
  independent builds; minimum rendered label 6.01pt across all sixteen. No
  registry content, evaluator semantics, canary hash (`72835fd8…f5aad7`), or
  boundary/canary wording changed.

- 2026-07-27 — legibility, composition, and claim-correction pass.
  **Figure legibility became a measured invariant.** `red_line.figures.legibility`
  derives, from the built PNG/SVG pair, the manuscript's declared `width=`, and
  the page geometry in `manuscript/config.yaml`, the point size at which each
  figure's smallest label lands on the page, and `tests/test_figure_legibility.py`
  fails below 6pt. Measured before: `fig:tier-monotonicity-lattice` rendered its
  smallest label at **2.71pt** — the shipped 1400x1320 PNG was height-capped to
  379.4pt wide (267 ppi measured with `pdfimages -list` on the shipped PDF,
  object 269, page 23) and drew 10-unit chips. Two structural fixes: the shared
  template's injected `height=0.5\textheight` cap was raised to 0.92 through
  `rendering.figure_height_fraction`, so width binds for every plate, and the
  canvas font floor `theme.MIN_FONT_PX` was raised to 16 — a value re-derived
  from the narrowest embed rather than chosen, and asserted to be the smallest
  integer that clears the floor. Measured after: **6.01pt** minimum across all
  sixteen figures, every figure width-bound at 192 ppi in the re-rendered PDF.
  The knob is bound end-to-end: a test compares the configured fraction with the
  `height=` the generated LaTeX actually received, which is what proves the
  config key is consumed rather than merely named.
  **Two derived figures.** `fig:registry-composition-profile` (per-line severity,
  tier floor, and four structural counts on one derived shared scale, with the
  `unevidenced_exemptions()` count rendered as a band so today's zero is legible
  as a result) and `fig:scope-vocabulary-collisions` (the full 34-token x 7-line
  presence grid from the new `scope_token_membership()`, with the executed hosted
  verdict for each shared token read out of the monotonicity sweep). Both are
  computed at build time, both plant a defect in a copy of the registry and
  require the plate to follow it, and both rebuild byte-identically.
  **A wrong number, corrected.** The scholarship ledger covers **39** sources in
  **38** table rows, not 38 sources: Kukutai and Taylor occupies a row in both
  tables while the Cugoano row cites the primary text and its Stanford
  Encyclopedia entry. `data/source_claims.json` now publishes both counts and
  `validate_source_claims` re-derives them from the records and the method
  tables. Also corrected: `docs/invariants.md` documented ten invariants while
  `all_invariants()` ran fourteen (the four undocumented checks are now written
  up and the doc is recomputed from the battery); the sweep's 36 is line/keyword
  *slots* over 34 distinct tokens, not 36 keywords; the abstract's stemming claim
  is scoped to normalization, since a light stemmer still runs on the advisory
  hint path; `docs/PROPOSED_RED_LINES.md` names a real test file for the
  evaluator-silence claim it makes; and `docs/hardening.md` no longer carries a
  test count (323) that matched no state of the tree at any date.
  **Inventories are now derived.** Every per-folder test count, folder total,
  mermaid node, and stated suite size under `tests/` is recomputed from a real
  pytest collection, and an undocumented module fails rather than hides. The same
  discipline covers the present-tense figure count across seven surfaces.
  Ten planted defects were run against the new gates and all ten went red. Suite
  504 -> 714 passed at 100.00% statement and branch coverage; figure set fourteen
  -> sixteen. No registry content, evaluator semantics, canary hash
  (`72835fd8...f5aad7`), or boundary/canary wording changed.

- 2026-07-27 — substitution audit: removed the affordances that let a real thing
  be described as a stand-in. `resolve_rasterizer` now resolves only through
  `shutil.which("rsvg-convert")` and fails closed with install guidance; its
  hard-coded `/opt/homebrew` fallback branch is gone, so the tool is either on
  `PATH` on every machine or the build says so. The `sys.path` bootstrap was
  deleted outright — `scripts/_bootstrap.py` and `tests/conftest.py` are gone,
  every script imports `red_line` as an ordinary top-level import against the
  editable install, and the `# noqa: E402` markers that existed only to permit
  imports below a bootstrap call went with them. Two test-local executables were
  renamed to what they are (`recording_uv`, `no-output-rsvg-convert`), and the
  canary's aggregate-hash path lost its "legacy" label without losing its
  behavior: a statement with `line_digests=()` is still verified against the
  aggregate hash, and the committed fixture contract is untouched. The policy is
  now executable: `tests/test_no_substitutes.py` (16 tests) scans `src/`,
  `tests/`, and `scripts/` for mocking-framework tokens, replacing `monkeypatch`
  forms, and retired branding, assembling its needles from fragments so it needs
  no self-exclusion, and proving detection on planted offences. Suite 488 → 504
  passed at 100.00% statement and branch coverage (2251 statements, 778
  branches); Ruff clean; all four validators and the figure build unchanged. No
  registry content, evaluator semantics, canary hash, or boundary wording
  changed, and no red line was adopted or canary re-issued.

- 2026-07-27 — thin-orchestrator + signpost pass: split the 874-line
  `src/red_line/figures/plates.py` into `plates_scholarship.py` (four
  literature- and boundary-derived plates) and `plates_analysis.py` (three
  plates whose numbers come from executed analysis), leaving `registry.py` and
  the package `__init__` as the unchanged public surface; moved the release
  logic out of `scripts/build_release_manifest.py`,
  `scripts/compare_render_artifacts.py`, and `scripts/build_release_data.py`
  into the new `src/red_line/release/` subpackage (`provenance`, `snapshot`,
  `manifest`, `determinism`) and reduced those three scripts to argument
  parsing plus one call each; added `tests/release/` with 66 real tests over
  isolated git repositories, real digest trees, and a real recording-`uv` render
  path. Suite 427 → 488 passed, 100.00% statement and branch coverage held,
  and all fourteen figure SVGs are byte-identical across the split
  (`build_figures` before/after digests match). No registry content, evaluator
  semantics, canary hash, or boundary wording changed.

- 2026-07-24 — repo-wide hardening pass: made the project gate build ignored
  figures before figure-dependent tests; separated source-only release binding
  checks from strict rendered-surface checks; bound evidence-registry numbers to
  live registry, outcome-coverage, and tier-monotonicity analysis metrics;
  updated the render comparator to the current sibling-template pipeline;
  added project/docs/cover signposts; reconciled current commands, lifecycle
  guidance, version authority, and analysis documentation. Final verification:
  398 tests and 100.00% coverage; template PDF/HTML/evidence validation passed;
  two render passes were content-identical; strict signposts had zero issues;
  strict manifest readiness remains blocked only by the dirty source checkout,
  while the sibling template checkout is clean.

- 2026-07-22 — analysis expansion + operability pass: added the read-only
  `src/red_line/analysis/` subpackage (`registry_metrics` — exemption ×
  evidence matrix, demand/severity/tier-floor/scope-token views, free-pass
  detector with planted-registry proof-of-detection; `outcome_coverage` —
  five-case battery through the real `evaluate_action` at fixed
  `BATTERY_AS_OF`, all five classifications reached); two figures rendered
  from executed analysis (`exemption_evidence_matrix`,
  `outcome_coverage_plate`, figure set eleven → thirteen); new manuscript
  section `09a_registry_composition.md` plus expansions of 08/09/10; every
  new prose number recomputed by
  `tests/integration/test_manuscript_composition_binding.py`; suite
  338 → 385 passed (100.00% statement+branch coverage held), then → 386
  after a same-day advisor-driven mutation A/B exposed one unbound totals
  sentence and `test_exemption_and_evidence_totals_match` was added (and
  shown to go red on a corrupted literal). Operability
  layer: SKILL.md gained worked evaluate/analyze/canary/gate recipes,
  README gained the derived-analytics section, ISA.md gained a dated
  changelog/decision entry. No registry content, evaluator semantics, or
  canary hash changed (`72835fd8…f5aad7` intact). Follow-ups tracked in P3.

- 2026-07-21 — improvement pass (review findings RL-1..RL-4): appended a
  current verification snapshot to `ISA.md` (338 tests, 100.00% coverage,
  registry SHA-256 `72835fd8…f5aad7`, v0.3.0) and retitled the superseded
  2026-07-17 section; fixed the stale `tests/test_trust_model.py` path in
  `README.md`; indexed seven previously unlisted docs in `docs/README.md`;
  completed the Test layout table in `docs/development.md` with the
  integration release suites and root-level suites. No boundary, beacon, or
  canary statement wording was altered.
