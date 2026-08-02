"""Regression tests for deterministic manuscript figures."""

from __future__ import annotations

import json
import re
import struct
import subprocess
import sys
from pathlib import Path

import pytest

from red_line.analysis.monotonicity import run_monotonicity_sweep
from red_line.analysis.registry_metrics import exemption_evidence_matrix, scope_token_frequency
from red_line.figures import FIGURE_TEXT, build_figures
from red_line.figures.plates_analysis import evidence_summary
from red_line.figures.rasterize import resolve_rasterizer
from red_line.model import EvidenceKind, EvidenceRecord, EvidenceStatus
from red_line.registry import PERSONAL_RED_LINES


def _png_dimensions(path: Path) -> tuple[int, int]:
    header = path.read_bytes()
    assert header[:8] == b"\x89PNG\r\n\x1a\n"
    return struct.unpack(">II", header[16:24])


def _write_executable(path: Path, contents: str) -> Path:
    path.write_text(contents, encoding="utf-8")
    path.chmod(path.stat().st_mode | 0o111)
    return path


def test_cover_asset_is_configured_and_sized_for_the_title_page() -> None:
    cover = Path("manuscript/assets/cover/red_line_cover.png")
    hero = Path("manuscript/assets/cover/red_line_hero.png")
    config = Path("manuscript/config.yaml").read_text(encoding="utf-8")
    provenance = Path("manuscript/assets/cover/README.md").read_text(encoding="utf-8")

    assert cover.exists()
    assert hero.exists()
    assert _png_dimensions(cover) == (1024, 1536)
    assert _png_dimensions(hero) == (1672, 941)
    assert 'image: "assets/cover/red_line_cover.png"' in config
    assert 'editorial_hero_image: "assets/cover/red_line_hero.png"' in config
    assert "portrait" in provenance.lower()
    assert "provenance" in provenance.lower()


def test_pdf_geometry_is_explicitly_tightened_in_project_config() -> None:
    config = Path("manuscript/config.yaml").read_text(encoding="utf-8")

    assert 'geometry: "left=0.33in,right=0.33in,top=0.55in,bottom=0.55in"' in config


def test_build_figures_writes_registered_pngs_and_svg_sources(tmp_path: Path) -> None:
    written = build_figures(tmp_path)
    figures = tmp_path / "output" / "figures"
    registry = json.loads((figures / "figure_registry.json").read_text(encoding="utf-8"))

    assert len(written) == len(FIGURE_TEXT)
    assert "fig:improvement-method-loop" in FIGURE_TEXT
    assert "fig:boundary-instrument-plate" in FIGURE_TEXT
    assert "fig:scholarship-intake-bridge" in FIGURE_TEXT
    assert "fig:tier-monotonicity-lattice" in FIGURE_TEXT
    assert registry["schema_version"] == "1.1"
    assert registry["figure_count"] == len(FIGURE_TEXT)
    assert {record["label"] for record in registry["figures"]} == set(FIGURE_TEXT)
    by_label = {record["label"]: record for record in registry["figures"]}
    assert by_label["fig:scholarship-intake-bridge"]["source_ids"] == [
        "haraway1988situated",
        "jasanoff2003humility",
        "costanzachock2020design",
        "dignazioklein2020data",
    ]
    assert by_label["fig:governance-architecture"]["generated_by"] == "red_line.figures::build_figures"
    assert by_label["fig:exemption-evidence-matrix"]["source_ids"] == []
    assert by_label["fig:outcome-coverage-plate"]["source_ids"] == []
    assert by_label["fig:tier-monotonicity-lattice"]["source_ids"] == []
    for path in written:
        assert path.exists()
        assert path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
        assert path.with_suffix(".svg").exists()


def test_build_figures_is_byte_deterministic(tmp_path: Path) -> None:
    build_figures(tmp_path)
    figures = tmp_path / "output" / "figures"
    first = {path.name: path.read_bytes() for path in figures.iterdir()}

    build_figures(tmp_path)
    second = {path.name: path.read_bytes() for path in figures.iterdir()}

    assert second == first


def test_resolve_rasterizer_returns_the_rsvg_convert_found_on_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bin_directory = tmp_path / "bin"
    bin_directory.mkdir()
    rasterizer = _write_executable(bin_directory / "rsvg-convert", "#!/bin/sh\nexit 0\n")

    monkeypatch.setenv("PATH", str(bin_directory))

    assert resolve_rasterizer() == str(rasterizer)


def test_resolve_rasterizer_fails_closed_when_path_holds_no_rasterizer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    empty_path = tmp_path / "empty-path"
    empty_path.mkdir()

    monkeypatch.setenv("PATH", str(empty_path))

    with pytest.raises(RuntimeError, match="rsvg-convert"):
        resolve_rasterizer()


def test_build_figures_fails_loudly_when_rasterizer_skips_png_write(tmp_path: Path) -> None:
    rasterizer = _write_executable(tmp_path / "no-output-rsvg-convert", "#!/bin/sh\nexit 0\n")

    with pytest.raises(RuntimeError, match="did not produce a non-empty PNG"):
        build_figures(tmp_path, rasterizer=rasterizer)


def test_build_figures_cli_reports_generated_count() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/build_figures.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout.strip() == f"generated {len(FIGURE_TEXT)} figures under output/figures"


def test_evidence_summary_reports_no_records() -> None:
    assert evidence_summary(()) == "evidence: none recorded"


def test_evidence_summary_reports_all_verified_records() -> None:
    records = tuple(
        EvidenceRecord(
            kind=kind,
            reference=f"fixture://figures/{kind.value}",
            summary=f"fixture record for {kind.value}",
            status=EvidenceStatus.VERIFIED,
            recorded_on="2026-07-15",
        )
        for kind in (EvidenceKind.PURPOSE, EvidenceKind.END_USE)
    )

    assert evidence_summary(records) == "evidence: 2 VERIFIED fixture records"


def test_evidence_summary_reports_partial_verification() -> None:
    records = (
        EvidenceRecord(
            kind=EvidenceKind.PURPOSE,
            reference="fixture://figures/purpose",
            summary="fixture record for purpose",
            status=EvidenceStatus.VERIFIED,
            recorded_on="2026-07-15",
        ),
        EvidenceRecord(
            kind=EvidenceKind.END_USE,
            reference="fixture://figures/end-use",
            summary="fixture record for end use",
            status=EvidenceStatus.UNVERIFIED,
            recorded_on="2026-07-15",
        ),
    )

    assert evidence_summary(records) == "evidence: 1 of 2 fixture records VERIFIED"


def test_manuscript_defines_every_registered_figure() -> None:
    manuscript = "\n".join(path.read_text(encoding="utf-8") for path in Path("manuscript").glob("*.md"))
    defined = set(re.findall(r"#(fig:[a-z0-9-]+)", manuscript))
    assert defined == set(FIGURE_TEXT)


_NUMBER_WORDS = {3: "three", 5: "five", 7: "seven", 9: "nine"}


def test_monotonicity_embed_numbers_re_derive_from_the_live_sweep() -> None:
    """Every number in the 05 lattice embed/prose equals the executed report.

    Binds EVERY occurrence (prose paragraph and figure caption both carry the
    numbers), so a single-site drift cannot hide behind its twin.
    """
    # Flattened so a line wrap between two words of a bound phrase cannot make
    # an assertion silently stop matching — the prose is hard-wrapped at ~78.
    body = " ".join(Path("manuscript/05_deployment_tiers.md").read_text(encoding="utf-8").split())
    report = run_monotonicity_sweep()
    assert report.monotone and report.inversion_count == 0
    slot_claims = re.findall(r"all (\d+) line/keyword slots \((\d+) distinct tokens\)", body)
    assert len(slot_claims) >= 2, "prose and caption must both state the sweep size"
    assert all(int(slots) == report.keyword_count for slots, _ in slot_claims)
    assert all(int(distinct) == report.distinct_keyword_count for _, distinct in slot_claims)
    # The two numbers must stay distinguishable: a registry with no shared
    # token would make them equal and this sentence vacuous.
    assert report.keyword_count > report.distinct_keyword_count
    assert "`handoff` and `provenance` are each declared by" in body
    shared = sorted(
        token for token, count in scope_token_frequency().items() if count > 1
    )
    assert shared == ["handoff", "provenance"]
    run_claims = re.findall(r"(\d+) executed evaluations", body)
    assert len(run_claims) >= 2, "prose and caption must both state the run count"
    assert all(int(claim) == report.evaluation_count for claim in run_claims)
    assert f"{_NUMBER_WORDS[len(PERSONAL_RED_LINES)]} current lines" in body
    assert f"{_NUMBER_WORDS[len(report.tiers)]} deployment tiers" in body
    # "zero inversions" is only honest while the executed count is zero.
    assert report.inversion_count == 0
    assert body.count("zero inversions") >= 2, "prose and caption must both state it"


def test_governance_embed_enumerates_the_six_drawn_stages() -> None:
    """The 03 embed matches the six boxes the generator draws — no phantom node."""
    body = Path("manuscript/03_adaptation_thesis.md").read_text(encoding="utf-8")
    assert f"{_NUMBER_WORDS[len(PERSONAL_RED_LINES)]}-line registry beacon" in body
    assert "draws six stages" in body
    for stage in (
        "registry beacon",
        "action-declaration intake",
        "evidence gate",
        "policy match",
        "transparency tally",
        "canary check",
    ):
        assert stage in body, stage
    assert "self-review finding" not in body


def test_derived_caption_counts_match_live_analysis_sources() -> None:
    """FIGURE_TEXT numbers that mirror live data really are the live values."""
    report = run_monotonicity_sweep()
    lattice = FIGURE_TEXT["fig:tier-monotonicity-lattice"]
    assert f"{report.keyword_count} line/keyword slots" in lattice["caption"]
    assert f"{report.distinct_keyword_count} distinct tokens" in lattice["caption"]
    assert f"{report.evaluation_count} evaluations" in lattice["caption"]
    assert f"{report.inversion_count} inversions" in lattice["caption"]
    matrix_rows = exemption_evidence_matrix()
    assert (
        f"Matrix of {len(matrix_rows)} typed exemptions"
        in FIGURE_TEXT["fig:exemption-evidence-matrix"]["alt"]
    )
    assert f"{len(PERSONAL_RED_LINES)}-line beacon" in FIGURE_TEXT["fig:governance-architecture"]["caption"]
    assert (
        f"{len(PERSONAL_RED_LINES)}-line commitment boundary"
        in FIGURE_TEXT["fig:boundary-instrument-plate"]["caption"]
    )


def test_visualization_brief_module_table_matches_generator_ownership() -> None:
    """Each module row in the brief states how many plates that module owns.

    The row for ``plates_analysis.py`` said "three plates" and named three
    while the module owned five — the composition profile and the collision
    grid were added to the module and to the brief's opening paragraph, but the
    module table two screens down was left behind. Counts stated as words in a
    table are claims about `GENERATORS`, so they are recomputed here.
    """

    from collections import Counter

    from red_line.figures.registry import GENERATORS

    words = {3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight"}
    owned = Counter(generator.__module__.rsplit(".", 1)[-1] for generator in GENERATORS.values())
    brief = (Path(__file__).resolve().parents[1] / "docs" / "visualization-briefs.md").read_text(
        encoding="utf-8"
    )

    assert set(owned) == {"diagrams", "plates_analysis", "plates_scholarship"}
    assert sum(owned.values()) == len(GENERATORS)
    for module, noun in (
        ("plates_scholarship", "plates"),
        ("plates_analysis", "plates"),
        ("diagrams", "schematics"),
    ):
        row = next(line for line in brief.splitlines() if f"figures/{module}.py" in line)
        expected = f"The {words[owned[module]]} {noun}"
        assert expected in row, f"{module} row must say {expected!r}; it owns {owned[module]}"
        for count, word in words.items():
            if count != owned[module]:
                assert f"The {word} {noun}" not in row, f"{module} row still says {word}"
