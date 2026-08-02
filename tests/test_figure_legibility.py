"""Rendered-legibility gate for the deterministic figure set.

The figure contract in ``docs/visualization-briefs.md`` says shape and text
repeat every colour meaning so colour is not required. That mitigation only
functions if the repeated text is readable on the printed page. These tests
derive the rendered point size of the *smallest* label in every figure from the
built artefacts plus the manuscript's own geometry, and fail below the floor.

Every assertion here is falsifiable: the planted-defect tests shrink a real
font, and tighten a real height cap, and assert the gate goes red on the same
artefacts it certifies today.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import pytest

from red_line.figures import build_figures
from red_line.figures.legibility import (
    DEFAULT_FIGURE_HEIGHT_FRACTION,
    MIN_LEGIBLE_PT,
    PageGeometry,
    declared_width_fractions,
    illegible_figures,
    measure_figure,
    measure_figure_set,
    min_font_px,
    parse_figure_height_fraction,
    parse_page_geometry,
    png_dimensions,
    rendered_width_pt,
    svg_canvas_size,
)
from red_line.figures.registry import GENERATORS
from red_line.figures.text import FIGURE_TEXT
from red_line.figures.theme import MIN_FONT_PX, WIDTH

ROOT = Path(__file__).resolve().parents[1]


def _built_tree(tmp_path: Path) -> Path:
    """Copy the manuscript and a freshly built figure set into a temp project."""

    shutil.copytree(ROOT / "manuscript", tmp_path / "manuscript")
    build_figures(tmp_path)
    return tmp_path


# --------------------------------------------------------------------------
# The gate itself, measured on the shipped artefacts.
# --------------------------------------------------------------------------


def test_every_figure_label_clears_the_legibility_floor() -> None:
    """No registered figure renders its smallest label below the floor."""

    measured = measure_figure_set(ROOT)

    assert len(measured) == len(GENERATORS), "the gate must cover every registered figure"
    offenders = [
        f"{figure.label}: {figure.rendered_min_pt:.2f}pt "
        f"({figure.min_font_px:g}px on a {figure.canvas_width_px:g}px canvas "
        f"rendered {figure.rendered_width_pt:.1f}pt wide"
        f"{', HEIGHT-CAPPED' if figure.height_bound else ''})"
        for figure in measured
        if not figure.legible
    ]
    assert not offenders, f"figures below {MIN_LEGIBLE_PT}pt: " + "; ".join(offenders)
    assert illegible_figures(ROOT) == ()


def test_no_figure_is_shrunk_by_the_template_height_cap() -> None:
    """Width, not the injected height cap, must set every plate's scale.

    A height-capped plate shrinks in both dimensions, so its labels shrink even
    though nothing in this project's sources changed. Keeping width binding is
    what makes the font floor in ``theme.py`` sufficient.
    """

    height_bound = [figure.label for figure in measure_figure_set(ROOT) if figure.height_bound]

    assert height_bound == []


def test_the_gate_scan_set_is_not_empty_and_matches_the_registry() -> None:
    """A gate over an empty scan set certifies nothing."""

    measured = measure_figure_set(ROOT)

    assert {figure.label for figure in measured} == set(GENERATORS)
    assert len(measured) > 0
    assert all(figure.min_font_px > 0 for figure in measured)


# --------------------------------------------------------------------------
# Planted defects: proof the gate can fail.
# --------------------------------------------------------------------------


def test_gate_catches_a_shrunken_font_planted_in_a_built_figure(tmp_path: Path) -> None:
    """Shrink one real label below the floor; the gate must name that figure."""

    project = _built_tree(tmp_path)
    assert illegible_figures(project) == ()

    victim = project / "output" / "figures" / "tier_monotonicity_lattice.svg"
    victim.write_text(
        victim.read_text(encoding="utf-8").replace(
            f'font-size="{MIN_FONT_PX}px"', 'font-size="4px"', 1
        ),
        encoding="utf-8",
    )

    caught = illegible_figures(project)

    assert [figure.label for figure in caught] == ["fig:tier-monotonicity-lattice"]
    assert caught[0].min_font_px == 4.0
    assert caught[0].rendered_min_pt < MIN_LEGIBLE_PT


def test_gate_catches_the_template_height_cap_reintroduced(tmp_path: Path) -> None:
    """Restore the renderer's default height cap; tall plates must go red.

    This is the defect the gate was written for: no figure source changes, but
    the injected ``height=0.5\\textheight`` bound shrinks the tallest plates
    until their labels are unreadable.
    """

    project = _built_tree(tmp_path)
    config = project / "manuscript" / "config.yaml"
    config.write_text(
        re.sub(
            r"^(\s{2,}figure_height_fraction:)\s*[0-9.]+\s*$",
            r"\g<1> 0.5",
            config.read_text(encoding="utf-8"),
            flags=re.MULTILINE,
        ),
        encoding="utf-8",
    )

    caught = illegible_figures(project)

    assert caught, "a 0.5 height cap must shrink at least one plate below the floor"
    assert all(figure.height_bound for figure in caught)


def test_gate_fails_closed_when_a_registered_figure_is_never_embedded(tmp_path: Path) -> None:
    """A figure with no manuscript embed is unmeasurable, so it must raise."""

    project = _built_tree(tmp_path)
    embed = project / "manuscript" / "05_deployment_tiers.md"
    embed.write_text(
        embed.read_text(encoding="utf-8").replace("{#fig:tier-monotonicity-lattice", "{#fig:removed"),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="embedded in no manuscript file"):
        measure_figure_set(project)


def test_gate_fails_closed_when_the_figures_are_not_built(tmp_path: Path) -> None:
    """An unbuilt figure set must raise, never silently measure nothing."""

    shutil.copytree(ROOT / "manuscript", tmp_path / "manuscript")

    with pytest.raises(FileNotFoundError, match="build the figures first"):
        measure_figure_set(tmp_path)


def test_measure_figure_rejects_a_resampled_rasterization(tmp_path: Path) -> None:
    """A PNG whose pixels disagree with the canvas breaks the ratio identity."""

    project = _built_tree(tmp_path)
    figures = project / "output" / "figures"
    svg_text = (figures / "line_set_compass.svg").read_text(encoding="utf-8")
    png_bytes = (figures / "line_set_compass.png").read_bytes()
    resampled = svg_text.replace('width="1400"', 'width="700"', 1)
    assert resampled != svg_text

    with pytest.raises(ValueError, match="does not match"):
        measure_figure(
            "fig:line-set-compass",
            resampled,
            png_bytes,
            0.95,
            PageGeometry(553.58849, 715.47255),
            0.9,
        )


# --------------------------------------------------------------------------
# The derivation's own inputs, bound to the artefacts they claim to model.
# --------------------------------------------------------------------------


def test_derived_page_geometry_matches_the_rendered_log() -> None:
    """The geometry derived from config.yaml equals what LaTeX actually used.

    Skipped on a checkout with no rendered PDF; when the log is present this is
    what stops the gate from measuring against an invented page.
    """

    log_path = ROOT / "output" / "pdf" / "_combined_manuscript.log"
    if not log_path.is_file():  # pragma: no cover - render artefact is optional
        pytest.skip("no rendered LaTeX log in this checkout")
    log = log_path.read_text(encoding="utf-8", errors="replace")
    geometry = parse_page_geometry((ROOT / "manuscript" / "config.yaml").read_text(encoding="utf-8"))

    logged_width = float(re.search(r"\\textwidth=([\d.]+)pt", log).group(1))
    logged_height = float(re.search(r"\\textheight=([\d.]+)pt", log).group(1))

    assert abs(geometry.text_width_pt - logged_width) < 0.01
    assert abs(geometry.text_height_pt - logged_height) < 0.01


def test_declared_width_fractions_match_the_generated_latex() -> None:
    """Each figure's ``width=NN%`` embed equals the ``width=`` LaTeX received."""

    tex_path = ROOT / "output" / "pdf" / "_combined_manuscript.tex"
    if not tex_path.is_file():  # pragma: no cover - render artefact is optional
        pytest.skip("no rendered LaTeX source in this checkout")
    tex = tex_path.read_text(encoding="utf-8", errors="replace")
    fractions = declared_width_fractions(ROOT / "manuscript")
    expected_by_file = {FIGURE_TEXT[label]["filename"]: fractions[label] for label in GENERATORS}

    seen = 0
    for match in re.finditer(r"\\includegraphics\[([^\]]*)\]\{([^}]*)\}", tex):
        name = match.group(2).rsplit("/", 1)[-1]
        if name not in expected_by_file:
            continue
        declared = re.search(r"width=([\d.]*)\\linewidth", match.group(1))
        assert declared is not None, name
        assert abs(float(declared.group(1) or 1.0) - expected_by_file[name]) < 1e-9, name
        seen += 1
    assert seen == len(expected_by_file), "every registered figure must appear in the rendered LaTeX"


def test_configured_height_fraction_is_read_from_the_rendering_block() -> None:
    """The knob only works inside ``rendering:``; assert the project uses it."""

    config_text = (ROOT / "manuscript" / "config.yaml").read_text(encoding="utf-8")

    assert parse_figure_height_fraction(config_text) > DEFAULT_FIGURE_HEIGHT_FRACTION


def test_height_fraction_falls_back_when_the_key_sits_outside_rendering() -> None:
    """A knob in the wrong block is dead config, so the default must apply."""

    misplaced = 'metadata:\n  geometry: "left=1in,right=1in,top=1in,bottom=1in"\n  figure_height_fraction: 0.9\n'

    assert parse_figure_height_fraction(misplaced) == DEFAULT_FIGURE_HEIGHT_FRACTION


def test_height_fraction_falls_back_when_rendering_block_omits_the_key() -> None:
    assert parse_figure_height_fraction("rendering:\n  section_breaks: true\n") == (
        DEFAULT_FIGURE_HEIGHT_FRACTION
    )


def test_page_geometry_rejects_a_config_without_a_geometry_string() -> None:
    with pytest.raises(ValueError, match="no metadata.geometry"):
        parse_page_geometry("paper:\n  title: x\n")


def test_page_geometry_rejects_a_geometry_string_missing_a_margin() -> None:
    with pytest.raises(ValueError, match="omits margin"):
        parse_page_geometry('metadata:\n  geometry: "left=1in,right=1in,top=1in"\n')


def test_declared_width_defaults_to_full_line_when_the_embed_omits_width(tmp_path: Path) -> None:
    manuscript = tmp_path / "manuscript"
    manuscript.mkdir()
    (manuscript / "01.md").write_text("![c](../output/figures/x.png){#fig:bare}\n", encoding="utf-8")

    assert declared_width_fractions(manuscript) == {"fig:bare": 1.0}


def test_min_font_px_rejects_an_svg_without_any_text() -> None:
    with pytest.raises(ValueError, match="no font-size"):
        min_font_px("<svg><rect/></svg>")


def test_svg_canvas_size_rejects_a_document_without_a_canvas() -> None:
    with pytest.raises(ValueError, match="no canvas width and height"):
        svg_canvas_size("<svg role='img'></svg>")


def test_png_dimensions_rejects_a_non_png_payload() -> None:
    with pytest.raises(ValueError, match="not a PNG"):
        png_dimensions(b"GIF89a not a png at all")


def test_rendered_width_reports_which_bound_applied() -> None:
    """The width/height branch is the whole point; pin both directions."""

    geometry = PageGeometry(text_width_pt=553.58849, text_height_pt=715.47255)

    wide, wide_bound = rendered_width_pt(1400, 700, 0.95, geometry, 0.9)
    tall, tall_bound = rendered_width_pt(1400, 2800, 0.95, geometry, 0.9)

    assert not wide_bound
    assert abs(wide - 0.95 * geometry.text_width_pt) < 1e-9
    assert tall_bound
    assert abs(tall - 0.9 * geometry.text_height_pt * 1400 / 2800) < 1e-9
    assert tall < wide


def test_theme_font_floor_is_the_value_the_page_geometry_demands() -> None:
    """``MIN_FONT_PX`` is derived from the floor, not chosen by eye.

    Re-derives the smallest canvas font that can clear ``MIN_LEGIBLE_PT`` for
    the narrowest embed the manuscript actually declares, so shrinking a figure
    embed or widening the canvas reddens this test.
    """

    geometry = parse_page_geometry((ROOT / "manuscript" / "config.yaml").read_text(encoding="utf-8"))
    narrowest = min(
        fraction
        for label, fraction in declared_width_fractions(ROOT / "manuscript").items()
        if label in GENERATORS
    )
    required = MIN_LEGIBLE_PT * WIDTH / (narrowest * geometry.text_width_pt)

    assert MIN_FONT_PX >= required
    assert MIN_FONT_PX - 1 < required, "floor is higher than the geometry requires"


# --------------------------------------------------------------------------
# The generated LaTeX is the only place the height cap becomes real. Deriving
# it from config.yaml is what makes the gate runnable on a fresh checkout, but
# a knob that is named and never consumed would leave the derivation measuring
# a page the renderer never produced.
# --------------------------------------------------------------------------


def test_configured_height_fraction_is_the_one_the_renderer_injected() -> None:
    """Bind ``figure_height_fraction`` to the ``height=`` LaTeX received.

    Skipped on a checkout with no rendered LaTeX. When the artefact is present
    this is the assertion that would catch the knob being renamed, moved out of
    the ``rendering:`` block, or silently ignored by the shared template.
    """

    tex_path = ROOT / "output" / "pdf" / "_combined_manuscript.tex"
    if not tex_path.is_file():  # pragma: no cover - render artefact is optional
        pytest.skip("no rendered LaTeX source in this checkout")
    tex = tex_path.read_text(encoding="utf-8", errors="replace")
    configured = parse_figure_height_fraction(
        (ROOT / "manuscript" / "config.yaml").read_text(encoding="utf-8")
    )
    filenames = {FIGURE_TEXT[label]["filename"] for label in GENERATORS}

    seen = 0
    for match in re.finditer(r"\\includegraphics\[([^\]]*)\]\{([^}]*)\}", tex):
        if match.group(2).rsplit("/", 1)[-1] not in filenames:
            continue
        declared = re.search(r"height=([\d.]+)\\textheight", match.group(1))
        assert declared is not None, match.group(2)
        assert abs(float(declared.group(1)) - configured) < 1e-9, match.group(2)
        seen += 1
    assert seen == len(filenames), "every registered figure must appear in the rendered LaTeX"


# --------------------------------------------------------------------------
# Figure-count prose. Adding a plate touches seven documentation surfaces; the
# count was written out as a word in every one of them and bound in none.
# --------------------------------------------------------------------------

_COUNT_WORDS = {
    11: "eleven",
    12: "twelve",
    13: "thirteen",
    14: "fourteen",
    15: "fifteen",
    16: "sixteen",
    17: "seventeen",
    18: "eighteen",
}

#: Present-tense surfaces that state how many figures the project has. Dated
#: log entries in TODO.md, ISA.md, and docs/improvement_protocol.md are
#: deliberately excluded: those are historical records of an earlier tree and
#: rewriting them would destroy the audit trail.
_FIGURE_COUNT_SURFACES = (
    "README.md",
    "docs/visualization-briefs.md",
    "docs/development.md",
    "src/red_line/figures/README.md",
    "src/red_line/figures/AGENTS.md",
    ".agents/skills/personal-red-lines/SKILL.md",
    ".agents/skills/personal-red-lines/README.md",
)


@pytest.mark.parametrize("relative", _FIGURE_COUNT_SURFACES)
def test_every_present_tense_figure_count_matches_the_registry(relative: str) -> None:
    """The word each surface uses must be the live ``len(GENERATORS)``."""

    body = " ".join((ROOT / relative).read_text(encoding="utf-8").split())
    word = _COUNT_WORDS[len(GENERATORS)]
    stale = {value for count, value in _COUNT_WORDS.items() if count != len(GENERATORS)}

    assert word in body, f"{relative} no longer states the figure count"
    for other in sorted(stale):
        assert f" {other} figure" not in body, f"{relative} still says {other}"
        assert f" {other} deterministic" not in body, f"{relative} still says {other}"
        assert f" {other} visuals" not in body, f"{relative} still says {other}"
        assert f" {other} entries" not in body, f"{relative} still says {other}"
        assert f" {other} SVGs" not in body, f"{relative} still says {other}"


def test_the_figure_count_surface_list_is_not_empty_and_the_word_exists() -> None:
    """Guards the parametrization above against becoming vacuous."""

    assert len(_FIGURE_COUNT_SURFACES) >= 5
    assert len(GENERATORS) in _COUNT_WORDS, "extend _COUNT_WORDS when the set grows"
