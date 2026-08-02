# Verifying the red_line canary

This is the third-party runbook for checking whether the author's red-line
registry has drifted, been weakened, or gone stale since a prior attestation.
It uses only artifacts that exist in the repository.

## What the canary can and cannot prove

The canary is a **tamper-evident freshness attestation**, not a cryptographic
non-forgeability guarantee. Its force rests on **one external condition**: you
must hold a *prior* `CanaryStatement` (its `issued_on` date and
`registry_digest`) obtained from a surface the author cannot silently rewrite —
a public commit you fetched earlier, a dated post, an OpenTimestamps proof, a
reserved DOI. Checking a statement the author regenerated *now* proves nothing:
it always matches the current registry by construction. Until such an external
copy exists, verification is self-referential (the committed prior lives in this
same repo, and a force-push rewrites both).

## Recompute the current registry hash

```bash
.venv/bin/python -c "from red_line.canary import registry_hash; print(registry_hash())"
```

Compare against the hash pinned in `README.md`, `manuscript/09_red_lines.md`,
and `tests/fixtures/canary_committed.json`. All four must agree; a mismatch
means the registry changed without a full canary re-issue — itself a defect.

## Check freshness and drift against a prior statement

```bash
# Prints the current statement, line ids, and SHA-256:
.venv/bin/python scripts/build_canary.py $(date +%F)

# Compares the committed prior attestation to the current registry and reports
# intact / drift / stale / removed / modified (exit 0 iff intact):
.venv/bin/python scripts/check_canary.py

# For a reproducible audit, supply an independently held prior and fixed date:
.venv/bin/python scripts/check_canary.py --prior /path/to/prior-canary.json --as-of 2026-07-17
```

`verify_canary(prev, PERSONAL_RED_LINES)` (in `src/red_line/canary/verification.py`) is the
programmatic form — pass YOUR independently-held prior statement as `prev`, not
one regenerated from the current tree. It reports:

- **drift** — the content hash changed (a line was added, removed, or edited);
- **removed / added ids** — exactly which lines changed membership;
- **modified ids** — lines whose content changed but whose id persisted;
- **CANARY-GRADE LINE ALTERED** — a Standard-analog (canary-severity) line was
  removed or modified: the loudest signal the instrument emits;
- **stale** — the attestation is older than the freshness window (180 days),
  missing, future-dated, or has an unparseable date (all fail closed).
- **metadata_consistent** — whether the prior statement's ids and per-line
  digests form a complete, valid snapshot of the live registry.
- **canary_altered_ids** — the subset of removed or modified ids whose
  issue-time severity was CANARY; this is exposed separately from the display
  string for machine consumers.

## Run the full self-test

```bash
.venv/bin/python -m pytest tests/ --cov=red_line --cov-fail-under=90
```

The suite pins the beacon prose to the machine registry, the invariants
(including that canary lines are never demoted or air-gapped, that every line
has typed exemptions, and that no line is scope-gutted), and the trust-model
boundaries above. It also tests that missing or unverified intake cannot produce
compliance and that authorizations cannot unblock findings. A green run means the
artifact is internally consistent — it does **not** substitute for the external
prior-statement check, which is the only thing that detects a coordinated
registry-plus-attestation rewrite.

## Run the release-preflight gate

The project-local gate combines linting, tests and coverage, source/registry
binding checks, canary verification, deterministic figure generation, and a
clean wheel import smoke test:

```bash
uv run python scripts/quality_gate.py --as-of 2026-07-17
```

The full release gate adds `--render`; it runs the canonical template
PDF/HTML/figure render twice, validates each rendered pass, writes
`output/reports/render_determinism.json`, and requires a strict release
manifest:

```bash
uv run python scripts/quality_gate.py --as-of 2026-07-17 --render
```

The strict manifest fails closed when a required validation report or rendered
surface is absent, when a report is malformed or failed, or when either the Red
Line source subtree or the template checkout is dirty. It scopes the project
check to this sidecar even though the project may live inside a larger monorepo;
the renderer's own checkout is a release input, so a dirty template cannot be
silently certified as clean.

The render report distinguishes byte identity from content identity. The
current renderer emits fresh PDF `CreationDate` and document-ID metadata on
each pass, so the gate compares extracted PDF text while requiring byte
identity for HTML and figures. This records a toolchain limitation; it is not
a claim of hermetic build security. For HTML visual QA, serve the `output/`
directory as the preview root because generated pages intentionally resolve
figures through `../figures/`:

```bash
python3 -m http.server 8765 --directory output
```

The current release manifest records the publication gate as
`released`. An external witness and independent reviewer have not yet been
obtained (`external_witness.status: not_published`, `independent_reviewer.status: not_obtained`).
Those fields should be filled in with an exact witness locator and preserved
review record as post-release follow-through.
