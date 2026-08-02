# Canary and trust model

The canary is the durability layer of Red Line's personal security boundary.
It makes registry drift visible; it does not prevent a rewrite, enforce a
finding, or turn a local attestation into independent truth.

## Canonical payload

`registry_hash()` sorts lines by id and serializes a fixed payload containing
the id, title, standard, rationale, scope, narrative carve-outs, typed
exemptions, tier, severity, author, and date. Exemption ids, trigger scopes,
and required evidence kinds are included, so changing executable narrowing
semantics changes the digest. The current digest is:

```text
72835fd81d1f7ecf70f47b1e0061cd56c385273dd846879ab639225913f5aad7
```

`line_digest()` applies the same canonical atom to one line. No timestamps or
environment inputs enter the content hash.

## Issue and verify

`issue_canary` binds the digest, sorted line ids, issue-time severity, and
per-line digests to a dated statement. With a prior canary, registry drift
requires a rationale before a successor can be emitted. `verify_canary` checks
hash drift, removed/added/modified lines, metadata consistency, and freshness.
Missing, future-dated, or unparseable attestations fail closed; the default
freshness window is 180 days.

CANARY-grade alteration is escalated using the severity held by the prior
statement, so demoting a CANARY line is itself visible.

## Trust boundary

The canary is forgeable by anyone who can rewrite both registry and attestation.
The committed fixture proves reproducibility and catches accidental local drift;
it is not an external witness. Meaningful detection requires an earlier copy in
a public, append-only, archived, or otherwise independently held location,
checked by someone other than the author.

The framework borrows the pattern of a warrant canary, not its legal instrument.
The author remains the enforcer, and the project makes that limitation explicit.
