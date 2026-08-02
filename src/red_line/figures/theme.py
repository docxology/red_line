"""Shared visual constants for deterministic figures."""

from __future__ import annotations

WIDTH = 1400

#: Smallest font size, in canvas units, any figure may draw.
#:
#: Derived, not chosen: a canvas unit becomes a rendered point through
#: ``pt = px * rendered_width_pt / WIDTH``. The narrowest embed in the
#: manuscript declares ``width=95%`` of a 553.59pt text block, so clearing the
#: 6pt legibility floor of :mod:`red_line.figures.legibility` needs
#: ``6 * 1400 / (0.95 * 553.59) = 15.97`` units. Sixteen is the smallest whole
#: value that clears it. ``tests/test_figure_legibility.py`` re-derives this
#: number from the live geometry rather than trusting the comment.
MIN_FONT_PX = 16

INK = "#17202a"
MUTED = "#536170"
PAPER = "#fbfaf7"
GRID = "#d9dee3"
TEAL = "#0f766e"
BLUE = "#2563eb"
AMBER = "#b45309"
RED = "#b42318"
PALE_TEAL = "#dff3ef"
PALE_BLUE = "#e7efff"
PALE_AMBER = "#fff2d9"
PALE_RED = "#fde7e5"

# Neutral / structural
WHITE = "#ffffff"
TABLE_HEADER = "#f5f7f9"
TABLE_ROW_ALT = "#fcfcfb"
TABLE_ROW_ALT2 = "#f7f8f9"
MUTED_FILL = "#eef0f2"
MUTED_FILL_ALT = "#f5f5f3"

# Large background areas (boundary panels, row-group backgrounds)
PALE_TEAL_BG = "#f2f7f6"
PALE_AMBER_BG = "#fff8e9"

# Strokes for dashed boundary panels
TEAL_STROKE = "#a8cbc5"
GOLD_STROKE = "#d5b36a"

# Light cream accent
CREAM = "#fffdf8"
