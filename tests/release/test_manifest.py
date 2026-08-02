"""Manifest assembly and fail-closed interpretation of validation reports."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import shutil

from red_line.release import (
    RENDERED_SURFACE_ERROR,
    TEMPLATE_ROOT_MARKER,
    build_manifest,
    candidate_ledger,
    candidate_validation,
    decidable_failures,
    release_ready,
    render_validation,
    template_validation,
    undecided_before_render,
)

ROOT = Path(__file__).resolve().parents[2]

#: Everything a fresh clone does not carry: the repository metadata, the
#: virtualenv, and every ignored generated tree.
_IGNORE_GENERATED = shutil.ignore_patterns(
    ".git",
    ".venv",
    ".pytest_cache",
    ".ruff_cache",
    ".benchmarks",
    "__pycache__",
    "htmlcov",
    "build",
    "dist",
    "output",
    "*.egg-info",
)


def _report(path: Path, payload: object) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


class TestCandidateLedger:
    def test_absent_ledger_reports_none_and_fails_closed(self, tmp_path):
        assert candidate_ledger(tmp_path) is None
        result = candidate_validation(tmp_path)
        assert result["passed"] is False
        assert result["errors"] == ["candidate ledger is missing"]

    def test_present_ledger_is_bound_by_path_and_digest(self, tmp_path):
        ledger = tmp_path / "data" / "proposed_red_lines.json"
        ledger.parent.mkdir()
        ledger.write_text("{}\n", encoding="utf-8")

        bound = candidate_ledger(tmp_path)
        assert bound == {"path": "data/proposed_red_lines.json", "sha256": bound["sha256"]}
        assert len(bound["sha256"]) == 64

        result = candidate_validation(tmp_path)
        assert result["passed"] is True
        assert result["errors"] == []
        assert result["path"] == "data/proposed_red_lines.json"


class TestTemplateValidation:
    def test_missing_report_fails_closed(self, tmp_path):
        result = template_validation(tmp_path / "missing.json")
        assert result["passed"] is False
        assert result["errors"] == ["template validation report is missing"]

    def test_malformed_report_fails_closed(self, tmp_path):
        malformed = tmp_path / "malformed.json"
        malformed.write_text("{not-json", encoding="utf-8")
        result = template_validation(malformed)
        assert result["passed"] is False
        assert "cannot be read" in result["errors"][0]

    def test_report_without_a_summary_fails_closed(self, tmp_path):
        result = template_validation(_report(tmp_path / "no-summary.json", {"passed": True}))
        assert result["passed"] is False
        assert result["errors"] == ["template validation report has no summary"]

    def test_failed_summary_surfaces_the_reports_own_errors(self, tmp_path):
        payload = {"summary": {"all_passed": False}, "errors": ["figure binding drifted"]}
        result = template_validation(_report(tmp_path / "failed.json", payload))
        assert result["passed"] is False
        assert result["errors"] == ["figure binding drifted"]
        assert len(result["report_sha256"]) == 64

    def test_failed_summary_without_errors_uses_a_default_message(self, tmp_path):
        result = template_validation(_report(tmp_path / "bare.json", {"summary": {"all_passed": False}}))
        assert result["errors"] == ["template output validation failed"]

    def test_passing_summary_reports_the_report_digest(self, tmp_path):
        result = template_validation(_report(tmp_path / "ok.json", {"summary": {"all_passed": True}}))
        assert result["passed"] is True
        assert result["errors"] == []
        assert len(result["report_sha256"]) == 64


class TestRenderValidation:
    def test_missing_report_fails_closed(self, tmp_path):
        result = render_validation(tmp_path / "missing.json")
        assert result["passed"] is False
        assert result["errors"] == ["render determinism report is missing"]

    def test_malformed_report_fails_closed(self, tmp_path):
        malformed = tmp_path / "malformed.json"
        malformed.write_text("{not-json", encoding="utf-8")
        result = render_validation(malformed)
        assert result["passed"] is False
        assert "cannot be read" in result["errors"][0]

    def test_differing_passes_carry_the_template_revision(self, tmp_path):
        payload = {"identical": False, "renderer": {"template_revision": "abc123"}}
        result = render_validation(_report(tmp_path / "differ.json", payload))
        assert result["passed"] is False
        assert result["errors"] == ["render passes differ"]
        assert result["template_revision"] == "abc123"

    def test_missing_renderer_block_leaves_the_revision_unknown(self, tmp_path):
        result = render_validation(_report(tmp_path / "no-renderer.json", {"identical": False}))
        assert result["passed"] is False
        assert result["template_revision"] is None

    def test_identical_passes_report_success(self, tmp_path):
        payload = {"identical": True, "renderer": {"template_revision": "def456"}}
        result = render_validation(_report(tmp_path / "same.json", payload))
        assert result["passed"] is True
        assert result["errors"] == []
        assert result["template_revision"] == "def456"


class TestReleaseReady:
    def test_manifest_without_validation_results_is_not_ready(self):
        assert release_ready({}) is False

    def test_empty_validation_results_are_not_ready(self):
        assert release_ready({"validation_results": {}}, strict=True) is False

    def test_any_failing_validation_blocks_release(self):
        manifest = {"validation_results": {"required": {"passed": False}}, "source_dirty": False}
        assert release_ready(manifest) is False
        assert release_ready(manifest, strict=True) is False

    def test_all_passing_validations_are_ready_without_strict(self):
        assert release_ready({"validation_results": {"required": {"passed": True}}}) is True

    def test_strict_mode_requires_a_clean_source_checkout(self):
        manifest = {"validation_results": {"required": {"passed": True}}, "source_dirty": True}
        assert release_ready(manifest) is True
        assert release_ready(manifest, strict=True) is False

    def test_strict_mode_requires_a_clean_template_checkout(self):
        manifest = {
            "validation_results": {"required": {"passed": True}},
            "source_dirty": False,
            "template_dirty": True,
        }
        assert release_ready(manifest, strict=True) is False

    def test_strict_mode_accepts_two_clean_checkouts(self):
        manifest = {
            "validation_results": {"required": {"passed": True}},
            "source_dirty": False,
            "template_dirty": False,
        }
        assert release_ready(manifest, strict=True) is True


class TestPreRenderJudgement:
    """Before a render, "undecided" and "failed" must not be the same word.

    The pre-render path exists because the analysis stage runs before the
    render, so the post-render reports are genuinely not yet knowable. The trap
    is that ``release_bindings`` is only *partly* post-render: one of its errors
    is about the missing rendered surfaces and every other one is decidable from
    source. Deferring the whole check would carry a drifted beacon or a stale
    README digest straight through the gate.
    """

    def _bindings(self, *errors: str) -> dict:
        return {
            "validation_results": {
                "source_claims": {"passed": True, "errors": []},
                "release_bindings": {"passed": not errors, "errors": list(errors)},
                "template_output": {"passed": False, "errors": ["report is missing"]},
                "render_determinism": {"passed": False, "errors": ["report is missing"]},
            }
        }

    def test_missing_rendered_surfaces_alone_are_undecided_not_failed(self):
        manifest = self._bindings(f"{RENDERED_SURFACE_ERROR} ['output/web/index.html']")

        assert decidable_failures(manifest) == []
        assert undecided_before_render(manifest) == [
            "template_output",
            "render_determinism",
            "release_bindings (rendered surfaces only)",
        ]

    def test_a_source_side_binding_failure_is_never_deferred(self):
        """The hole this closes: a real defect hiding behind an absent render."""

        manifest = self._bindings(
            f"{RENDERED_SURFACE_ERROR} ['output/web/index.html']",
            "RL-001: beacon standard drifted",
        )

        assert decidable_failures(manifest) == [
            "release_bindings: ['RL-001: beacon standard drifted']"
        ]

    def test_a_non_binding_validation_failure_is_never_deferred(self):
        manifest = self._bindings()
        manifest["validation_results"]["source_claims"] = {"passed": False, "errors": ["stale"]}

        assert decidable_failures(manifest) == ["source_claims"]

    def test_an_empty_validation_set_fails_closed(self):
        assert decidable_failures({}) == ["validation_results is empty"]
        assert decidable_failures({"validation_results": {}}) == ["validation_results is empty"]

    def test_nothing_is_deferred_once_the_render_reports_pass(self):
        manifest = self._bindings()
        for name in ("template_output", "render_determinism"):
            manifest["validation_results"][name] = {"passed": True, "errors": []}

        assert undecided_before_render(manifest) == []
        assert decidable_failures(manifest) == []


class TestBuildManifest:
    def test_pinned_render_timestamp_is_carried_verbatim(self):
        manifest = build_manifest(ROOT, as_of="2026-07-17", render_timestamp="2026-07-17T00:00:00Z")
        assert manifest["render_timestamp"] == "2026-07-17T00:00:00Z"
        assert manifest["freshness_as_of"] == "2026-07-17"
        assert manifest["manifest_schema_version"] == "1.0"

    def test_omitted_render_timestamp_is_generated_in_utc(self):
        manifest = build_manifest(ROOT, as_of="2026-07-17")
        generated = datetime.fromisoformat(manifest["render_timestamp"])
        assert generated.microsecond == 0
        assert generated.utcoffset().total_seconds() == 0

    def test_manifest_excludes_the_manifest_it_is_writing(self):
        manifest = build_manifest(ROOT, as_of="2026-07-17", render_timestamp="2026-07-17T00:00:00Z")
        assert "output/reports/release_manifest.json" not in manifest["artifact_hashes"]
        assert manifest["figure_hashes"]

    def test_manifest_records_absence_when_no_render_toolchain_is_beside_the_checkout(
        self, tmp_path, monkeypatch
    ):
        """A source-only copy must record "no renderer", not a fictional path.

        The old resolver returned ``root.parents[2] / "template"`` whether or
        not anything was there, so a standalone clone produced a manifest whose
        ``template_revision`` was ``null`` for an unstated reason — the path was
        recorded as real and the git call merely failed. Absence is now stated.
        """

        monkeypatch.delenv("RED_LINE_TEMPLATE_ROOT", raising=False)
        root = tmp_path / "red_line"
        shutil.copytree(ROOT, root, ignore=_IGNORE_GENERATED, symlinks=True)
        # Positive control: nothing that could pass for the toolchain is here.
        assert not any(
            (ancestor / "template" / TEMPLATE_ROOT_MARKER).exists()
            for ancestor in root.resolve().parents
        )

        manifest = build_manifest(root, as_of="2026-07-17", render_timestamp="2026-07-17T00:00:00Z")

        assert manifest["template_root"] is None
        assert manifest["template_revision"] is None
        assert manifest["template_dirty"] is None
        assert release_ready(manifest, strict=True) is False

    def test_manifest_records_the_render_toolchain_it_was_pointed_at(self, tmp_path, monkeypatch):
        override = tmp_path / "engine"
        marker = override / TEMPLATE_ROOT_MARKER
        marker.parent.mkdir(parents=True)
        marker.write_text("# stand-in for the external render stage\n", encoding="utf-8")
        monkeypatch.setenv("RED_LINE_TEMPLATE_ROOT", str(override))

        manifest = build_manifest(ROOT, as_of="2026-07-17", render_timestamp="2026-07-17T00:00:00Z")

        assert manifest["template_root"] == str(override.resolve())
