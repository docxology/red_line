"""Source and artifact provenance primitives shared by release assembly."""

from __future__ import annotations

from collections.abc import Collection, Iterable
import hashlib
import os
from pathlib import Path
import subprocess

TEMPLATE_ROOT_ENV = "RED_LINE_TEMPLATE_ROOT"

#: The stage script this project actually invokes. A directory is only accepted
#: as the render toolchain when it carries this file, so a directory that merely
#: happens to be named ``template`` is never mistaken for the engine.
TEMPLATE_ROOT_MARKER = Path("scripts") / "pipeline" / "stage_03_render.py"


class TemplateRootUnavailable(RuntimeError):
    """Raised when the external render toolchain cannot be located."""


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of one file, read in bounded chunks."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_revision(path: Path) -> str | None:
    """Return the checked-out revision, or ``None`` when it cannot be read."""

    try:
        return subprocess.run(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def git_dirty(path: Path) -> bool | None:
    """Report whether the checkout has uncommitted changes, or ``None`` when unknown."""

    try:
        return bool(
            subprocess.run(
                ["git", "-C", str(path), "status", "--porcelain", "--", "."],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
        )
    except (OSError, subprocess.CalledProcessError):
        return None


def template_root_candidates(root: Path) -> tuple[Path, ...]:
    """Ancestor-relative locations searched for a template checkout.

    The old default was ``root.parents[2] / "template"``: the exact shape of the
    author's private monorepo, three levels above this project. Outside that
    layout it named a directory that has never existed, so the manifest recorded
    a null renderer revision and the render invocation ran with a ``cwd`` that
    was not there. Searching every ancestor for a directory that actually
    carries the stage script keeps the historical location working when it is
    real and stops asserting it when it is not.
    """

    resolved = root.expanduser().resolve()
    return tuple(ancestor / "template" for ancestor in resolved.parents)


def find_template_root(root: Path) -> Path | None:
    """Locate the external render toolchain, or report that there is none.

    ``RED_LINE_TEMPLATE_ROOT`` is an explicit statement by the operator and is
    honoured verbatim — it is taken as given, not re-validated, so a checkout
    laid out differently is still usable. Without it the ancestors of ``root``
    are searched for a directory carrying :data:`TEMPLATE_ROOT_MARKER`.
    """

    configured = os.environ.get(TEMPLATE_ROOT_ENV)
    if configured:
        return Path(configured).expanduser().resolve()
    for candidate in template_root_candidates(root):
        if (candidate / TEMPLATE_ROOT_MARKER).is_file():
            return candidate
    return None


def require_template_root(root: Path) -> Path:
    """Return the render toolchain path, or fail naming what is missing."""

    found = find_template_root(root)
    if found is not None:
        return found
    searched = ", ".join(str(candidate) for candidate in template_root_candidates(root))
    raise TemplateRootUnavailable(
        "the external render toolchain is not available: no checkout carrying "
        f"{TEMPLATE_ROOT_MARKER} was found. Clone https://github.com/docxology/template "
        f"anywhere and set {TEMPLATE_ROOT_ENV} to it, or place it at one of: {searched}. "
        "Rendering is the only part of this project that needs it; the test suite, "
        "the figure build, and every script under scripts/ run without it."
    )


def digest_tree(
    root: Path,
    directory: str,
    suffixes: Iterable[str],
    *,
    exclude_names: Collection[str] = (),
) -> dict[str, str]:
    """Digest every matching file under one directory, keyed by root-relative path."""

    base = root / directory
    if not base.exists():
        return {}
    accepted = frozenset(suffixes)
    return {
        str(path.relative_to(root)): sha256_file(path)
        for path in sorted(base.rglob("*"))
        if path.is_file() and path.suffix.lower() in accepted and path.name not in exclude_names
    }
