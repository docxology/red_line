# manuscript

This folder holds the source manuscript. The numbered Markdown files compose the body, `config.yaml` and `preamble.md` configure the renderer, and `references.bib` carries the citation keys bound to the source-claims ledger.

## Composition order

1. [Abstract](00_abstract.md)
2. [Introduction](01_introduction.md)
3. [Background — Turner as a bounded mechanism source](02_background_turner_framework.md)
4. [Global and Historical Scholarship: Situated Questions, Not a Universal Lineage](02a_global_and_historical_scholarship.md)
5. [Historical four-line orientation: boundary, method, aspiration, absence](02b_line_set_orientation.md)
6. [First-principles design: what the artifact can actually do](02c_first_principles_design.md)
7. [Operating method: from first principles to a bounded release](02d_operating_method.md)
8. [The Adaptation Thesis](03_adaptation_thesis.md)
9. [The two CANARY-severity boundaries](04_standards.md)
10. [Deployment tiers as oversight-retention grades](05_deployment_tiers.md)
11. [Written review and transparency](06_review_and_transparency.md)
12. [Durability and transparency: a hash-based canary](07_durability_canary.md)
13. [Evidence, ambiguity, and evaluation](08_ambiguity_and_evaluation.md)
14. [The instrument stated formally](08a_formalism.md)
15. [The red-line registry](09_red_lines.md)
16. [Registry composition as derived data](09a_registry_composition.md)
17. [Limitations and negative space](10_limitations.md)
18. [Conclusion](11_conclusion.md)
19. [References](99_references.md)

## Support files

| Path | Role |
| --- | --- |
| [config.yaml](config.yaml) | Project metadata, cover assets, render formats, page geometry, and source-framework metadata. |
| [preamble.md](preamble.md) | LaTeX package setup for the renderer. |
| [references.bib](references.bib) | Bibliography keys bound to [source_claims.json](../../data/source_claims.json) by [`validate_source_claims`](../../src/red_line/contracts/source_claims.py). |
| [assets/cover/README.md](assets/cover/README.md) | Cover provenance and semantic contract for the two image assets. |

## Rendering

Use the [pinned render and validation commands](../development.md#rendered-publication-artifacts).
Markdown figure links resolve to the project-local `output/figures/` directory.
The figure builder writes those assets before rendering. The cover and editorial
hero are tracked under [assets/cover/](assets/cover/README.md).

## Related

- [AGENTS.md](AGENTS.md)
- [architecture.md](../architecture.md)
- [data README](../../data/README.md)
- [cover README](assets/cover/README.md)
