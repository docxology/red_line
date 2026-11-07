# Publication and citation

## How to cite

Cite version 0.5.0 through its repository until its own DOI is reserved and verified:

> Friedman, D. A. (2026). *Personal Red Lines for Development* (version
> 0.5.0) [Software and manuscript]. GitHub.
> <https://github.com/docxology/red_line>

BibTeX:

```bibtex
@software{friedman_red_line_2026,
  author  = {Friedman, Daniel Ari},
  title   = {Personal Red Lines for Development},
  version = {0.5.0},
  year    = {2026},
  url     = {https://github.com/docxology/red_line}
}
```

`src/red_line/version.py` is the version authority. `CITATION.cff`,
`.zenodo.json` and `manuscript/config.yaml` share its version;
`tests/test_publication_metadata.py` fails if they disagree. Historical
identifiers remain separate references rather than current-version identifiers.

## Migrating to 0.5.0

Use `evaluate_action(action, as_of=...)` for action readiness and retain its
classification and decision trace. `Exemption.satisfied`,
`RedLine.satisfied_exemptions`, and `RedLine.carved_out` are removed with no
aliases. `Exemption.applicable` and `RedLine.applicable_exemptions` require a
review date and establish only context-evidenced triggers; unknown scope,
tier/scope conflicts and ambiguity still stop full action review.

New bound reports retain native schema 2 and now identify the 0.5.0 producer.
Preserve original schema 1 reports, issued canaries, prior envelopes and dated
release packets byte-for-byte. Replaying an old finding does not replace its
review-time producer or registry binding. Pointer agreement, envelope-contract
validation and comparison with an independently retained archive digest remain
separate checks; none grants permission or independently certifies the archive.

Template-validation JSON must be an object. Arrays, scalars and `null` now
produce a failed validation result instead of aborting manifest assembly.
This does not relax any release gate or change refusal policy, registry
content, noncompensation, candidate non-adoption or native schema versions.

The current metadata describes a release candidate, not a publication receipt.
The deterministic figures and native package can be checked without typesetting;
a current PDF/HTML render, two-pass render custody and strict manifest on clean
source and renderer checkouts remain separate publication requirements.
Historical render evidence must not be relabeled as a 0.5.0 render.


## Persistent Identifiers and Verification

This repository carries an asserted, verified Zenodo DOI (`10.5281/zenodo.21754240`).
Version 0.5.0 retains that last verified DOI in historical references; no new
Zenodo version has been reserved or minted by this run. It must not be read as
confirmation that the 0.5.0 artifacts are deposited there. Daniel reserves the
successor version DOI before updating the metadata and depositing its render.
`tests/test_publication_metadata.py` refuses any unverified DOI-shaped string in
the citation metadata unless that exact DOI is listed as verified inside the test
itself. A placeholder DOI that renders like a real one is worse than no DOI: it
survives copy-and-paste into someone else's bibliography and points nowhere.

## Reserving and Minting DOIs (reserve-first order)

1. Create the Zenodo deposition **without publishing it**, and reserve its DOI.
2. Record the reserved DOI in this repository: add it under `identifiers:` in
   `CITATION.cff`, add it to `related_identifiers` in `.zenodo.json` if
   relevant, add `publication.doi` to `manuscript/config.yaml`, and add the
   exact string to the verified list in `tests/test_publication_metadata.py`.
   The gate turns green only when a person has asserted the DOI is real.
3. Re-render the manuscript so the printed artifact carries its own DOI. A PDF
   deposited without its DOI on the cover cannot be cited from the paper alone.
4. Upload the re-rendered artifacts and publish the deposition.

## The other works

The table retains historical publication references, not an exhaustive current
membership list or evidence of successor publication. Current membership is the
eight-color [Line Set declaration](https://github.com/docxology/line_set);
the reader and Witness Register are companions, not colors. Native instruments
remain independent, and the report-envelope schema is aligned by convention
rather than dependency. Source availability is distinct from declaration.

| Work | Role | Repository | DOI |
| --- | --- | --- | --- |
| `black_line` | line — how I try to do strong work (declaration coverage) | <https://github.com/docxology/black_line> | `https://doi.org/10.5281/zenodo.21754236` |
| `golden_line` | line — what is worth reaching toward (directional readings) | <https://github.com/docxology/golden_line> | `https://doi.org/10.5281/zenodo.21754238` |
| `white_line` | line — what is absent, withheld, or unknowable (absence ledger) | <https://github.com/docxology/white_line> | `https://doi.org/10.5281/zenodo.21754242` |
| `line_set` | the reader that declares the set and checks vocabulary separation | <https://github.com/docxology/line_set> | `https://doi.org/10.5281/zenodo.21754244` |
| `witness_register` | companion beside the set — co-registration without aggregation | <https://github.com/docxology/witness_register> | `https://doi.org/10.5281/zenodo.21754246` |

## Before the repository goes public

- [ ] Every gate in `AGENTS.md` green on a clean checkout.
- [ ] `LICENSE` present and accurate.
- [ ] No absolute local paths, secrets, or private-project names in any tracked
      file (`tests/test_publication_metadata.py` checks the first of these).
- [ ] Git history contains nothing that should not be public — the published
      history is a fresh initial-release commit, not a monorepo extract.
- [ ] The rendered PDF regenerated at the release tree.
