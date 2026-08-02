"""Rendered-legibility derivation for the deterministic figure set.

Every figure in this project repeats its colour encoding in text so the plate
stays readable in greyscale. That mitigation is worthless if the repeated text
is too small to read on the printed page, and until this module existed nothing
in the tree measured it: the accessibility claim in
``docs/visualization-briefs.md`` was asserted, never derived.

This module derives, from artefacts that already exist, the point size at which
each figure's *smallest* label lands in the rendered PDF:

``rendered_pt = min_font_px * rendered_width_pt / canvas_width_px``

The identity holds because LaTeX scales the raster to a declared width, so a
canvas unit and a point are related by one ratio for the whole plate. The
rasterized pixel width equals the SVG canvas width (``rsvg-convert`` runs 1:1),
which is why the PNG's IHDR dimensions may be used as the canvas dimensions.

``rendered_width_pt`` is the smaller of two bounds, matching the shared render
template's ``\\includegraphics[width=...,height=...,keepaspectratio]``:

* the declared width fraction of ``\\textwidth`` (from the ``width=NN%``
  attribute on the figure's markdown embed); and
* the height cap ``figure_height_fraction * \\textheight`` converted back to a
  width through the canvas aspect ratio.

When the height cap binds first, the whole plate shrinks and every label shrinks
with it — the failure mode this module was written to catch.

Page geometry is derived from ``manuscript/config.yaml`` rather than from a
build artefact, so the gate runs on a fresh checkout with no rendered PDF
present. Lengths are TeX points (``1in = 72.27pt``), which is the unit both
``geometry`` and LaTeX font sizes use; the conversion cancels out of the ratio
above, but is kept explicit so the intermediate values match the render log.
"""

from __future__ import annotations

import re
import struct
from dataclasses import dataclass
from pathlib import Path

from .registry import GENERATORS
from .text import FIGURE_TEXT

#: TeX points per inch. ``geometry`` reports ``\paperwidth=614.295pt`` for US
#: Letter, which is ``8.5 * 72.27``; LaTeX font sizes use the same unit.
TEX_PT_PER_INCH = 72.27

#: US Letter, the ``geometry`` package default this manuscript inherits.
PAPER_WIDTH_IN = 8.5
PAPER_HEIGHT_IN = 11.0

#: Floor for the smallest in-figure label, in rendered TeX points. Below this
#: the "shape and text repeat the meaning" mitigation stops functioning: the
#: text is present in the raster but not readable at print scale. Six points is
#: the smallest size the figure set treats as readable body-adjacent text; the
#: manuscript's own caption text renders far larger.
MIN_LEGIBLE_PT = 6.0

#: Height cap the shared render template applies when the project sets no
#: ``rendering.figure_height_fraction``. Recorded here because the cap is
#: invisible in the project's own sources — it is injected into the generated
#: LaTeX — and it is the single largest cause of shrunken plates.
DEFAULT_FIGURE_HEIGHT_FRACTION = 0.50

_GEOMETRY_RE = re.compile(r'geometry:\s*"([^"]+)"')
_GEOMETRY_KEY_RE = re.compile(r"(left|right|top|bottom)\s*=\s*([0-9.]+)in")
_HEIGHT_FRACTION_RE = re.compile(r"^\s{2,}figure_height_fraction:\s*([0-9.]+)\s*$", re.MULTILINE)
_RENDERING_BLOCK_RE = re.compile(r"^rendering:\s*$", re.MULTILINE)
_EMBED_RE = re.compile(r"\{#(fig:[a-z0-9-]+)([^}]*)\}")
_WIDTH_ATTR_RE = re.compile(r"width=([0-9.]+)%")
_FONT_SIZE_RE = re.compile(r'font-size="([0-9.]+)px"')
_SVG_SIZE_RE = re.compile(r'<svg[^>]*?width="([0-9.]+)"[^>]*?height="([0-9.]+)"')


@dataclass(frozen=True)
class PageGeometry:
    """Text block of the rendered page, in TeX points."""

    text_width_pt: float
    text_height_pt: float


@dataclass(frozen=True)
class FigureLegibility:
    """One figure's smallest label, measured through to the rendered page.

    Attributes:
        label: The ``fig:`` cross-reference label.
        filename: The rasterized PNG filename.
        canvas_width_px: SVG canvas width, equal to the PNG pixel width.
        canvas_height_px: SVG canvas height, equal to the PNG pixel height.
        min_font_px: Smallest ``font-size`` the generator emitted, canvas units.
        width_fraction: The ``width=NN%`` attribute on the markdown embed.
        rendered_width_pt: Width the raster occupies on the page.
        height_bound: True when the height cap, not the declared width,
            determined ``rendered_width_pt`` — the shrink-the-whole-plate case.
        rendered_min_pt: ``min_font_px`` as it lands on the page.
    """

    label: str
    filename: str
    canvas_width_px: float
    canvas_height_px: float
    min_font_px: float
    width_fraction: float
    rendered_width_pt: float
    height_bound: bool
    rendered_min_pt: float

    @property
    def legible(self) -> bool:
        """True when the smallest label clears :data:`MIN_LEGIBLE_PT`."""

        return self.rendered_min_pt >= MIN_LEGIBLE_PT


def parse_page_geometry(config_text: str) -> PageGeometry:
    """Derive the page text block from a manuscript ``config.yaml`` body.

    The ``metadata.geometry`` string is the same one handed to the LaTeX
    ``geometry`` package, so parsing it here reproduces the renderer's own
    numbers without requiring a build.
    """

    match = _GEOMETRY_RE.search(config_text)
    if match is None:
        raise ValueError("config.yaml declares no metadata.geometry string")
    margins = {key: float(value) for key, value in _GEOMETRY_KEY_RE.findall(match.group(1))}
    missing = {"left", "right", "top", "bottom"} - set(margins)
    if missing:
        raise ValueError(f"geometry string omits margin(s): {sorted(missing)}")
    width_in = PAPER_WIDTH_IN - margins["left"] - margins["right"]
    height_in = PAPER_HEIGHT_IN - margins["top"] - margins["bottom"]
    return PageGeometry(
        text_width_pt=width_in * TEX_PT_PER_INCH,
        text_height_pt=height_in * TEX_PT_PER_INCH,
    )


def parse_figure_height_fraction(config_text: str) -> float:
    """Return the configured figure height cap, or the template default.

    The renderer reads ``rendering.figure_height_fraction``; a project that
    never declares it silently inherits
    :data:`DEFAULT_FIGURE_HEIGHT_FRACTION`, which is strict enough to shrink a
    tall plate below legibility. Fail closed on a key placed outside the
    ``rendering:`` block, because the renderer would ignore it there.
    """

    if _RENDERING_BLOCK_RE.search(config_text) is None:
        return DEFAULT_FIGURE_HEIGHT_FRACTION
    match = _HEIGHT_FRACTION_RE.search(config_text)
    if match is None:
        return DEFAULT_FIGURE_HEIGHT_FRACTION
    return float(match.group(1))


def declared_width_fractions(manuscript_dir: Path) -> dict[str, float]:
    """Map each ``fig:`` label to the width fraction its embed declares.

    A label embedded without an explicit ``width=`` attribute maps to ``1.0``,
    matching Pandoc's ``width=\\linewidth`` default.
    """

    fractions: dict[str, float] = {}
    for path in sorted(manuscript_dir.glob("*.md")):
        for label, attributes in _EMBED_RE.findall(path.read_text(encoding="utf-8")):
            width = _WIDTH_ATTR_RE.search(attributes)
            fractions[label] = float(width.group(1)) / 100.0 if width else 1.0
    return fractions


def min_font_px(svg_text: str) -> float:
    """Return the smallest ``font-size`` in an SVG document, in canvas units."""

    sizes = [float(size) for size in _FONT_SIZE_RE.findall(svg_text)]
    if not sizes:
        raise ValueError("SVG document carries no font-size declaration")
    return min(sizes)


def svg_canvas_size(svg_text: str) -> tuple[float, float]:
    """Return the ``(width, height)`` of an SVG document's canvas."""

    match = _SVG_SIZE_RE.search(svg_text)
    if match is None:
        raise ValueError("SVG document declares no canvas width and height")
    return float(match.group(1)), float(match.group(2))


def png_dimensions(png_bytes: bytes) -> tuple[int, int]:
    """Return ``(width, height)`` from a PNG's IHDR chunk."""

    if png_bytes[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG file")
    return struct.unpack(">II", png_bytes[16:24])


def rendered_width_pt(
    canvas_width_px: float,
    canvas_height_px: float,
    width_fraction: float,
    geometry: PageGeometry,
    height_fraction: float,
) -> tuple[float, bool]:
    """Return the on-page raster width and whether the height cap bound it.

    Reproduces ``keepaspectratio``: the declared width wins unless honouring it
    would exceed the height cap, in which case the plate is scaled down until
    its height fits and every label shrinks with it.
    """

    by_width = width_fraction * geometry.text_width_pt
    cap_pt = height_fraction * geometry.text_height_pt
    by_height = cap_pt * canvas_width_px / canvas_height_px
    if by_height < by_width:
        return by_height, True
    return by_width, False


def measure_figure(
    label: str,
    svg_text: str,
    png_bytes: bytes,
    width_fraction: float,
    geometry: PageGeometry,
    height_fraction: float,
) -> FigureLegibility:
    """Measure one figure's smallest rendered label.

    The PNG dimensions are authoritative for the canvas because they are what
    LaTeX actually scales; the SVG canvas is cross-checked against them so a
    rasterizer that silently resamples cannot make this measurement lie.
    """

    png_width, png_height = png_dimensions(png_bytes)
    svg_width, svg_height = svg_canvas_size(svg_text)
    if (svg_width, svg_height) != (float(png_width), float(png_height)):
        raise ValueError(
            f"{label}: rasterized PNG {png_width}x{png_height} does not match "
            f"SVG canvas {svg_width:g}x{svg_height:g}; the point-size derivation "
            "assumes a 1:1 rasterization"
        )
    smallest = min_font_px(svg_text)
    width_pt, height_bound = rendered_width_pt(
        png_width, png_height, width_fraction, geometry, height_fraction
    )
    return FigureLegibility(
        label=label,
        filename=FIGURE_TEXT[label]["filename"],
        canvas_width_px=float(png_width),
        canvas_height_px=float(png_height),
        min_font_px=smallest,
        width_fraction=width_fraction,
        rendered_width_pt=width_pt,
        height_bound=height_bound,
        rendered_min_pt=smallest * width_pt / png_width,
    )


def measure_figure_set(project_root: Path) -> tuple[FigureLegibility, ...]:
    """Measure every registered figure, sorted by label.

    Reads the built ``output/figures/`` artefacts, the manuscript embeds, and
    ``manuscript/config.yaml``. Fails closed when a registered figure has no
    embed, no rendered SVG, or no rendered PNG: an unmeasurable figure is a gap
    in the gate, not a pass.
    """

    root = project_root.resolve()
    config_text = (root / "manuscript" / "config.yaml").read_text(encoding="utf-8")
    geometry = parse_page_geometry(config_text)
    height_fraction = parse_figure_height_fraction(config_text)
    fractions = declared_width_fractions(root / "manuscript")
    figures_dir = root / "output" / "figures"

    measured: list[FigureLegibility] = []
    for label in sorted(GENERATORS):
        if label not in fractions:
            raise ValueError(f"{label} is registered but embedded in no manuscript file")
        filename = FIGURE_TEXT[label]["filename"]
        png_path = figures_dir / filename
        svg_path = figures_dir / filename.replace(".png", ".svg")
        if not png_path.is_file() or not svg_path.is_file():
            raise FileNotFoundError(
                f"{label}: build the figures first — expected {svg_path} and {png_path}"
            )
        measured.append(
            measure_figure(
                label,
                svg_path.read_text(encoding="utf-8"),
                png_path.read_bytes(),
                fractions[label],
                geometry,
                height_fraction,
            )
        )
    return tuple(measured)


def illegible_figures(project_root: Path) -> tuple[FigureLegibility, ...]:
    """Return every measured figure whose smallest label falls below the floor."""

    return tuple(figure for figure in measure_figure_set(project_root) if not figure.legible)
