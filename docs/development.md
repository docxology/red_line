# Development guide

Contributor guide for `red_line` — a personal red-line framework that adapts
Alex Turner's ["A Red Line and Oversight Framework for Government AI
Contracts"](https://turntrout.com/red-line-framework) (2026-07-15) from an
organization-selling-to-governments down to a single practitioner governing his
own development work.

The registry is released publicly at <https://github.com/docxology/red_line>. There
is **no external verifier**. Named authorizations are self-reported escalation
records and never release a blocking result.
The framework's honest scope is **auditability, not enforcement**: each red line
is the author's dated, first-person, revisable commitment — not a universal
moral claim, and not authored by any AI.

## Setup

Pure-stdlib package; the only third-party dependencies are test tools.

```bash
uv sync --extra dev          # installs pytest + pytest-cov into .venv
```

`.venv/bin/python` is the interpreter for every command below. There is no
`infrastructure/` layer and no LLM/network dependency — the package imports only
`dataclasses`, `enum`, `hashlib`, `json`, `datetime`, and `collections`.

## The gate

One command is the full self-test:

```bash
.venv/bin/python -m pytest tests/ --cov=red_line --cov-fail-under=90
```

- `--cov-fail-under=90` is the enforced floor (also pinned in
  `pyproject.toml` → `[tool.coverage.report].fail_under = 90`).
- The suite is expected to hold `src/red_line/` comfortably above the 90% statement and
  branch floor. `__init__.py` files are omitted from measurement
  (`[tool.coverage.run].omit`), so the 100% bar applies to every module that
  carries logic. Treat any drop below 100% as a missing test, not as "still
  above the floor."
- Coverage is branch-aware (`branch = true`); a new conditional needs both arms
  exercised.

A green run means the artifact is internally consistent (beacon prose pinned to
the machine registry, invariants hold, trust-model boundaries asserted). It does
**not** substitute for the external prior-statement canary check described in
[`VERIFY.md`](VERIFY.md).

The current reconstructed tree is expected to keep every logic-bearing module at
100.00% statement and branch coverage. The exact test count and artifact hashes
belong to the generated release manifest rather than this guide, because they
change whenever a justified regression test is added. A green run is a regression
gate, not evidence that the personal commitments are universally correct or that
the artifact has an external auditor.

## Rendered publication artifacts

The canonical rendered artifacts are the combined manuscript PDF
(`output/pdf/red_line_combined.pdf`) and combined HTML
(`output/web/index.html`). The project configuration deliberately disables slide
rendering because the shared slide path leaves citation tokens unresolved; no
slide deck is a release deliverable. The renderer also emits per-section HTML
files for local navigation, but the combined HTML is the citation-resolved web
artifact and the one to publish.

The render comparison also materializes `output/data/release_inputs.json`, a
deterministic snapshot of the source ledgers, figure-registry hash, and live
analysis metrics. This keeps the shared output validator and release manifest
pointed at the same source-to-render boundary.

Figures are a separate deterministic input stage. Regenerate them before the
template render so both PDF and combined HTML see the current source-derived
assets:

```bash
.venv/bin/python scripts/build_figures.py

# The render engine is a separate repository. Clone it wherever you like:
git clone https://github.com/docxology/template /path/of/your/choosing/template
export RED_LINE_TEMPLATE_ROOT=/path/of/your/choosing/template

# Then render from that checkout, naming this project by its qualified name.
# The engine expects the project reachable under its own projects/ tree; link
# or copy this checkout there as `working/red_line`.
(cd "$RED_LINE_TEMPLATE_ROOT" \
  && uv run python scripts/pipeline/stage_03_render.py --project working/red_line \
  && uv run python scripts/pipeline/stage_04_validate.py --project working/red_line)
```

`RED_LINE_TEMPLATE_ROOT` names the engine for both the render and the manifest.
When it is unset, `red_line.release.provenance.find_template_root` searches the
ancestors of this project root for a directory named `template` that actually
carries `scripts/pipeline/stage_03_render.py`, and reports `None` when there is
none. Nothing is assumed to sit at a fixed relative path: the previous default,
`root.parents[2] / "template"`, was the private monorepo's shape and named a
directory that does not exist in a standalone clone. `require_template_root`
raises `TemplateRootUnavailable` naming the variable, the marker file, and every
location searched, rather than handing the renderer a `cwd` that is not there.

This is an honest external dependency, not a hidden one. Without the engine this
repository still runs its full test suite, the coverage gate, the deterministic
figure build, and every script under `scripts/`; what it cannot do is typeset
itself. See [`STANDALONE.md`](../STANDALONE.md).

For a release candidate, run the render comparison after those inputs are
current. The `--render` path also requires the strict release manifest: every
required report must exist and pass, and both the Red Line subtree and sibling
template checkout must be clean.

```bash
uv run python scripts/quality_gate.py --as-of 2026-07-24 --render
```

When the shared template checkout has unrelated working changes, use a clean
detached template worktree and set `RED_LINE_TEMPLATE_ROOT` for the render and
manifest commands. The manifest records that resolved renderer path; never
discard another task's template changes merely to satisfy this gate.

The eighteen figures are explanatory schematics, a source-reading map, a
transfer matrix, a line-set orientation, an outcome-precedence ladder, an
explicit improvement loop, and seven analysis-derived views (the exemption
evidence matrix, the exercised outcome-coverage plate, the
tier-monotonicity lattice, the registry composition profile, the
scope-vocabulary collision grid, the evidence-gate sensitivity sweep, and the
exemption trigger-semantics probe). A green
figure-registry check is necessary but not sufficient: inspect the final PDF
and combined HTML for clipping, figure labels, caption length, and caveat
visibility. The public release remains gated on an external canary witness and
private-file scrubbing.

## Test layout

`tests/` mirrors `src/red_line/` one-to-one, plus a `hardening/` package for the
adversarial battery, an `integration/` package for cross-module trust-model
tests, and the root-level modules that sit outside the mirror by design because
each one checks a property of the whole tree rather than of one module. The
root-level list below is bound to disk by
`tests/test_suite_inventory_binding.py`, which is what stopped it from saying
"two" while seven modules were present:

| `src/red_line/` module | test package |
| --- | --- |
| `src/red_line/model/{enums,red_line,action}.py` | `tests/model/test_{enums,red_line,action}.py` |
| `src/red_line/registry/lines.py` | `tests/registry/test_lines.py`, `tests/registry/test_provenance.py` |
| `src/red_line/evaluation/evaluator.py` | `tests/evaluation/test_evaluator.py`, `tests/evaluation/test_monotonicity.py` |
| `src/red_line/oversight/{findings,transparency}.py` | `tests/oversight/test_{findings,transparency}.py` |
| `src/red_line/canary/{hashing,statement,verification}.py` | `tests/canary/test_{hashing,statement,verification}.py`, `tests/canary/test_scripts.py` |
| `src/red_line/invariants/checks.py` | `tests/invariants/test_checks.py` |
| `src/red_line/analysis/{registry_metrics,outcome_coverage,monotonicity}.py` | `tests/analysis/test_registry_metrics.py`, `tests/analysis/test_outcome_coverage.py`, `tests/analysis/test_monotonicity_sweep.py` |
| `src/red_line/release/{provenance,snapshot,manifest,determinism}.py` | `tests/release/test_{provenance,snapshot,manifest,determinism}.py` |
| `src/red_line/contracts/*.py` | `tests/integration/test_contracts_branch_coverage.py` (branch coverage) plus the live-tree checks in `tests/integration/test_release_bindings.py` |
| `src/red_line/figures/*.py` | `tests/test_figures.py` |
| `src/red_line/envelope.py` | `tests/test_witness_envelope.py` |
| (adversarial, cross-cutting) | `tests/hardening/test_{canary,constructor_rejections,digest,invariants,registry_anchors,scope,staleness}.py` |
| (cross-module) | `tests/integration/test_beacon_binding.py`, `tests/integration/test_trust_model.py`, `tests/integration/test_manuscript_composition_binding.py`, `tests/integration/test_release_bindings.py`, `tests/integration/test_release_hardening.py` |
| (root-level, outside the mirror) | `tests/test_figures.py` (figure registry and generators), `tests/test_figure_legibility.py` (rendered point size of every figure's smallest label), `tests/test_new_composition_figures.py` (derivation and planted-defect falsifiability for the two composition plates), `tests/test_decision_surface_figures.py` (derivation and planted-defect falsifiability for the evidence-gate sensitivity sweep and the exemption trigger-semantics probe), `tests/test_no_substitutes.py` (lexical no-mock policy over `src/`, `tests/`, `scripts/`), `tests/test_script_clis.py` (fail-closed argument handling for every `scripts/` entrypoint), `tests/test_suite_inventory_binding.py` (this table and the `tests/` maps, recomputed from a real collection), `tests/test_standalone_contract.py` (the separated-copy contract: tracked sources, no link out of the repository root, and a current `STANDALONE.md`), `tests/test_witness_envelope.py` (the canonical review-finding serialization, its digest, and the common report envelope — determinism, completeness, tamper detection, and the non-claims traveling inside the record), and `tests/test_hardening_contracts.py` (residual multi-concern contract suite — see [`tests/AGENTS.md`](../tests/AGENTS.md) for why it has not been folded into `tests/hardening/`), and `tests/test_publication_metadata.py` (publication-metadata contract: version agreement across four artifacts, exact sibling URLs, no unverified DOI, dual LICENSE, no absolute local paths) |

`pyproject.toml` sets `pythonpath = ["src", "."]` for pytest, so the package
imports as `red_line` (`from red_line.canary import registry_hash`) and the test
package imports as `tests.helpers` — no `conftest.py` path bootstrap exists or is
needed. Fixtures live in `tests/fixtures/` — notably `canary_committed.json`, the
git-committed prior attestation the canary scripts anchor against.

**Where to add a test:** put it in the test module that mirrors the `src/red_line/`
module you touched. If a change spans modules (e.g. registry content that must
re-bind against the beacon prose or the canary hash), add it under
`tests/integration/`. New behaviour must land with the test that would fail
without it, and every branch you introduce must be covered.

## No mocks, real objects

No mocking framework is used or permitted — no `unittest.mock`, `MagicMock`, or
`monkeypatch`-based dependency replacement. `monkeypatch` is used only to
isolate the environment (`setenv`/`delenv` on `PATH`, `VIRTUAL_ENV`, and
`RED_LINE_TEMPLATE_ROOT`), never to swap a function for a stand-in. That rule is
enforced, not just stated: [`tests/test_no_substitutes.py`](../tests/test_no_substitutes.py)
scans every `.py` file under `src/`, `tests/`, and `scripts/` for the framework
tokens, the replacing `monkeypatch` forms, and retired substitute branding, and
carries planted-offence tests proving it detects each one. The policy path is
deterministic and I/O-free, so tests construct real values and assert on real
output:

- Build real `RedLine`, `ProposedAction`, and `CanaryStatement` objects.
- Call the real `evaluate_action`, `verify_canary`, `registry_hash`, and
  `all_invariants` against the real `PERSONAL_RED_LINES` registry.
- Invariant tests are **proof-of-detection**: each `check_*` is asserted to pass
  on the real registry **and** to fail on a planted-bad registry, so a green
  check cannot be vacuous.
- Script tests (`tests/canary/test_scripts.py`) invoke the real
  `scripts/*.py` entrypoints and read real files (`canary_committed.json`).

`src/red_line/release/` is the one subpackage that does I/O, and its tests stay
real rather than mocked by construction:

- `tests/release/test_provenance.py` runs real `git init`, `add`, and `commit`
  in `tmp_path` to exercise clean, dirty, and non-repository states, and hashes
  real files written to disk.
- `tests/release/test_determinism.py` reaches the render path by writing a real
  executable named `uv` into a `tmp_path` directory and pointing `PATH` at it,
  so `template_render_passes` genuinely runs a subprocess and its invocations
  are recorded in a log file. The unavailable-tool branches are reached by
  pointing `PATH` at an empty directory, not by patching `shutil.which`.
- Every release entry point takes `root: Path` explicitly, which is what makes
  a temporary tree a first-class argument instead of something to patch around.

## Adding a red line

The registry is `PERSONAL_RED_LINES` in
[`src/red_line/registry/lines.py`](../src/red_line/registry/lines.py) (`REGISTRY_IS_EXHAUSTIVE =
False` — absence of a line is not endorsement). Adding one is **not** a code
change alone; it changes the published registry hash and requires a full canary
re-issue. The amendment runbook — the candidate lines already scoped and
verified against the evidence-gated evaluator, plus the exact re-issue checklist — is
[`docs/PROPOSED_RED_LINES.md`](PROPOSED_RED_LINES.md). In outline:

1. Add the `RedLine` to `PERSONAL_RED_LINES` with a content-bearing narrative
   `carve_outs` clause, a non-empty `scope`, at least one typed `Exemption` with
   required evidence, and honest `stated_by` / `stated_on` provenance.
2. Run `all_invariants(PERSONAL_RED_LINES)` — unique ids, non-empty scope,
   content-bearing narrative carve-out, typed exemptions with required evidence,
   valid enum field types, and non-empty standard/rationale text must all hold.
   `CANARY` severity stays reserved for
   the two Turner-Standard analogs (`STANDARD_ANALOG_IDS`); extensions are
   `ABSOLUTE` or `STRONG`, and a `CANARY` line may never be `AIR_GAPPED`.
3. Recompute the hash and update every pin: `README.md`,
   `manuscript/09_red_lines.md`, the beacon prose, the line count in
   `manuscript/11_conclusion.md`, and regenerate
   `tests/fixtures/canary_committed.json`.
4. Issue a dated **successor** canary (`build_canary.py --rationale ...`) so the
   prior attestation is not silently re-attested.
5. Re-run the gate.

An amendment must be the author's own explicit, dated decision. A model must not
add, remove, or weaken a line unilaterally.

## Running the canary scripts

Both scripts are thin orchestrators (I/O only; all logic in `src/red_line/canary/`). The
JSON form includes the issue-time `line_digests` triples, so the committed
fixture transports the same per-line binding that `issue_canary` creates.

```bash
# Print the current statement, line ids, and registry SHA-256 (defaults to today):
.venv/bin/python scripts/build_canary.py $(date +%F)

# JSON form, byte-identical to the committed fixture serialization:
.venv/bin/python scripts/build_canary.py $(date +%F) --json

# Verify the git-committed prior canary against the live registry.
# Exit 0 iff intact (hash unchanged, fresh, and metadata-consistent), else 1:
.venv/bin/python scripts/check_canary.py

# Recompute just the pinned registry hash:
.venv/bin/python -c "from red_line.canary import registry_hash; print(registry_hash())"
```

The current pinned registry SHA-256 is:

```
72835fd81d1f7ecf70f47b1e0061cd56c385273dd846879ab639225913f5aad7
```

`registry_hash()` is a deterministic SHA-256 over canonicalized `RedLine`
content — **no timestamps** — so two runs on an unchanged registry print an
identical hash. `build_canary.py` honors a successor guard: unless `--no-prior`
is passed, it loads the committed prior (`tests/fixtures/canary_committed.json`)
so a drifted registry cannot be silently re-attested.

`verify_canary` reports drift, removed/added/modified line ids, and staleness
(180-day freshness window, failing closed on missing, future, or unparseable
dates). A removed or modified **CANARY-severity** line escalates to
`CANARY-GRADE LINE ALTERED`, the loudest signal the instrument emits.

**Honesty of the instrument.** The canary uses the *pattern* of a warrant
canary, not the legal instrument. The statement is **forgeable by anyone with
write access** to this tree — a force-push rewrites both the registry and the
committed prior. Its only real force comes from an **external** prior copy (a
dated post, an earlier fetched commit, an OpenTimestamps proof, a reserved DOI)
checked by **someone other than the author**. Checking a statement the author
regenerated now proves nothing; it always matches the current registry by
construction. See [`VERIFY.md`](VERIFY.md) for the third-party runbook.

## Package rules

- `src/red_line/` **must never import `infrastructure.*`** and must stay **pure
  stdlib**. This mirrors the `template_code_project` lineage: the package is
  infrastructure-independent domain logic with deterministic behaviour and no
  I/O. Any I/O belongs in `scripts/`.
- The public API is re-exported from
  [`src/red_line/__init__.py`](../src/red_line/__init__.py) — `RedLine`, `DeploymentTier`
  (`HOSTED`/`CONNECTED`/`AIR_GAPPED`), `Severity`
  (`CANARY`/`ABSOLUTE`/`STRONG`), `Classification`
  (`INSUFFICIENT_INFORMATION`/`OUTSIDE_SCOPE`/`COMPLIANT`/`REQUIRES_MODIFICATION`/`NON_COMPLIANT`), `ProposedAction`,
  `ActionAssessment`, `PERSONAL_RED_LINES`, `evaluate_action`, `ReviewFinding`,
  `review_engagement`, `transparency_report`, `CanaryStatement`,
  `verify_canary`, `registry_hash`, `issue_canary`, `is_stale`,
  `detect_line_removal`, `line_digest`, `all_invariants`, `invariants_pass`,
  and the report-envelope surface (`REPORT_SCHEMA`, `ENVELOPE_SCHEMA`,
  `RED_LINE_ID`, `SCOPE_AND_NONCLAIMS`, `ReportEnvelope`, `canonical_report`,
  `report_digest`, `finding_envelope`, `canonical_envelope`,
  `envelope_matches_finding`).
  Import from `red_line` (or the submodule), and update `__all__` when you add a
  public symbol.
- Keep behaviour deterministic: no wall-clock reads inside the hashed content,
  no randomness, no network.

## Evaluator semantics (for tests you write)

When you touch `evaluate_action`, preserve the staged contract (see
`docs/evaluator-semantics.md` and `tests/evaluation/test_monotonicity.py`):

1. Validate and normalize the mandatory `ActionContext`.
2. Return `INSUFFICIENT_INFORMATION` for missing, unknown, ambiguous,
   self-asserted, contradicted, or otherwise unresolved required information.
3. Canonicalize scope with explicit aliases only; do not use trailing-`s`
   heuristics or free-form exemption tokens.
4. Apply typed exemptions only when every required evidence kind is verified.
5. Return `NON_COMPLIANT`, `REQUIRES_MODIFICATION`, `COMPLIANT`, or the explicit
   `OUTSIDE_SCOPE` result. A description never supplies scope or evidence, and a
   review authorization never downgrades a blocking result.
