"""Executable binding checks for source claims and publication surfaces."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from red_line.contracts import (
    validate_claim_register,
    validate_proposed_red_lines,
    validate_release_bindings,
    validate_source_claims,
    validate_visual_bindings,
)
from red_line.release import build_manifest

ROOT = Path(__file__).resolve().parents[2]


def test_source_claim_ledger_binds_every_manuscript_citation():
    assert validate_source_claims(ROOT) == []


def test_machine_readable_claim_register_binds_documentation():
    assert validate_claim_register(ROOT) == []


def test_source_driven_figures_bind_to_briefs_manuscript_and_outputs():
    assert validate_visual_bindings(ROOT) == []


def test_machine_readable_claim_register_rejects_duplicate_ids(tmp_path: Path):
    (tmp_path / "data").mkdir()
    (tmp_path / "docs").mkdir()
    source = json.loads((ROOT / "data" / "claim_register.json").read_text(encoding="utf-8"))
    source["claims"].append(dict(source["claims"][0]))
    (tmp_path / "data" / "claim_register.json").write_text(json.dumps(source), encoding="utf-8")
    shutil.copy(ROOT / "docs" / "claim-register.md", tmp_path / "docs" / "claim-register.md")

    errors = validate_claim_register(tmp_path)
    assert any("duplicate claim_id: CLM-001" in error for error in errors)


#: The render host writes these; nothing in this repository produces them.
RENDERED_SURFACES = (
    Path("output") / "web" / "index.html",
    Path("output") / "pdf" / "_combined_manuscript.md",
)


def _missing_rendered_surfaces() -> list[str]:
    return [str(relative) for relative in RENDERED_SURFACES if not (ROOT / relative).exists()]


def test_beacon_metadata_and_registry_bindings_are_complete():
    assert validate_release_bindings(ROOT, require_rendered=False) == []

    missing = _missing_rendered_surfaces()
    if missing:
        # Positive control: strict mode must *report* the absence rather than
        # pass silently. Asserting the exact message keeps this branch bound to
        # the real behaviour instead of degrading into an unconditional skip.
        assert validate_release_bindings(ROOT, require_rendered=True) == [
            f"required rendered surfaces are missing: {missing}"
        ]
        pytest.skip(f"no rendered surfaces in this checkout: {missing}")

    assert validate_release_bindings(ROOT, require_rendered=True) == []


def test_proposed_candidate_ledger_remains_non_adopted():
    assert validate_proposed_red_lines(ROOT) == []


def test_release_manifest_carries_source_canary_and_artifact_hashes():
    manifest = build_manifest(
        ROOT,
        as_of="2026-07-17",
        render_timestamp="2026-07-17T00:00:00Z",
    )
    assert manifest["manifest_schema_version"] == "1.0"
    assert manifest["package_version"]
    assert len(manifest["registry_hash"]) == 64
    assert manifest["canary_statement"]["registry_digest"] == manifest["registry_hash"]
    assert manifest["candidate_ledger"]["path"] == "data/proposed_red_lines.json"
    assert len(manifest["candidate_ledger"]["sha256"]) == 64
    assert manifest["figure_hashes"]
    assert "output/reports/release_manifest.json" not in manifest["artifact_hashes"]
    assert manifest["validation_results"]["source_claims"]["passed"]
    assert manifest["validation_results"]["canary"]["passed"]
    assert manifest["publication_gate"]["status"] == "released"
    assert manifest["publication_gate"]["external_witness"]["status"] == "not_published"
    assert manifest["publication_gate"]["external_witness"]["locator"] is None
    assert manifest["publication_gate"]["independent_reviewer"]["status"] == "not_obtained"
    assert manifest["publication_gate"]["independence_verified"] is False
    # ``render_determinism`` is always present, so keying the guard on the key
    # made this branch vacuous. Bind it to the artifact instead: when the
    # render-determinism report exists it must pass, and when it does not the
    # manifest must say so rather than report a silent pass.
    render_report = ROOT / "output" / "reports" / "render_determinism.json"
    render_determinism = manifest["validation_results"]["render_determinism"]
    if render_report.exists():
        assert render_determinism["passed"]
    else:
        assert render_determinism["passed"] is False
        assert render_determinism["errors"] == ["render determinism report is missing"]
