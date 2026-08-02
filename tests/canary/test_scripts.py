"""Tests for the canary build/check orchestrators (no mocks; real subprocess).

Covers A5 (build_canary.py: today-default date, ISO validation, --json fixture
parity) and A6 (check_canary.py: verify the committed canary, real exit code).
"""

from __future__ import annotations

import subprocess
import sys
from datetime import date
from pathlib import Path

from scripts import build_canary, check_canary

ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = ROOT / "scripts"
FIXTURE = ROOT / "tests" / "fixtures" / "canary_committed.json"


# --------------------------------------------------------------------------- #
# A5: build_canary.py
# --------------------------------------------------------------------------- #


def test_build_canary_no_date_uses_today(capsys):
    rc = build_canary.main(["build_canary.py"])
    assert rc == 0
    out = capsys.readouterr().out
    issued_line = next(ln for ln in out.splitlines() if ln.startswith("issued_on:"))
    issued = issued_line.split("issued_on:", 1)[1].strip()
    # Must be a real, parseable ISO date — never a placeholder.
    assert issued != "unspecified-date"
    assert date.fromisoformat(issued) == date.today()


def test_build_canary_explicit_valid_date(capsys):
    rc = build_canary.main(["build_canary.py", "2026-07-15"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "issued_on: 2026-07-15" in out


def test_build_canary_invalid_date_exits_2(capsys):
    rc = build_canary.main(["build_canary.py", "not-a-date"])
    assert rc == 2
    err = capsys.readouterr().err
    assert "invalid ISO date" in err


def test_build_canary_json_is_byte_identical_to_fixture(capsys):
    rc = build_canary.main(["build_canary.py", "2026-07-15", "--json"])
    assert rc == 0
    out = capsys.readouterr().out
    assert out == FIXTURE.read_text(encoding="utf-8")


def test_build_canary_no_prior_bypasses_guard(capsys):
    rc = build_canary.main(["build_canary.py", "2026-07-15", "--no-prior"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "registry_sha256:" in out


def test_build_canary_missing_default_prior_falls_through(tmp_path, capsys):
    # When the default committed prior is absent (and none is passed), the guard
    # is simply not applied.
    original = build_canary.COMMITTED_PRIOR
    build_canary.COMMITTED_PRIOR = tmp_path / "absent.json"
    try:
        rc = build_canary.main(["build_canary.py", "2026-07-15"])
    finally:
        build_canary.COMMITTED_PRIOR = original
    assert rc == 0
    out = capsys.readouterr().out
    assert "registry_sha256:" in out


def test_build_canary_explicit_prior_with_rationale_on_drift(tmp_path, capsys):
    # A prior with a mismatched digest forces drift; --rationale emits a successor.
    prior = tmp_path / "prior.json"
    prior.write_text(
        '{"statement": "old", "issued_on": "2026-01-01", '
        '"registry_digest": "' + ("0" * 64) + '", "line_ids": []}',
        encoding="utf-8",
    )
    rc = build_canary.main(
        [
            "build_canary.py",
            "2026-08-01",
            "--prior",
            str(prior),
            "--rationale",
            "documented drift",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "Supersedes canary 00000000" in out
    assert "Rationale: documented drift" in out


# --------------------------------------------------------------------------- #
# A6: check_canary.py
# --------------------------------------------------------------------------- #


def test_check_canary_in_process_intact(capsys):
    rc = check_canary.main([])
    assert rc == 0
    out = capsys.readouterr().out
    assert "intact" in out


def test_check_canary_subprocess_exit_0_on_real_fixture():
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "check_canary.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "intact" in result.stdout
