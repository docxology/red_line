"""Tests that every red line carries revisable author provenance, not moral fact.

These pin the Advisor-surfaced requirement: no line may read as the framework's
(or an AI's) universal moral claim; each is the author's dated, first-person,
revisable commitment, and the set is explicitly non-exhaustive.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from red_line import PERSONAL_RED_LINES, REGISTRY_IS_EXHAUSTIVE
from red_line.registry import SOURCE_DATE, SOURCE_FRAMEWORK, SOURCE_URL

ROOT = Path(__file__).resolve().parents[2]


def test_every_line_has_author_provenance():
    for rl in PERSONAL_RED_LINES:
        assert rl.stated_by == "Daniel Ari Friedman"
        # ISO date shape.
        assert len(rl.stated_on) == 10 and rl.stated_on.count("-") == 2


def test_every_standard_is_first_person_commitment():
    # A commitment ("I will not…") — never a universal moral assertion.
    for rl in PERSONAL_RED_LINES:
        assert rl.standard.strip().lower().startswith("i "), rl.id


def test_registry_marked_non_exhaustive():
    assert REGISTRY_IS_EXHAUSTIVE is False


# ---------------------------------------------------------------------------
# RL-15: the source-framework attribution constants are public API with no
# consumer. `SOURCE_URL` is read by scripts/build_canary.py, but
# `SOURCE_FRAMEWORK` and `SOURCE_DATE` were exported, documented as the public
# API surface in docs/README.md, and asserted nowhere — so a drift in the
# attribution string or the source's publication date would have been invisible
# to the gate while three other files continued to state the same facts.
#
# These bind the three constants to the surfaces that restate them:
# manuscript/config.yaml's project_config.source_framework block, CITATION.cff's
# reference entry, and manuscript/references.bib. All four must agree.
# ---------------------------------------------------------------------------


def _text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_source_framework_constant_names_the_author_and_title_verbatim():
    """The constant is `author, title`; both halves must be real, not a label."""

    author, _, title = SOURCE_FRAMEWORK.partition(", ")

    assert author == "Alex Turner"
    assert title == "A Red Line and Oversight Framework for Government AI Contracts"


def test_source_constants_match_the_manuscript_config_block():
    """`project_config.source_framework` is what the rendered front matter uses."""

    config = _text("manuscript/config.yaml")
    author, _, title = SOURCE_FRAMEWORK.partition(", ")

    assert f'author: "{author}"' in config
    assert f'title: "{title}"' in config
    assert f'url: "{SOURCE_URL}"' in config
    assert f'date: "{SOURCE_DATE}"' in config


def test_source_constants_match_the_citation_reference_block():
    """CITATION.cff is the machine-readable citation a reuser will read first."""

    citation = _text("CITATION.cff")
    author, _, title = SOURCE_FRAMEWORK.partition(", ")
    family, given = author.split(" ")[-1], author.split(" ")[0]

    assert f'title: "{title}"' in citation
    assert f'family-names: "{family}"' in citation
    assert f'given-names: "{given}"' in citation
    assert f'url: "{SOURCE_URL}"' in citation
    assert f"year: {SOURCE_DATE[:4]}" in citation


def test_source_date_matches_the_bibliography_entry():
    """references.bib carries the same publication date, split across fields."""

    bib = _text("manuscript/references.bib")
    entry = bib.split("@misc{turner2026redline,")[1].split("\n@")[0]
    year, month, day = SOURCE_DATE.split("-")
    months = (
        "jan", "feb", "mar", "apr", "may", "jun",
        "jul", "aug", "sep", "oct", "nov", "dec",
    )

    assert f"year         = {{{year}}}" in entry
    assert f"month        = {months[int(month) - 1]}" in entry
    assert f"day          = {{{int(day)}}}" in entry
    assert SOURCE_URL in entry


def test_source_date_is_an_iso_day_not_a_year_or_a_range():
    """A loosened date format would let the other assertions pass vacuously."""

    date.fromisoformat(SOURCE_DATE)

    assert len(SOURCE_DATE) == 10
