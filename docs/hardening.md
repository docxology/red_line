# Hardening suite — adversarial and boundary tests

**Files:** [`tests/hardening/`](../tests/hardening/) and
[`tests/test_hardening_contracts.py`](../tests/test_hardening_contracts.py)
**Added:** 2026-07-17 (additive pass; no production behavior changed except the
one new invariant below)

This suite strengthens verification of *existing* public behavior along four
angles the original per-module suites covered only partially. It restored the
suite to 100% line + branch coverage after the `src/` package restructure and
grew the suite substantially in one pass. No absolute count is recorded here:
the figure this file once carried (323) matched no state of the tree at any
date, and a hand-maintained count in a dated narrative section cannot be
re-derived. `docs/development.md` already routes the question — "the exact test
count and artifact hashes belong to the generated release manifest rather than
this guide" — so the current totals live in
`output/reports/release_manifest.json` and the per-area tables in
[`tests/AGENTS.md`](../tests/AGENTS.md).

## 1. Hostile scope inputs to `evaluate_action`

The constructor (`ProposedAction`) already normalizes and rejects malformed
scope, so these tests attack the *post-construction* surface — the paths
`_safe_normalize_scope` exists for:

- A Cyrillic-homoglyph token (`surveillancе`) smuggled past the constructor via
  `object.__setattr__` yields `INSUFFICIENT_INFORMATION` with the
  "non-canonical or non-ASCII token" reason — never a policy match, never a
  crash.
- A smuggled non-string token (`42`) takes the same fail-closed path.
- Punctuation-only tokens (`"__"`, `"!!!"`) that survive the constructor but
  normalize to nothing produce the "scope declaration is empty" stop signal.
- Every unknown-scope marker (`unknown`, `unspecified`, `tbd`, `unclear`)
  blocks evaluation even when a real prohibited token is also declared.
- A full-width Unicode spelling (`ｓｕｒｖｅｉｌｌａｎｃｅ`) NFKC-folds to the
  canonical token and **still implicates** the profiling line — spelling tricks
  cannot dodge coverage.
- Declaring only a prohibited dimension with complete verified evidence is
  `NON_COMPLIANT`: no line's exemption triggers overlap its own scope (see the
  invariant below), so a bare prohibited declaration cannot self-exempt.

## 2. Additional proof-of-detection angles

New planted-bad registries confirm the battery fires on defect classes the
original tests did not plant: a corrupted exemption `match_mode`, an invalid or
non-string `stated_on`/`stated_by` (provenance), non-canonical and
unnormalizable scope spellings, and — for the new check — a planted
self-exempting exemption, including one smuggled through an alias spelling
(`weapon` vs canonical `weapons`).

### New invariant: `exemption_triggers_disjoint`

`check_exemption_triggers_disjoint` (in
[`src/red_line/invariants/checks.py`](../src/red_line/invariants/checks.py),
documented in [`invariants.md`](invariants.md)) pins the property that no
exemption trigger token repeats its own line's prohibited scope. It passes on
the real registry, fails closed on unnormalizable tokens, and has
proof-of-detection tests for both the direct and the alias-smuggled planting.

## 3. Digest determinism and sensitivity

The registry digest and per-line digests are review/drift instruments, so their
determinism is load-bearing: the suite asserts repeatability, invariance to
exemption ordering *within* a line (canonicalization sorts by exemption id),
distinctness across lines, and that any content change moves both the line
digest and the registry hash. (Invariance to registry-level reordering was
already pinned in `tests/canary/test_hashing.py`.)

## 4. Boundary dates and fail-closed metadata

- Evidence staleness at the exact window edge: `recorded + 180d` is fresh,
  `+181d` is stale; future-dated records are stale; a zero-day window behaves
  at its own boundary. The same edge is exercised end-to-end through
  `evaluate_action`.
- Canary staleness at the exact `DEFAULT_MAX_AGE_DAYS` edge, future-dated
  issuance, and rejection of invalid windows (negative, boolean, non-int).
- Exhaustive rejection tables for hand-crafted `CanaryStatement` construction
  and for corrupted metadata reaching `verify_canary` — every malformed field
  reads as "canary metadata invalid", `intact=False`, `stale=True`, never a
  silent pass.
- Strict-constructor rejection tables for `Exemption`, `RedLine`,
  `ProposedAction`/`ActionContext`/`ActionAssessment`, `ReviewFinding`, and
  `TransparencyReport` — the typed model refuses malformed input at the door.

## Gate

```bash
uv run pytest tests/ --cov=red_line --cov-branch -q
```

Expected: all tests pass, total coverage 100.00% (line + branch).
