# Evidence-gated evaluator semantics

Red Line is a personal security boundary and explicit No document. Its
evaluator is an auditability aid: it refuses to return `COMPLIANT` until the
action has a complete, reviewable intake. It does not prove that an evidence
record is true, prevent execution, or create an external authority.

## Public records

`ProposedAction(description, scope, context, tier, ambiguous)` contains:

- `description`: human-readable work description; never evidence;
- `scope`: declared capability tokens, normalized through explicit aliases;
- `context`: mandatory `ActionContext` record;
- `tier`: `HOSTED`, `CONNECTED`, or `AIR_GAPPED`;
- `ambiguous`: explicit uncertainty, which blocks evaluation.

`ActionContext` requires values for `purpose`, `end_use`, `affected_parties`,
`data_provenance`, `legal_basis`, `human_control`, `deployment`,
`downstream_transfer`, and `capability_scope`. Each dimension requires a
`VERIFIED` `EvidenceRecord`, including an explicit `not_applicable` value. A
`SELF_ASSERTED`, `UNVERIFIED`, or `CONTRADICTED` record cannot satisfy the gate.
Verified records older than the 180-day review window, or dated in the future,
are stale and likewise block until refreshed. The evaluator accepts an explicit
review date so this freshness rule can be tested reproducibly.

The evidence status is epistemic bookkeeping, not truth adjudication. A
verified record means that a reviewable source or artifact was identified; it
does not mean that this package independently validates the source.

## Decision order

The evaluator runs the following sequence:

1. Normalize scope tokens with explicit aliases and reject empty, ambiguous, or
   unknown-marker scope.
2. Check all required context values and evidence statuses.
3. Match normalized scope against each line's prohibited coverage dimensions.
4. Match any explicitly declared typed exemption.
5. Require every exemption's evidence kinds to be verified.
6. Apply the line's tier floor and multi-dimension rule.
7. Return exactly one classification.

`review_engagement` supplies its `reviewed_on` date as the evaluator's `as_of`
date. This keeps the freshness decision and the date printed on a finding bound
to the same review event.

Every `ActionAssessment` also carries stable `AssessmentReasonCode` values. The
human-readable `reasons` are allowed to improve for clarity; the codes are the
machine-readable audit surface for aggregation and regression tests. A
`ReviewFinding` copies those codes and the evidence/scope dimensions into its
frozen record, so a later reader does not have to parse prose to recover why a
finding blocked or passed.

The code distinguishes an undeclared context unknown (`undeclared_unknown`)
from an explicit unknown scope marker (`unknown_scope`). Both stop intake, but
they describe different repair actions: declare or resolve the missing context
versus replace the non-specific scope token with a canonical scope declaration.

The early information gate is intentional. A missing legal basis cannot be
converted into a consent claim by adding `consented` to a scope set.

## Classifications

| Result | Meaning | Permission effect |
|---|---|---|
| `INSUFFICIENT_INFORMATION` | Required context is missing, ambiguous, unsupported, unverified, or contradicted | Blocks; resolve evidence first |
| `NON_COMPLIANT` | An implicated line has no satisfied exemption | Blocks at every tier |
| `REQUIRES_MODIFICATION` | A verified exemption exists, but multiple prohibited dimensions or an inadequate tier remain | Blocks until corrected |
| `COMPLIANT` | The intake is complete, implicated lines are narrowed by verified evidence, and tier requirements are met | May proceed within the documented scope |
| `OUTSIDE_SCOPE` | Complete evidence exists and no registered line is implicated | Not a compliance finding; review remains bounded by registry scope |

`ActionAssessment.outside_scope` is true only for the explicit
`OUTSIDE_SCOPE` result. Outside scope is never silently relabeled compliant.

## Exemptions and normalization

Human-readable `carve_outs` remain in every registry record for publication,
but executable policy uses typed `Exemption` records. Each exemption has an id,
description, trigger tokens, and required evidence kinds. Trigger tokens are
not proof of the exemption.

Scope matching uses NFKC normalization, a strict ASCII boundary, and an
explicit alias table. The ASCII boundary rejects confusable Unicode spellings
instead of allowing them to become unrelated tokens. The evaluator does not
strip arbitrary suffixes or infer semantics from prose. A new synonym must be
reviewed and added to the alias table before it affects policy.

## Review records

`review_engagement` creates a frozen `ReviewFinding`. A
`ReviewAuthorization` records who documented an escalation, what authority was
claimed, why it was recorded, and when. It is not a bypass: a finding classified
as `NON_COMPLIANT`, `REQUIRES_MODIFICATION`, or `INSUFFICIENT_INFORMATION`
continues to block. The transparency report counts named authorizations on
blocking findings without pretending that a decision was safe.

## False-certification controls

The test suite must fail when:

- a dangerous description is paired with a benign or empty scope;
- “consented surveillance” lacks verified legal-basis and provenance evidence;
- a self-asserted or contradicted record is treated as verified;
- a stale duplicate record is ignored because a newer duplicate exists;
- a scope token uses a Unicode confusable to evade a prohibited token;
- an evidence reference contains a raw secret or obvious personal identifier;
- a scope alias changes a prohibited token into an unrelated token;
- an exemption is declared without its required evidence;
- an authorization downgrades a blocking result;
- a complete action outside the registry is reported as compliant rather than
  explicitly outside scope.
- a finding loses its structured reason codes or normalized scope while retaining
  only a display string.

These controls improve the oracle but do not turn a lexical evaluator into a
semantic classifier. Independent review remains a release requirement for any
claim stronger than local auditability.
