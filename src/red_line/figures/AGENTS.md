# figures — Figures editing guidance

This folder owns deterministic figure generation: source-bound captions and alt text, SVG construction helpers, the figure registry, rasterization, scholarship/editorial plates, and analysis-backed plates.

## Package surface

The package `__init__` re-exports exactly three names, and that surface must stay stable across any internal reorganization:

| Name | Shape | Source |
| --- | --- | --- |
| `build_figures` | callable | [build.py](build.py) |
| `GENERATORS` | `dict[str, Callable[[], str]]`, eighteen entries keyed by `fig:` label | [registry.py](registry.py) |
| `FIGURE_TEXT` | `dict[str, dict[str, str]]` of filename, title, caption, alt text, and source IDs | [text.py](text.py) |

[registry.py](registry.py) is the only module that knows which file a generator lives in. Moving a generator between plate modules is therefore a one-line import change in `registry.py` and is invisible to every caller.

## Where a new figure goes

| Module | Takes | Test obligation when it drifts |
| --- | --- | --- |
| [plates_scholarship.py](plates_scholarship.py) | Plates whose content is fixed by the literature ledger and the boundary statements. Four today: reading map, transfer matrix, boundary-instrument plate, intake bridge. | Re-read against `data/source_claims.json` and the bibliography; drift here is a source question, not a code question. |
| [plates_analysis.py](plates_analysis.py) | Plates whose numbers are computed by `red_line.analysis` at build time. Three today: exemption/evidence matrix, outcome-coverage plate, tier-monotonicity lattice. | Caught automatically by the analysis and manuscript-binding tests; never hand-transcribe a number into these. |
| [diagrams.py](diagrams.py) | Schematics that assert code paths or orientation rather than data. Seven today. | Re-read against the code path being drawn; the diagram is explanatory, not evidence. |

The split is by **provenance of the numbers**, not by size. A plate that starts scholarship-derived and gains an analysis-computed count moves to `plates_analysis.py`; do not leave it behind and import across.

## Public API inventory

| Name | Signature | Behavior | Source |
| --- | --- | --- | --- |
| `build_figures` | <code>def&nbsp;build_figures(project_root:&nbsp;Path,&nbsp;*,&nbsp;rasterizer:&nbsp;str&nbsp;|&nbsp;Path&nbsp;|&nbsp;None&nbsp;=&nbsp;None)&nbsp;-&gt;&nbsp;list[Path]:</code> | Write all SVG/PNG figures and their registry; return generated PNG paths. | [build.py](build.py) |
| `GENERATORS` | <code>dict[str,&nbsp;Callable[[],&nbsp;str]]</code> | Map each `fig:` label to the generator that returns its SVG string. | [registry.py](registry.py) |
| `FIGURE_TEXT` | <code>dict[str,&nbsp;dict[str,&nbsp;str]]</code> | Filename, title, subtitle, caption, alt text, and source IDs per figure; counts inside it are derived from the live registry and analysis at import time. | [text.py](text.py) |
| `governance_architecture` | <code>def&nbsp;governance_architecture()&nbsp;-&gt;&nbsp;str:</code> | Render the governance architecture SVG schematic. | [diagrams.py](diagrams.py) |
| `tier_ladder` | <code>def&nbsp;tier_ladder()&nbsp;-&gt;&nbsp;str:</code> | Render the deployment-tier ladder SVG. | [diagrams.py](diagrams.py) |
| `evaluation_path` | <code>def&nbsp;evaluation_path()&nbsp;-&gt;&nbsp;str:</code> | Render the evaluation-path SVG schematic. | [diagrams.py](diagrams.py) |
| `canary_trust_boundary` | <code>def&nbsp;canary_trust_boundary()&nbsp;-&gt;&nbsp;str:</code> | Render the canary trust-boundary SVG. | [diagrams.py](diagrams.py) |
| `line_set_compass` | <code>def&nbsp;line_set_compass()&nbsp;-&gt;&nbsp;str:</code> | Render the four-line orientation SVG. | [diagrams.py](diagrams.py) |
| `outcome_precedence` | <code>def&nbsp;outcome_precedence()&nbsp;-&gt;&nbsp;str:</code> | Render the outcome-precedence ladder SVG. | [diagrams.py](diagrams.py) |
| `improvement_method_loop` | <code>def&nbsp;improvement_method_loop()&nbsp;-&gt;&nbsp;str:</code> | Render the improvement-loop SVG schematic. | [diagrams.py](diagrams.py) |
| `scholarship_map` | <code>def&nbsp;scholarship_map()&nbsp;-&gt;&nbsp;str:</code> | Render the scholarship reading-map SVG plate. | [plates_scholarship.py](plates_scholarship.py) |
| `scholarship_transfer_matrix` | <code>def&nbsp;scholarship_transfer_matrix()&nbsp;-&gt;&nbsp;str:</code> | Render the scholarship transfer-matrix SVG plate. | [plates_scholarship.py](plates_scholarship.py) |
| `boundary_instrument_plate` | <code>def&nbsp;boundary_instrument_plate()&nbsp;-&gt;&nbsp;str:</code> | Render the editorial boundary-instrument SVG plate. | [plates_scholarship.py](plates_scholarship.py) |
| `scholarship_intake_bridge` | <code>def&nbsp;scholarship_intake_bridge()&nbsp;-&gt;&nbsp;str:</code> | Render the scholarship-to-intake bridge SVG plate. | [plates_scholarship.py](plates_scholarship.py) |
| `exemption_evidence_matrix_figure` | <code>def&nbsp;exemption_evidence_matrix_figure()&nbsp;-&gt;&nbsp;str:</code> | Render the analysis-derived exemption × evidence-kind matrix. | [plates_analysis.py](plates_analysis.py) |
| `evidence_summary` | <code>def&nbsp;evidence_summary(records:&nbsp;Sequence[EvidenceRecord])&nbsp;-&gt;&nbsp;str:</code> | Summarize how many fixture evidence records are verified. | [plates_analysis.py](plates_analysis.py) |
| `outcome_coverage_plate` | <code>def&nbsp;outcome_coverage_plate()&nbsp;-&gt;&nbsp;str:</code> | Render the exercised outcome-coverage report from the real evaluator. | [plates_analysis.py](plates_analysis.py) |
| `tier_monotonicity_lattice` | <code>def&nbsp;tier_monotonicity_lattice()&nbsp;-&gt;&nbsp;str:</code> | Render the executed verdict-strictness lattice from the real evaluator. | [plates_analysis.py](plates_analysis.py) |
| `registry_composition_profile` | <code>def&nbsp;registry_composition_profile(</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;lines:&nbsp;tuple[RedLine,&nbsp;...]&nbsp;=&nbsp;PERSONAL_RED_LINES,</code><br><code>)&nbsp;-&gt;&nbsp;str:</code> | Render the per-line structural profile of the live registry. | [plates_analysis.py](plates_analysis.py) |
| `scope_vocabulary_collisions` | <code>def&nbsp;scope_vocabulary_collisions(</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;lines:&nbsp;tuple[RedLine,&nbsp;...]&nbsp;=&nbsp;PERSONAL_RED_LINES,</code><br><code>)&nbsp;-&gt;&nbsp;str:</code> | Render the token × line presence grid for the whole declared vocabulary. | [plates_analysis.py](plates_analysis.py) |
| `resolve_rasterizer` | <code>def&nbsp;resolve_rasterizer()&nbsp;-&gt;&nbsp;str:</code> | Return the `rsvg-convert` path found on `PATH`, or fail closed with install guidance. Resolution is `PATH`-only: no machine-specific location is consulted. | [rasterize.py](rasterize.py) |
| `esc` | <code>def&nbsp;esc(value:&nbsp;object)&nbsp;-&gt;&nbsp;str:</code> | Escape a value for XML text or attributes. | [svg.py](svg.py) |
| `text_lines` | <code>def&nbsp;text_lines(text:&nbsp;str,&nbsp;width:&nbsp;int)&nbsp;-&gt;&nbsp;list[str]:</code> | Wrap text deterministically for diagram labels. | [svg.py](svg.py) |
| `label` | <code>def&nbsp;label(x:&nbsp;float,&nbsp;y:&nbsp;float,&nbsp;text:&nbsp;str,&nbsp;*,&nbsp;size:&nbsp;int&nbsp;=&nbsp;18,&nbsp;fill:&nbsp;str&nbsp;=&nbsp;INK,&nbsp;weight:&nbsp;str&nbsp;=&nbsp;&quot;400&quot;,&nbsp;anchor:&nbsp;str&nbsp;=&nbsp;&quot;start&quot;)&nbsp;-&gt;&nbsp;str:</code> | Emit one SVG text label. | [svg.py](svg.py) |
| `paragraph` | <code>def&nbsp;paragraph(x:&nbsp;float,&nbsp;y:&nbsp;float,&nbsp;text:&nbsp;str,&nbsp;*,&nbsp;width:&nbsp;int&nbsp;=&nbsp;50,&nbsp;size:&nbsp;int&nbsp;=&nbsp;16,&nbsp;leading:&nbsp;int&nbsp;=&nbsp;22,&nbsp;fill:&nbsp;str&nbsp;=&nbsp;MUTED,&nbsp;weight:&nbsp;str&nbsp;=&nbsp;&quot;400&quot;)&nbsp;-&gt;&nbsp;str:</code> | Emit wrapped SVG text as stacked labels. | [svg.py](svg.py) |
| `rect` | <code>def&nbsp;rect(x:&nbsp;float,&nbsp;y:&nbsp;float,&nbsp;w:&nbsp;float,&nbsp;h:&nbsp;float,&nbsp;*,&nbsp;fill:&nbsp;str&nbsp;=&nbsp;PAPER,&nbsp;stroke:&nbsp;str&nbsp;=&nbsp;GRID,&nbsp;radius:&nbsp;int&nbsp;=&nbsp;14,&nbsp;dash:&nbsp;bool&nbsp;=&nbsp;False,&nbsp;width:&nbsp;float&nbsp;=&nbsp;1.5)&nbsp;-&gt;&nbsp;str:</code> | Emit one SVG rectangle element. | [svg.py](svg.py) |
| `line` | <code>def&nbsp;line(x1:&nbsp;float,&nbsp;y1:&nbsp;float,&nbsp;x2:&nbsp;float,&nbsp;y2:&nbsp;float,&nbsp;*,&nbsp;stroke:&nbsp;str&nbsp;=&nbsp;GRID,&nbsp;width:&nbsp;float&nbsp;=&nbsp;2,&nbsp;dash:&nbsp;bool&nbsp;=&nbsp;False,&nbsp;arrow:&nbsp;bool&nbsp;=&nbsp;False,&nbsp;opacity:&nbsp;float&nbsp;=&nbsp;1)&nbsp;-&gt;&nbsp;str:</code> | Emit one SVG line element. | [svg.py](svg.py) |
| `path` | <code>def&nbsp;path(d:&nbsp;str,&nbsp;*,&nbsp;stroke:&nbsp;str&nbsp;=&nbsp;GRID,&nbsp;width:&nbsp;float&nbsp;=&nbsp;2,&nbsp;fill:&nbsp;str&nbsp;=&nbsp;&quot;none&quot;,&nbsp;dash:&nbsp;bool&nbsp;=&nbsp;False,&nbsp;opacity:&nbsp;float&nbsp;=&nbsp;1)&nbsp;-&gt;&nbsp;str:</code> | Emit one SVG path element. | [svg.py](svg.py) |
| `circle` | <code>def&nbsp;circle(cx:&nbsp;float,&nbsp;cy:&nbsp;float,&nbsp;r:&nbsp;float,&nbsp;*,&nbsp;fill:&nbsp;str,&nbsp;stroke:&nbsp;str&nbsp;=&nbsp;PAPER,&nbsp;width:&nbsp;float&nbsp;=&nbsp;2)&nbsp;-&gt;&nbsp;str:</code> | Emit one SVG circle element. | [svg.py](svg.py) |
| `svg_document` | <code>def&nbsp;svg_document(title:&nbsp;str,&nbsp;description:&nbsp;str,&nbsp;body:&nbsp;str,&nbsp;*,&nbsp;height:&nbsp;int)&nbsp;-&gt;&nbsp;str:</code> | Assemble the full SVG document wrapper around generated figure content. | [svg.py](svg.py) |
| `figure_header` | <code>def&nbsp;figure_header(title:&nbsp;str,&nbsp;subtitle:&nbsp;str)&nbsp;-&gt;&nbsp;str:</code> | Emit the shared title, subtitle, and banner block used by generated figures. | [svg.py](svg.py) |

## Import direction

May import `analysis`, `model`, `registry`, stdlib, and sibling figure helpers. `contracts/` may import `figures/`; older policy packages must not import it back.

## Invariants

- Figure output remains byte-deterministic for unchanged source and toolchain state.
- `FIGURE_TEXT` and `GENERATORS` must stay in lock-step, with bindings validated against rendered outputs.
- Counts and captions derived from analysis or registry state stay source-driven rather than hand-maintained.
- Reorganizing plate modules must not change a single output byte. When splitting or moving generators, prove it: compare each generator's returned SVG string before and after, rather than eyeballing the rendered PNG.
- Plate modules do not import each other. A helper needed by both belongs in [svg.py](svg.py) or [theme.py](theme.py).

## Tests

Tests for this folder live in:
- [../../../tests/test_figures.py](../../../tests/test_figures.py)
- [../../../tests/integration/test_release_bindings.py](../../../tests/integration/test_release_bindings.py)
- [../../../tests/integration/test_contracts_branch_coverage.py](../../../tests/integration/test_contracts_branch_coverage.py)
