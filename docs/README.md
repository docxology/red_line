# Red Line documentation index

Red Line is a versioned personal security boundary and explicit No document.
The machine-readable source is `src/red_line/`; the manuscript is the interpretive
account; the generated PDF and HTML are release artifacts. When prose and code
disagree, the code and tests identify the actual implementation, while the
disagreement itself is a publication defect.

## Honesty boundary

The package provides evidence-gated auditability, not enforcement or truth
verification. The registry is first-person, non-exhaustive, revisable, and
private in this sidecar. A same-repository canary fixture is a regression
anchor, not an independent witness. Named authorizations are visible
escalation records and never release a blocking result.

Current registry SHA-256:

```text
72835fd81d1f7ecf70f47b1e0061cd56c385273dd846879ab639225913f5aad7
```

## Core references

| Area | Source |
|---|---|
| Public API | [`../src/red_line/__init__.py`](../src/red_line/__init__.py) |
| Evidence and classifications | [`evaluator-semantics.md`](evaluator-semantics.md) |
| Operator sequence | [`decision-protocol.md`](decision-protocol.md) |
| Claim-to-evidence map | [`claim-register.md`](claim-register.md) |
| Improvement protocol | [`improvement_protocol.md`](improvement_protocol.md) |
| Module boundaries | [`architecture.md`](architecture.md) |
| Design-review correspondence | [`correspondence.md`](correspondence.md) |
| Registry | [`../src/red_line/registry/lines.py`](../src/red_line/registry/lines.py) |
| Threat model | [`security-threat-model.md`](security-threat-model.md) |
| Scholarship ledger | [`research-method.md`](research-method.md) |
| Visual QA | [`visualization-briefs.md`](visualization-briefs.md) |
| Canary mechanism | [`canary-and-trust-model.md`](canary-and-trust-model.md) |
| Third-party verification | [`VERIFY.md`](VERIFY.md) |
| Amendment runbook | [`amendment-runbook.md`](amendment-runbook.md) |
| Development guide | [`development.md`](development.md) |
| Glossary | [`glossary.md`](glossary.md) |
| Hardening tests | [`hardening.md`](hardening.md) |
| Structural invariants | [`invariants.md`](invariants.md) |
| Turner mechanism mapping | [`mechanism-mapping.md`](mechanism-mapping.md) |
| Proposed candidate lines | [`PROPOSED_RED_LINES.md`](PROPOSED_RED_LINES.md) |

## Public model

`ActionContext` requires nine values and evidence records. `EvidenceStatus`
distinguishes verified, self-asserted, unverified, and contradicted material.
`ProposedAction` cannot be constructed without context. `Classification` has
five results: `INSUFFICIENT_INFORMATION`, `NON_COMPLIANT`,
`REQUIRES_MODIFICATION`, `COMPLIANT`, and `OUTSIDE_SCOPE`.

`RedLine` keeps human-readable `carve_outs`, but executable narrowing uses
typed `Exemption` records. `normalize_token` uses an explicit alias table;
there is no heuristic pluralization or semantic inference.

The manuscript's first-principles design section explains why these are
separate surfaces: a declaration, a reviewable record, a local result, a
change signal, and an external witness solve different problems and cannot
substitute for one another.

## Generated figures

Run `uv run python scripts/build_figures.py`, a thin CLI over
[`src/red_line/figures/`](../src/red_line/figures/), which owns the figure set:
`plates_scholarship.py` for the source-derived plates, `plates_analysis.py` for
the analysis-derived ones, `diagrams.py` for the schematics, and `registry.py`
for the single name → generator mapping. The build writes deterministic
SVG sources, PNG fallbacks, and `output/figures/figure_registry.json`. Eighteen
figures cover the evidence-gated method, tier floors, canary boundary,
outcome-precedence ladder, scholarship reading map, scholarship-transfer matrix,
four-line orientation, the explicit improvement loop that connects
deconstruction, evidence, evaluation, recording, revision, the boundary
instrument plate, scholarship-intake bridge, evaluation decision path, and
seven analysis-derived views: the exemption evidence matrix, outcome-coverage
plate, tier-monotonicity lattice, registry-composition profile,
scope-vocabulary collisions, evidence-gate sensitivity sweep, and
exemption-trigger semantics probe (all computed by `red_line.analysis` at
build time).
The boundary instrument plate adds a source-driven visual summary of the
decision moment: declare, evidence, stop, and witness. The scholarship-intake
bridge makes the transfer from reading to operator questions explicit.
Each caption states the source and the limit of the visual claim. Source-driven
figures also carry machine-readable source IDs;
[`red_line.contracts.visual_bindings`](../src/red_line/contracts/visual_bindings.py)
(invoked by `scripts/validate_visual_bindings.py`) checks those IDs, captions,
alt text, and rendered files against the source ledger before release. The other
four validators are its siblings in
[`src/red_line/contracts/`](../src/red_line/contracts/): `source_claims`,
`claim_register`, `proposed_red_lines`, and `release_bindings`.

Red Line remains the refusal boundary. Black, Golden, and White are separate
sibling instruments documented by the sidecar line-set map.

See [AGENTS.md](AGENTS.md) for the working contract.
