# personal-red-lines skill — folder contract

This folder holds a **public descriptor stub** for a private skill. It covers the
frontmatter, the worked operations, and the pointer to the private
implementation. It does not hold prompt logic, client context, or any private
workflow; those live only in `docxology/daf-skills`.

| File | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Descriptor consumed by agent runtimes and skill indexes. |
| [AGENTS.md](AGENTS.md) | This file — folder contract. |
| [README.md](README.md) | Human pointer. |

## Frontmatter contract

`SKILL.md` must carry these keys, and the values must stay bound to the code:

| Key | Value shape | Bound to |
| --- | --- | --- |
| `name` | `personal-red-lines` | The folder name; the two must match. |
| `description` | One paragraph ending in a `USE WHEN:` trigger list | The operations actually available in this repo. |
| `source` | `docxology/daf-skills (private)` | Where the operational skill lives. |
| `public_descriptor` | `true` | Asserts this file carries no private content. |
| `version` | Matches `PROJECT_VERSION` | [`src/red_line/version.py`](../../../src/red_line/version.py) is the single version authority. |

## Invariants

- **Every command must run from the project root and be copy-pasteable.** The
  descriptor's value is that an agent can execute it without translation. A
  command that needs an unstated `cd` or an unstated environment variable is a
  defect.
- **Every quoted output must be real.** The `Classification.NON_COMPLIANT` /
  `['unexempted_line']` block and the analytics counts are transcribed from
  actual runs against the live registry. If the registry or evaluator changes
  and these drift, the descriptor is wrong — re-run and re-transcribe rather
  than adjusting prose around a stale number.
- **Point at the package, not the script.** Behavior lives in `src/red_line/`;
  `scripts/` is argument parsing plus one call. The Public entry points table
  must name the package module that owns the behavior — `figures/` for figure
  generation, `contracts/` for the five validators, `release/` for provenance,
  manifest, and determinism — with the script listed only as its CLI wrapper.
- **No private content.** No prompt text, no client names, no workflow that is
  not already public in this repo. `public_descriptor: true` is a claim that a
  reader can check by reading the file.
- **The boundary statement stays.** The descriptor states that these instruments
  are not safety scores, accreditations, moral authorities, or permission
  mechanisms. That sentence is load-bearing and is not softened for brevity.

## When this file changes

Update the descriptor whenever any of these move:

- A package under `src/red_line/` is added, split, or renamed — the Public entry
  points table names modules, so a split like `plates.py` →
  `plates_scholarship.py` + `plates_analysis.py` must be reflected.
- `scripts/quality_gate.py` changes its stage order — the Gates section
  transcribes that order.
- `PROJECT_VERSION` bumps — the frontmatter `version` follows it.
- The registry changes — re-run the analytics block and the canary check, and
  re-transcribe their output.

## Verification

The descriptor is checked by the sidecar's signpost validator, which reads agent
prompts and skills across the project tree. It runs from the sidecar repo root,
which is `../..` relative to the project root:

```bash
# from the project root
cd ../..
uv run python scripts/check_signposts.py working/red_line --manuscript-images --strict-pairs
```

The worked commands are verified by running them; there is no test that asserts
the descriptor's transcribed output, so the re-run is the check.
