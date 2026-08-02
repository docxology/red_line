# manuscript - Manuscript-folder guidance

This folder holds the numbered manuscript sections, the render configuration, the bibliography, and the cover assets consumed by the sibling template checkout.

## Composition order

The body composes in lexical filename order. Whole-number files carry the main sequence, lettered inserts such as `02a` through `02d`, `08a`, and `09a` stay between their neighboring whole-number sections, and `99_references.md` closes the numbered run.

- `00_abstract.md`
- `01_introduction.md`
- `02_background_turner_framework.md`
- `02a_global_and_historical_scholarship.md`
- `02b_line_set_orientation.md`
- `02c_first_principles_design.md`
- `02d_operating_method.md`
- `03_adaptation_thesis.md`
- `04_standards.md`
- `05_deployment_tiers.md`
- `06_review_and_transparency.md`
- `07_durability_canary.md`
- `08_ambiguity_and_evaluation.md`
- `08a_formalism.md`
- `09_red_lines.md`
- `09a_registry_composition.md`
- `10_limitations.md`
- `11_conclusion.md`
- `99_references.md`

`preamble.md` is support material for the renderer, not a numbered body section.

## Support surfaces

| Path | Role |
| --- | --- |
| [config.yaml](config.yaml) | Render metadata, cover settings, authorship metadata, project source-framework metadata, format toggles, and page geometry. |
| [preamble.md](preamble.md) | LaTeX package and theorem setup injected into the render. |
| [references.bib](references.bib) | Bibliography of 45 cited sources, bound to [source_claims.json](../data/source_claims.json) by [`validate_source_claims`](../src/red_line/contracts/source_claims.py). |
| [assets/cover/README.md](assets/cover/README.md) | Provenance and semantic contract for `red_line_cover.png` and `red_line_hero.png`. |

## `config.yaml` fields present

- `paper`: `title`, `subtitle`, `version`, `date`, `description`, `cover.image`, `cover.alt`.
- `authors`: `name`, `orcid`, `email`, `affiliation`, `corresponding`.
- `publication`: `github_repository`, `repository_url`.
- `keywords`: eleven keyword strings.
- `project_config.source_framework`: `author`, `title`, `url`, `date`.
- `render`: `formats.pdf`, `formats.html`, `formats.slides`, `formats.docx`, `formats.epub`, `cover_height_fraction`.
- `metadata`: `license`, `status`, `editorial_hero_image`, `geometry`.

## Render path

Do not render from this directory. Rendering runs in a separate checkout of the template engine, <https://github.com/docxology/template> — located anywhere and named by `RED_LINE_TEMPLATE_ROOT`, not assumed to sit at a fixed relative path — using its `scripts/pipeline/stage_03_render.py` and `scripts/pipeline/stage_04_validate.py` with the project name `working/red_line`. The engine is a stated external dependency: without it this repository still runs its full test suite, its figure build, and every script under `scripts/`, but it cannot typeset itself.

## Invariants

- Keep numbered section files in lexical order; do not hide body prose in `preamble.md` or under `assets/`.
- Keep `references.bib` and [source_claims.json](../data/source_claims.json) synchronized; citation drift is a contract failure.
- For cover assets, update the files and then update [assets/cover/README.md](assets/cover/README.md) rather than repeating the provenance here.
