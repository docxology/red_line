"""Bind the per-folder test inventories to what pytest actually collects.

Every folder under ``tests/`` carries an ``AGENTS.md`` and a ``README.md`` with
a module table and a "Collected tests" column, and ``tests/README.md`` carries a
mermaid map of the same numbers. All of it was hand-maintained, so adding a
module left the tables both undercounted and missing a row — the reader's map of
the suite silently stopped matching the suite.

These tests recompute the tables from a real collection run. They assert two
things a count alone cannot: that every documented module exists and its number
is right, and that every module on disk is documented, so a new file cannot be
added without appearing in the map.

The collection runs as a subprocess with ``-o addopts=""`` because the project's
``addopts`` forces ``-v``, whose tree output has no ``path::name`` lines to
count. Parsing zero lines would make this whole module vacuous, so the parsed
total is asserted against the number pytest prints for itself.
"""

from __future__ import annotations

import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"

_MODULE_ROW_RE = re.compile(r"^\| \[([A-Za-z0-9_./-]+\.py)\]\([^)]*\) \|.*\| (\d+) \|$", re.M)
_FOLDER_ROW_RE = re.compile(r"^\| \[([A-Za-z0-9_./-]*/)\]\([^)]*\) \|.*\| (\d+) \|$", re.M)
_AREA_ROW_RE = re.compile(r"^\| [a-z-]+ \| \[tests(?:/([a-z]+))?\]\([^)]*\) \| (\d+) \|", re.M)
_MERMAID_ROOT_RE = re.compile(r'root\["tests/ (\d+) collected"\]')
_MERMAID_TOP_RE = re.compile(r'top\["top-level modules (\d+)"\]')
_MERMAID_DIR_RE = re.compile(r'^  [a-z]+\["([a-z]+)/ (\d+)"\]$', re.M)
_SUITE_SIZE_RE = re.compile(r"with `(\d+)` passed tests on")


@pytest.fixture(scope="module")
def collected() -> Counter:
    """Per-file collected-test counts, measured by a real pytest collection."""

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/",
            "--collect-only",
            "-q",
            "-p",
            "no:cacheprovider",
            "-o",
            "addopts=",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    counts = Counter(line.split("::")[0] for line in result.stdout.splitlines() if "::" in line)
    reported = re.search(r"(\d+) tests collected", result.stdout)

    assert counts, "collection produced no `path::name` lines; this gate would be vacuous"
    assert reported is not None, "pytest did not report a collected total"
    assert sum(counts.values()) == int(reported.group(1))
    return counts


def _docs() -> list[Path]:
    return sorted(TESTS.rglob("AGENTS.md")) + sorted(TESTS.rglob("README.md"))


def test_the_documentation_set_being_checked_is_not_empty() -> None:
    assert len(_docs()) >= 20


@pytest.mark.parametrize("doc", _docs(), ids=lambda path: str(path.relative_to(ROOT)))
def test_every_documented_module_count_matches_collection(doc: Path, collected: Counter) -> None:
    """Each ``| [module.py](module.py) | … | N |`` row states the real N."""

    for name, stated in _MODULE_ROW_RE.findall(doc.read_text(encoding="utf-8")):
        target = (doc.parent / name).resolve().relative_to(ROOT).as_posix()
        assert target in collected, f"{doc.name} documents {target}, which collects nothing"
        assert int(stated) == collected[target], target


@pytest.mark.parametrize("doc", _docs(), ids=lambda path: str(path.relative_to(ROOT)))
def test_every_documented_folder_count_matches_collection(doc: Path, collected: Counter) -> None:
    """Folder rows are the sum over their directory, recomputed here."""

    for name, stated in _FOLDER_ROW_RE.findall(doc.read_text(encoding="utf-8")):
        prefix = (doc.parent / name).resolve().relative_to(ROOT).as_posix().rstrip("/") + "/"
        expected = sum(count for path, count in collected.items() if path.startswith(prefix))
        assert int(stated) == expected, f"{doc}: {prefix}"


def test_every_test_module_on_disk_is_documented_in_its_folder(collected: Counter) -> None:
    """A new module must appear in the map, not merely run.

    This is the half a count check cannot do: an undocumented file makes every
    stated number correct and the map wrong.
    """

    for directory in sorted({TESTS, *(path.parent for path in TESTS.rglob("test_*.py"))}):
        modules = {path.name for path in directory.glob("test_*.py")}
        if not modules:
            continue
        complete = 0
        for doc_name in ("AGENTS.md", "README.md"):
            doc = directory / doc_name
            if not doc.is_file():
                continue
            documented = {name for name, _ in _MODULE_ROW_RE.findall(doc.read_text(encoding="utf-8"))}
            if not documented:
                # `tests/README.md` maps the suite by folder rather than by
                # module; a doc that carries no module table is not required to
                # grow one. A doc that carries a partial one is a defect.
                continue
            assert modules <= documented, (
                f"{doc.relative_to(ROOT)} omits {sorted(modules - documented)}"
            )
            complete += 1
        assert complete >= 1, f"no doc in {directory.relative_to(ROOT)} lists its test modules"


def test_the_suite_map_in_tests_readme_matches_collection(collected: Counter) -> None:
    """The mermaid map and the area table carry the same measured numbers."""

    body = (TESTS / "README.md").read_text(encoding="utf-8")
    total = sum(collected.values())
    top_level = sum(count for path, count in collected.items() if path.count("/") == 1)

    assert int(_MERMAID_ROOT_RE.search(body).group(1)) == total
    assert int(_MERMAID_TOP_RE.search(body).group(1)) == top_level
    directories = _MERMAID_DIR_RE.findall(body)
    assert directories, "the mermaid map lists no directories"
    for name, stated in directories:
        expected = sum(
            count for path, count in collected.items() if path.startswith(f"tests/{name}/")
        )
        assert int(stated) == expected, name

    areas = _AREA_ROW_RE.findall(body)
    assert areas, "the area table is empty"
    for folder, stated in areas:
        expected = (
            top_level
            if not folder
            else sum(count for path, count in collected.items() if path.startswith(f"tests/{folder}/"))
        )
        assert int(stated) == expected, folder or "cross-cutting"


def test_the_development_guide_lists_every_root_level_test_module() -> None:
    """``docs/development.md`` names the root-level modules; bind it to disk.

    This surface sat outside every other check in this file, which reads only
    ``tests/**/AGENTS.md`` and ``tests/**/README.md``. It drifted accordingly:
    the guide said "two root-level modules" while seven were present and named
    only two of them. A prose list of files is a claim about the tree, so it is
    recomputed here rather than maintained by hand.
    """

    guide = (ROOT / "docs" / "development.md").read_text(encoding="utf-8")
    on_disk = {path.name for path in TESTS.glob("test_*.py")}
    named = set(re.findall(r"`tests/(test_[a-z0-9_]+\.py)`", guide))

    assert on_disk, "no root-level test modules found; this check would be vacuous"
    assert on_disk <= named, f"docs/development.md omits {sorted(on_disk - named)}"
    assert named <= on_disk, f"docs/development.md names absent modules {sorted(named - on_disk)}"


def test_every_stated_full_suite_size_matches_collection(collected: Counter) -> None:
    """The "N passed tests" sentence repeated across the folder READMEs."""

    total = sum(collected.values())
    seen = 0
    for doc in sorted(TESTS.rglob("README.md")):
        for stated in _SUITE_SIZE_RE.findall(doc.read_text(encoding="utf-8")):
            assert int(stated) == total, doc.relative_to(ROOT)
            seen += 1
    assert seen >= 10, "the suite-size sentence disappeared; this check went vacuous"
