# Red Line standalone guide

Red Line is its own repository — `docxology/red_line` — as well as one project
inside the author's private projects tree, and it runs in both. The package is
pure standard library with no runtime dependencies; the only third-party
installs are `pytest`, `pytest-cov`, and `ruff`, all declared under
`[project.optional-dependencies].dev`. No sibling project is imported, and none
is on the import path: `black_line`, `golden_line`, `white_line`, and `line_set`
appear in this repository only as prose, never as code.

Separation is not the hard part. Staying honest after separation is, because a
separated copy still has to say what it is, what it can establish, and what it
cannot do without the things it was separated from. What follows is that
statement.

## What a separated copy is

A versioned personal security boundary: a registry of red lines, an
evidence-gated evaluator over proposed actions, an oversight-tier model, a
content-hash canary, and the manuscript that explains all of it. It is a
**beacon** — something to read and align to — and a **canary** — a dated hash
whose staleness or removal is meant to be visible. It is not a compliance
system, not an enforcement mechanism, and not a claim about anyone but its
author. The epistemic limits are stated at length in the README's "Limitations
(read this)" section and in `manuscript/10_limitations.md`; separation does not
soften any of them, and a copy must carry them forward unedited.

## What it can do alone

Everything except typeset itself.

| Surface | Command | Needs anything external? |
| --- | --- | --- |
| Full test suite and coverage gate | `.venv/bin/python -m pytest tests/ --cov=red_line --cov-fail-under=90` | no |
| Deterministic figures (18 SVG + 18 PNG + registry) | `.venv/bin/python scripts/build_figures.py` | `rsvg-convert` for PNG rasterization |
| Canary statement and hash | `scripts/build_canary.py`, `scripts/check_canary.py` | no |
| Every contract validator | `scripts/validate_*.py` | no |
| Release input snapshot and manifest | `scripts/build_release_data.py`, `scripts/build_release_manifest.py` | no |
| Project quality gate (without `--render`) | `scripts/quality_gate.py --as-of <date>` | no |

`rsvg-convert` is a system tool, not a Python dependency; without it the SVG
figures still build and the rasterization step fails loudly rather than
producing a silently empty PNG.

## What it cannot do alone

**Render.** Nothing in this repository writes `output/pdf/` or `output/web/`.
Typesetting runs in a separate checkout of the template engine,
<https://github.com/docxology/template>, which is a stated external dependency
and is never vendored here. Locate it anywhere and name it with
`RED_LINE_TEMPLATE_ROOT`; when that variable is unset,
`red_line.release.provenance.find_template_root` searches the ancestors of the
project root for a directory named `template` that actually carries
`scripts/pipeline/stage_03_render.py`, and reports `None` rather than inventing
a path. The exact invocation is in [`docs/development.md`](docs/development.md).

Two consequences follow, and both are designed rather than tolerated:

- The **rendered-surface checks are skipped, not failed**, in a checkout with no
  `output/web/index.html` or `output/pdf/_combined_manuscript.md`. Each such
  skip first asserts the artifact is absent and that the strict validator
  *reports* that absence, so a skip is a positive control and never a silent
  pass. `tests/test_figure_legibility.py` models the same pattern for the
  rendered LaTeX log.
- The **release manifest records `template_root: null`** and `release_ready(…,
  strict=True)` is `False`. That is the correct answer for a source-only copy:
  a publication gate that passes without a renderer would be attesting to
  artifacts nobody built.

**Publish the canary externally.** The committed prior statement lives in this
same repository, so verification is self-referential until a copy exists on a
surface the author cannot rewrite. See [`docs/VERIFY.md`](docs/VERIFY.md). That
limit is a property of the instrument, not of the separation.

## Where the companion works are

Red Line is the first of four instruments and answers only *what must be
refused*. Black Line asks how to do strong, concise work; Golden Line asks what
higher direction is worth reaching toward; White Line records what is absent or
withheld. A fifth work, `line_set`, is a thin reader that declares the set. Each
is its own repository:

- <https://github.com/docxology/black_line>
- <https://github.com/docxology/golden_line>
- <https://github.com/docxology/white_line>
- <https://github.com/docxology/line_set>

Red Line does not import, depend on, or defer to any of them, and none of them
needs to be present for anything in this repository to run.

The set's relationship was first written down in a short internal note,
`docs/line-set.md`, in the author's private projects tree. It is unpublished and
does not travel with this repository, so it is cited by name rather than linked:
a relative path out of the repository root resolves to nothing for anyone
holding only this repository. The acknowledgement stays; the note's prose is
never pasted into the manuscript in its place, and the durable references are
the four repositories above.

## Validation after separation

Run the offline gate first — the suite and the figure build are the surfaces
that must pass unchanged in a clone. Then check that the copy has not acquired a
path out of itself:

```bash
.venv/bin/python -m pytest tests/test_standalone_contract.py -v
```

That module is the executable form of this document. It asserts that every
source file the suite needs is tracked by git (an untracked `conftest.py` is
invisible to a clone), that no relative markdown link in a tracked file escapes
the repository root, and that this file exists and still names what a separated
copy cannot do.

The local gates are necessary and not sufficient. Rendered PDF and HTML output
must also pass the template's own validation, which needs the external engine
described above.
