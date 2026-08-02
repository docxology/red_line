#!/usr/bin/env python3
"""Run the project-local quality and release-preflight gates."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent


def _run(command: list[str], *, cwd: Path = ROOT, env: dict[str, str] | None = None) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=cwd, env=env, check=True)


def _tree_digest(path: Path) -> str:
    digest = hashlib.sha256()
    files = [child for child in sorted(path.rglob("*")) if child.is_file()]
    if not files:
        raise RuntimeError(f"figure generation produced no files in {path}")
    for child in files:
        digest.update(str(child.relative_to(path)).encode())
        digest.update(child.read_bytes())
    return digest.hexdigest()


def _wheel_smoke() -> None:
    uv = shutil.which("uv")
    if uv is None:
        raise RuntimeError("uv is required for the wheel build gate")
    with tempfile.TemporaryDirectory(prefix="red-line-quality-") as temp:
        dist = Path(temp) / "dist"
        _run([uv, "build", "--wheel", "--out-dir", str(dist)])
        wheel = next(dist.glob("*.whl"))
        venv = Path(temp) / "venv"
        _run([sys.executable, "-m", "venv", str(venv)])
        python = venv / "bin" / "python"
        if not python.exists():
            python = venv / "Scripts" / "python.exe"
        _run([str(python), "-m", "pip", "install", "--no-deps", str(wheel)])
        _run(
            [
                str(python),
                "-c",
                "import red_line; assert red_line.__version__; assert red_line.PERSONAL_RED_LINES",
            ]
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Red Line's full local quality gate.")
    parser.add_argument("--as-of", default=None, help="explicit canary date for deterministic verification")
    parser.add_argument(
        "--render",
        action="store_true",
        help="run the canonical PDF/HTML/figure render comparison",
    )
    args = parser.parse_args(argv)
    python = sys.executable
    figure_command = [python, "scripts/build_figures.py"]
    # Figure-dependent tests validate generated bindings. Build ignored,
    # reproducible figures before pytest so the gate is self-sufficient from a
    # clean checkout rather than depending on a developer's prior output tree.
    _run(figure_command)
    _run([python, "scripts/validate_visual_bindings.py"])
    _run([python, "-m", "ruff", "check", "."])
    _run([python, "-m", "pytest", "tests/", "--cov=red_line", "--cov-fail-under=90"])
    _run([python, "scripts/validate_source_claims.py"])
    _run([python, "scripts/validate_claim_register.py"])
    _run([python, "scripts/validate_proposed_red_lines.py"])
    _run([python, "scripts/validate_release_bindings.py"])
    canary_command = [python, "scripts/check_canary.py"]
    if args.as_of:
        canary_command.extend(["--as-of", args.as_of])
    _run(canary_command)
    first = _tree_digest(ROOT / "output" / "figures")
    _run(figure_command)
    second = _tree_digest(ROOT / "output" / "figures")
    if first != second:
        raise RuntimeError("figure generation is not byte deterministic")
    _wheel_smoke()
    if args.render:
        _run([python, "scripts/compare_render_artifacts.py"])
        # The comparison's render-only passes rewrite artifacts AFTER the
        # engine's artifact manifest was captured, and the engine's PDF is
        # not byte-stable, so the engine's own validation now reports drift.
        # Run the engine's full core pipeline as the final tree-producing
        # step: it regenerates the manifest alongside the artifacts and
        # leaves a validation verdict about the tree it actually produced.
        # Only then is the strict release manifest reading a coherent tree.
        # Measured 2026-07-29: with the old order (compare -> strict) the
        # gate failed at its own last step from every starting state.
        from red_line.release import template_full_pipeline

        print("+ engine full core pipeline (final tree-producing step)")
        template_full_pipeline(ROOT)()
        manifest_command = [python, "scripts/build_release_manifest.py", "--strict"]
        if args.as_of:
            manifest_command.extend(["--as-of", args.as_of])
        _run(manifest_command)
    print("quality gate: passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
