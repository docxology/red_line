# src — src layout guidance

This directory is the src-layout package root. It should contain importable package code under `src/red_line/`, not release artifacts, test-only helpers, or standalone business logic.

## Public API inventory

| Name | Signature | Behavior | Source |
| --- | --- | --- | --- |
| none | n/a | This folder exports structure, constants, or re-exports rather than defining public functions or classes directly. | n/a |

## Import direction

Keep runtime imports inside `src/red_line/`. Nothing should import `src/` as a package.

## Invariants

- Preserve the src-layout boundary: importable code lives under `src/red_line/`.
- Do not add generated outputs or top-level helper scripts here.

## Tests

Tests for this folder live in:
- [../tests/](../tests/)
