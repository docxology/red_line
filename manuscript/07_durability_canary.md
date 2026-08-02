# Durability and transparency: a hash-based canary {#sec:canary}

Turner's framework protects the *durability* of a red-line commitment through
procedure: a material modification requires advance notice with a rationale, and
an impairment of the Review Body's capacity must be disclosed
[@turner2026redline]. A single practitioner has no review body and no
counterparty to notify. The personal analog is therefore cryptographic rather
than procedural — it makes weakening the standard visible and auditable, not
procedurally gated.

## Deterministic registry hashing

`registry_hash` reduces the red-line registry to a single SHA-256 digest over
its canonicalized content. Canonicalization sorts the lines by `id`, serializes
each fixed payload including narrative carve-outs and typed exemption ids,
trigger scopes, and required evidence kinds, and dumps the whole as JSON with
stable separators. No timestamps or environment inputs enter the payload, so the
hash is a pure function of registry *content*: the current seven lines yield the
pinned digest `72835fd8…f5aad7`, and any change to a line's policy semantics
changes it. `line_digest` applies the same atom to a single line. This is a
cryptographic checksum, not a digital signature: it does not authenticate who
issued a statement or make a rewrite impossible.

## The canary statement

A `CanaryStatement` is a dated attestation. It binds the registry digest, the
set of line ids present at issue time, and a tuple of per-line `(id, severity,
digest)` triples, all captured on a stated `issued_on` date. Binding the
issue-time severity alongside each digest — not merely the aggregate hash — lets
a later check tell *which* line changed and how severe it was when the author
last vouched for it. `issue_canary` also enforces a successor guard: when a
prior canary is supplied and the hash has drifted, a silent re-issue is refused
unless the author supplies a rationale, which is folded into a self-describing
successor statement naming the superseded digest and the removed or added ids.

## Verification and escalation

`verify_canary` compares a prior statement to the live registry. It reports
`drift` (any hash change), explicit `removed_ids` and `modified_ids`, and
`stale` independently, so a caller sees *how* a canary failed. `intact` requires
an unchanged hash, a fresh attestation, complete line-id agreement, and
internally consistent populated per-line metadata. Freshness is always evaluated
against a 180-day window and fails closed: a missing, future-dated, or
unparseable date reads as stale rather than as a silent pass. When a removed or
modified line was CANARY-grade at issue time, the detail escalates to
`CANARY-GRADE LINE ALTERED`, surfacing it above any lower-severity change.

## The honest trust model

This is the *pattern* of a warrant canary, not the legal instrument: a warrant
canary's force rests on a legal asymmetry that does not apply to a personal
commitment. The statement is forgeable by anyone with write access to the
registry, and the author is also its only enforcer. Its evidential force rests
entirely on an external prior copy — a git-committed or otherwise independently
held statement, checked by someone other than the author. The registry is
pre-publication and there is no external verifier. The instrument makes
weakening the standard tamper-evident under that condition; it does not prevent
it, and that limitation is disclosed rather than papered over.

An external verifier should: obtain a prior statement from outside the author's
write boundary; recompute the current registry hash and per-line metadata; run
the freshness and drift check; inspect any successor rationale; and report the
result without treating a regenerated current statement as independent evidence.
The full command-level procedure is in [`docs/VERIFY.md`](../docs/VERIFY.md).

The trust boundary is therefore more important than the hash itself;
[@fig:canary-trust-boundary]
shows what the mechanism can and cannot signal.

## Defensive security context

The nation-state lens is applied here as a defensive threat model for a static
private artifact, not as a claim that the repository is an APT-resistant
service. The relevant crown jewels are the registry, evidence and review
records, prior canary, private scholarship, release boundary, and
rendered outputs. A patient adversary could alter a privileged checkout, poison
a dependency or renderer, rewrite a same-author canary fixture, or make a
source appear more authoritative than it is. The threat model records these
paths and their residual limits in
[`docs/security-threat-model.md`](../docs/security-threat-model.md).

NIST's Secure Software Development Framework, MITRE ATT&CK, and SLSA provide
useful vocabularies for provenance, adversary behavior, and future artifact
attestation [@souppaya2022ssdf; @mitre2026attack; @slsa2026]. They are
implementation context, not evidence of legal compliance, secure operation, or
resistance to a nation-state actor. This project currently demonstrates
dependency-light deterministic domain logic, locked development dependencies,
local canary and render validation, and explicit external-witness limitations;
it does not claim signed provenance, a generated SBOM, hermetic builds, or
runtime telemetry.

![The canary detects drift only when a prior copy is outside the writer's reach. Trust-boundary schematic for the canary mechanism: issuance binds the registry to an aggregate digest and per-line metadata; verification compares those values with the live registry and checks freshness. The dashed boundary is the critical condition: the prior statement must be held by someone or some system that cannot be rewritten by the same author who edits the registry. A canary cannot detect semantic violations hidden by misleading labels, cannot stop a malicious re-issuance, and cannot enforce an action finding. It is tamper evidence conditional on an independent witness, not prevention or legal protection.](../output/figures/canary_trust_boundary.png){#fig:canary-trust-boundary width=95%}
