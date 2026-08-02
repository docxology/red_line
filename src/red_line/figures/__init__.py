"""Public API for deterministic manuscript figures."""

from __future__ import annotations

from .build import build_figures
from .registry import GENERATORS
from .text import FIGURE_TEXT

__all__ = [
    "FIGURE_TEXT",
    "GENERATORS",
    "build_figures",
]
