"""Two-pass artifact comparison establishing render determinism for a local toolchain."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import subprocess

from .provenance import digest_tree, find_template_root, git_revision, require_template_root
from .snapshot import write_snapshot

ARTIFACT_DIRECTORIES = ("pdf", "web", "figures")
ARTIFACT_SUFFIXES = frozenset({".html", ".json", ".pdf", ".png", ".svg"})
RENDER_STAGES = (
    "scripts/pipeline/stage_03_render.py",
    "scripts/pipeline/stage_04_validate.py",
)
RENDER_COMMAND = (
    "uv run python scripts/pipeline/stage_03_render.py "
    "--project working/red_line; "
    "uv run python scripts/pipeline/stage_04_validate.py "
    "--project working/red_line"
)


def artifact_hashes(root: Path) -> dict[str, str]:
    """Digest every comparable rendered artifact under the output tree."""

    hashes: dict[str, str] = {}
    for directory in ARTIFACT_DIRECTORIES:
        hashes.update(digest_tree(root, f"output/{directory}", ARTIFACT_SUFFIXES))
    return hashes


def pdf_text(path: Path) -> str | None:
    """Extract laid-out PDF text, or ``None`` when extraction is unavailable."""

    try:
        return subprocess.run(
            ["pdftotext", "-layout", str(path), "-"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return None


def pdf_texts_equal(
    first: dict[str, str | None], second: dict[str, str | None], pdf_paths: list[str]
) -> bool:
    """Report whether both passes extracted identical text for every expected PDF."""

    if not pdf_paths or set(first) != set(pdf_paths) or set(second) != set(pdf_paths):
        return False
    if any(first[path] is None or second[path] is None for path in pdf_paths):
        return False
    return first == second


def classify_nondeterminism(*, byte_identical: bool, non_pdf_equal: bool, pdf_text_equal: bool) -> list[str]:
    """Name the artifact drift observed between two passes, if any."""

    if byte_identical:
        return []
    if non_pdf_equal and pdf_text_equal:
        return ["PDF metadata (CreationDate and document ID)"]
    return ["unclassified artifact bytes"]


def template_render_passes(root: Path) -> Callable[[], None]:
    """Build the callable that runs one canonical render pass in the sibling template."""

    # A render genuinely cannot proceed without the external engine, so this is
    # the one caller that must fail rather than degrade — and it fails here,
    # naming what is missing, instead of handing ``subprocess`` a ``cwd`` that
    # does not exist.
    template_root = require_template_root(root)

    def run_render() -> None:
        uv = shutil.which("uv")
        if uv is None:
            raise RuntimeError("uv is required for the canonical render comparison")
        write_snapshot(root)
        # The project gate runs from the sidecar's virtualenv, while the canonical
        # renderer belongs to the sibling template checkout. Do not let the parent
        # VIRTUAL_ENV make nested ``uv run`` resolve the wrong project environment.
        render_env = os.environ.copy()
        render_env.pop("VIRTUAL_ENV", None)
        for script in RENDER_STAGES:
            subprocess.run(
                [uv, "run", "python", script, "--project", "working/red_line"],
                cwd=template_root,
                env=render_env,
                check=True,
            )

    return run_render


def template_full_pipeline(root: Path) -> Callable[[], None]:  # pragma: no cover
    """Build the callable that runs the engine's full core pipeline once.

    The render-only passes of :func:`template_render_passes` rewrite the PDF
    after the engine's artifact manifest was captured, and the engine's PDF
    is not byte-stable, so any render-only re-run leaves the engine's own
    output validation reporting artifact-manifest drift. The full core
    pipeline is the engine's one tree-producing entrypoint that ends
    coherent: it regenerates the artifact manifest alongside the artifacts
    and leaves ``output/reports/validation_report.json`` with a verdict
    about the tree it actually produced. The strict release manifest must
    therefore run after THIS, not after a bare render.
    """

    template_root = require_template_root(root)

    def run_pipeline() -> None:
        uv = shutil.which("uv")
        if uv is None:
            raise RuntimeError("uv is required for the canonical engine pipeline")
        pipeline_env = os.environ.copy()
        pipeline_env.pop("VIRTUAL_ENV", None)
        subprocess.run(
            [
                uv,
                "run",
                "python",
                "scripts/runner/execute_pipeline.py",
                "--project",
                "working/red_line",
                "--core-only",
            ],
            cwd=template_root,
            env=pipeline_env,
            check=True,
        )

    return run_pipeline


def compare_artifacts(root: Path, *, render: Callable[[], None] | None = None) -> dict:
    """Compare two artifact passes for content-identical render output.

    When ``render`` is supplied it runs before each hashing pass. When it is
    ``None`` the current artifact tree is hashed twice without re-rendering.
    """

    if render is not None:
        render()
    first = artifact_hashes(root)
    first_pdf_text = {key: pdf_text(root / key) for key in first if key.endswith(".pdf")}
    if render is not None:
        render()
    second = artifact_hashes(root)
    byte_identical = first == second and bool(first)
    non_pdf_equal = {key: value for key, value in first.items() if not key.endswith(".pdf")} == {
        key: value for key, value in second.items() if not key.endswith(".pdf")
    }
    pdf_paths = sorted(key for key in first if key.endswith(".pdf"))
    second_pdf_text = {key: pdf_text(root / key) for key in second if key.endswith(".pdf")}
    text_equal = pdf_texts_equal(first_pdf_text, second_pdf_text, pdf_paths)
    content_identical = byte_identical or (non_pdf_equal and text_equal)
    nondeterminism_scope = classify_nondeterminism(
        byte_identical=byte_identical,
        non_pdf_equal=non_pdf_equal,
        pdf_text_equal=text_equal,
    )
    # Reporting, not rendering: a comparison of an already-built tree is
    # meaningful with no engine present, and the report says so with ``None``.
    template_root = find_template_root(root)
    return {
        "schema_version": "1.0",
        "comparison_scope": list(ARTIFACT_DIRECTORIES),
        "artifact_suffixes": sorted(ARTIFACT_SUFFIXES),
        "first_pass_hashes": first,
        "second_pass_hashes": second,
        "identical": content_identical,
        "byte_identical": byte_identical,
        "nondeterminism": {
            "present": not byte_identical,
            "scope": nondeterminism_scope,
            "pdf_text_equal": text_equal,
        },
        "renderer": {
            "command": RENDER_COMMAND,
            "template_revision": None if template_root is None else git_revision(template_root),
            "template_root": None if template_root is None else str(template_root),
        },
        "rendered_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "trust_boundary": (
            "Two local passes establish artifact determinism for the recorded toolchain; "
            "they do not establish hermetic build security, independent truth, or external certification."
        ),
    }
