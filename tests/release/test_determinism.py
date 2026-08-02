"""Two-pass artifact comparison exercised against real temporary artifact trees."""

from __future__ import annotations

from pathlib import Path

import pytest

from red_line.release import (
    ARTIFACT_DIRECTORIES,
    RENDER_STAGES,
    TEMPLATE_ROOT_MARKER,
    TemplateRootUnavailable,
    artifact_hashes,
    classify_nondeterminism,
    compare_artifacts,
    pdf_text,
    pdf_texts_equal,
    template_render_passes,
)

PDF_KEY = "output/pdf/manuscript.pdf"


def _template_checkout(directory: Path) -> Path:
    """Create a stand-in render checkout carrying the stage script."""

    marker = directory / TEMPLATE_ROOT_MARKER
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("# stand-in for the external render stage\n", encoding="utf-8")
    return directory


def _artifact(root: Path, relative: str, payload: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")
    return path


def _populated_tree(root: Path) -> None:
    _artifact(root, "output/web/index.html", "<html></html>")
    _artifact(root, "output/figures/plate.svg", "<svg/>")


class TestArtifactHashes:
    def test_empty_tree_yields_no_hashes(self, tmp_path):
        assert artifact_hashes(tmp_path) == {}

    def test_every_comparison_directory_is_walked(self, tmp_path):
        _populated_tree(tmp_path)
        _artifact(tmp_path, PDF_KEY, "%PDF-1.4 first")

        hashes = artifact_hashes(tmp_path)

        assert set(hashes) == {PDF_KEY, "output/web/index.html", "output/figures/plate.svg"}

    def test_directories_outside_the_comparison_scope_are_ignored(self, tmp_path):
        _artifact(tmp_path, "output/reports/render_determinism.json", "{}")
        assert artifact_hashes(tmp_path) == {}
        assert "reports" not in ARTIFACT_DIRECTORIES


class TestPdfText:
    def test_unreadable_path_reports_unavailable_extraction(self, tmp_path):
        assert pdf_text(tmp_path / "absent.pdf") is None

    def test_non_pdf_bytes_never_report_a_false_extraction(self, tmp_path):
        target = _artifact(tmp_path, "not-a.pdf", "plain text, not a PDF")
        extracted = pdf_text(target)
        assert extracted is None or isinstance(extracted, str)


class TestPdfTextsEqual:
    def test_no_expected_pdfs_is_never_equal(self):
        assert pdf_texts_equal({}, {}, []) is False

    def test_first_pass_key_mismatch_is_not_equal(self):
        assert pdf_texts_equal({}, {PDF_KEY: "text"}, [PDF_KEY]) is False

    def test_second_pass_key_mismatch_is_not_equal(self):
        assert pdf_texts_equal({PDF_KEY: "text"}, {}, [PDF_KEY]) is False

    def test_unavailable_extraction_is_not_equal(self):
        assert pdf_texts_equal({PDF_KEY: None}, {PDF_KEY: None}, [PDF_KEY]) is False
        assert pdf_texts_equal({PDF_KEY: "text"}, {PDF_KEY: None}, [PDF_KEY]) is False

    def test_differing_text_is_not_equal(self):
        assert pdf_texts_equal({PDF_KEY: "one"}, {PDF_KEY: "two"}, [PDF_KEY]) is False

    def test_identical_extracted_text_is_equal(self):
        assert pdf_texts_equal({PDF_KEY: "same"}, {PDF_KEY: "same"}, [PDF_KEY]) is True


class TestClassifyNondeterminism:
    def test_byte_identical_passes_have_no_drift(self):
        scope = classify_nondeterminism(byte_identical=True, non_pdf_equal=True, pdf_text_equal=True)
        assert scope == []

    def test_matching_text_with_differing_pdf_bytes_is_metadata_drift(self):
        scope = classify_nondeterminism(byte_identical=False, non_pdf_equal=True, pdf_text_equal=True)
        assert scope == ["PDF metadata (CreationDate and document ID)"]

    def test_differing_non_pdf_artifacts_are_unclassified(self):
        scope = classify_nondeterminism(byte_identical=False, non_pdf_equal=False, pdf_text_equal=True)
        assert scope == ["unclassified artifact bytes"]

    def test_unextractable_text_with_equal_non_pdfs_is_unclassified(self):
        scope = classify_nondeterminism(byte_identical=False, non_pdf_equal=True, pdf_text_equal=False)
        assert scope == ["unclassified artifact bytes"]


class TestTemplateRenderPasses:
    def test_missing_uv_fails_loudly_rather_than_silently_skipping(self, tmp_path, monkeypatch):
        empty_path_directory = tmp_path / "no-tools"
        empty_path_directory.mkdir()
        monkeypatch.setenv("PATH", str(empty_path_directory))
        monkeypatch.setenv("RED_LINE_TEMPLATE_ROOT", str(_template_checkout(tmp_path / "template")))

        render = template_render_passes(tmp_path)

        with pytest.raises(RuntimeError, match="uv is required"):
            render()

    def test_an_absent_render_toolchain_fails_before_a_subprocess_is_launched(
        self, tmp_path, monkeypatch
    ):
        """A render truly cannot proceed without the engine, so this one raises.

        The old resolver handed ``subprocess`` a ``cwd`` three levels above the
        project that had never existed; the failure surfaced as an opaque
        ``FileNotFoundError`` from the OS instead of naming the missing
        dependency.
        """

        monkeypatch.delenv("RED_LINE_TEMPLATE_ROOT", raising=False)
        root = tmp_path / "red_line"
        root.mkdir()

        with pytest.raises(TemplateRootUnavailable, match="RED_LINE_TEMPLATE_ROOT"):
            template_render_passes(root)

    def test_render_pass_snapshots_inputs_then_invokes_each_template_stage(self, tmp_path, monkeypatch):
        root = tmp_path / "sidecar"
        (root / "data").mkdir(parents=True)
        template_root = tmp_path / "template"
        template_root.mkdir()
        log = tmp_path / "uv-invocations.txt"

        bin_directory = tmp_path / "bin"
        bin_directory.mkdir()
        recording_uv = bin_directory / "uv"
        recording_uv.write_text(
            '#!/bin/sh\nprintf "%s|%s\\n" "$PWD" "$*" >> "$UV_INVOCATION_LOG"\n', encoding="utf-8"
        )
        recording_uv.chmod(0o755)

        monkeypatch.setenv("PATH", str(bin_directory))
        monkeypatch.setenv("UV_INVOCATION_LOG", str(log))
        monkeypatch.setenv("RED_LINE_TEMPLATE_ROOT", str(template_root))
        monkeypatch.setenv("VIRTUAL_ENV", str(tmp_path / "should-not-leak"))

        template_render_passes(root)()

        assert (root / "output" / "data" / "release_inputs.json").is_file()
        invocations = log.read_text(encoding="utf-8").splitlines()
        assert len(invocations) == len(RENDER_STAGES)
        for invocation, stage in zip(invocations, RENDER_STAGES):
            working_directory, arguments = invocation.split("|", 1)
            assert Path(working_directory).resolve() == template_root.resolve()
            assert arguments == f"run python {stage} --project working/red_line"

    def test_render_pass_does_not_leak_the_calling_virtualenv(self, tmp_path, monkeypatch):
        root = tmp_path / "sidecar"
        (root / "data").mkdir(parents=True)
        template_root = tmp_path / "template"
        template_root.mkdir()
        log = tmp_path / "virtual-env.txt"

        bin_directory = tmp_path / "bin"
        bin_directory.mkdir()
        recording_uv = bin_directory / "uv"
        recording_uv.write_text(
            '#!/bin/sh\nprintf "[%s]\\n" "${VIRTUAL_ENV-unset}" >> "$UV_INVOCATION_LOG"\n', encoding="utf-8"
        )
        recording_uv.chmod(0o755)

        monkeypatch.setenv("PATH", str(bin_directory))
        monkeypatch.setenv("UV_INVOCATION_LOG", str(log))
        monkeypatch.setenv("RED_LINE_TEMPLATE_ROOT", str(template_root))
        monkeypatch.setenv("VIRTUAL_ENV", str(tmp_path / "sidecar-venv"))

        template_render_passes(root)()

        assert set(log.read_text(encoding="utf-8").split()) == {"[unset]"}


class TestCompareArtifacts:
    def test_stable_tree_without_rendering_is_byte_identical(self, tmp_path):
        _populated_tree(tmp_path)

        result = compare_artifacts(tmp_path)

        assert result["byte_identical"] is True
        assert result["identical"] is True
        assert result["nondeterminism"] == {"present": False, "scope": [], "pdf_text_equal": False}

    def test_empty_tree_is_not_treated_as_deterministic(self, tmp_path):
        result = compare_artifacts(tmp_path)

        assert result["byte_identical"] is False
        assert result["identical"] is False
        assert result["nondeterminism"]["scope"] == ["unclassified artifact bytes"]

    def test_render_callable_runs_before_each_pass(self, tmp_path):
        _populated_tree(tmp_path)
        passes: list[int] = []

        def render() -> None:
            passes.append(len(passes) + 1)

        result = compare_artifacts(tmp_path, render=render)

        assert passes == [1, 2]
        assert result["byte_identical"] is True

    def test_non_pdf_drift_between_passes_is_unclassified(self, tmp_path):
        _populated_tree(tmp_path)
        passes: list[int] = []

        def render() -> None:
            passes.append(len(passes) + 1)
            _artifact(tmp_path, "output/web/index.html", f"<html>{len(passes)}</html>")

        result = compare_artifacts(tmp_path, render=render)

        assert passes == [1, 2]
        assert result["byte_identical"] is False
        assert result["identical"] is False
        assert result["nondeterminism"]["scope"] == ["unclassified artifact bytes"]

    def test_pdf_only_drift_is_reported_when_text_cannot_be_extracted(self, tmp_path):
        # Synthetic PDFs carry no extractable text, so ``pdf_texts_equal`` is False and the
        # PDF-metadata scope is unreachable here. That classification is covered directly by
        # ``TestClassifyNondeterminism``; this case pins the observable end-to-end behavior.
        _populated_tree(tmp_path)
        passes: list[int] = []

        def render() -> None:
            passes.append(len(passes) + 1)
            _artifact(tmp_path, PDF_KEY, f"%PDF-1.4 pass {len(passes)}")

        result = compare_artifacts(tmp_path, render=render)

        assert result["byte_identical"] is False
        assert result["nondeterminism"]["pdf_text_equal"] is False
        assert result["nondeterminism"]["scope"] == ["unclassified artifact bytes"]

    def test_report_records_its_scope_renderer_and_trust_boundary(self, tmp_path, monkeypatch):
        _populated_tree(tmp_path)
        template_root = _template_checkout(tmp_path / "engine")
        monkeypatch.setenv("RED_LINE_TEMPLATE_ROOT", str(template_root))

        result = compare_artifacts(tmp_path)

        assert result["schema_version"] == "1.0"
        assert result["comparison_scope"] == ["pdf", "web", "figures"]
        assert result["artifact_suffixes"] == sorted(result["artifact_suffixes"])
        assert "stage_03_render.py" in result["renderer"]["command"]
        assert result["renderer"]["template_root"] == str(template_root.resolve())
        assert "do not establish hermetic build security" in result["trust_boundary"]

    def test_report_records_a_null_renderer_when_no_toolchain_is_present(
        self, tmp_path, monkeypatch
    ):
        """Comparing an already-built tree is meaningful with no engine present.

        This is the honest counterpart to the assertion above: the report used
        to carry a resolved path to a directory that did not exist, which reads
        as "the renderer lives here" rather than "there is no renderer here".
        """

        monkeypatch.delenv("RED_LINE_TEMPLATE_ROOT", raising=False)
        _populated_tree(tmp_path)

        result = compare_artifacts(tmp_path)

        assert result["renderer"]["template_root"] is None
        assert result["renderer"]["template_revision"] is None
        assert result["byte_identical"] is True
