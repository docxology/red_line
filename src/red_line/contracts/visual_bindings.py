"""Check that every source-driven figure is documented and rendered."""

from __future__ import annotations

import json
from pathlib import Path
import re

from red_line.figures import FIGURE_TEXT, GENERATORS


def validate_visual_bindings(root: Path) -> list[str]:
    errors: list[str] = []
    expected = set(FIGURE_TEXT)
    generated = set(GENERATORS)
    if expected != generated:
        errors.append(f"figure source/generator mismatch: {sorted(expected ^ generated)}")

    brief_path = root / "docs" / "visualization-briefs.md"
    brief = brief_path.read_text(encoding="utf-8") if brief_path.exists() else ""
    if not brief:
        errors.append("visualization brief is missing or empty")
    manuscript_files = sorted((root / "manuscript").glob("*.md"))
    manuscript = "\n".join(path.read_text(encoding="utf-8") for path in manuscript_files)
    ledger_path = root / "data" / "source_claims.json"
    try:
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return errors + [f"source ledger cannot be read for figure bindings: {exc}"]
    source_records = ledger.get("records", [])
    source_ids = {
        record.get("source_id")
        for record in source_records
        if isinstance(record, dict) and isinstance(record.get("source_id"), str)
    }
    figure_bindings = ledger.get("figure_bindings", {})
    if not isinstance(figure_bindings, dict):
        errors.append("source ledger figure_bindings must be an object")
        figure_bindings = {}
    registry_path = root / "output" / "figures" / "figure_registry.json"
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return errors + [f"figure registry cannot be read: {exc}"]
    records = registry.get("figures")
    labels = {record.get("label") for record in records} if isinstance(records, list) else set()
    if labels != expected:
        errors.append(f"figure registry labels differ from source: {sorted(expected ^ labels)}")
    registry_by_label = (
        {
            record.get("label"): record
            for record in records
            if isinstance(record, dict) and isinstance(record.get("label"), str)
        }
        if isinstance(records, list)
        else {}
    )

    for figure_label, spec in FIGURE_TEXT.items():
        if figure_label not in brief:
            errors.append(f"{figure_label}: missing from visualization brief")
        anchor_pattern = rf"\{{#{re.escape(figure_label)}(?:\s[^}}]*)?\}}"
        if not re.search(anchor_pattern, manuscript):
            errors.append(f"{figure_label}: missing manuscript anchor")
        for suffix in (".png", ".svg"):
            path = root / "output" / "figures" / spec["filename"].replace(".png", suffix)
            if not path.exists() or path.stat().st_size == 0:
                errors.append(f"{figure_label}: missing or empty {path.relative_to(root)}")
        registry_record = registry_by_label.get(figure_label, {})
        if not isinstance(spec.get("caption"), str) or not spec["caption"].strip():
            errors.append(f"{figure_label}: figure source has no non-empty caption")
        if not isinstance(spec.get("alt"), str) or not spec["alt"].strip():
            errors.append(f"{figure_label}: figure source has no non-empty alt text")
        if registry_record.get("caption") != spec.get("caption"):
            errors.append(f"{figure_label}: registry caption drifted from figure source")
        if registry_record.get("alt") != spec.get("alt"):
            errors.append(f"{figure_label}: registry alt text drifted from figure source")
        expected_sources = list(spec.get("source_ids", ()))
        if registry_record.get("source_ids", []) != expected_sources:
            errors.append(f"{figure_label}: registry source_ids drifted from figure source")
        if expected_sources:
            bound_sources = figure_bindings.get(figure_label)
            if bound_sources != expected_sources:
                errors.append(f"{figure_label}: source ledger binding differs from figure source_ids")
            unknown_sources = sorted(set(expected_sources) - source_ids)
            if unknown_sources:
                errors.append(f"{figure_label}: unknown source ids: {unknown_sources}")
        elif figure_label in figure_bindings:
            errors.append(f"{figure_label}: source ledger has bindings but figure source_ids are absent")
    return errors
