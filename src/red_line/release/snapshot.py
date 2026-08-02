"""Deterministic release-input snapshot derived from the live analysis APIs."""

from __future__ import annotations

import json
from pathlib import Path

from red_line import PERSONAL_RED_LINES
from red_line.analysis import (
    evidence_kind_demand,
    exemption_evidence_matrix,
    line_summaries,
    run_monotonicity_sweep,
    run_outcome_coverage,
    scope_token_frequency,
)

from .provenance import git_revision, sha256_file

SOURCE_LEDGERS = (
    "data/claim_register.json",
    "data/source_claims.json",
    "data/proposed_red_lines.json",
)
FIGURE_REGISTRY = "output/figures/figure_registry.json"


def analysis_metrics() -> dict[str, object]:
    """Derive manuscript-facing numeric facts from the live analysis APIs."""

    matrix = exemption_evidence_matrix()
    demand = evidence_kind_demand()
    frequencies = scope_token_frequency()
    outcomes = run_outcome_coverage()
    monotonicity = run_monotonicity_sweep()
    return {
        "registry_line_count": len(PERSONAL_RED_LINES),
        "exemption_count": len(matrix),
        "evidence_requirement_count": sum(row.required_count for row in matrix),
        "intake_dimension_count": len(demand),
        "evidence_kind_demand": {kind.value: count for kind, count in demand.items()},
        "line_summaries": [
            {
                "line_id": summary.line_id,
                "scope_size": summary.scope_size,
                "carve_out_count": summary.carve_out_count,
                "exemption_count": summary.exemption_count,
                "any_mode_count": summary.any_mode_count,
                "all_mode_count": summary.all_mode_count,
            }
            for summary in line_summaries()
        ],
        "scope_token_slots": sum(frequencies.values()),
        "scope_token_distinct_count": len(frequencies),
        "scope_token_frequency": dict(sorted(frequencies.items())),
        "shared_scope_token_count": sum(1 for frequency in frequencies.values() if frequency > 1),
        "scope_token_disjoint_count": sum(1 for frequency in frequencies.values() if frequency == 1),
        "outcome_coverage": {
            "case_count": len(outcomes.results),
            "classification_count": len(outcomes.reached),
            "complete": outcomes.complete,
            "all_matched": outcomes.all_matched,
        },
        "monotonicity": {
            "keyword_count": monotonicity.keyword_count,
            "evaluation_count": monotonicity.evaluation_count,
            "inversion_count": monotonicity.inversion_count,
            "monotone": monotonicity.monotone,
        },
    }


def build_snapshot(root: Path) -> dict[str, object]:
    """Return the source and generated inputs carried into a release tree."""

    sources = {
        path.relative_to(root).as_posix(): sha256_file(path)
        for path in (root / ledger for ledger in SOURCE_LEDGERS)
        if path.is_file()
    }
    figure_registry = root / FIGURE_REGISTRY
    figures: dict[str, object] = {"path": FIGURE_REGISTRY}
    if figure_registry.is_file():
        payload = json.loads(figure_registry.read_text(encoding="utf-8"))
        figures.update(
            {
                "sha256": sha256_file(figure_registry),
                "figure_count": payload.get("figure_count", len(payload.get("figures", []))),
            }
        )
    else:
        figures.update({"sha256": None, "figure_count": 0})
    return {
        "schema_version": "1.1",
        "source_revision": git_revision(root),
        "source_hashes": sources,
        "figure_registry": figures,
        "analysis_metrics": analysis_metrics(),
        "trust_boundary": (
            "This snapshot binds release inputs to the local artifact tree; it does not "
            "establish external witnessing, semantic truth, legal compliance, or safety."
        ),
    }


def write_snapshot(root: Path) -> Path:
    """Write the deterministic release-input snapshot and return its path."""

    destination = root / "output" / "data" / "release_inputs.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(build_snapshot(root), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return destination
