# Mechanism mapping: source pattern to personal instrument

Turner's framework is cited as a mechanism source, not as institutional or
legal authority for this project. The current implementation is a breaking
revision: it retains the questions of precommitment, retained oversight,
review, and durability while adding an evidence gate and refusing to collapse
outside scope into compliance.

| Governance question | Red Line implementation |
|---|---|
| What is refused? | `PERSONAL_RED_LINES`, seven dated first-person `RedLine` records |
| What does an action claim to be? | `ProposedAction` plus canonical scope tokens |
| What must be established before evaluation? | `ActionContext` and `EvidenceRecord` values for nine required dimensions |
| How are adjacent uses represented? | Narrative `carve_outs` plus typed `Exemption` records |
| What happens when context is weak? | `INSUFFICIENT_INFORMATION`, a blocking result |
| What happens when no policy line applies? | Explicit `OUTSIDE_SCOPE`, not `COMPLIANT` |
| How is less oversight handled? | `DeploymentTier` and each line's `max_tier` |
| How is a decision recorded? | Frozen `ReviewFinding`, evaluated as of its review date, with a non-bypassable `ReviewAuthorization` |
| How is registry drift surfaced? | Canonical SHA-256, per-line digests, freshness, and successor rationale |

The transfer boundary is as important as the analogy. Red Line does not inherit
Turner's contracting environment, standing Review Body, legal framework,
government scope, or institutional enforcement. It is a self-authored refusal
instrument with a local verifier and a future external-witness hook.

## Evidence discipline

The registry's wording describes a boundary. The executable exemption describes
what must be evidenced before an adjacent use can be considered. A token such
as `consented` or `vetted` is a declaration, not proof. Only a `VERIFIED`
evidence record satisfies the corresponding requirement.

## Scope discipline

The evaluator remains lexical by design. Explicit aliases prevent trivial
singular/plural near-misses, but no language model or semantic inference is
used. Description/scope disagreement produces an advisory hint. Missing
capability evidence blocks classification; it does not silently produce a
compliant result.

## Authorization discipline

The former boolean override has been removed. A reviewer can record an
authorization with identity, authority, rationale, and date, but the finding
continues to block. The transparency count therefore measures documented
escalations, not exceptions to the security boundary.
