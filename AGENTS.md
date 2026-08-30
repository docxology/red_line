# Red Line project guidance

This project is its own repository — `docxology/red_line` — and is also
developed as one project inside the author's private projects tree. It runs in
both. Read this file with [`README.md`](README.md),
[`STANDALONE.md`](STANDALONE.md), and the relevant documentation under
[`docs/`](docs/README.md) before editing. There is no parent guidance file to
read: a copy of this repository is the whole of what is being edited, and any
instruction that only makes sense one directory up does not travel with it.

- Keep the executable source of truth in `src/red_line/`; keep tests mirrored in
  `tests/`; keep scripts thin and deterministic.
- Do not add mocks, infrastructure imports, copied template payloads, or
  generated `output/` files to this repository.
- Treat `src/red_line/version.py` as the package-version authority and
  `src/red_line/registry/` as the red-line registry authority.
- Preserve the canary, registry hash, fail-closed validators, and explicit
  pre-publication limits unless an author-controlled amendment is recorded.
- Run the project quality gate from this directory; it needs nothing outside
  this repository. Rendering does: it runs in a separate checkout of
  <https://github.com/docxology/template>, located anywhere and named by
  `RED_LINE_TEMPLATE_ROOT`, with `scripts/pipeline/stage_03_render.py` and
  `scripts/pipeline/stage_04_validate.py` under the project name
  `working/red_line`. See [`STANDALONE.md`](STANDALONE.md).

The current project contract, release limitations, and historical verification
records belong in the README, development guide, and TODO; do not copy
those documents into nested guidance files.
