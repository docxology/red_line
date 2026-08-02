"""Executable enforcement of the project's no-substitute rule.

Every ``AGENTS.md`` under `tests/` states the rule in prose: real package objects,
real ``tmp_path`` trees, real executables on ``PATH``, real subprocesses — no mocking
framework, and no name that describes a real thing as a stand-in. This module makes
that rule fail the suite instead of relying on review.

Two families are blocked. Mocking-framework tokens replace real behavior with
stand-ins. ``monkeypatch`` attribute and item replacement does the same thing by
hand. The ``monkeypatch.setenv`` and ``monkeypatch.delenv`` forms stay allowed:
isolating ``PATH`` or ``VIRTUAL_ENV`` is real isolation of a real process, not a
substitute for the code under test.

A third family blocks two retired branding words in Python sources: the one meaning
counterfeit and the one meaning superseded-but-kept. Both were just renamed out of
this tree — a recording executable written under ``tmp_path`` is real, and the
aggregate-only canary path is a supported protocol rule, not a leftover — and neither
label should come back. The blocked words are listed only as fragments below, so this
paragraph does not trip its own gate.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

# Each needle is assembled from fragments rather than written literally. That keeps
# this module out of its own results without a self-exclusion branch (which a later
# edit could widen into a hole), and it keeps a repository-wide grep for the blocked
# tokens at zero hits. Do not "simplify" these into literals.
SUBSTITUTE_TOKENS: tuple[tuple[tuple[str, ...], str, bool], ...] = (
    (
        ("unit", "test", ".", "mock"),
        "mocking framework replaces real package behavior with stand-ins",
        False,
    ),
    (
        ("from unit", "test import ", "mock"),
        "mocking framework replaces real package behavior with stand-ins",
        False,
    ),
    (
        ("Magic", "Mock"),
        "mocking framework replaces real package behavior with stand-ins",
        False,
    ),
    (
        ("mocker", ".", "patch"),
        "mocking framework replaces real package behavior with stand-ins",
        False,
    ),
    (
        ("mock", ".", "patch"),
        "mocking framework replaces real package behavior with stand-ins",
        False,
    ),
    (
        ("monkeypatch", ".", "setattr"),
        "attribute replacement swaps a real dependency for a stand-in",
        False,
    ),
    (
        ("monkeypatch", ".", "delattr"),
        "attribute replacement swaps a real dependency for a stand-in",
        False,
    ),
    (
        ("monkeypatch", ".", "setitem"),
        "item replacement swaps a real dependency for a stand-in",
        False,
    ),
    (
        ("monkeypatch", ".", "delitem"),
        "item replacement swaps a real dependency for a stand-in",
        False,
    ),
    (
        ("fa", "ke"),
        "retired substitute branding must not return to source names",
        True,
    ),
    (
        ("le", "gacy"),
        "retired substitute branding must not return to source names",
        True,
    ),
)

NEEDLES: tuple[tuple[re.Pattern[str], str], ...] = tuple(
    (re.compile(re.escape("".join(fragments)), re.IGNORECASE if ignore_case else 0), reason)
    for fragments, reason, ignore_case in SUBSTITUTE_TOKENS
)

SKIPPED_DIRECTORIES = frozenset({"__pycache__", ".venv", "build", "output"})

SOURCE_ROOTS = ("src", "tests", "scripts")


def substitute_hits(root: Path) -> list[tuple[Path, int, str, str]]:
    """Return every blocked token found in the Python sources under ``root``.

    Each hit is ``(path, line_number, matched_text, reason)``, sorted by path then
    line then text so a failure names all offending sites at once. Generated and
    vendored directories are skipped; non-Python files are ignored, because the
    documentation legitimately quotes these token names while stating the rule.
    A file that cannot be decoded as UTF-8 raises rather than passing silently.
    """

    hits: list[tuple[Path, int, str, str]] = []
    for path in root.rglob("*.py"):
        directories = path.relative_to(root).parts[:-1]
        if any(part in SKIPPED_DIRECTORIES or part.startswith(".") for part in directories):
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for needle, reason in NEEDLES:
                for match in needle.finditer(line):
                    hits.append((path, line_number, match.group(0), reason))
    return sorted(hits, key=lambda hit: (str(hit[0]), hit[1], hit[2]))


def test_project_sources_contain_no_substitute_markers() -> None:
    project_root = Path(__file__).resolve().parent.parent
    hits = sorted(
        (hit for name in SOURCE_ROOTS for hit in substitute_hits(project_root / name)),
        key=lambda hit: (str(hit[0]), hit[1], hit[2]),
    )

    assert not hits, "blocked substitute markers found:\n" + "\n".join(
        f"{path.relative_to(project_root)}:{line_number} — {token} ({reason})"
        for path, line_number, token, reason in hits
    )


@pytest.mark.parametrize(
    ("fragments", "reason", "ignore_case"),
    SUBSTITUTE_TOKENS,
    ids=["".join(fragments) for fragments, _reason, _ignore_case in SUBSTITUTE_TOKENS],
)
def test_every_blocked_token_is_detected_where_it_is_planted(
    tmp_path: Path, fragments: tuple[str, ...], reason: str, ignore_case: bool
) -> None:
    """Each table entry is proven detectable, so a new entry cannot ship unexercised."""

    planted = "".join(fragments)
    if ignore_case:
        planted = planted.upper()
    target = tmp_path / "pkg" / "probe.py"
    target.parent.mkdir()
    target.write_text(f'"""planted marker"""\nvalue = "{planted}"\n', encoding="utf-8")

    assert substitute_hits(tmp_path) == [(target, 2, planted, reason)]


def test_allowed_environment_isolation_and_prose_are_not_flagged(tmp_path: Path) -> None:
    target = tmp_path / "pkg" / "clean.py"
    target.parent.mkdir()
    target.write_text(
        '"""Prose may say no mocks; the setenv form is real environment isolation."""\n'
        'monkeypatch.setenv("PATH", "/usr/bin")\n'
        'monkeypatch.delenv("VIRTUAL_ENV", raising=False)\n',
        encoding="utf-8",
    )

    assert substitute_hits(tmp_path) == []


def test_generated_directories_are_skipped(tmp_path: Path) -> None:
    token = "".join(SUBSTITUTE_TOKENS[0][0])
    target = tmp_path / "__pycache__" / "probe.py"
    target.parent.mkdir()
    target.write_text(f'value = "{token}"\n', encoding="utf-8")

    assert substitute_hits(tmp_path) == []


def test_non_python_files_are_not_scanned(tmp_path: Path) -> None:
    token = "".join(SUBSTITUTE_TOKENS[0][0])
    target = tmp_path / "docs" / "notes.md"
    target.parent.mkdir()
    target.write_text(token, encoding="utf-8")

    assert substitute_hits(tmp_path) == []


def test_every_offending_site_is_reported_not_just_the_first(tmp_path: Path) -> None:
    first, second = "".join(SUBSTITUTE_TOKENS[5][0]), "".join(SUBSTITUTE_TOKENS[2][0])
    target = tmp_path / "probe.py"
    target.write_text(f'a = "{first}"\nb = "{second}"\nc = "{second}"\n', encoding="utf-8")

    assert [(hit[1], hit[2]) for hit in substitute_hits(tmp_path)] == [
        (1, first),
        (2, second),
        (3, second),
    ]
