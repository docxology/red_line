"""Regression tests for fail-closed document-boundary and gate checks.

Fail-closed behavior of the release modules themselves lives under
``tests/release/``; this module covers the contract and gate surfaces that
surround them.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from red_line.contracts import validate_proposed_red_lines, validate_source_claims
from scripts import quality_gate

ROOT = Path(__file__).resolve().parents[2]


def test_source_claim_validation_rejects_unknown_and_url_less_citations(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "manuscript").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "data" / "source_claims.json").write_text(
        json.dumps({"schema_version": "1.0", "records": []}),
        encoding="utf-8",
    )
    (tmp_path / "manuscript" / "references.bib").write_text(
        "@article{known,\n  title = {Known}\n}\n",
        encoding="utf-8",
    )
    (tmp_path / "manuscript" / "01_text.md").write_text("Cites @known and @unknown.\n", encoding="utf-8")
    (tmp_path / "docs" / "research-method.md").write_text("\n", encoding="utf-8")
    errors = validate_source_claims(tmp_path)
    assert any("unknown bibliography keys" in error for error in errors)
    assert any("cited bibliography entry has no verified URL" in error for error in errors)


def test_candidate_binding_requires_decision_row_not_free_text(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "docs").mkdir()
    shutil.copy2(ROOT / "data" / "proposed_red_lines.json", tmp_path / "data" / "proposed_red_lines.json")
    source = (ROOT / "docs" / "PROPOSED_RED_LINES.md").read_text(encoding="utf-8")
    decision_row = next(
        line
        for line in source.splitlines()
        if line.startswith("| `agent-autonomy-limit` |") and "Assent not granted" in line
    )
    altered = source.replace(decision_row, "The candidate `agent-autonomy-limit` remains under discussion.")
    (tmp_path / "docs" / "PROPOSED_RED_LINES.md").write_text(altered, encoding="utf-8")
    errors = validate_proposed_red_lines(tmp_path)
    assert any("agent-autonomy-limit" in error and "decision row" in error for error in errors)


def test_figure_tree_digest_rejects_empty_output(tmp_path):
    with pytest.raises(RuntimeError, match="produced no files"):
        quality_gate._tree_digest(tmp_path)
