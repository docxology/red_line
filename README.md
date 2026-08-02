# red_line

**A versioned personal security boundary — a beacon, canary, and explicit No
document — for dual-use development work.**

`red_line` makes explicit the boundaries its author (Daniel Ari Friedman,
[docxology](https://github.com/docxology)) will not cross while developing
open-source scientific software, proprietary modeling, and cognitive-security and
intelligence products. It packages those refusals as a versioned, executable,
and reviewable personal security boundary: a concise **No document** that makes
the author's prohibitions inspectable before a request becomes a project. Its
architecture has a comparative antecedent in Alex Turner's
[**A Red Line and Oversight Framework for Government AI Contracts**](https://turntrout.com/red-line-framework)
(2026-07-15), whose mechanism is re-scoped here from an organization selling to
governments to a single practitioner governing their own work.

It is two things at once:

- a **beacon** — a structured, machine-readable registry of red lines designed for
  publication (released at <https://github.com/docxology/red_line>) that anyone can
  read and align to once public; and
- a **canary** — a reproducible content hash carried in a dated statement, so that
  *silently removing, weakening, or letting the standard go stale becomes a
  detectable state*. This uses the *pattern* of a warrant canary (absence or
  staleness of a fresh attestation is the signal), **not** the legal instrument: it
  makes weakening the standard visible and auditable; it does not prevent it.

> Version `0.3.0` · registry SHA-256 `72835fd8…f5aad7` · living document — versioned, revisable, diffable (publicly so once published).

## What it does

| Component | Turner analog | Module |
| --- | --- | --- |
| Red-line registry (7 lines, 2 `CANARY`-grade) | The two Standards + typed exemptions | `src/red_line/registry/lines.py` |
| `RedLine`, enums, `ProposedAction` | The model of a boundary | `src/red_line/model/` |
| `evaluate_action` → insufficient-information / outside-scope / compliant / requires-modification / non-compliant | Evidence-gated review classification | `src/red_line/evaluation/evaluator.py` |
| Oversight-retention tiers (hosted / connected / air-gapped) | Deployment Tiers 1/2/3 | `src/red_line/model/enums.py` |
| `review_engagement` + `transparency_report` | Review Body + annual transparency report | `src/red_line/oversight/` |
| `registry_hash` + `CanaryStatement` + `verify_canary` | Durability & transparency protections | `src/red_line/canary/` |
| Structural invariants (with proof-of-detection) | Framework coherence | `src/red_line/invariants/checks.py` |

Three further subpackages carry the surrounding machinery, and they own their
behavior outright — every file in `scripts/` parses arguments and calls one
package function:

| Subpackage | Owns | CLI wrappers |
| --- | --- | --- |
| [`src/red_line/figures/`](src/red_line/figures/) | The eighteen deterministic figures: `plates_scholarship.py` (source-derived), `plates_analysis.py` (analysis-derived), `diagrams.py` (schematics), `registry.py` (the name → generator map), `text.py` (captions and alt text). | `scripts/build_figures.py` |
| [`src/red_line/contracts/`](src/red_line/contracts/) | The five validators: `source_claims`, `claim_register`, `proposed_red_lines`, `release_bindings`, `visual_bindings`. | the five `scripts/validate_*.py` |
| [`src/red_line/release/`](src/red_line/release/) | Release provenance digests, the input snapshot, the release manifest, and render-determinism comparison. | `scripts/build_release_data.py`, `scripts/build_release_manifest.py`, `scripts/compare_render_artifacts.py` |

The full architecture — the modular `src/red_line/` package, the import DAG, and how
`tests/` mirrors it — is in [`docs/architecture.md`](docs/architecture.md); the
[`docs/`](docs/README.md) directory is the complete reference.

## The four-line set

Red Line answers **what must be refused**. It is the security boundary and the
explicit No document. Three separate works are being developed beside it:

- **Black Line** asks how to do strong, concise, intelligent work and research.
- **Golden Line** asks what higher direction is worth reaching toward.
- **White Line** records what is absent, withheld, uncertain, or left outside
  the claim.

The works are standalone and non-redundant, and each is its own repository:
`docxology/black_line`, `docxology/golden_line`, and `docxology/white_line`.
Their relationship was first written down in a short internal note,
`docs/line-set.md`, in the author's private projects tree; that note is
unpublished and does not travel with this repository, so it is named here rather
than linked — a relative path out of the repository root resolves to nothing for
anyone holding only this repository. The durable references are the companion
repositories themselves. Red Line does not borrow the substantive methods of the
companion works.

A fifth work, `line_set`, is a thin reader that declares the set and checks that
no two lines gave the same spelling to different things. It adds no substantive
instrument — the set is still four lines — and Red Line does not import, depend
on, or defer to it. The same acknowledgement, with the shared-token detail, is
in [`manuscript/02b_line_set_orientation.md`](manuscript/02b_line_set_orientation.md).

## Quick start

```bash
# run the gate (tests + coverage; ≥90% enforced on src/red_line/)
uv run pytest tests/ --cov=red_line --cov-fail-under=90

# print the current canary statement + attested hash (deterministic)
uv run python scripts/build_canary.py 2026-07-17

# rebuild deterministic figures before a template render
uv run python scripts/build_figures.py
```

Evaluate a proposed engagement. A context and verified evidence are mandatory;
the description is never evidence:

```python
from red_line import ActionContext, EvidenceKind, EvidenceRecord, EvidenceStatus, ProposedAction, evaluate_action

evidence = tuple(
    EvidenceRecord(kind, f"case://intake/{kind.value}", "reviewed intake record", EvidenceStatus.VERIFIED, "2026-07-17")
    for kind in EvidenceKind
)
context = ActionContext(
    purpose="model tuning",
    end_use="target selection",
    affected_parties="people in the target environment",
    data_provenance="documented source",
    legal_basis="review required",
    human_control="accountable human review",
    deployment="hosted",
    downstream_transfer="none",
    capability_scope="target selection and engagement",
    evidence=evidence,
)

action = ProposedAction(
    description="Tune an autonomous targeting model",
    scope=frozenset({"targeting", "autonomous_weapon"}),
    context=context,
)
print(evaluate_action(action).classification)  # Classification.NON_COMPLIANT
```

## The red lines

The full, human-readable beacon is in
[`manuscript/09_red_lines.md`](manuscript/09_red_lines.md); the authoritative,
machine-readable source is `PERSONAL_RED_LINES` in `src/red_line/registry/lines.py`. The
manuscript (`manuscript/`) explains the adaptation from Turner's framework in full.

## Derived registry analytics

`src/red_line/analysis/` is a read-only analytics subpackage — pure-compute,
zero-I/O, deterministic — with five modules:

- **`registry_metrics`** derives composition views over the live registry:
  the exemption × evidence-kind matrix, per-kind evidence demand, per-line
  structural summaries, severity and tier-floor distributions, scope-token
  frequency and per-token line membership, and a free-pass detector
  (`unevidenced_exemptions`) that returns empty on the live registry and whose
  detection power is proven against a planted-bad registry in tests.
- **`outcome_coverage`** runs a canonical five-case battery through the *real*
  `evaluate_action` at a fixed review date and reports which classifications
  are reached, with per-case reason codes.
- **`monotonicity`** sweeps every live line/keyword slot through the real
  evaluator at all three deployment tiers and records whether reduced oversight
  ever softens a verdict; the live sweep is 36 slots over 34 distinct tokens,
  108 evaluations, and zero inversions.
- **`evidence_sensitivity`** degrades one intake dimension at a time on an
  otherwise-compliant baseline — removed, self-asserted, unverified,
  contradicted, or stale — and reports what the real evaluator returned; the
  live sweep is 45 evaluations, all of which withdraw the compliant result and
  name only the degraded dimension. A baseline that is not `COMPLIANT` raises
  rather than producing a report whose zeros read backwards.
- **`trigger_semantics`** probes every typed exemption with one trigger token
  and then with all of them, beside an anchor from its own line's coverage
  scope; the live probe is 58 evaluations across 13 `ANY` and 3 `ALL` mode
  exemptions, with every row behaving as its mode requires.

Seven figures render directly from this executed analysis (never hand-drawn
data): `exemption_evidence_matrix`, `outcome_coverage_plate`,
`tier_monotonicity_lattice`, `registry_composition_profile`,
`scope_vocabulary_collisions`, `evidence_gate_sensitivity`, and
`exemption_trigger_semantics`, defined in
[`src/red_line/figures/plates_analysis.py`](src/red_line/figures/plates_analysis.py)
and written under `output/figures/` by the `scripts/build_figures.py` CLI. The derived numbers are
written up in
[`manuscript/09a_registry_composition.md`](manuscript/09a_registry_composition.md),
and every number in that prose is recomputed from the analysis code by two
suites: `tests/integration/test_manuscript_composition_binding.py` covers the
per-line table and the totals, and
`tests/integration/test_unbound_count_binding.py` covers the severity split,
the tier-floor split, the joint CANARY/`air_gapped` claim, and the structural
ranges — the three regions the first suite did not read. The second suite also
scans every manuscript file for an unlisted restatement of the line count, so a
new surface fails rather than drifts. This is the same prose-code binding
discipline as the beacon itself. These views describe the
registry's *shape*, not its strength: they are registry introspection, not a
risk model, a safety score, or a basis for cross-author comparison (see
[`manuscript/10_limitations.md`](manuscript/10_limitations.md)).

## The common report envelope

Red Line exports one envelope per review finding, under the schema string
`line.report-envelope/1.0` — the shape the 2026-07-29 line-set design review
proposed for co-registration (see
[`docs/correspondence.md`](docs/correspondence.md)). The envelope
(`src/red_line/envelope.py`) points at the complete canonical finding by
SHA-256 digest (`canonical_report`, schema `red-line.report/1.0`) rather than
copying or reinterpreting it: `native_status` is the evaluator's own
classification word, the full derivation (finding prose, reason codes,
evidence stops, any named authorization) stays behind `report_ref`, and the
instrument's non-claims travel inside the record. Envelopes from different
lines must not be compared, ranked, averaged, or merged on `native_status`;
sibling instruments align by publishing the same schema string, never by
import. The shared witness register that would co-register such envelopes is
deliberately a separate work, not part of any line.

```python
from red_line import canonical_report, envelope_matches_finding, finding_envelope, review_engagement

finding = review_engagement(action, reviewed_on="2026-07-15")
envelope = finding_envelope(finding, subject_id="worked-example", source_snapshot_refs=("git://…",))
assert envelope_matches_finding(envelope, finding)  # archived-pair read-back
archive_pair = (canonical_report(finding), envelope)  # smallest verifiable archive
```

## Skills

Operational skills for working *with* this framework — running reviews, issuing and
checking canaries, proposing versioned edits — are maintained in the author's
private skills repository **`docxology/daf-skills`**. A public descriptor stub lives
at [`.agents/skills/personal-red-lines/SKILL.md`](.agents/skills/personal-red-lines/SKILL.md)
alongside its [folder contract](.agents/skills/personal-red-lines/AGENTS.md) and
[pointer](.agents/skills/personal-red-lines/README.md); it carries no private
content and points at the private source.

## Limitations (read this)

The honest scope of this artifact is **evidence-gated auditability, not enforcement**. Turner's
framework gains institutional friction from a standing Review Body that records
findings and makes leadership decisions transparent. A single practitioner is simultaneously author,
enforcer, and auditor, which collapses that separation of powers. Consequently:

- The structural checks are **tamper-evident conventions, not immutable
  invariants** — the author *can* edit them; the framework makes the edit
  **visible and dated**, it does not make it impossible.
- The canary is the *pattern* of absence-as-signal, not a legal warrant canary
  (see above). Its force is transparency, not immunity.
- Each red line is the author's **current, non-exhaustive, revisable** commitment
  (`RedLine.stated_by` / `stated_on`), phrased in the first person. It is **not** a
  universal moral claim, and not a claim asserted by any AI that helped author it.
- The canary's force rests entirely on the prior statement being stored **outside
  the registry writer's reach** (committed git history, a published post) and being
  checked **by someone other than the author**. A verifier holding only a
  regenerated statement sees nothing — `tests/integration/test_trust_model.py` pins both the
  detection (against a committed prior statement) and this boundary, executably.
- The evaluator is **lexical over a declared scope**, not semantic over free
  text. Description/scope disagreement produces an advisory hint, while missing
  or unverified capability evidence produces `INSUFFICIENT_INFORMATION` rather
  than a false compliant result.
- There is **no external verifier in the loop**: named authorizations are
  self-reported escalation records and never release a blocking result. The
  oversight language describes a discipline the author imposes on himself in
  public, not third-party enforcement.
- The committed prior canary statement lives in **this same repository**, so
  verification is self-referential until a copy exists on a surface the author
  cannot rewrite — a force-push rewrites both the registry and its attestation.
  Publishing the statement and hash to an independent timestamped surface (public
  repo, dated post, OpenTimestamps, or a reserved DOI) is what makes the canary
  externally checkable; see [`docs/VERIFY.md`](docs/VERIFY.md).

These limitations are the point of publishing: a boundary you cannot audit is a
boundary you cannot trust, including for yourself.

## Provenance & status

- **Source framework:** Alex Turner, *A Red Line and Oversight Framework for
  Government AI Contracts*, 2026-07-15, <https://turntrout.com/red-line-framework>.
- **Lineage:** derived from the `template_code_project` research-project template
  (thin-orchestrator scripts, mock-free tests, ≥90% `src/red_line/` coverage).
- **Status:** living document. Version, hash, and git history are the change record.
  A red line here is non-negotiable in the moment and revisable over time — but only
  out loud.

## License

Code: MIT. Prose (`manuscript/`): CC-BY-4.0.
