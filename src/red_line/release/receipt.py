"""Carry a local two-render comparison across a destructive output rebuild."""

from __future__ import annotations

from collections.abc import Callable
import hashlib
import json
from pathlib import Path

from .determinism import artifact_hashes, pdf_text
from .provenance import render_source_binding, sha256_file

COMPARISON_PATH = "output/reports/render_determinism.json"
BINDING_PATH = "output/reports/render_comparison_binding.json"
BINDING_SCHEMA = "red-line.render-comparison-binding/1.0"


def _comparison_issues(root: Path, report: dict) -> list[str]:
    issues = []
    if (report.get("schema_version") != "2.0" or report.get("render_pass_count") != 2
            or report.get("identical") is not True):
        issues.append("comparison requires two successful render passes, not a hash-only report")
    current = render_source_binding(root)
    if (report.get("input_binding") != current or not current["source_revision"]
            or not current["source_hashes"] or current["source_dirty"] is not False
            or not current["template_revision"] or current["template_dirty"] is not False):
        issues.append("comparison source/renderer binding is unavailable, dirty or changed")
    artifacts = artifact_hashes(root)
    expected = report.get("second_pass_hashes")
    if not isinstance(expected, dict) or not expected or set(artifacts) != set(expected):
        issues.append("comparison artifact inventory changed")
        return issues
    text_hashes = report.get("pdf_text_hashes", {})
    for name, digest in artifacts.items():
        if digest == expected[name]:
            continue
        prior_text = text_hashes.get(name) if isinstance(text_hashes, dict) else None
        text = pdf_text(root / name) if name.endswith(".pdf") and prior_text is not None else None
        if text is None or hashlib.sha256(text.encode()).hexdigest() != prior_text:
            issues.append(f"comparison artifact changed: {name}")
    return issues


def finalize_render_pipeline(root: Path, pipeline: Callable[[], None], custody_directory: Path) -> Path:
    """Preserve executed comparison bytes, rebuild, then bind the final artifacts.

    Custody must be outside the project. Pipeline exceptions retain the original
    receipt there; binding disagreements prevent restoration into a changed tree.
    PDF text equality retains the comparison's existing limited boundary; the
    separate final binding pins every final artifact's exact bytes.
    """

    if custody_directory.resolve().is_relative_to(root.resolve()):
        raise ValueError("comparison custody must be outside the project")
    path = root / COMPARISON_PATH
    original = path.read_bytes()
    report = json.loads(original)
    if not isinstance(report, dict):
        raise RuntimeError("comparison report must be an object")
    issues = _comparison_issues(root, report)
    if issues:
        raise RuntimeError("; ".join(issues))
    custody_directory.mkdir(parents=True, exist_ok=True)
    held = custody_directory / path.name
    with held.open("xb") as handle:
        handle.write(original)
    try:
        pipeline()
    except Exception as exc:
        raise RuntimeError(f"full pipeline failed; comparison preserved at {held}") from exc
    if held.read_bytes() != original:
        raise RuntimeError("preserved receipt changed")
    issues = _comparison_issues(root, report)
    if issues:
        raise RuntimeError("; ".join(issues))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(original)
    binding = {
        "schema": BINDING_SCHEMA,
        "comparison_sha256": sha256_file(path),
        "input_binding": report["input_binding"],
        "artifact_hashes": artifact_hashes(root),
    }
    (root / BINDING_PATH).write_text(json.dumps(binding, sort_keys=True, indent=2) + "\n")
    return held


def render_binding_issues(root: Path, report: dict) -> list[str]:
    """Check comparison custody against the current source and exact final bytes."""

    issues = _comparison_issues(root, report)
    try:
        binding = json.loads((root / BINDING_PATH).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return [*issues, f"final comparison binding unavailable: {exc}"]
    if (not isinstance(binding, dict) or binding.get("schema") != BINDING_SCHEMA
            or binding.get("comparison_sha256") != sha256_file(root / COMPARISON_PATH)
            or binding.get("input_binding") != report.get("input_binding")
            or binding.get("artifact_hashes") != artifact_hashes(root)):
        issues.append("final comparison binding disagrees with the current tree")
    return issues
