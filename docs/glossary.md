# Glossary

## ActionContext

The mandatory intake record for an action: purpose, end use, affected parties,
data provenance, legal basis, human control, deployment, downstream transfer,
and capability scope, plus evidence and declared unknowns.

## authorization

A frozen `ReviewAuthorization` naming the reviewer, authority, rationale, and
date. It records escalation or remediation; it never releases a blocking
finding.

## beacon

The readable, versioned registry of first-person boundaries. The beacon tells a
reader what the author refuses; it does not claim universal authority.

## canary

A dated `CanaryStatement` binding registry content to an aggregate digest, line
ids, severity, and per-line digests. It is a tamper-evidence pattern, not the
legal instrument of a warrant canary. It requires an external prior copy to be
meaningful beyond local regression testing. The digest is not a signature,
proof of authorship, or guarantee of semantic integrity.

## carve-out and exemption

`carve_outs` are human-readable narrowing clauses. `Exemption` records are the
executable form: each has a trigger scope and required evidence kinds. A trigger
token is not proof; only verified evidence satisfies the condition.

## classification

One of five evaluator results:

- `INSUFFICIENT_INFORMATION`: required context is missing, ambiguous,
  unsupported, unverified, or contradicted;
- `NON_COMPLIANT`: an implicated line has no satisfied exemption;
- `REQUIRES_MODIFICATION`: a verified exemption still has multiple prohibited
  dimensions or a tier deficit;
- `COMPLIANT`: complete intake, verified exemption, and tier requirements pass;
- `OUTSIDE_SCOPE`: complete intake, but no current line is implicated.

Outside scope is not silently counted as compliance.

## evidence status

`VERIFIED` means a reviewable source or artifact exists. `SELF_ASSERTED`,
`UNVERIFIED`, and `CONTRADICTED` are unresolved for required fields. The
package records epistemic status but does not adjudicate source truth. Verified
evidence is also time-bounded: a record older than 180 days or dated in the
future is stale for the current review.

## deployment tier

`HOSTED`, `CONNECTED`, and `AIR_GAPPED` represent decreasing retained ability
to observe, update, suspend, or withdraw a work product. A line's `max_tier` is
its least-oversight floor, not a permission by itself.

## outside scope

An explicit classification produced only after complete intake when no current
registry line is implicated. It is a bounded statement about this registry,
not a safety result.

## prohibited dimension

A normalized scope token shared by an action and a line. Two or more shared
prohibited dimensions cannot be laundered by one adjacent-use exemption.

## red line

A frozen, dated, first-person `RedLine` record stating what the author will not
cross. The registry contains seven lines and remains non-exhaustive.

## registry hash

The deterministic SHA-256 over canonicalized line content, including typed
exemption semantics. Current pin:
`72835fd81d1f7ecf70f47b1e0061cd56c385273dd846879ab639225913f5aad7`.

## trust model

The package provides local auditability, not enforcement. A green test suite
proves internal consistency, not real-world safety. A canary is externally
meaningful only when a prior statement is held outside the author's write
boundary and checked by another party.
