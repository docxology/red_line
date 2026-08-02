"""Figure build orchestration for deterministic manuscript figures."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .rasterize import resolve_rasterizer
from .registry import GENERATORS
from .text import FIGURE_TEXT


def build_figures(project_root: Path, *, rasterizer: str | Path | None = None) -> list[Path]:
    """Write all SVG/PNG figures and their registry; return generated PNG paths."""

    root = project_root.resolve()
    figures_dir = root / "output" / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    converter = str(rasterizer) if rasterizer is not None else resolve_rasterizer()
    written: list[Path] = []
    records: list[dict[str, object]] = []
    for figure_label, generator in GENERATORS.items():
        spec = FIGURE_TEXT[figure_label]
        svg_path = figures_dir / spec["filename"].replace(".png", ".svg")
        png_path = figures_dir / spec["filename"]
        svg_path.write_text(generator(), encoding="utf-8")
        subprocess.run([converter, str(svg_path), "--output", str(png_path)], check=True)
        if not png_path.exists() or png_path.stat().st_size == 0:
            raise RuntimeError(
                f"rasterizer {converter} did not produce a non-empty PNG for {figure_label}: {png_path}"
            )
        written.append(png_path)
        records.append(
            {
                "label": figure_label,
                "filename": spec["filename"],
                "caption": spec["caption"],
                "alt": spec["alt"],
                "source": spec["source"],
                "source_ids": list(spec.get("source_ids", ())),
                "generated_by": "red_line.figures::build_figures",
                "format": "PNG rasterized from deterministic SVG",
            }
        )
    (figures_dir / "figure_registry.json").write_text(
        json.dumps(
            {"schema_version": "1.1", "figure_count": len(records), "figures": records},
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    return written
