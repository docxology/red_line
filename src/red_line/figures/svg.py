"""SVG construction helpers for deterministic figures."""

from __future__ import annotations

import html
import textwrap

from .theme import GRID, INK, MIN_FONT_PX, MUTED, PAPER, WIDTH


def esc(value: object) -> str:
    """Escape a value for XML text or attributes."""

    return html.escape(str(value), quote=True)


def text_lines(text: str, width: int) -> list[str]:
    """Wrap text deterministically for diagram labels."""

    return textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False) or [""]


def label(
    x: float,
    y: float,
    text: str,
    *,
    size: int = 18,
    fill: str = INK,
    weight: str = "400",
    anchor: str = "start",
) -> str:
    """Emit one text run, never below the legibility floor.

    The floor is applied here rather than trusted at every call site: a figure
    that draws sub-floor text ships an accessibility claim it cannot honour at
    print scale, and there are over a hundred call sites. Clamping is not the
    gate — ``tests/test_figure_legibility.py`` measures the emitted SVG against
    the real page geometry and can still fail if the canvas or the manuscript's
    declared embed width changes.
    """

    drawn = max(size, MIN_FONT_PX)
    return f'<text x="{x}" y="{y}" fill="{fill}" font-family="Arial,Helvetica,sans-serif" font-size="{drawn}px" font-weight="{weight}" text-anchor="{anchor}">{esc(text)}</text>'


def paragraph(
    x: float,
    y: float,
    text: str,
    *,
    width: int = 50,
    size: int = 16,
    leading: int = 22,
    fill: str = MUTED,
    weight: str = "400",
) -> str:
    """Emit a wrapped text block whose leading tracks the floor-clamped size."""

    drawn = max(size, MIN_FONT_PX)
    step = max(leading, drawn + 6)
    out = []
    for index, line in enumerate(text_lines(text, width)):
        out.append(label(x, y + index * step, line, size=drawn, fill=fill, weight=weight))
    return "".join(out)


def rect(
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    fill: str = PAPER,
    stroke: str = GRID,
    radius: int = 14,
    dash: bool = False,
    width: float = 1.5,
) -> str:
    dash_attr = ' stroke-dasharray="8 7"' if dash else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"{dash_attr}/>'


def line(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    *,
    stroke: str = GRID,
    width: float = 2,
    dash: bool = False,
    arrow: bool = False,
    opacity: float = 1,
) -> str:
    dash_attr = ' stroke-dasharray="7 6"' if dash else ""
    marker = ' marker-end="url(#arrow)"' if arrow else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{width}" opacity="{opacity}"{dash_attr}{marker}/>'


def path(
    d: str,
    *,
    stroke: str = GRID,
    width: float = 2,
    fill: str = "none",
    dash: bool = False,
    opacity: float = 1,
) -> str:
    dash_attr = ' stroke-dasharray="8 7"' if dash else ""
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" opacity="{opacity}" stroke-linecap="round" stroke-linejoin="round"{dash_attr}/>'


def circle(cx: float, cy: float, r: float, *, fill: str, stroke: str = PAPER, width: float = 2) -> str:
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>'


def svg_document(title: str, description: str, body: str, *, height: int) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" role="img" aria-labelledby="title desc">
  <title id="title">{esc(title)}</title>
  <desc id="desc">{esc(description)}</desc>
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{MUTED}"/></marker>
    <style>text {{ dominant-baseline: alphabetic; }} .hairline {{ shape-rendering: crispEdges; }}</style>
  </defs>
  <rect width="100%" height="100%" fill="{PAPER}"/>
  {body}
</svg>
'''


_HEADER_SUBTITLE_WIDTH = 108
_HEADER_SUBTITLE_TOP = 88
_HEADER_SUBTITLE_LEADING = 22


def figure_header_notice_y(subtitle: str) -> float:
    """Baseline for the non-measurement notice, below the wrapped subtitle.

    Computed rather than fixed: a subtitle that wraps to two lines used to
    overprint the notice, which is exactly the kind of silent degradation the
    figure set claims not to have.
    """

    lines = len(text_lines(subtitle, _HEADER_SUBTITLE_WIDTH))
    return _HEADER_SUBTITLE_TOP + (lines - 1) * _HEADER_SUBTITLE_LEADING + 28


def figure_header(title: str, subtitle: str) -> str:
    return (
        label(64, 58, title, size=28, weight="700")
        + paragraph(
            64,
            _HEADER_SUBTITLE_TOP,
            subtitle,
            width=_HEADER_SUBTITLE_WIDTH,
            size=16,
            leading=_HEADER_SUBTITLE_LEADING,
        )
        + label(
            64,
            figure_header_notice_y(subtitle),
            "SOURCE-DRIVEN SCHEMATIC · NOT AN EMPIRICAL MEASUREMENT",
            size=16,
            fill=MUTED,
            weight="700",
        )
    )
