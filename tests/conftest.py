"""Session setup for the Red Line suite.

``output/`` is ignored and disposable, so a clean checkout — or a render host
that wipes generated output before running the tests — arrives with no
``output/figures``. Eleven gates in this suite read that directory: the visual
binding validators, the figure legibility floor, and the release manifest's
figure hashes. Without this fixture they fail for a reason that has nothing to
do with the property under test, which is how a fresh clone reports eighteen
failures against a source tree that is in fact correct.

The rebuild uses this project's own deterministic builder and nothing else. It
is a rebuild of an ignored artifact, not a fixture: the same bytes the
committed registry already pins. If the builder cannot run, the gates that
need figures are left to fail loudly rather than being skipped, because a
broken figure build is a real defect and must not be masked here.
"""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
FIGURES = ROOT / "output" / "figures"
REGISTRY = FIGURES / "figure_registry.json"


@pytest.fixture(scope="session", autouse=True)
def _ensure_generated_figures() -> None:
    """Rebuild ``output/figures`` when the ignored directory is absent."""

    if REGISTRY.exists():
        return

    from red_line.figures import build_figures

    build_figures(ROOT)
