---
name: personal-red-lines
description: >-
  Operate the red_line personal red-line framework — evaluate a proposed
  engagement against the author's versioned red lines, produce a review finding,
  issue or verify a warrant canary over the registry hash, derive registry
  composition and outcome-coverage analytics, and propose versioned edits. USE
  WHEN: red line check, is this engagement in bounds, evaluate an action against
  my red lines, issue canary, verify canary, registry composition, outcome
  coverage, has a red line changed, propose a red-line edit.
source: docxology/daf-skills (private)
public_descriptor: true
version: 0.3.0
---

# personal-red-lines

Public descriptor stub. This skill's **operational implementation is `daf-red-line`
in the author's private skills repository `docxology/daf-skills`** and is not included
in this public tree. The stub exists so that agent runtimes and skill indexes can
discover the capability and route to the private source; it carries no private
content. Everything below runs against the public entry points in this repo.

The instruments here are **not** safety scores, accreditations, moral
authorities, or permission mechanisms. They make one author's commitments
inspectable and their weakening detectable — nothing more.

## What the full skill does (`daf-red-line` in `docxology/daf-skills`)

1. **Evaluate** — wrap `red_line.evaluate_action` to classify a proposed engagement as
   compliant / requires-modification / non-compliant, with reasons.
2. **Review** — produce a durable `ReviewFinding` (via `red_line.oversight`) and
   record any override for the transparency report.
3. **Canary** — issue/verify the dated statement over the registry hash and
   surface drift or a warrant-canary trip.
4. **Analyze** — derive registry-composition, outcome-coverage, and tier-
   monotonicity views from `red_line.analysis` (read-only; describes shape and
   evaluator consistency, never safety or strength).
5. **Amend** — propose a versioned edit to `PERSONAL_RED_LINES`, bump the version,
   re-issue the canary with a dated rationale, and never remove a `CANARY`-severity
   line silently.

## Operations (copy-pasteable, run from the project root)

### Evaluate an action (worked example)

A context and verified evidence are mandatory; the description is never evidence.

```bash
.venv/bin/python -c "
from red_line import (ActionContext, EvidenceKind, EvidenceRecord, EvidenceStatus,
                      ProposedAction, evaluate_action)
evidence = tuple(
    EvidenceRecord(kind, f'case://intake/{kind.value}', 'reviewed intake record',
                   EvidenceStatus.VERIFIED, '2026-07-17')
    for kind in EvidenceKind
)
context = ActionContext(
    purpose='model tuning', end_use='target selection',
    affected_parties='people in the target environment',
    data_provenance='documented source', legal_basis='review required',
    human_control='accountable human review', deployment='hosted',
    downstream_transfer='none',
    capability_scope='target selection and engagement', evidence=evidence,
)
action = ProposedAction(description='Tune an autonomous targeting model',
                        scope=frozenset({'targeting', 'autonomous_weapon'}),
                        context=context)
assessment = evaluate_action(action)
print(assessment.classification)
print(sorted(r.value for r in assessment.reason_codes))
"
```

Output (verbatim, deterministic):

```text
Classification.NON_COMPLIANT
['unexempted_line']
```

Missing or unverified evidence yields `INSUFFICIENT_INFORMATION`, never a false
compliant; a scope outside every line yields `OUTSIDE_SCOPE`.

### Registry and coverage analytics (`red_line.analysis`)

Read-only, pure-compute, deterministic. These describe the registry's *shape*
(counts, distributions, reachability) — they are not a risk model and support
no cross-author comparison.

```bash
.venv/bin/python -c "
from red_line.analysis import (evidence_kind_demand, exemption_evidence_matrix,
                               run_monotonicity_sweep, run_outcome_coverage,
                               severity_distribution, tier_floor_distribution,
                               unevidenced_exemptions)
print('rows:', len(exemption_evidence_matrix()))          # exemption x evidence matrix
print('demand:', dict(evidence_kind_demand()))            # per-kind requirement counts
print('severity:', dict(severity_distribution()))
print('tier floors:', dict(tier_floor_distribution()))
print('unevidenced:', unevidenced_exemptions())           # free-pass detector; () is good
report = run_outcome_coverage()                           # real evaluate_action battery
print('complete:', report.complete, 'all_matched:', report.all_matched)
monotone = run_monotonicity_sweep()
print('monotone:', monotone.monotone, 'inversions:', monotone.inversion_count)
"
```

On the live registry this prints 16 matrix rows, `unevidenced: ()`, and
`complete: True all_matched: True` (all five classifications reached through
the real evaluator at the fixed review date `BATTERY_AS_OF`). Also available:
`line_summaries()`, `scope_token_frequency()`, `canonical_battery()`, and
`run_monotonicity_sweep()` (36 keywords × 3 tiers = 108 real evaluations;
zero inversions on the current evaluator).

### Canary: issue and verify

```bash
# print the dated statement + attested registry hash (deterministic, stdout only)
.venv/bin/python scripts/build_canary.py 2026-07-22

# verify: recompute registry_hash + per-line digests against the committed
# prior statement (tests/fixtures/canary_committed.json); exit 0 = intact
.venv/bin/python scripts/check_canary.py
# -> registry hash unchanged and attestation fresh — canary intact
```

Verification only means something against a prior statement stored outside the
registry writer's reach and checked by someone other than the author — see
`docs/VERIFY.md`.

### Gates

`scripts/quality_gate.py` runs, in order: build figures → visual bindings →
Ruff → pytest with `--cov=red_line --cov-fail-under=90` → source claims → claim
register → proposed red lines → source release bindings → canary → a
byte-determinism double build of the figure tree → wheel smoke test. `--render`
adds the canonical PDF/HTML pipeline comparison and strict release manifest;
`--as-of DATE` pins the canary date.

```bash
.venv/bin/python scripts/quality_gate.py --as-of 2026-07-22
```

## Public entry points (this repo)

Behavior lives in `src/red_line/`; everything under `scripts/` is a thin CLI
that parses arguments and calls one package function.

| Surface | Behavior lives in | CLI wrapper |
| --- | --- | --- |
| Model, registry, evaluator, oversight, canary, invariants | `src/red_line/` | `scripts/build_canary.py`, `scripts/check_canary.py` |
| Read-only analytics and evaluator consistency | `src/red_line/analysis/` | — (imported directly) |
| Figure generation (eighteen deterministic SVGs) | `src/red_line/figures/` — `plates_scholarship.py`, `plates_analysis.py`, `diagrams.py`, `registry.py`, `build.py` | `scripts/build_figures.py` |
| Validators (source claims, claim register, proposed lines, release bindings, visual bindings) | `src/red_line/contracts/` | the five `scripts/validate_*.py` |
| Release provenance, input snapshot, manifest, render determinism | `src/red_line/release/` | `scripts/build_release_data.py`, `scripts/build_release_manifest.py`, `scripts/compare_render_artifacts.py` |
| Full local gate | `scripts/quality_gate.py` (sequencing only) | — |

- `manuscript/09_red_lines.md` — the human-readable beacon;
  `manuscript/09a_registry_composition.md` — the derived-data composition section.

Version authority is `src/red_line/version.py`; `manuscript/config.yaml` and
other surfaces are bound to it by validation.

## The report envelope (cross-instrument transport)

```python
from red_line import finding_envelope, canonical_envelope, envelope_matches_finding

envelope = finding_envelope(finding, subject_id="your reference for what was reviewed")
canonical_envelope(envelope)                 # store beside canonical_report(finding)
envelope_matches_finding(envelope, finding)  # read-back check for an archived pair
```

One `line.report-envelope/1.0` record pointing at the complete canonical
finding (`red-line.report/1.0`, absent authorization arm as explicit `null`).
`native_status` is this line's classification word; never compare, rank,
average, or merge it across lines.

## Line-set orientation

Red Line is one of four standalone works — the line **set** (never "suite"):
Red Line (what must be refused), Black Line (strong concise work), Golden Line
(higher direction), White Line (what is absent or withheld). They share no
prose, registry entries, or code. Each is its own repository —
`docxology/black_line`, `docxology/golden_line`, `docxology/white_line` — and
the set's declaration, ordering, and non-overlap contract are published in the
companion `line_set` work at <https://github.com/docxology/line_set>. A sixth
companion, `witness_register` (<https://github.com/docxology/witness_register>),
co-registers each line's report envelopes without aggregating them.

## Boundary

This descriptor is public and safe to publish. Any prompt logic, private
workflows, or client-specific context lives only in `docxology/daf-skills`.
