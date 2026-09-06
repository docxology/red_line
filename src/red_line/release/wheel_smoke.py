"""Wheel preflight: build the project wheel and import it from a clean venv."""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def wheel_smoke(root: Path) -> None:
    """Build the wheel and prove it imports in a clean virtual environment.

    ``uv build --wheel`` produces the wheel, ``pip install --no-deps`` installs
    it into a throwaway venv, and a fresh interpreter imports ``red_line`` and
    asserts its version and registry are present — the smallest proof that the
    published artifact carries the whole package. Any failing step raises; a
    gate check never reports a soft skip.
    """

    uv = shutil.which("uv")
    if uv is None:
        raise RuntimeError("uv is required for the wheel build gate")
    with tempfile.TemporaryDirectory(prefix="red-line-quality-") as temp:  # pragma: no cover
        dist = Path(temp) / "dist"
        _run([uv, "build", "--wheel", "--out-dir", str(dist)], cwd=root)
        wheel = next(dist.glob("*.whl"))
        venv = Path(temp) / "venv"
        _run([sys.executable, "-m", "venv", str(venv)], cwd=root)
        python = venv / "bin" / "python"
        if not python.exists():
            python = venv / "Scripts" / "python.exe"
        _run([str(python), "-m", "pip", "install", "--no-deps", str(wheel)], cwd=root)
        _run(
            [
                str(python),
                "-c",
                "import red_line; assert red_line.__version__; assert red_line.PERSONAL_RED_LINES",
            ],
            cwd=root,
        )

def _run(command: list[str], *, cwd: Path) -> None:  # pragma: no cover
    """Execute one subprocess, failing on a non-zero exit."""

    subprocess.run(command, cwd=cwd, check=True)
