# Amendment Runbook — Changing the Registry Out Loud

This is the operational discipline for editing the red-line registry. The point
of the framework is not that the author *cannot* change a line — a single
practitioner is simultaneously author, enforcer, and auditor, so nothing stops
the edit. The point is that every change is **dated, rationaled, and diffable**,
and that a silent change is a **detectable state**. This runbook is what makes
that true in practice.

The registry is released at <https://github.com/docxology/red_line>. There is **no
external verifier**: the canary's force rests entirely on a prior copy of the
statement living on a surface the author cannot rewrite, checked by someone other
than the author. Until that copy exists, verification is self-referential. Follow
these steps anyway — the git history *is* the amendment record, and the discipline
is what you carry forward to publication.

## What binds to what

Before editing, know the four surfaces that carry the registry state. An
amendment that updates one and not the others is exactly the "silent fork" the
tests exist to catch.

| Surface | File | What it carries |
| --- | --- | --- |
| Machine-readable registry | `src/red_line/registry/lines.py` (`PERSONAL_RED_LINES`) | The authoritative red lines. Everything else is derived from this. |
| Deterministic hash | `src/red_line/canary/hashing.py` (`registry_hash`) | SHA-256 over canonicalized `RedLine` content (no timestamps). |
| README truncated pin | `README.md` | `` `first8…last6` `` form (`72835fd8…f5aad7` at v0.3.0). |
| Beacon full pin + prose | `manuscript/09_red_lines.md` | The full 64-hex hash and the human-readable rendering of each line. |
| Committed prior canary | `tests/fixtures/canary_committed.json` | The dated statement + hash + `line_ids` + per-line digests that `check_canary.py` and the trust-model tests verify against. |

The current pinned registry hash (do not alter except by re-issuing a canary):

```
72835fd81d1f7ecf70f47b1e0061cd56c385273dd846879ab639225913f5aad7
```

## The steps

### 1. Edit the registry and date the change

Edit `PERSONAL_RED_LINES` in `src/red_line/registry/lines.py`. When you add, remove, or
revise a line, set that line's `stated_on` to the ISO date of the revision
(`RedLine.stated_on` defaults to the version date; an amended line must carry its
own current date so the provenance is honest). `stated_by` stays first-person —
each line is the author's revisable commitment, not a universal claim and not
authored by any AI.

Structural invariants still apply after the edit (`src/red_line/invariants/checks.py`):
unique ids; a content-bearing narrative carve-out on every line; typed
exemptions with valid evidence kinds; non-empty scope on every line; both
Standard analogs present and `CANARY`-severity; no `CANARY` line ever
`AIR_GAPPED`; valid enum field types; non-empty standard and rationale text. An
edit that violates one of these is caught by the invariant tests, each of which
has a proof-of-detection counterpart.

### 2. Run the gate and CONFIRM IT FAILS

```bash
pytest tests/ --cov=red_line --cov-fail-under=90
```

**A green suite immediately after a registry edit means the binding is broken.**
The whole design depends on the registry being pinned in multiple places:

- `tests/integration/test_beacon_binding.py` recomputes `registry_hash` and
  asserts it equals the full hash in `manuscript/09_red_lines.md` and the
  truncated `first8…last6` in `README.md`, and that the README's
  `(N lines, M CANARY-grade)` counts match the live registry.
- `tests/canary/*` and `tests/integration/test_trust_model.py` pin the committed
  fixture (`tests/fixtures/canary_committed.json`) against the live registry via
  `verify_canary`.

If you changed the registry, these **must** go red — they are reporting the drift
they were built to report. If they stay green, either the edit did not change any
canonicalized content, or a pin was already stale; investigate before proceeding.
Do not "fix" a red beacon-binding test by loosening it — re-issue the canary
(step 3), which is what makes it green legitimately.

### 3. Re-issue the canary

Recompute the hash and propagate it to every bound surface.

```bash
# Print the new statement + hash (deterministic; today's date if omitted).
# The committed prior fixture is loaded automatically as the successor anchor,
# so a drifted registry cannot be silently re-attested.
python scripts/build_canary.py <YYYY-MM-DD>

# If the registry has drifted from the prior, emit a dated successor with reason:
python scripts/build_canary.py <YYYY-MM-DD> --rationale "why this line changed"
```

Then update, in this order:

1. **README truncated pin** — replace the `` `first8…last6` `` value with the new
   hash's first 8 and last 6 hex chars. Also update the `(N lines, M CANARY-grade)`
   counts if the line set changed.
2. **Beacon full pin** — replace the single 64-hex hash block in
  `manuscript/09_red_lines.md` with the new full hash.
   (`test_beacon_pinned_hash_matches_registry` asserts the beacon carries
   **exactly one** 64-hex string, and that it equals the computed hash.)
3. **Beacon prose for the edited line** — update the human-readable rendering
   (standard text, rationale, scope, carve-outs) so the prose still matches the
   code. `test_beacon_contains_every_standard_verbatim` compares the normalized
   beacon text against each line's standard.
3b. **Every manuscript surface that restates the line count** — the count is
   written out as a word in eight files, and all eight are now recomputed from
   `PERSONAL_RED_LINES` by
   `tests/integration/test_unbound_count_binding.py::test_every_restated_line_count_matches_the_registry`:
   `manuscript/00_abstract.md`, `manuscript/01_introduction.md`,
   `manuscript/05_deployment_tiers.md`, `manuscript/07_durability_canary.md`,
   `manuscript/09_red_lines.md`, `manuscript/09a_registry_composition.md`,
   `manuscript/10_limitations.md`, and `manuscript/11_conclusion.md`. That test
   also scans every manuscript file for an unlisted restatement, so a ninth
   surface fails rather than drifts. The composition section additionally
   restates the severity split, the tier-floor split, and the structural ranges;
   those are recomputed by the same module against
   `red_line.analysis.registry_metrics`.
4. **Regenerate the committed fixture** — this replaces the successor anchor:

   ```bash
   python scripts/build_canary.py <YYYY-MM-DD> --json > tests/fixtures/canary_committed.json
   ```

   The `--json` output is byte-identical to the fixture serialization
   (`statement`, `issued_on`, `registry_digest`, `line_ids`, `line_digests`).
   `line_digests` is the seven `(id, severity, digest)` triples, and it is not
   optional: `verify_canary` can only reach per-line modification detection and
   the `CANARY-GRADE LINE ALTERED` escalation when it is populated. A fixture
   regenerated without it silently downgrades the canary to aggregate-hash-only
   detection — the suite stays green while the escalation path goes dead.
   Regenerating it
   moves the anchor forward to the amended registry — which is exactly why the
   *prior* copy must already exist somewhere you cannot rewrite (committed git
   history, a published post) before you overwrite it here. A force-push rewrites
   both the registry and its attestation; only an external timestamped copy makes
   the canary externally checkable.

### 4. Never remove or weaken a CANARY line silently

Two lines are `CANARY`-severity (the Standard-1 and Standard-2 analogs:
`s1-human-control-force`, `s2-untargeted-profiling`). `verify_canary` reports
drift/removed/added/modified/stale in general; a **removed or modified
`CANARY`-severity line escalates** to `CANARY-GRADE LINE ALTERED`. Removing or
weakening one is permitted only with a **dated, rationaled successor statement**
(`build_canary.py --rationale …`). The committed statement is explicit about this
contract:

> If a line disappears without a dated, rationaled successor statement, treat that
> silence as signal.

The invariants also forbid demoting a `CANARY` line from `CANARY` or letting it
permit `AIR_GAPPED` (beyond-recall) release — those are structural, not
discretionary.

### 5. Run the full gate to green

```bash
pytest tests/ --cov=red_line --cov-fail-under=90
```

Now the suite should pass: the recomputed hash matches the README and beacon pins,
the regenerated fixture verifies against the live registry, and the invariants
hold. A green suite here means the amendment is internally consistent across all
bound surfaces. Optionally confirm the canary end-to-end:

```bash
python scripts/check_canary.py   # exits 0 iff hash unchanged, fresh, metadata-consistent
```

Freshness fails closed: missing, future, or unparseable dates fail, and the
attestation is stale outside a 180-day window against today. A canary that stops
being re-issued eventually trips this — that is the instrument working.

### 6. Commit with the change and the reason

```bash
git add src/red_line/registry/lines.py README.md manuscript/09_red_lines.md \
        tests/fixtures/canary_committed.json
git commit -m "red-line: <what changed> — <why>"
```

The commit message states **what changed and why**. The git history is the
amendment record — there is no separate ledger. A reviewer diffing two commits
sees the registry delta, the hash delta, and the rationale together. This is the
"out loud" in "revisable, but only out loud."

## What this does and does not guarantee

- **Auditability, not enforcement.** The structural checks are tamper-evident
  conventions, not immutable invariants. The author can edit anything; the
  framework makes the edit visible and dated.
- **The statement is forgeable.** Anyone with write access can regenerate a
  green-looking canary. Its force rests on an external prior copy checked by
  someone other than the author — it uses the *pattern* of a warrant canary, not
  the legal instrument.
- **The evaluator is lexical over a typed, self-declared intake**, with
  description text treated as advisory only. Missing or unverified evidence
  blocks classification; named authorizations document escalation but never
  release a blocking result. The threat model covers registry tampering
  (canary), stale or fabricated evidence, and good-faith self-review, not an
  author lying to their own tool.

## See also

- `docs/VERIFY.md` — how an external party verifies the canary once the prior
  statement lives on an independent timestamped surface.
- `manuscript/07_durability_canary.md` — the canonicalization and hashing rationale.
- **`daf-red-line`** skill (in the author's private `docxology/daf-skills`
  repository; public descriptor stub at
  `.agents/skills/personal-red-lines/SKILL.md`) — the operational skill for
  running reviews, issuing/checking canaries, and proposing versioned edits.
