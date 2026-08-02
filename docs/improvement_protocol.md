# Improvement protocol

**Protocol date:** 2026-07-18
**Scope:** Red Line methods, documentation, manuscript, visualizations, and release evidence
**Mode:** bounded autonomous improvement using FirstPrinciples Reconstruct, Science FullCycle, and three Loop iterations

This document is the working protocol for the current improvement pass. It is
not a claim that the framework is externally validated. It records what was
observed, what will be changed, what would count as failure, and when the pass
must stop.

## Objective

Make Red Line easier to inspect as an epistemic boundary instrument: a local,
deterministic method for declining or narrowing high-risk development work
before commitment, while making uncertainty, evidence limits, scope, and
remaining external dependencies visible. The improvement must strengthen the
connection among four layers:

1. the operational evaluator and its typed records;
2. the research and claim ledgers;
3. the manuscript's methods and non-claims; and
4. the generated figures and release gates.

The pass must not turn a local self-governance tool into a universal ethics
code, a semantic safety classifier, a legal determination, an enforcement
system, or an external certification.

## Loop 1: observation and challenge

### Baseline observation

The existing Red Line tree is already strong on local integrity. On 2026-07-18
the working tree produced:

| Gate | Result |
|---|---|
| Ruff | pass |
| Test suite | 338 passed; 100% statement and branch coverage |
| Source/claim ledger | valid |
| Proposed red-line ledger | valid; six candidates remain non-adopted |
| Release bindings | valid |
| Generated figures | 11; deterministic across repeated builds |
| Template output | rendered and locally inspected; template output validation passed |
| Canary | unchanged and fresh |

The active working tree also contains a concurrent, in-scope manuscript edit in
`manuscript/02b_line_set_orientation.md`; it is preserved as input to this
pass, not overwritten.

This record was re-audited on 2026-07-18. The current evidence is recorded in
the gates and release artifacts produced by this pass; the earlier baseline is
historical context, not a current release claim.

### First-principles deconstruction

The fundamental job is not “classify all development.” It is:

> help one practitioner decline or narrow a high-risk action before commitment,
> leave an inspectable record of why, and disclose what the instrument cannot
> establish.

Its necessary parts are therefore:

| Necessary part | Current realization | Required coherence check |
|---|---|---|
| Prior commitment | beacon, registry, canonical hash | the commitment must be distinguishable from later interpretation |
| Action representation | typed scope, deployment tier, nine context dimensions | every decision path must expose missingness and evidence state |
| Decision rule | deterministic evaluator and five outcomes | the prose and figures must use the same precedence |
| Review record | finding, authorization, transparency tally | authorization must not silently override a block |
| Drift witness | canary statement and external-prior condition | a hash must not be described as prevention or independent truth |
| Research boundary | source ledger, claim register, transfer limits | descriptive, transfer, implementation, and release claims must remain separate |
| Release boundary | figure registry, render validation, manifest | generated artifacts must bind back to source and remain inspectable |

### Constraints to preserve or challenge

| Constraint | Classification | Decision for this pass |
|---|---|---|
| Deterministic, pure local evaluator | hard | preserve |
| No semantic truth inference from lexical input | hard | preserve and state more prominently |
| No external witness available inside the package | hard | preserve and expose as a residual dependency |
| No author assent assumed for proposed red lines | hard | preserve; candidates remain non-adopted |
| Source/generated surfaces must bind | hard | strengthen with a machine-readable claim contract |
| Seven current first-person lines | current design choice | preserve as current state, not universal completeness |
| Fourteen generated figures (eleven at the time of this record) | current design choice | keep the source, registry, brief, manuscript, and artifact inventory aligned |
| No slide deck | output choice | preserve; do not create a new format without evidence of need |
| Lexical interface | implementation boundary | preserve; document the semantic limits instead of implying coverage |
| Ignored generated output | repository policy | preserve; require deterministic rebuild and rendered validation |

### Hidden assumptions to test

1. Passing local tests could be mistaken for evidence that an action is safe.
2. A populated source ledger could be mistaken for independent source
   verification or systematic-review coverage.
3. A polished diagram could be read as empirical evidence rather than a
   source-driven control-flow or provenance schematic.
4. `OUTSIDE_SCOPE` could be read as permission instead of a registry result.
5. A methods reader may not be able to move mechanically from a claim to its
   evidence, stopping point, and falsification condition.

## Pre-registered hypotheses

### H1 — operational coherence

Adding one explicit methods contract and machine-readable claim vocabulary will
reduce ambiguity between evaluator semantics, documentation, and manuscript
claims.

**Falsification:** any release gate can pass while the five evaluator outcomes,
evidence states, or claim classes disagree across source, methods, and generated
documentation.

### H2 — reader calibration

Adding a source-driven method-loop figure and explicit non-claims will make the
boundary between local decision evidence, scholarship transfer, and external
witness conditions visible without relying on color or surrounding prose.

**Falsification:** the rendered figure or caption implies enforcement, safety,
legal validity, empirical performance, or external certification; or the same
meaning cannot be recovered from the alt text and caption in a text-only read.

### H3 — trust through negative controls

Adding negative-control checks to the validation path will improve trust more
than adding untested prose: the system should refuse a malformed claim row,
unknown claim class, missing stopping point, or figure-inventory drift.

**Falsification:** a deliberately malformed contract, stale figure count, or
unsupported claim can still pass the relevant gate; or a new control weakens
fail-closed behavior by silently substituting defaults.

## Reconstruction

The reconstructed method will use this sequence:

```text
deconstruct the question
        ↓
challenge scope, evidence, authority, and hidden assumptions
        ↓
declare claim class + evidence state + stopping point
        ↓
represent action and context as typed records
        ↓
evaluate with fail-closed precedence
        ↓
freeze finding, authorization, and transparency record
        ↓
verify canary and source/generated bindings
        ↓
revise only through an explicit, reviewable amendment
```

The sequence is a method for producing inspectable records, not a promise that
the resulting records are true in the world. The implementation will keep the
following evidence states distinct: `MISSING`, `SELF_ASSERTED`, `UNVERIFIED`,
`CONTRADICTED`, `STALE`, and `VERIFIED`. Only the final state can support a
narrowing exemption, and even then only within the local rule's scope.

## Success criteria and stopping rules

The pass is successful only if all of the following are true:

- every publication-facing claim has a class, supporting surface, verification
  mode, and explicit stopping point;
- the operational protocol covers all five classifications and the evidence
  gate without a prose-only exception;
- the figure registry, visualization brief, manuscript references, and generated
  output agree on the complete figure set;
- the new method-level figure is deterministic, accessible in text, and bounded
  as a schematic;
- the full test suite, Ruff, source claims, proposed ledger, release bindings,
  and canary pass; the release gate reports explicit readiness or an explicit
  blocker, and no warning is promoted to a pass;
- PDF and HTML are regenerated from the current source and both rendered passes
  validate; repeated rendering produces identical content hashes;
- explicit non-claims remain present: no semantic truth inference, no
  enforcement, no legal conclusion, no universal ethics code, no external
  certification, and no independent witness unless one actually exists; and
- no proposed red line becomes adopted without a separately recorded amendment.

Stop and report instead of weakening a gate if any criterion fails, if a new
claim requires unverified external research, or if a change would alter the
public identity of an existing work without an explicit migration decision.

## Iteration record

| Loop | Focus | Status | Evidence |
|---:|---|---|---|
| 1 | observe, deconstruct, challenge, pre-register | complete | this protocol; baseline table above |
| 2 | reconstruct methods, ledgers, and manuscript | complete | claim-register validator; 338 tests with 100% statement/branch coverage; manuscript section 02d; structured reason/evidence trace |
| 3 | rebuild visuals, render, and release coherence | complete with release boundary | eleven-figure registry; valid PDF/HTML/output structure; two-pass comparison identical; strict clean-checkout gate remains blocked by dirty source/template checkouts, while publication remains pre-publication without an external witness and independent reviewer |

This protocol is itself a bounded project record. It should be revised only by
adding a dated result or by recording why a criterion was blocked; it must not
be edited retroactively to make a failed experiment appear successful.

## Verification result — 2026-07-24

The repo-wide hardening pass preserved the registry and canary while making the
source gate independent of ignored rendered output, binding release evidence to
live analysis metrics, updating the comparator to the current sibling-template
pipeline, and adding the missing project/docs/cover signposts. The source gate
passed with 398 tests and 100.00% statement/branch coverage. The canonical
template render and validation passed with 14 figures, a valid PDF/HTML tree,
and no unsupported evidence numbers. Two render passes reported identical
content. Strict signpost and agent-prompt validation passed with zero warnings
or errors. The strict release manifest has all validation results passing and
is blocked only because the source checkout remains dirty; the sibling template
checkout is clean. Publication remains pre-publication without an external
canary witness or independent reviewer.

## Verification result — 2026-07-27

The thin-orchestrator pass changed structure without changing behavior. The
874-line figure plates module was split by the provenance of its numbers into
`plates_scholarship.py` and `plates_analysis.py`, and release assembly moved out
of three `scripts/` files into a new `src/red_line/release/` subpackage
(`provenance`, `snapshot`, `manifest`, `determinism`), leaving those scripts as
argument parsing plus one call each.

The source gate passed: `quality_gate.py --as-of 2026-07-27` reported
`quality gate: passed`, including the byte-determinism double build and the
wheel smoke install. The suite is `488 passed` at 100.00% statement and branch
coverage (2254 statements, 780 branches, zero missed, zero partial), grown from
427 by the new `tests/release/` package of 66 tests over isolated git
repositories, real digest trees, and a real render path exercised through a
recording `uv` executable on `PATH`. Ruff reported no findings and left all 107
files unchanged. All five validators exit 0 and the canary is intact.

Figure output was proven unchanged rather than assumed: all fourteen SVGs
rebuild byte-identically, and each of the seven plate generators was compared
against the pre-split module's compiled bytecode and returned an identical SVG
string. The remaining seven figures come from `diagrams.py`, which the split did
not touch.

The canonical PDF/HTML render was **not** re-run in this pass. The 2026-07-24
render, validation, and two-pass determinism evidence above remains the most
recent; because `CLM-008` is a per-run source-to-render claim, it is not carried
forward by an unchanged SVG boundary. Strict release manifest readiness remains
blocked by the dirty source checkout, and publication remains pre-publication
without an external canary witness or independent reviewer.

## Verification result — 2026-07-27, substitution audit

A follow-up pass removed the remaining affordances that let a real thing be
described as a stand-in, and made the no-mock rule executable rather than
advisory.

Three substantive changes. `resolve_rasterizer` lost its hard-coded
`/opt/homebrew/bin/rsvg-convert` fallback and now resolves only through
`shutil.which("rsvg-convert")`, failing closed with install guidance — a
missing tool is reported on every machine instead of being silently satisfied
on the one where it happens to be installed. The `sys.path` bootstrap was
deleted: `scripts/_bootstrap.py` and `tests/conftest.py` are gone, every script
imports `red_line` as an ordinary top-level import against the editable install,
and the `# noqa: E402` markers that only existed to permit imports below a
bootstrap call went with them. Both execution modes were re-proven —
`uv run python scripts/<name>.py` and `from scripts import <name>`.

Two renamings and one de-branding carried no behavior change. The test-local
executables became `recording_uv` (it appends each invocation to
`$UV_INVOCATION_LOG`) and `no-output-rsvg-convert` (it exits 0 without writing a
PNG, which is precisely what the test exercises). The canary's aggregate-hash
path is described as an aggregate-only statement rather than a legacy one: a
`CanaryStatement` with `line_digests=()` is still verified against the aggregate
hash, and the committed fixture contract is untouched.

The policy is now enforced by `tests/test_no_substitutes.py`, which scans every
`.py` file under `src/`, `tests/`, and `scripts/` for mocking-framework tokens,
the replacing `monkeypatch` forms, and retired substitute branding, while
leaving `monkeypatch.setenv`/`delenv` allowed. Its needles are assembled from
string fragments, so the module never matches itself and needs no
self-exclusion branch. It is not a tautology: eleven planted-offence cases prove
each blocked token is detected with the right path, line, and text, and a
planted probe file was observed failing the gate before being removed.

Measured: `504 passed` at 100.00% statement and branch coverage (2251
statements, 778 branches, zero missed, zero partial), up from 488 by the 16 gate
tests; statement and branch totals fell by 3 and 2 with the deleted fallback
branch. Ruff reports no findings across 106 files. `build_figures.py` regenerates
all fourteen figures, and the source-claims, claim-register, visual-bindings,
and release-bindings validators all exit 0. No red line was adopted and no
canary was re-issued; the rendered-output and strict-manifest statuses above are
unchanged by this pass.
