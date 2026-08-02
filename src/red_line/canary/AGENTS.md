# canary — Canary editing guidance

This folder implements the canary side of the instrument: canonical registry hashing, dated statements, freshness checks, and drift verification.

## Public API inventory

| Name | Signature | Behavior | Source |
| --- | --- | --- | --- |
| `registry_hash` | <code>def&nbsp;registry_hash(lines:&nbsp;tuple[RedLine,&nbsp;...]&nbsp;=&nbsp;PERSONAL_RED_LINES)&nbsp;-&gt;&nbsp;str:</code> | Deterministic sha256 hex digest over the canonicalized registry content. | [hashing.py](hashing.py) |
| `line_digest` | <code>def&nbsp;line_digest(rl:&nbsp;RedLine)&nbsp;-&gt;&nbsp;str:</code> | Deterministic sha256 hex digest over a single red line's canonical content. | [hashing.py](hashing.py) |
| `CanaryStatement` | <code>class&nbsp;CanaryStatement:</code> | A dated attestation binding a registry hash to a public statement. | [statement.py](statement.py) |
| `issue_canary` | <code>def&nbsp;issue_canary(</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;issued_on:&nbsp;str,</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;lines:&nbsp;tuple[RedLine,&nbsp;...]&nbsp;=&nbsp;PERSONAL_RED_LINES,</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;statement:&nbsp;str&nbsp;=&nbsp;DEFAULT_CANARY_TEXT,</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;*,</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;prev:&nbsp;CanaryStatement&nbsp;|&nbsp;None&nbsp;=&nbsp;None,</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;rationale:&nbsp;str&nbsp;|&nbsp;None&nbsp;=&nbsp;None,</code><br><code>)&nbsp;-&gt;&nbsp;CanaryStatement:</code> | Create a ``CanaryStatement`` for ``lines`` at ``issued_on`` (ISO date). | [statement.py](statement.py) |
| `CanaryVerification` | <code>class&nbsp;CanaryVerification:</code> | Result of comparing a prior canary against the current registry. | [verification.py](verification.py) |
| `detect_line_removal` | <code>def&nbsp;detect_line_removal(prev_ids:&nbsp;tuple[str,&nbsp;...],&nbsp;lines:&nbsp;tuple[RedLine,&nbsp;...])&nbsp;-&gt;&nbsp;tuple[str,&nbsp;...]:</code> | Return ids present in ``prev_ids`` but absent from ``lines`` — removals. | [verification.py](verification.py) |
| `is_stale` | <code>def&nbsp;is_stale(</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;prev:&nbsp;CanaryStatement&nbsp;|&nbsp;None,</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;as_of:&nbsp;str&nbsp;|&nbsp;None&nbsp;=&nbsp;None,</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;max_age_days:&nbsp;int&nbsp;=&nbsp;DEFAULT_MAX_AGE_DAYS,</code><br><code>)&nbsp;-&gt;&nbsp;bool:</code> | True if there is no fresh attestation as of ``as_of`` (default: today). | [verification.py](verification.py) |
| `verify_canary` | <code>def&nbsp;verify_canary(</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;prev:&nbsp;CanaryStatement&nbsp;|&nbsp;None,</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;lines:&nbsp;tuple[RedLine,&nbsp;...]&nbsp;=&nbsp;PERSONAL_RED_LINES,</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;as_of:&nbsp;str&nbsp;|&nbsp;None&nbsp;=&nbsp;None,</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;max_age_days:&nbsp;int&nbsp;=&nbsp;DEFAULT_MAX_AGE_DAYS,</code><br><code>)&nbsp;-&gt;&nbsp;CanaryVerification:</code> | Compare a prior ``CanaryStatement`` to the current registry. | [verification.py](verification.py) |

## Import direction

May import `model`, `registry`, and sibling canary modules. Keep `canary/` below `contracts/` and above no other package that depends on it.

## Invariants

- Canonical payload shape and digest semantics are load-bearing; changes alter the registry hash and per-line digests.
- Issue-time CANARY severity must stay bound into `line_digests` so later demotion cannot hide a canary-grade change.
- Verification remains fail-closed for stale, future-dated, malformed, or metadata-inconsistent prior statements.

## Tests

Tests for this folder live in:
- [../../../tests/canary/test_hashing.py](../../../tests/canary/test_hashing.py)
- [../../../tests/canary/test_statement.py](../../../tests/canary/test_statement.py)
- [../../../tests/canary/test_verification.py](../../../tests/canary/test_verification.py)
- [../../../tests/canary/test_scripts.py](../../../tests/canary/test_scripts.py)
- [../../../tests/integration/test_trust_model.py](../../../tests/integration/test_trust_model.py)
