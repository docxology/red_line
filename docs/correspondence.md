<!-- Note (2026-07-29): reviewer attribution has been anonymized pending explicit
consent for inclusion in permanently archived DOI records. Attribution will be
restored on confirmation. -->

# Correspondence: design reviews received

This page records external design reviews of Red Line and what this
repository did about them. It is a decision record, not an endorsement chain:
each item names what was adopted, what was deferred with a reason, and what
was declined with a reason.

## 2026-07-29 — "The Space Between the Lines" (an external reviewer, with an analytic reader)

A two-voiced review of the collected line set. Its reading of Red Line: the
classification a review emits is a *safe projection* — the evaluator resolves
toward the most severe applicable outcome (an intake stop short-circuits
before any line matching, a hard block wins over a narrowing, ambiguity
resolves toward coverage), and that word must not become the whole state.
Strong narrowing evidence and strong line coverage co-present are not the
same as no evidence, and Red Line's native report already keeps that state
beneath the projection: `ReviewFinding` retains the stable reason codes
(including `VERIFIED_EXEMPTION` beside `MULTIPLE_PROHIBITED_DIMENSIONS` when
a verified narrowing is overridden), the evidence-stop dimensions, the full
rendered prose with its advisory hints, and any named authorization — which
is an escalation record and never an unblock. The review's central proposal
for the set: each line should export one *common report envelope* pointing
at its complete native report, and the missing layer is a *shared witness
register* that co-registers those envelopes without ranking, averaging,
merging, or overriding any line — "precedence without information
destruction."

**Adopted here:**

- *The canonical native report.* Red Line had a canonical serialization and
  digest for its registry (`canary/hashing.py`) but none for a review
  finding, so there was nothing durable for an envelope to point at.
  `envelope.py` now exports `canonical_report` under `red-line.report/1.0` —
  the complete derivation of one `ReviewFinding`, with the set-aside
  authorization arm serialized as an explicit `null` rather than omitted —
  and `report_digest`, its SHA-256, following the house sorted-keys
  compact-separators convention.
- *The common report envelope.* `envelope.py` exports the contract under
  `line.report-envelope/1.0`, with the digest pointer, the review date, the
  registry version and content digest (the same deterministic hash the
  canary attests), the classification word in this line's own vocabulary as
  `native_status`, caller-supplied source snapshot references, and the
  instrument's non-claims in transportable form, so a stored envelope cannot
  quietly outgrow what the instrument was allowed to say.
  `envelope_matches_finding` is the archived-pair read-back check.

**Deferred (stated in TODO):** manuscript formalism definitions for the
canonical report and the envelope await the next manuscript window, because
formal edits require a re-render and manifest pass, and this repository's
formalism bindings reject hand-written formal claims that no gate executed.

**Declined, by design:**

- The shared witness register itself. The review is explicit that it should
  not be smuggled into any existing line, and this repository agrees: Red
  Line ships its envelope export and stops. A register that stores cross-line
  relations and joint records is a separate work with its own tests and its
  own claim boundaries.
- Any change that would let the envelope carry a merged verdict, a score, or
  a cross-line comparison. `native_status` is this instrument's word in this
  instrument's vocabulary; the envelope documentation forbids ranking,
  averaging, or merging on it, and sibling instruments align by publishing
  the same schema string, never by import.


### Wave-3 update (2026-07-29, later the same day)

The deferred manuscript formalism landed: `def:report-envelope` and
`prop:envelope-pointer` in `manuscript/08a_formalism.md`, bound by two new
tests proven to bite via planted drifts, with the claim ledger and the
fourteen suite-inventory sites moved (868 -> 870). Strict release evidence
went green for the first time under the engine-pipeline-last-then-strict
sequence; `quality_gate.py --render` as a single command remains
self-defeating in its current step order (TODO records the measurement and
the fix's scope). The skill descriptor gained the envelope surface. The
companion register now exists and accepted this line's actually-exported
envelope unmodified.
