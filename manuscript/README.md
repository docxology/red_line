# manuscript

This folder holds the source manuscript. The numbered Markdown files compose the body, `config.yaml` and `preamble.md` configure the renderer, and `references.bib` carries the citation keys bound to the source-claims ledger.

## Composition order

| Sequence | Files | Notes |
| --- | --- | --- |
| opening | `00_abstract.md`, `01_introduction.md` | Front matter and problem statement. |
| background inserts | `02_background_turner_framework.md`, `02a_global_and_historical_scholarship.md`, `02b_line_set_orientation.md`, `02c_first_principles_design.md`, `02d_operating_method.md` | The `02*` block stays together in lexical order. |
| core body | `03_adaptation_thesis.md` through `11_conclusion.md` | Main argument, standards, deployment tiers, transparency, canary, evaluation, formalism, registry text, composition, limitations, and close. |
| bibliography | `99_references.md` | Final numbered section. |

## Support files

| Path | Role |
| --- | --- |
| [config.yaml](config.yaml) | Project metadata, cover assets, render formats, page geometry, and source-framework metadata. |
| [preamble.md](preamble.md) | LaTeX package setup for the renderer. |
| [references.bib](references.bib) | Bibliography keys bound to [source_claims.json](../data/source_claims.json) by [`validate_source_claims`](../src/red_line/contracts/source_claims.py). |
| [assets/cover/README.md](assets/cover/README.md) | Cover provenance and semantic contract for the two image assets. |

## Rendering

This project does not render from `manuscript/` itself, and nothing in this repository produces `output/pdf/` or `output/web/`. Rendering runs in a separate checkout of the template engine, <https://github.com/docxology/template>, which is a stated external dependency and is never vendored here. Clone it anywhere, point `RED_LINE_TEMPLATE_ROOT` at it, and run its `scripts/pipeline/stage_03_render.py` then `scripts/pipeline/stage_04_validate.py` with the lifecycle-qualified project name `working/red_line`. The exact invocation is in [development.md](../docs/development.md); what this repository can do without the engine is in [STANDALONE.md](../STANDALONE.md).

## Related

- [AGENTS.md](AGENTS.md)
- [architecture.md](../docs/architecture.md)
- [data README](../data/README.md)
- [cover README](assets/cover/README.md)
