"""Every ``scripts/`` entrypoint must fail closed on an argument it does not know.

A thin orchestrator that accepts an unrecognized flag in silence and still
prints its pass line is a gate that cannot fail: a typo inside a release script
(``--as-off`` for ``--as-of``, ``--strct`` for ``--strict``) reads as success.
Six scripts were in exactly that state — ``build_figures.py`` and the five
``validate_*.py`` wrappers parsed no arguments at all — and ``check_canary.py``
was worse: it parsed a hard-coded empty list whenever ``argv`` was ``None``,
which is the ``__main__`` path, so its ``--prior`` and ``--as-of`` flags were
accepted and discarded by the real command line.

These tests run each script the way a shell does — a real subprocess, real
``sys.argv`` — because that is the path that was broken while every in-process
call with an explicit argument list already worked.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

#: Every executable entrypoint in ``scripts/``. Derived from disk rather than
#: listed by hand so a new script joins the gate instead of dodging it.
SCRIPT_NAMES = tuple(sorted(path.name for path in SCRIPTS.glob("*.py") if not path.name.startswith("_")))

#: Scripts whose happy path is read-only, fast, and needs no rendered artifacts,
#: so the good-input half of the contract can be asserted here too.
READ_ONLY_SCRIPTS = (
    "check_canary.py",
    "validate_claim_register.py",
    "validate_proposed_red_lines.py",
    "validate_release_bindings.py",
    "validate_source_claims.py",
    "validate_visual_bindings.py",
)


def _run(*arguments: str) -> subprocess.CompletedProcess[str]:
    """Invoke a script as a real subprocess, exactly as a shell would."""

    return subprocess.run(
        [sys.executable, str(SCRIPTS / arguments[0]), *arguments[1:]],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )


def test_the_script_inventory_is_not_empty() -> None:
    """A parametrization over an empty scan set would certify nothing."""

    assert len(SCRIPT_NAMES) >= 11
    assert "check_canary.py" in SCRIPT_NAMES
    assert all((SCRIPTS / name).is_file() for name in SCRIPT_NAMES)


@pytest.mark.parametrize("script", SCRIPT_NAMES)
def test_every_script_rejects_an_unknown_flag(script: str) -> None:
    """An unrecognized option must exit non-zero and say so on stderr."""

    result = _run(script, "--definitely-not-a-real-flag")

    assert result.returncode != 0, f"{script} accepted an unknown flag and exited 0"
    assert "unrecognized arguments" in result.stderr or "invalid" in result.stderr


@pytest.mark.parametrize("script", SCRIPT_NAMES)
def test_every_script_rejects_a_garbage_positional(script: str) -> None:
    """A stray positional must exit non-zero, never be ignored into a pass."""

    result = _run(script, "GARBAGE_POSITIONAL_ARGUMENT")

    assert result.returncode != 0, f"{script} accepted a garbage positional and exited 0"


@pytest.mark.parametrize("script", READ_ONLY_SCRIPTS)
def test_every_read_only_script_still_passes_on_good_input(script: str) -> None:
    """Fail-closed on garbage is only meaningful if good input still passes."""

    result = _run(script)

    assert result.returncode == 0, f"{script} failed on good input: {result.stderr}"
    assert result.stdout.strip()


@pytest.mark.parametrize("script", SCRIPT_NAMES)
def test_every_script_answers_help_without_running(script: str) -> None:
    """``--help`` proves a parser exists at all, which is what was missing."""

    result = _run(script, "--help")

    assert result.returncode == 0, script
    assert "usage:" in result.stdout


# --------------------------------------------------------------------------
# check_canary.py's flags were accepted and discarded. Assert they are live —
# a flag that changes nothing is indistinguishable from no flag at all.
# --------------------------------------------------------------------------


def test_check_canary_as_of_reaches_the_freshness_check() -> None:
    """A far-future review date must make the attestation read as stale.

    If ``--as-of`` were discarded again this call would evaluate against today
    and exit 0, so this is the assertion that pins the flag to behaviour rather
    than to a help string.
    """

    stale = _run("check_canary.py", "--as-of", "2099-01-01")
    fresh = _run("check_canary.py", "--as-of", "2026-07-15")

    assert stale.returncode == 1, stale.stdout
    assert "stale" in stale.stdout.lower()
    assert fresh.returncode == 0, fresh.stdout
    assert "intact" in fresh.stdout


def test_check_canary_rejects_an_invalid_as_of_date() -> None:
    result = _run("check_canary.py", "--as-of", "not-a-date")

    assert result.returncode == 2
    assert "invalid ISO date" in result.stderr


def test_check_canary_prior_flag_reaches_the_file_read(tmp_path: Path) -> None:
    """``--prior`` must select the file actually read, and fail on a bad one."""

    absent = _run("check_canary.py", "--prior", str(tmp_path / "absent.json"))

    assert absent.returncode == 1
    assert "canary metadata invalid" in absent.stdout


def test_check_canary_prior_flag_accepts_a_real_alternate_copy(tmp_path: Path) -> None:
    """The same committed payload at a different path still verifies."""

    committed = ROOT / "tests" / "fixtures" / "canary_committed.json"
    copy = tmp_path / "elsewhere.json"
    copy.write_text(committed.read_text(encoding="utf-8"), encoding="utf-8")

    result = _run("check_canary.py", "--prior", str(copy), "--as-of", "2026-07-15")

    assert result.returncode == 0, result.stdout
    assert "intact" in result.stdout


def test_check_canary_detects_a_drifted_prior_digest(tmp_path: Path) -> None:
    """Proof the exit code can go red on content, not only on arguments."""

    committed = json.loads((ROOT / "tests" / "fixtures" / "canary_committed.json").read_text())
    committed["registry_digest"] = "0" * 64
    drifted = tmp_path / "drifted.json"
    drifted.write_text(json.dumps(committed), encoding="utf-8")

    result = _run("check_canary.py", "--prior", str(drifted), "--as-of", "2026-07-15")

    assert result.returncode == 1
    assert "intact" not in result.stdout


def test_render_comparison_names_the_absent_toolchain_instead_of_raising(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The one script that needs the external engine must say so, not traceback.

    Run from a copy of this project with no template checkout above it — which
    is what a standalone clone is — the script previously died with an
    unhandled exception after the old resolver handed it a directory that had
    never existed. It now reports the missing dependency and the flag that
    works without it.
    """

    monkeypatch.delenv("RED_LINE_TEMPLATE_ROOT", raising=False)
    copy = tmp_path / "red_line"
    copy.mkdir()
    (copy / "scripts").mkdir()
    for name in ("__init__.py", "compare_render_artifacts.py"):
        (copy / "scripts" / name).write_text(
            (SCRIPTS / name).read_text(encoding="utf-8"), encoding="utf-8"
        )

    result = subprocess.run(
        [sys.executable, str(copy / "scripts" / "compare_render_artifacts.py")],
        cwd=str(copy),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert result.stderr == "", f"unhandled failure: {result.stderr}"
    assert "RED_LINE_TEMPLATE_ROOT" in result.stdout
    assert "https://github.com/docxology/template" in result.stdout
    assert "--hash-only" in result.stdout
