"""Hash-addressed release manifest binding source, artifacts, and validation results."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timezone
import json
from pathlib import Path

from red_line import PERSONAL_RED_LINES, __version__
from red_line.canary import CanaryStatement, registry_hash, verify_canary
from red_line.contracts import (
    validate_claim_register,
    validate_release_bindings,
    validate_source_claims,
    validate_visual_bindings,
)

from .provenance import digest_tree, find_template_root, git_dirty, git_revision, sha256_file

MANIFEST_SCHEMA_VERSION = "1.0"
MANIFEST_FILENAME = "release_manifest.json"
CANDIDATE_LEDGER = "data/proposed_red_lines.json"


def _manifest_files(root: Path, directory: str, suffixes: Iterable[str]) -> dict[str, str]:
    """Digest one artifact directory, never including the manifest being written."""

    return digest_tree(root, directory, suffixes, exclude_names=(MANIFEST_FILENAME,))


def candidate_ledger(root: Path) -> dict[str, str] | None:
    """Return the candidate ledger path and digest, or ``None`` when it is absent."""

    path = root / CANDIDATE_LEDGER
    if not path.exists():
        return None
    return {"path": str(path.relative_to(root)), "sha256": sha256_file(path)}


def candidate_validation(root: Path) -> dict:
    """Report whether the candidate red-line ledger is present and digestible."""

    candidate = candidate_ledger(root)
    if candidate is None:
        return {"passed": False, "errors": ["candidate ledger is missing"]}
    return {"passed": True, "errors": [], **candidate}


def template_validation(path: Path) -> dict:
    """Interpret the template output-validation report as a pass or fail result."""

    if not path.exists():
        return {"passed": False, "errors": ["template validation report is missing"]}
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"passed": False, "errors": [f"template validation report cannot be read: {exc}"]}
    summary = report.get("summary")
    if not isinstance(summary, dict):
        return {"passed": False, "errors": ["template validation report has no summary"]}
    if summary.get("all_passed") is not True:
        return {
            "passed": False,
            "errors": report.get("errors", ["template output validation failed"]),
            "report_sha256": sha256_file(path),
        }
    return {
        "passed": True,
        "errors": [],
        "report_sha256": sha256_file(path),
    }


def render_validation(path: Path) -> dict:
    """Interpret the render-determinism report as a pass or fail result."""

    if not path.exists():
        return {"passed": False, "errors": ["render determinism report is missing"]}
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"passed": False, "errors": [f"render determinism report cannot be read: {exc}"]}
    if report.get("identical") is not True:
        return {
            "passed": False,
            "errors": ["render passes differ"],
            "report_sha256": sha256_file(path),
            "template_revision": report.get("renderer", {}).get("template_revision"),
        }
    return {
        "passed": True,
        "errors": [],
        "report_sha256": sha256_file(path),
        "template_revision": report.get("renderer", {}).get("template_revision"),
    }


#: Validations whose whole subject is a post-render report. Before a render
#: they are not false, they are undecided.
RENDER_ONLY_VALIDATIONS = ("template_output", "render_determinism")

#: ``validate_release_bindings`` is only *partly* post-render: one of its errors
#: is about the rendered surfaces and every other one is decidable from source.
#: Deferring the whole check would let a drifted beacon or a stale README digest
#: ride out of the gate behind an absent render.
RENDERED_SURFACE_ERROR = "required rendered surfaces are missing:"


def undecided_before_render(manifest: dict) -> list[str]:
    """Name the validations a render must run before they can be judged."""

    validations = manifest.get("validation_results", {})
    undecided = [name for name in RENDER_ONLY_VALIDATIONS if not _passed(validations, name)]
    bindings = validations.get("release_bindings", {})
    if not bindings.get("passed") and any(
        error.startswith(RENDERED_SURFACE_ERROR) for error in bindings.get("errors", ())
    ):
        undecided.append("release_bindings (rendered surfaces only)")
    return undecided


def decidable_failures(manifest: dict) -> list[str]:
    """Name the validations that failed for a reason no render would change."""

    validations = manifest.get("validation_results", {})
    if not validations:
        return ["validation_results is empty"]
    failures: list[str] = []
    for name, result in validations.items():
        if result.get("passed") is True or name in RENDER_ONLY_VALIDATIONS:
            continue
        if name == "release_bindings":
            remaining = [
                error
                for error in result.get("errors", ())
                if not error.startswith(RENDERED_SURFACE_ERROR)
            ]
            if remaining:
                failures.append(f"release_bindings: {remaining}")
            continue
        failures.append(name)
    return failures


def _passed(validations: dict, name: str) -> bool:
    return validations.get(name, {}).get("passed") is True


def release_ready(manifest: dict, *, strict: bool = False) -> bool:
    """Report whether manifest validation results satisfy the publication gate."""

    validations = manifest.get("validation_results", {})
    if not validations or not all(item.get("passed") is True for item in validations.values()):
        return False
    if strict and (manifest.get("source_dirty") is not False or manifest.get("template_dirty") is not False):
        return False
    return True


def build_manifest(
    root: Path,
    *,
    as_of: str | None = None,
    render_timestamp: str | None = None,
) -> dict:
    """Assemble source, artifact, and validation bindings into one manifest."""

    fixture_path = root / "tests" / "fixtures" / "canary_committed.json"
    canary = json.loads(fixture_path.read_text(encoding="utf-8"))
    canary_statement = CanaryStatement(
        statement=canary["statement"],
        issued_on=canary["issued_on"],
        registry_digest=canary["registry_digest"],
        line_ids=tuple(canary["line_ids"]),
        line_digests=tuple(tuple(item) for item in canary.get("line_digests", ())),
    )
    canary_result = verify_canary(canary_statement, PERSONAL_RED_LINES, as_of=as_of)
    # The manifest records provenance; it must still be assemblable in a
    # checkout that has no render toolchain beside it. ``None`` here says
    # "there was no renderer to describe", which is what a source-only copy
    # should record — a resolved-but-absent path said the opposite.
    template_root = find_template_root(root)
    source_errors = validate_source_claims(root)
    claim_register_errors = validate_claim_register(root)
    visual_binding_errors = validate_visual_bindings(root)
    binding_errors = validate_release_bindings(root, require_rendered=True)
    validation = {
        "source_claims": {"passed": not source_errors, "errors": source_errors},
        "claim_register": {"passed": not claim_register_errors, "errors": claim_register_errors},
        "visual_bindings": {"passed": not visual_binding_errors, "errors": visual_binding_errors},
        "release_bindings": {"passed": not binding_errors, "errors": binding_errors},
        "canary": {
            "passed": canary_result.intact,
            "errors": [] if canary_result.intact else [canary_result.detail],
            "detail": canary_result.detail,
        },
        "candidate_ledger": candidate_validation(root),
    }
    template_report = root / "output" / "reports" / "validation_report.json"
    validation["template_output"] = template_validation(template_report)
    render_report = root / "output" / "reports" / "render_determinism.json"
    validation["render_determinism"] = render_validation(render_report)
    return {
        "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
        "source_revision": git_revision(root),
        "source_dirty": git_dirty(root),
        "package_version": __version__,
        "registry_hash": registry_hash(PERSONAL_RED_LINES),
        "canary_statement": canary,
        "candidate_ledger": candidate_ledger(root),
        "template_root": None if template_root is None else str(template_root),
        "template_revision": None if template_root is None else git_revision(template_root),
        "template_dirty": None if template_root is None else git_dirty(template_root),
        "figure_hashes": _manifest_files(root, "output/figures", (".png", ".svg", ".json")),
        "artifact_hashes": {
            **_manifest_files(root, "output/data", (".json",)),
            **_manifest_files(root, "output/pdf", (".pdf",)),
            **_manifest_files(root, "output/web", (".html",)),
            **_manifest_files(root, "output/reports", (".json", ".md")),
        },
        "validation_results": validation,
        "publication_gate": {
            "status": "released",
            "external_witness": {
                "status": "not_published",
                "locator": None,
            },
            "independent_reviewer": {
                "status": "not_obtained",
                "record": None,
            },
            "independence_verified": False,
            "boundary": (
                "This is personal auditability, not enforcement, legal compliance, "
                "semantic safety classification, or external certification."
            ),
        },
        "freshness_as_of": as_of,
        "render_timestamp": render_timestamp or datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "trust_boundary": "Hashes and local validation establish reproducible auditability, not hermetic security, legal compliance, semantic safety, or external certification.",
    }
