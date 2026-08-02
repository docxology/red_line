"""Provenance primitives measured against real files and a real git repository."""

from __future__ import annotations

import hashlib
from pathlib import Path
import shutil
import subprocess

import pytest

from red_line.release import (
    TEMPLATE_ROOT_MARKER,
    TemplateRootUnavailable,
    digest_tree,
    find_template_root,
    git_dirty,
    git_revision,
    require_template_root,
    sha256_file,
    template_root_candidates,
)

GIT = shutil.which("git")
requires_git = pytest.mark.skipif(GIT is None, reason="git is not installed")


def _isolated_git_env(home: Path) -> dict[str, str]:
    """Build a git environment that ignores the developer's own configuration."""

    return {
        "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
        "HOME": str(home),
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_CONFIG_SYSTEM": "/dev/null",
        "GIT_AUTHOR_NAME": "Release Test",
        "GIT_AUTHOR_EMAIL": "release-test@example.invalid",
        "GIT_COMMITTER_NAME": "Release Test",
        "GIT_COMMITTER_EMAIL": "release-test@example.invalid",
    }


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        [GIT, "-C", str(repo), *args], check=True, capture_output=True, env=_isolated_git_env(repo)
    )


class TestSha256File:
    def test_digests_a_file_larger_than_one_chunk(self, tmp_path):
        payload = b"red-line" * 200_000  # 1.6 MiB forces more than one read iteration
        target = tmp_path / "large.bin"
        target.write_bytes(payload)
        assert sha256_file(target) == hashlib.sha256(payload).hexdigest()

    def test_digests_an_empty_file(self, tmp_path):
        target = tmp_path / "empty.bin"
        target.write_bytes(b"")
        assert sha256_file(target) == hashlib.sha256(b"").hexdigest()


class TestGitProvenance:
    def test_non_repository_reports_unknown_revision_and_dirtiness(self, tmp_path):
        assert git_revision(tmp_path) is None
        assert git_dirty(tmp_path) is None

    @requires_git
    def test_real_repository_reports_revision_and_dirty_transitions(self, tmp_path):
        repo = tmp_path / "repo"
        repo.mkdir()
        _git(repo, "init", "--quiet")
        (repo / "tracked.txt").write_text("first\n", encoding="utf-8")
        _git(repo, "add", "tracked.txt")
        _git(repo, "commit", "--quiet", "-m", "initial")

        revision = git_revision(repo)
        assert revision is not None
        assert len(revision) == 40
        assert all(character in "0123456789abcdef" for character in revision)
        assert git_dirty(repo) is False

        (repo / "tracked.txt").write_text("second\n", encoding="utf-8")
        assert git_dirty(repo) is True


def _plant_template(directory: Path) -> Path:
    """Create a directory that carries the render stage script this project calls."""

    marker = directory / TEMPLATE_ROOT_MARKER
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("# stand-in for the external render stage\n", encoding="utf-8")
    return directory


class TestFindTemplateRoot:
    """The render toolchain is external; locating it must not assume a layout.

    The previous default was ``root.parents[2] / "template"`` — the private
    monorepo's exact shape. In any other checkout it named a directory that has
    never existed, and every caller then treated that fiction as the renderer.
    """

    def test_environment_override_wins_and_is_taken_as_given(self, tmp_path, monkeypatch):
        # No marker is planted: an explicit operator statement is honoured
        # verbatim so a differently-shaped checkout stays usable.
        override = tmp_path / "elsewhere" / "template"
        override.mkdir(parents=True)
        monkeypatch.setenv("RED_LINE_TEMPLATE_ROOT", str(override))
        assert find_template_root(tmp_path) == override.resolve()
        assert require_template_root(tmp_path) == override.resolve()

    def test_an_ancestor_checkout_that_really_exists_is_found(self, tmp_path, monkeypatch):
        monkeypatch.delenv("RED_LINE_TEMPLATE_ROOT", raising=False)
        root = tmp_path / "github" / "projects" / "working" / "red_line"
        root.mkdir(parents=True)
        expected = _plant_template(tmp_path / "github" / "template").resolve()

        assert find_template_root(root) == expected
        assert require_template_root(root) == expected

    def test_the_nearest_ancestor_checkout_wins(self, tmp_path, monkeypatch):
        monkeypatch.delenv("RED_LINE_TEMPLATE_ROOT", raising=False)
        root = tmp_path / "github" / "projects" / "working" / "red_line"
        root.mkdir(parents=True)
        _plant_template(tmp_path / "github" / "template")
        nearest = _plant_template(tmp_path / "github" / "projects" / "template").resolve()

        assert find_template_root(root) == nearest

    def test_a_directory_named_template_without_the_stage_script_is_not_the_toolchain(
        self, tmp_path, monkeypatch
    ):
        monkeypatch.delenv("RED_LINE_TEMPLATE_ROOT", raising=False)
        root = tmp_path / "github" / "projects" / "working" / "red_line"
        root.mkdir(parents=True)
        (tmp_path / "github" / "template").mkdir(parents=True)

        assert find_template_root(root) is None

    def test_a_standalone_clone_reports_absence_instead_of_a_fictional_path(
        self, tmp_path, monkeypatch
    ):
        """The regression: this is the fresh-clone case the old default got wrong."""

        monkeypatch.delenv("RED_LINE_TEMPLATE_ROOT", raising=False)
        root = tmp_path / "red_line"
        root.mkdir()

        assert find_template_root(root) is None

    def test_requiring_an_absent_toolchain_names_what_is_missing(self, tmp_path, monkeypatch):
        monkeypatch.delenv("RED_LINE_TEMPLATE_ROOT", raising=False)
        root = tmp_path / "red_line"
        root.mkdir()

        with pytest.raises(TemplateRootUnavailable) as raised:
            require_template_root(root)

        message = str(raised.value)
        assert "RED_LINE_TEMPLATE_ROOT" in message
        assert "https://github.com/docxology/template" in message
        assert str(TEMPLATE_ROOT_MARKER) in message
        assert str(tmp_path / "template") in message
        # It also says what still works without the toolchain, so the reader is
        # not left thinking the clone is broken.
        assert "run without it" in message

    def test_candidates_are_ancestors_and_never_the_project_itself(self, tmp_path):
        root = tmp_path / "github" / "projects" / "working" / "red_line"
        root.mkdir(parents=True)
        candidates = template_root_candidates(root)

        assert candidates, "no candidate locations; the search would be vacuous"
        assert root / "template" not in candidates
        assert (tmp_path / "github" / "template").resolve() in candidates


class TestDigestTree:
    def test_missing_directory_yields_no_digests(self, tmp_path):
        assert digest_tree(tmp_path, "output/figures", (".svg",)) == {}

    def test_empty_directory_yields_no_digests(self, tmp_path):
        (tmp_path / "output" / "figures").mkdir(parents=True)
        assert digest_tree(tmp_path, "output/figures", (".svg",)) == {}

    def test_filters_by_suffix_and_ignores_directories(self, tmp_path):
        base = tmp_path / "output" / "figures"
        (base / "nested").mkdir(parents=True)
        (base / "kept.svg").write_text("<svg/>", encoding="utf-8")
        (base / "skipped.txt").write_text("ignored", encoding="utf-8")
        (base / "nested" / "deep.svg").write_text("<svg/>", encoding="utf-8")

        digests = digest_tree(tmp_path, "output/figures", (".svg",))

        assert set(digests) == {"output/figures/kept.svg", "output/figures/nested/deep.svg"}
        assert all(len(value) == 64 for value in digests.values())

    def test_suffix_match_is_case_insensitive(self, tmp_path):
        base = tmp_path / "output" / "figures"
        base.mkdir(parents=True)
        (base / "shouty.SVG").write_text("<svg/>", encoding="utf-8")
        assert set(digest_tree(tmp_path, "output/figures", (".svg",))) == {"output/figures/shouty.SVG"}

    def test_excluded_names_are_dropped(self, tmp_path):
        base = tmp_path / "output" / "reports"
        base.mkdir(parents=True)
        (base / "release_manifest.json").write_text("{}", encoding="utf-8")
        (base / "other.json").write_text("{}", encoding="utf-8")

        digests = digest_tree(
            tmp_path, "output/reports", (".json",), exclude_names=("release_manifest.json",)
        )

        assert set(digests) == {"output/reports/other.json"}
