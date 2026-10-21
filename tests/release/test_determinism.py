"""Two-pass artifact comparison exercised against real temporary artifact trees."""

from __future__ import annotations

from pathlib import Path
import json
import os
import shutil
import subprocess

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
    template_full_pipeline,
    tree_digest,
    wheel_smoke,
)

PDF_KEY = "output/pdf/manuscript.pdf"


def _small_pdf(text: str = "bound text") -> bytes:
    stream = f"BT /F1 12 Tf 20 100 Td ({text}) Tj ET".encode()
    objects = [b"<< /Type /Catalog /Pages 2 0 R >>",
               b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
               b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
               b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
               b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream"]
    payload = b"%PDF-1.4\n"
    offsets = [0]
    for index, obj in enumerate(objects, 1):
        offsets.append(len(payload))
        payload += f"{index} 0 obj\n".encode() + obj + b"\nendobj\n"
    xref = len(payload)
    payload += b"xref\n0 6\n0000000000 65535 f \n"
    payload += b"".join(f"{offset:010} 00000 n \n".encode() for offset in offsets[1:])
    return payload + f"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()


@pytest.fixture
def receipt_tree(tmp_path, monkeypatch):
    root = tmp_path / "red_line"
    template = tmp_path / "template"
    environment = os.environ | {
        "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_AUTHOR_NAME": "Receipt test", "GIT_AUTHOR_EMAIL": "receipt@example.invalid",
        "GIT_COMMITTER_NAME": "Receipt test", "GIT_COMMITTER_EMAIL": "receipt@example.invalid",
    }
    for repo in (root, template):
        repo.mkdir()
        (repo / ".gitignore").write_text("output/\n")
        (repo / "source.txt").write_text("intact\n")
        for args in (["init", "-q"], ["add", "."], ["commit", "-qm", "fixture"]):
            subprocess.run(["git", "-C", str(repo), *args], check=True, env=environment)
    monkeypatch.setenv("RED_LINE_TEMPLATE_ROOT", str(template))
    _populated_tree(root)
    (root / PDF_KEY).parent.mkdir(parents=True)
    (root / PDF_KEY).write_bytes(_small_pdf())
    report = compare_artifacts(root, render=lambda: None)
    destination = root / "output/reports/render_determinism.json"
    destination.parent.mkdir(parents=True)
    destination.write_text(json.dumps(report))
    return root, report, destination, tmp_path / "custody"


def _clean_and_rebuild(root):
    contents = {key: (root / key).read_bytes() for key in artifact_hashes(root)}
    shutil.rmtree(root / "output")
    for key, payload in contents.items():
        destination = root / key
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(payload)


class TestRenderReceipt:
    @pytest.mark.parametrize("changed_pass", [1, 2])
    def test_committed_input_changes_during_comparison_are_rejected(self, receipt_tree, changed_pass):
        root, _, _, _ = receipt_tree
        calls = 0
        def render():
            nonlocal calls
            calls += 1
            if calls == changed_pass:
                (root / "source.txt").write_text("changed during comparison")
                subprocess.run(
                    ["git", "-C", str(root), "-c", "user.name=Receipt test",
                     "-c", "user.email=receipt@example.invalid", "commit", "-qam", "change"],
                    check=True, env=os.environ | {"GIT_CONFIG_GLOBAL": os.devnull,
                                                 "GIT_CONFIG_NOSYSTEM": "1"},
                )
        with pytest.raises(RuntimeError, match="changed during"):
            compare_artifacts(root, render=render)

    def test_non_object_receipt_is_rejected(self, receipt_tree):
        from red_line.release import finalize_render_pipeline

        root, _, path, custody = receipt_tree
        path.write_text("[]")
        with pytest.raises(RuntimeError, match="object"):
            finalize_render_pipeline(root, lambda: None, custody)

    def test_genuine_comparison_survives_output_cleanup(self, receipt_tree):
        from red_line.release import finalize_render_pipeline, render_binding_issues, render_validation

        root, report, path, custody = receipt_tree
        original = path.read_bytes()
        held = finalize_render_pipeline(root, lambda: _clean_and_rebuild(root), custody)
        assert held.read_bytes() == path.read_bytes() == original
        assert not held.is_relative_to(root)
        assert render_binding_issues(root, report) == []
        assert render_validation(path, root=root)["passed"] is True

    @pytest.mark.parametrize("mutation", ["source", "html", "pdf", "addition", "renderer"])
    def test_changed_inputs_or_artifacts_prevent_receipt_reuse(self, receipt_tree, mutation):
        from red_line.release import finalize_render_pipeline

        root, _, path, custody = receipt_tree
        template = Path(os.environ["RED_LINE_TEMPLATE_ROOT"])
        def pipeline():
            _clean_and_rebuild(root)
            if mutation == "source":
                (root / "source.txt").write_text("changed")
            elif mutation == "renderer":
                (template / "source.txt").write_text("changed")
            elif mutation == "pdf":
                (root / PDF_KEY).write_bytes(_small_pdf("different text"))
            else:
                _artifact(root, "output/web/index.html" if mutation == "html" else "output/web/extra.html", "changed")
        with pytest.raises(RuntimeError, match="binding|artifact"):
            finalize_render_pipeline(root, pipeline, custody)
        assert not path.exists()

    def test_pipeline_failure_retains_external_receipt_and_failure(self, receipt_tree):
        from red_line.release import finalize_render_pipeline

        root, _, path, custody = receipt_tree
        original = path.read_bytes()
        def pipeline():
            _clean_and_rebuild(root)
            raise ValueError("deliberate pipeline failure")
        with pytest.raises(RuntimeError, match="preserved") as error:
            finalize_render_pipeline(root, pipeline, custody)
        assert isinstance(error.value.__cause__, ValueError)
        assert (custody / path.name).read_bytes() == original
        assert not path.exists()

    @pytest.mark.parametrize("field,value", [("render_pass_count", 0), ("schema_version", "1.0"),
                                              ("identical", False), ("input_binding", {}),
                                              ("second_pass_hashes", {})])
    def test_unbound_or_hash_only_reports_are_rejected(self, receipt_tree, field, value):
        from red_line.release import finalize_render_pipeline

        root, report, path, custody = receipt_tree
        report[field] = value
        path.write_text(json.dumps(report))
        with pytest.raises(RuntimeError):
            finalize_render_pipeline(root, lambda: pytest.fail("pipeline must not run"), custody)

    @pytest.mark.parametrize("mutation", ["missing", "malformed", "shape", "receipt", "source", "artifact",
                                         "binding_schema", "binding_digest", "binding_source", "binding_artifacts"])
    def test_final_binding_detects_later_mutation(self, receipt_tree, mutation):
        from red_line.release import finalize_render_pipeline, render_binding_issues

        root, report, path, custody = receipt_tree
        finalize_render_pipeline(root, lambda: _clean_and_rebuild(root), custody)
        binding = root / "output/reports/render_comparison_binding.json"
        if mutation == "missing":
            binding.unlink()
        elif mutation == "malformed":
            binding.write_text("{")
        elif mutation == "shape":
            binding.write_text("[]")
        elif mutation == "receipt":
            path.write_bytes(path.read_bytes() + b"\n")
        elif mutation == "source":
            (root / "source.txt").write_text("changed")
        elif mutation.startswith("binding_"):
            payload = json.loads(binding.read_text())
            key = {"binding_schema": "schema", "binding_digest": "comparison_sha256",
                   "binding_source": "input_binding", "binding_artifacts": "artifact_hashes"}[mutation]
            payload[key] = None
            binding.write_text(json.dumps(payload))
        else:
            (root / PDF_KEY).write_bytes((root / PDF_KEY).read_bytes() + b"\n% changed\n")
        assert render_binding_issues(root, report)

    def test_metadata_only_pdf_variation_requires_available_equal_text(self, receipt_tree):
        from red_line.release import finalize_render_pipeline, render_binding_issues

        root, report, path, custody = receipt_tree
        def pipeline():
            _clean_and_rebuild(root)
            (root / PDF_KEY).write_bytes((root / PDF_KEY).read_bytes() + b"\n% metadata variation\n")
        if pdf_text(root / PDF_KEY) is None:
            with pytest.raises(RuntimeError, match="artifact"):
                finalize_render_pipeline(root, pipeline, custody)
        else:
            finalize_render_pipeline(root, pipeline, custody)
            assert render_binding_issues(root, report) == []

    def test_custody_must_be_outside_the_project(self, receipt_tree):
        from red_line.release import finalize_render_pipeline

        root, _, _, _ = receipt_tree
        with pytest.raises(ValueError, match="outside"):
            finalize_render_pipeline(root, lambda: None, root / "output/custody")

    def test_existing_custody_is_preserved(self, receipt_tree):
        from red_line.release import finalize_render_pipeline

        root, _, path, custody = receipt_tree
        custody.mkdir()
        held = custody / path.name
        held.write_text("existing")
        with pytest.raises(FileExistsError):
            finalize_render_pipeline(root, lambda: None, custody)
        assert held.read_text() == "existing"

    def test_changed_external_receipt_is_rejected(self, receipt_tree):
        from red_line.release import finalize_render_pipeline

        root, _, path, custody = receipt_tree
        def pipeline():
            _clean_and_rebuild(root)
            (custody / path.name).write_text("changed")
        with pytest.raises(RuntimeError, match="preserved receipt changed"):
            finalize_render_pipeline(root, pipeline, custody)


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
    def test_explicit_template_environment_is_separate(self, monkeypatch):
        from red_line.release.determinism import _template_environment

        monkeypatch.setenv("UV_PROJECT_ENVIRONMENT", "project-env")
        monkeypatch.setenv("RED_LINE_TEMPLATE_ENVIRONMENT", "renderer-env")
        assert _template_environment()["UV_PROJECT_ENVIRONMENT"] == "renderer-env"

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


class TestTreeDigest:
    def test_empty_tree_fails_instead_of_digesting_to_a_stable_value(self, tmp_path):
        with pytest.raises(RuntimeError, match="produced no files"):
            tree_digest(tmp_path)

    def test_identical_trees_digest_identically(self, tmp_path):
        _populated_tree(tmp_path)
        first = tree_digest(tmp_path)
        sibling = tmp_path / "sibling"
        sibling.mkdir()
        _populated_tree(sibling)
        assert tree_digest(sibling) == first

    def test_content_presence_and_name_changes_all_move_the_digest(self, tmp_path):
        _populated_tree(tmp_path)
        first = tree_digest(tmp_path)

        _artifact(tmp_path, "output/figures/plate.svg", "<svg/><!--changed-->")
        assert tree_digest(tmp_path) != first

        _artifact(tmp_path, "output/figures/extra.svg", "<svg/>")
        assert tree_digest(tmp_path) != first

        plate = tmp_path / "output" / "figures" / "plate.svg"
        plate.rename(plate.with_name("renamed.svg"))
        assert tree_digest(tmp_path) != first


class TestWheelSmoke:
    def test_missing_uv_fails_loudly_rather_than_silently_skipping(self, tmp_path, monkeypatch):
        empty_path_directory = tmp_path / "no-tools"
        empty_path_directory.mkdir()
        monkeypatch.setenv("PATH", str(empty_path_directory))

        with pytest.raises(RuntimeError, match="uv is required"):
            wheel_smoke(tmp_path)



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
    def test_full_pipeline_uses_the_current_core_mode_cli(self, tmp_path, monkeypatch):
        template_root = _template_checkout(tmp_path / "template")
        bin_directory = tmp_path / "bin"
        bin_directory.mkdir()
        recording_uv = bin_directory / "uv"
        log = tmp_path / "pipeline-invocation.txt"
        recording_uv.write_text(
            '#!/bin/sh\nprintf "%s\\n" "$*" > "$UV_INVOCATION_LOG"\n', encoding="utf-8"
        )
        recording_uv.chmod(0o755)
        monkeypatch.setenv("PATH", str(bin_directory))
        monkeypatch.setenv("RED_LINE_TEMPLATE_ROOT", str(template_root))
        monkeypatch.setenv("UV_INVOCATION_LOG", str(log))

        template_full_pipeline(tmp_path)()

        assert log.read_text().strip() == (
            "run python scripts/runner/execute_pipeline.py --project working/red_line --mode core"
        )

    def test_full_pipeline_requires_uv(self, tmp_path, monkeypatch):
        bin_directory = tmp_path / "bin"
        bin_directory.mkdir()
        monkeypatch.setenv("PATH", str(bin_directory))
        monkeypatch.setenv("RED_LINE_TEMPLATE_ROOT", str(_template_checkout(tmp_path / "template")))

        with pytest.raises(RuntimeError, match="uv is required"):
            template_full_pipeline(tmp_path)()

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
            '#!/bin/sh\nprintf "%s|%s\\n" "$PWD" "$*" >> "$UV_INVOCATION_LOG"\n'
            'printf "%s" "${UV_PROJECT_ENVIRONMENT-unset}" > "$UV_RENDER_ENV_LOG"\n', encoding="utf-8"
        )
        recording_uv.chmod(0o755)

        monkeypatch.setenv("PATH", str(bin_directory))
        monkeypatch.setenv("UV_INVOCATION_LOG", str(log))
        monkeypatch.setenv("RED_LINE_TEMPLATE_ROOT", str(template_root))
        monkeypatch.setenv("VIRTUAL_ENV", str(tmp_path / "should-not-leak"))
        monkeypatch.setenv("UV_PROJECT_ENVIRONMENT", str(tmp_path / "red-line-environment"))
        monkeypatch.setenv("UV_RENDER_ENV_LOG", str(tmp_path / "render-env.txt"))
        monkeypatch.delenv("RED_LINE_TEMPLATE_ENVIRONMENT", raising=False)

        template_render_passes(root)()
        assert (tmp_path / "render-env.txt").read_text() == "unset"

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

        assert result["schema_version"] == "2.0"
        assert result["render_pass_count"] == 0
        assert result["input_binding"]["source_revision"] is None
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
