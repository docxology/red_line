"""Executable form of `STANDALONE.md`: this copy must survive being separated.

Red Line is developed inside a larger private projects tree and published as its
own repository. Three defects only appear on the published side, and none of
them is visible from the development tree, because the development tree has the
missing things sitting next to it:

- **A source file that was never committed.** ``tests/conftest.py`` rebuilds the
  ignored figure tree before the gates that read it, and ``scripts/__init__.py``
  keeps the local ``scripts`` directory a regular package. Both existed on disk
  and neither was tracked, so a clone got neither and eleven gates failed for a
  reason that had nothing to do with the property under test.
- **A relative link that leaves the repository.** ``../../docs/line-set.md``
  resolves inside the private tree and to nothing at all for a reader holding
  only this repository. Under the set's own rule a cross-reference is an
  orientation link, and an orientation link that resolves to nothing is not
  orientation.
- **A missing statement of scope.** A separated copy has to be able to say what
  it is, what it can establish alone, and what it cannot do without the external
  render engine.

Each check here is falsifiable on this tree: the tracked-file check reads what
git actually reports rather than a hand-kept list, and the link check is proved
able to reject by running the same classifier over a planted escaping link.
"""

from __future__ import annotations

from pathlib import Path
import re
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
GIT = shutil.which("git")

#: Directories whose Python sources the suite and the CLIs both need present.
SOURCE_ROOTS = ("src", "tests", "scripts")

#: Text files whose relative links a reader is expected to be able to follow.
LINK_SUFFIXES = (".md",)

#: A link target that leaves this repository cannot be followed by a reader who
#: has only this repository, whatever it points at.
_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
_ADDRESSED_ELSEWHERE = ("http://", "https://", "mailto:", "tel:", "#")


def _git(arguments: list[str]) -> str | None:
    """Run one git command inside the project, or report that git cannot answer."""

    if GIT is None:
        return None
    result = subprocess.run(
        [GIT, *arguments],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout


def escaping_links(path: Path, root: Path) -> list[str]:
    """Return every relative link in ``path`` that resolves outside ``root``.

    Absolute URLs and in-page anchors are addressed elsewhere by construction
    and are not relative links at all, so they are not candidates.
    """

    escaping: list[str] = []
    for target in _LINK_RE.findall(path.read_text(encoding="utf-8")):
        if target.startswith(_ADDRESSED_ELSEWHERE):
            continue
        without_anchor = target.split("#", 1)[0]
        if not without_anchor:
            continue
        resolved = (path.parent / without_anchor).resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            escaping.append(target)
    return escaping


def _linked_documents() -> list[Path]:
    tracked = _git(["ls-files", "-z"])
    if tracked is None:
        return []
    return [
        ROOT / entry
        for entry in tracked.split("\0")
        if entry and entry.endswith(LINK_SUFFIXES) and (ROOT / entry).is_file()
    ]


requires_git_checkout = pytest.mark.skipif(
    GIT is None or _git(["rev-parse", "--is-inside-work-tree"]) is None,
    reason="no git checkout here: tracking and link inventories are read from git",
)


# --------------------------------------------------------------------------
# Everything the clone needs is actually committed.
# --------------------------------------------------------------------------


@requires_git_checkout
def test_no_python_source_the_suite_needs_is_left_untracked() -> None:
    """An uncommitted source file is invisible to every clone.

    This is read from git rather than from a maintained list, so a new
    uncommitted module under `src/`, `tests/`, or `scripts/` fails here on the
    run that introduces it.
    """

    others = _git(["ls-files", "--others", "--exclude-standard", "-z", *SOURCE_ROOTS])
    assert others is not None, "git could not report untracked files"
    untracked = sorted(
        entry for entry in others.split("\0") if entry and entry.endswith(".py")
    )

    assert untracked == [], f"present on disk but absent from every clone: {untracked}"


@requires_git_checkout
def test_the_tracked_inventory_is_not_empty_and_carries_the_two_that_regressed() -> None:
    """Pin the two files whose absence a clone previously discovered for us."""

    tracked_output = _git(["ls-files", "-z", *SOURCE_ROOTS])
    assert tracked_output is not None, "git could not report tracked files"
    tracked = {entry for entry in tracked_output.split("\0") if entry}

    assert len(tracked) > 50, "the tracked inventory is too small; this check went vacuous"
    assert "tests/conftest.py" in tracked
    assert "scripts/__init__.py" in tracked


@requires_git_checkout
def test_generated_trees_are_ignored_by_this_repositorys_own_gitignore() -> None:
    """`output/` is disposable, and the docs say so; a clone must agree."""

    ignore_file = ROOT / ".gitignore"
    assert ignore_file.is_file(), "no tracked .gitignore: a clone would inherit nothing"

    patterns = {line.strip() for line in ignore_file.read_text(encoding="utf-8").splitlines()}
    assert {"output/", "__pycache__/", ".venv/", "*.egg-info/", ".coverage"} <= patterns

    tracked_output = _git(["ls-files", "-z", "output"])
    assert tracked_output is not None, "git could not report tracked files"
    assert tracked_output.strip("\0") == "", "generated output is tracked"


# --------------------------------------------------------------------------
# Every cross-reference a reader can follow, resolves.
# --------------------------------------------------------------------------


@requires_git_checkout
def test_no_relative_link_in_a_tracked_document_leaves_the_repository() -> None:
    documents = _linked_documents()
    assert len(documents) > 20, "no tracked documents found; this check would be vacuous"

    offending = {
        str(path.relative_to(ROOT)): escaping
        for path in documents
        if (escaping := escaping_links(path, ROOT))
    }

    assert offending == {}, (
        "relative links that resolve outside the repository root, and so resolve "
        f"to nothing for a reader holding only this repository: {offending}"
    )


@requires_git_checkout
def test_the_link_inventory_examined_a_real_body_of_links() -> None:
    """A classifier that finds no links at all would report zero escapes."""

    examined = sum(
        len(_LINK_RE.findall(path.read_text(encoding="utf-8"))) for path in _linked_documents()
    )
    assert examined > 100, f"only {examined} links parsed; the escape check is not doing work"


def test_the_escape_check_rejects_a_planted_outward_link(tmp_path: Path) -> None:
    """Positive control: prove the classifier can go red on the real pattern."""

    repository = tmp_path / "repository"
    (repository / "docs").mkdir(parents=True)
    document = repository / "docs" / "guide.md"
    document.write_text(
        "See the [line-set map](../../docs/line-set.md), the "
        "[local note](note.md), the [site](https://example.invalid/x), "
        "and the [section](#heading).\n",
        encoding="utf-8",
    )
    (repository / "docs" / "note.md").write_text("ok\n", encoding="utf-8")

    assert escaping_links(document, repository) == ["../../docs/line-set.md"]


# --------------------------------------------------------------------------
# The copy still explains itself.
# --------------------------------------------------------------------------


def test_the_standalone_guide_exists_and_states_the_external_dependency() -> None:
    guide = ROOT / "STANDALONE.md"
    assert guide.is_file(), "a separated copy with no statement of its own scope"

    body = guide.read_text(encoding="utf-8")
    assert "docxology/red_line" in body
    assert "https://github.com/docxology/template" in body
    assert "RED_LINE_TEMPLATE_ROOT" in body
    # What it can do alone, and what it cannot.
    assert "What it can do alone" in body
    assert "What it cannot do alone" in body
    assert "scripts/build_figures.py" in body


def test_no_top_level_guidance_still_calls_this_a_worktree_of_something_else() -> None:
    """It is its own repository now; guidance that says otherwise misdirects."""

    for name in ("AGENTS.md", "README.md", "STANDALONE.md"):
        body = (ROOT / name).read_text(encoding="utf-8")
        assert "sidecar worktree" not in body, name

    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "docxology/red_line" in agents
    assert "STANDALONE.md" in agents


@requires_git_checkout
def test_the_project_does_not_describe_itself_as_part_of_a_larger_checkout() -> None:
    """Pre-publication and private-sidecar language must not survive the public flip."""

    documents = _linked_documents()
    assert len(documents) > 20, "no tracked documents found; this check would be vacuous"

    stale = ("private sidecar", "symlinked sidecar", "sidecar project", "sidecar checkout")
    offenders = [
        f"{path.relative_to(ROOT)}: {phrase}"
        for path in documents
        for text in (path.read_text(encoding="utf-8").lower(),)
        for phrase in stale
        if phrase in text
    ]

    assert not offenders, "stale self-description remains at: " + ", ".join(offenders)
