# Publication and citation

## How to cite

For source version 0.5.2, use the repository citation until an archive for that exact edition is independently verified:

> Friedman, D. A. (2026). *Personal Red Lines for Development* (version
> 0.5.2) [Software source]. GitHub.
> <https://github.com/docxology/red_line>

BibTeX:

```bibtex
@software{friedman_red_line_2026,
  author  = {Friedman, Daniel Ari},
  title   = {Personal Red Lines for Development},
  version = {0.5.2},
  year    = {2026},
  url     = {https://github.com/docxology/red_line}
}
```

`src/red_line/version.py` is the version authority. `CITATION.cff`,
`.zenodo.json` and `manuscript/config.yaml` share its version;
`tests/test_publication_metadata.py` fails if they disagree. Historical
identifiers remain separate references rather than current-version identifiers.

## Current documentation-only patch

Version 0.5.2 updates citation and publication metadata. Native semantics,
registry identity, and schemas are unchanged. Retained reports, canaries, source
captures, and earlier renders keep their original identities. A source edit is
not a publication receipt or evidence of a current manuscript render.

## Historical migration to 0.5.0

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

At preparation of 0.5.0, the metadata described a release candidate, not a publication receipt.
The deterministic figures and native package can be checked without typesetting;
a current PDF/HTML render, two-pass render custody and strict manifest on clean
source and renderer checkouts remain separate publication requirements.
Historical render evidence must not be relabeled as a 0.5.0 render.


## Persistent Identifiers and Verification

Previously verified source archive: version 0.5.1,
<https://doi.org/10.5281/zenodo.24069256>. That DOI identifies that source ZIP
only, not version 0.5.2 or a standalone rendered manuscript. The earlier
`10.5281/zenodo.21754240` remains a historical archive reference.
Current metadata uses the repository until the exact edition/object is
independently verified. Verify the archive's repository, tag, version, and
contents against the actual public record; a local metadata assertion is not
external publication evidence. Never invent identifiers or rewrite issued bytes.

## Authorized automatic publication

On November 8, 2026, the owner authorized this GitHub Release campaign with the
existing public repositories' Zenodo hooks left active. Future use requires
actual owner authority for that release and object. Inspect the authenticated
hook state immediately before publication and verify the resulting archive's
repository, tag, version, and contents. Never prefill a DOI or amend an immutable
tag to add one learned afterward. PyPI, private-source disclosure, and new
private-sibling deposit automation remain unauthorized. The manual procedure
below is an alternative, not a universal prerequisite.

## Manual reserve-first DOI publication

1. With owner authority for the specific object, create an unpublished Zenodo
   deposition and reserve its DOI. A reservation is not a published deposit.
2. Identify the exact software source or standalone manuscript being deposited.
   If rendering a manuscript with its reserved DOI, label the reservation
   accurately; a source ZIP DOI does not identify a separate PDF.
3. Publish only the authorized bytes, then independently verify the actual
   record's repository, tag, version, and contents.
4. Record the verified identifier for that exact edition/object. If source has
   advanced, retain it as a versioned historical reference, not a current DOI.
   Never amend an immutable tag or archive to insert a DOI learned afterward.

## The other works

The table retains historical publication references, not an exhaustive current
membership list or evidence of successor publication. Current membership belongs
to the [Line Set declaration](https://github.com/docxology/line_set);
the reader and Witness Register are companions, not colors. Native instruments
remain independent, and the report-envelope schema is aligned by convention
rather than dependency. Source availability is distinct from declaration.
Copper's dimensioned resource accounting and Iron's recorded scenario-target
recovery comparisons neither grant permission nor compensate for refusal.
Violet, Copper, and Iron sources are access-controlled.

| Work | Role | Repository | DOI |
| --- | --- | --- | --- |
| `black_line` | line — how I try to do strong work (declaration coverage) | <https://github.com/docxology/black_line> | `https://doi.org/10.5281/zenodo.21754236` |
| `golden_line` | line — what is worth reaching toward (directional readings) | <https://github.com/docxology/golden_line> | `https://doi.org/10.5281/zenodo.21754238` |
| `white_line` | line — what is absent, withheld, or unknowable (absence ledger) | <https://github.com/docxology/white_line> | `https://doi.org/10.5281/zenodo.21754242` |
| `line_set` | the reader that declares the set and checks vocabulary separation | <https://github.com/docxology/line_set> | `https://doi.org/10.5281/zenodo.21754244` |
| `witness_register` | companion beside the set — co-registration without aggregation | <https://github.com/docxology/witness_register> | `https://doi.org/10.5281/zenodo.21754246` |

## Before each release

- [ ] Every gate in `AGENTS.md` green on a clean checkout.
- [ ] `LICENSE` present and accurate.
- [ ] No absolute local paths, secrets, or private-project names in any tracked
      file (`tests/test_publication_metadata.py` checks the first of these).
- [ ] Review newly published Git history for disclosure. The fresh initial-release
      history was a first-publication decision, not an instruction to reset it.
- [ ] The rendered PDF regenerated at the release tree.
