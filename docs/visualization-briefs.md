# Visualization briefs and QA contract

The manuscript uses eighteen static, source-driven figures. Eleven are
explanatory diagrams rather than empirical charts: the source fields are
registry values, function branches, trust-boundary conditions, and a curated
source ledger. Seven are analysis-derived: the exemption evidence matrix, the
outcome-coverage plate, the tier-monotonicity lattice, the registry
composition profile, the scope-vocabulary collision grid, the evidence-gate
sensitivity sweep, and the exemption trigger-semantics probe are computed by
`red_line.analysis` functions executed at build time over the live registry
and the real evaluator. No figure should be read as a measured safety outcome.

## Shared visual contract

- Primary marks are neutral boxes, arrows, threshold cells, and direct labels.
- Teal means retained oversight / compliant path; amber means threshold or
  modification; red means a hard block or a residual risk. Shape and text repeat
  those meanings so color is not required.
- Captions state the claim, source, schematic status, and important limitation.
- Each source-driven figure declares machine-readable `source_ids` when it
  summarizes the source ledger; the validator checks those IDs, the registry
  caption, and the registry alt text against the generator and ledger before a
  render can be trusted.
- PNGs are the document fallback; deterministic SVGs remain beside them for
  inspection. The figures contain no hover-only information and no animation.
- At mobile widths, the static export remains the source of truth: captions and
  alt text carry the long explanation, while the image preserves the primary
  reading path. No controls or permissions are required.

## Layer inventory

| Figure | Story job | Evidence / encoding | Accessibility and fallback | QA |
|---|---|---|---|---|
| `fig:governance-architecture` | Show how a private commitment becomes a reviewable event | registry → action → evaluator → finding → transparency/canary → witness; boundary boxes and arrows | alt text names the flow; caption states no enforcement | SVG/PNG byte determinism; rendered PDF inspection |
| `fig:oversight-tier-ladder` | Explain tier floors and the two CANARY constraints | registry-derived rows, three direct-labeled tiers, filled threshold cells | text labels and check/dash marks duplicate color | registry values, PNG dimensions, figure registry |
| `fig:evaluation-decision-path` | Make evidence-gated evaluator semantics inspectable | evidence gate, canonical scope, typed exemption, and five outcome branches | outcome labels are textual; caption states lexical limitation | branch labels, rendered PDF inspection |
| `fig:outcome-precedence` | Make short-circuit and severity precedence explicit | intake stop above non-compliant, modification, compliant, and outside-scope rungs | labels, ranking, and caption repeat the control-flow rule | deterministic output; rendered PDF inspection |
| `fig:canary-trust-boundary` | Show the external-witness precondition | author-writable vs witness-held boundary; drift/stale/no-signal outputs | dashed boundary, labels, and negative-space claim are textual | source/output registry and rendered PDF inspection |
| `fig:scholarship-reading-map` | Make the global/historical source base visible without claiming lineage | situated cards by broad period and region/tradition, including Latin American colonial-encounter and Aotearoa Indigenous data-governance work | card text plus long caption; no geographic precision or universal lineage implied | source ledger cross-check; visual inspection for collisions |
| `fig:scholarship-transfer-matrix` | Show how scholarship is transferred without authority-washing | source rows, claim classes, and explicit stopping points, with collective data authority kept distinct from individual consent | direct text labels, caption and alt text carry the interpretation boundary | ledger fields, row clipping, grayscale inspection; URLs and locators maintained in docs/research-method.md must be verified before publication |
| `fig:line-set-compass` | Distinguish the four line works without merging their contents | four direct-labelled role panels with cross-reference arrows | role labels, dashed White boundary, and non-substitution note | deterministic output; rendered PDF inspection |
| `fig:improvement-method-loop` | Make the first-principles, science, and iteration method explicit | eight-step bounded loop plus an outside-the-artifact panel | numbered labels, arrows, alt text, and negative-space list duplicate the boundary | deterministic output; caption/alt-text audit; rendered PDF inspection |
| `fig:boundary-instrument-plate` | Make the decision moment memorable and operationally relevant | three labelled traces (declaration, evidence, boundary), a nine-dimension intake field, five outcome nodes, and an external-prior mark | direct labels, repeated semantics, alt text, and caption state the boundary and non-claims | deterministic output; live enum/registry counts (trace subtitles are f-string derived); rendered PDF inspection |
| `fig:scholarship-intake-bridge` | Turn additional scholarship into better operator questions | four source cards cross a deliberate non-authority gap into intake fields and stopping questions | source names, fields, consequences, caption, and alt text repeat the transfer boundary | deterministic output; bibliography/ledger binding; rendered PDF inspection |
| `fig:exemption-evidence-matrix` | State the registry's narrowing structure as derived data, not prose | analysis-computed matrix of 16 typed exemptions × 9 evidence kinds with per-column demand counts and match modes | filled/hollow cells plus text counts and mode chips duplicate color; caption states structure-not-safety | analysis module tests; deterministic output; rendered PDF inspection |
| `fig:outcome-coverage-plate` | Prove five-outcome reachability by exercising the real evaluator | executed battery report: five cases, returned classifications, reason codes, and a coverage summary at a fixed review date; per-case evidence labels are derived from each case's actual context records, not name special-cases | every chip and code is text-labelled; caption states fixture-evidence and non-safety limits | harness tests incl. negative controls; deterministic output; rendered PDF inspection |
| `fig:tier-monotonicity-lattice` | Prove verdict strictness is monotone in dropped oversight by exercising the real evaluator | executed sweep report: every line/keyword slot × three tiers (36 slots over 34 distinct tokens × 3 = 108 real `evaluate_action` runs), verdict chips, per-row monotone marks, and an inversion-count summary | every chip is text-labelled; caption states fixture-evidence, positive-control, and non-safety limits | sweep tests incl. positive control on the replicated pre-fix defect; manuscript number binding; deterministic output; rendered PDF inspection |
| `fig:registry-composition-profile` | Show the shape of the boundary — severity, tier floor, and breadth per line — which the tier ladder does not | `line_summaries` rows as four bars on one derived shared scale, plus `severity_distribution` / `tier_floor_distribution` totals and a `unevidenced_exemptions` count band that renders its zero | every bar carries its number; severity and tier-floor chips are text; the free-pass band states its count in words and digits | analysis-module tests; planted evidence-free exemption must change the band; deterministic output; rendered point-size gate |
| `fig:scope-vocabulary-collisions` | Show exactly which words let one declaration implicate two boundaries — the lexical evaluator's central limitation, made concrete | `scope_token_membership` presence grid over all 34 tokens × 7 lines, with per-row line counts and the executed hosted verdict for each shared token read from the monotonicity sweep | filled/hollow marks are duplicated by a numeric count column and a `SHARED` text tag; footer states the single-line token count | membership/frequency consistency test; shared-token evaluator probe; deterministic output; rendered point-size gate |
| `fig:evidence-gate-sensitivity` | Show that every intake dimension is individually load-bearing, and that the stop names the field it stopped on — the part the outcome-coverage plate cannot show | `run_evidence_sensitivity` grid: 9 dimensions × 5 degradations = 45 real `evaluate_action` runs against a compliant baseline, each cell carrying the returned verdict and the reason codes it raised | every chip is text-labelled with both verdict and code signature; a trailing per-row column repeats the localization result in words and digits | analysis-module tests incl. a refusal when the baseline is not compliant; plated planted-defect test; deterministic output; rendered point-size gate |
| `fig:exemption-trigger-semantics` | Show what ANY and ALL match modes actually do, which the evidence matrix records as a chip but never exercises | `run_trigger_semantics` rows: each exemption probed with one trigger token and then with all of them beside an anchor from its own line — 58 real `evaluate_action` runs, with match counts and returned verdicts | mode chips and both outcome chips are text-labelled; match counts are printed as `n of m` rather than shown only by colour | analysis-module tests incl. a relabelled-mode positive control; plated planted-defect tests for a widened mode and an added ALL-mode exemption; deterministic output; rendered point-size gate |

## Where the figures are defined

Figure behavior lives in [`src/red_line/figures/`](../src/red_line/figures/);
`scripts/build_figures.py` is a thin CLI that calls `build_figures()`.

| Module | Owns |
| --- | --- |
| [`plates_scholarship.py`](../src/red_line/figures/plates_scholarship.py) | The four plates whose content comes from the literature ledger and the boundary statements: reading map, transfer matrix, boundary-instrument plate, intake bridge. |
| [`plates_analysis.py`](../src/red_line/figures/plates_analysis.py) | The seven plates whose numbers are computed by `red_line.analysis` at build time: exemption/evidence matrix, outcome-coverage plate, tier-monotonicity lattice, registry composition profile, scope-vocabulary collision grid, evidence-gate sensitivity sweep, exemption trigger-semantics probe. |
| [`diagrams.py`](../src/red_line/figures/diagrams.py) | The seven schematics that are neither source- nor analysis-derived plates. |
| [`registry.py`](../src/red_line/figures/registry.py) | `GENERATORS`, the single name → generator mapping that defines the figure set. |
| [`text.py`](../src/red_line/figures/text.py) | `FIGURE_TEXT` — every caption and alt-text string, kept out of the drawing code. |
| [`svg.py`](../src/red_line/figures/svg.py), [`theme.py`](../src/red_line/figures/theme.py) | Primitive emission and the shared palette/geometry. |
| [`build.py`](../src/red_line/figures/build.py), [`rasterize.py`](../src/red_line/figures/rasterize.py) | Orchestration and the `rsvg-convert` call. |

Caption and alt-text validation is owned by
[`red_line.contracts.visual_bindings`](../src/red_line/contracts/visual_bindings.py),
invoked through `scripts/validate_visual_bindings.py`.

## Reproduction

Run `uv run python scripts/build_figures.py` from the project root before
rendering through the sibling template. It imports the live registry, writes
deterministic SVG source, rasterizes with `rsvg-convert`, and writes
`output/figures/figure_registry.json`. The manuscript references PNGs using
`../output/figures/<name>.png`, so the generated assets are visible to both PDF
and HTML renderers.

The acceptance gate is three-part: every referenced figure is registered, every
PNG is regenerated from source without a content change, and the final PDF and
combined HTML are inspected for clipping, missing labels, unreadable captions,
and source/caveat separation. A green figure-registry check alone is not visual
validation.
