"""Synthetic-tree branch coverage for the packaged contracts validators."""

from __future__ import annotations

import copy
from contextlib import contextmanager
from importlib.metadata import PackageNotFoundError
import json
from pathlib import Path
import shutil

from red_line import PERSONAL_RED_LINES
from red_line.contracts.claim_register import validate_claim_register
from red_line.contracts.proposed_red_lines import (
    LIVE_SCOPE_TOKENS,
    _proposed_scope_errors,
    validate_proposed_red_lines,
)
from red_line.contracts.source_claims import validate_source_claims
from red_line.contracts.release_bindings import validate_release_bindings
import red_line.contracts.release_bindings as release_bindings_module
from red_line.contracts.visual_bindings import validate_visual_bindings
import red_line.contracts.visual_bindings as visual_bindings_module

ROOT = Path(__file__).resolve().parents[2]


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: object) -> None:
    _write(path, json.dumps(payload, indent=2) + "\n")


def _copy_path(destination_root: Path, relative: str) -> None:
    source = ROOT / relative
    destination = destination_root / relative
    if source.is_dir():
        shutil.copytree(source, destination)
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


#: Rendered surfaces are written by the external render engine; nothing in this
#: repository produces them, so in a source-only checkout they are absent by
#: construction and copying them out of ``ROOT`` fails in setup.
#:
#: These branch-coverage tests do not need the rendered publication. What
#: ``validate_release_bindings`` asks of these two paths is only that a file is
#: there and that it carries the package version — the drift each test exercises
#: is then written into the synthetic tree by the test itself. So the surfaces
#: are always built here rather than copied: a fixture that is sometimes the
#: real artifact and sometimes a stand-in would make the same assertion mean two
#: different things depending on whether a render happened to have run.
_RENDERED_SURFACES: dict[str, str] = {
    "output/web/index.html": (
        '<!doctype html>\n<html lang="en">\n<head>\n'
        '<meta name="generator" content="red_line {version}">\n'
        "<title>Red Line</title>\n</head>\n<body></body>\n</html>\n"
    ),
    "output/pdf/_combined_manuscript.md": ("---\nversion: {version}\n---\n\n# Red Line\n"),
}


def _write_rendered_surface(destination_root: Path, relative: str) -> None:
    body = _RENDERED_SURFACES[relative]
    _write(destination_root / relative, body.format(version=release_bindings_module.__version__))


def _copy_release_tree(destination_root: Path) -> None:
    for relative in (
        "README.md",
        "CITATION.cff",
        "pyproject.toml",
        "manuscript/09_red_lines.md",
        "manuscript/config.yaml",
        ".agents/skills/personal-red-lines/SKILL.md",
        "tests/fixtures/canary_committed.json",
    ):
        _copy_path(destination_root, relative)
    for relative in _RENDERED_SURFACES:
        _write_rendered_surface(destination_root, relative)


def _copy_visual_tree(destination_root: Path) -> None:
    for relative in (
        "docs/visualization-briefs.md",
        "manuscript",
        "data/source_claims.json",
        "output/figures",
    ):
        _copy_path(destination_root, relative)


@contextmanager
def _override_attr(target: object, name: str, value):
    original = getattr(target, name)
    setattr(target, name, value)
    try:
        yield
    finally:
        setattr(target, name, original)


@contextmanager
def _override_figure_spec(label: str, **changes):
    original = copy.deepcopy(visual_bindings_module.FIGURE_TEXT[label])
    updated = copy.deepcopy(original)
    updated.update(changes)
    visual_bindings_module.FIGURE_TEXT[label] = updated
    try:
        yield updated
    finally:
        visual_bindings_module.FIGURE_TEXT[label] = original


def test_validate_source_claims_load_error_has_context(tmp_path: Path):
    errors = validate_source_claims(tmp_path)
    assert len(errors) == 1
    assert errors[0].startswith("source ledger cannot be loaded:")


def test_validate_source_claims_rejects_non_list_records(tmp_path: Path):
    _write_json(tmp_path / "data" / "source_claims.json", {"schema_version": "1.0", "records": {}})
    _write(tmp_path / "manuscript" / "references.bib", "")
    _write(tmp_path / "docs" / "research-method.md", "")
    assert validate_source_claims(tmp_path) == ["source ledger records must be a list"]


def test_validate_source_claims_rejects_non_object_figure_bindings(tmp_path: Path):
    _write_json(
        tmp_path / "data" / "source_claims.json",
        {"schema_version": "1.0", "records": [], "figure_bindings": []},
    )
    _write(tmp_path / "manuscript" / "references.bib", "")
    _write(tmp_path / "manuscript" / "01_text.md", "")
    _write(tmp_path / "docs" / "research-method.md", "")
    errors = validate_source_claims(tmp_path)
    assert "source ledger figure_bindings must be an object" in errors


def test_validate_source_claims_reports_structural_errors(tmp_path: Path):
    _write_json(
        tmp_path / "data" / "source_claims.json",
        {
            "schema_version": "0.9",
            "records": [
                "bad",
                {"source_id": "   "},
                {
                    "source_id": "dup",
                    "edition_locator": "",
                    "verified_url": "https://wrong.example/one",
                    "claim_class": "",
                    "transferred_question": "",
                    "stopping_boundary": "",
                    "uses": [],
                },
                {
                    "source_id": "dup",
                    "edition_locator": "pp. 1-2",
                    "verified_url": "https://wrong.example/two",
                    "claim_class": "descriptive",
                    "transferred_question": "question",
                    "stopping_boundary": "boundary",
                    "uses": ["summary"],
                },
                {
                    "source_id": "extra",
                    "edition_locator": "pp. 3-4",
                    "verified_url": "https://extra.example",
                    "claim_class": "descriptive",
                    "transferred_question": "question",
                    "stopping_boundary": "boundary",
                    "uses": ["summary"],
                },
            ],
            "figure_bindings": {
                "": ["dup"],
                "figure-empty": [],
                "figure-bad": ["", "dup", "dup", "missing"],
            },
        },
    )
    _write(
        tmp_path / "manuscript" / "references.bib",
        "@article{dup,\n  url = {https://expected.example}\n}\n"
        "@article{known,\n  title = {Known without URL}\n}\n",
    )
    _write(tmp_path / "manuscript" / "01_text.md", "Cites @dup, @known, @unknown, and @fig:ignore.\n")
    _write(tmp_path / "docs" / "research-method.md", "\n")
    errors = validate_source_claims(tmp_path)
    assert "source ledger schema_version must be 1.0" in errors
    assert "source ledger record is not an object" in errors
    assert "source ledger record has no source_id" in errors
    assert "duplicate source_id: dup" in errors
    assert "dup: missing edition_locator" in errors
    assert "dup: missing verified_url" not in errors
    assert "dup: missing claim_class" in errors
    assert "dup: missing transferred_question" in errors
    assert "dup: missing stopping_boundary" in errors
    assert "dup: uses must be a non-empty list" in errors
    assert "dup: verified_url differs from references.bib" in errors
    assert "dup: verified_url is absent from docs/research-method.md" in errors
    assert "source ledger figure binding has no figure label" in errors
    assert "figure-empty: figure binding must be a non-empty list" in errors
    assert "figure-bad: figure binding source ids must be non-empty strings" in errors
    assert "figure-bad: figure binding contains duplicate source ids" in errors
    assert "figure-bad: figure binding references unknown source id missing" in errors
    assert "manuscript cites unknown bibliography keys: ['unknown']" in errors
    assert "known: cited bibliography entry has no verified URL" in errors
    assert "cited sources missing from ledger: ['known', 'unknown']" in errors
    assert "ledger sources missing from bibliography: ['extra']" in errors


def test_validate_claim_register_load_error_has_context(tmp_path: Path):
    errors = validate_claim_register(tmp_path)
    assert len(errors) == 1
    assert errors[0].startswith("claim register cannot be read:")


def test_validate_claim_register_rejects_non_list_claims(tmp_path: Path):
    _write_json(
        tmp_path / "data" / "claim_register.json",
        {
            "schema_version": "0.9",
            "claim_classes": [],
            "verification_modes": ["duplicate", "duplicate"],
            "claims": {},
        },
    )
    errors = validate_claim_register(tmp_path)
    assert "claim register schema_version must be 1.0" in errors
    assert "claim_classes must be a non-empty unique list" in errors
    assert "verification_modes must be a non-empty unique list" in errors
    assert "claims must be a non-empty list" in errors


def test_validate_claim_register_reports_missing_document(tmp_path: Path):
    _write_json(
        tmp_path / "data" / "claim_register.json",
        {
            "schema_version": "1.0",
            "claim_classes": ["class-a"],
            "verification_modes": ["mode-a"],
            "claims": [
                {
                    "claim_id": "CLM-001",
                    "claim": "Claim",
                    "status": "live",
                    "stopping_point": "stop",
                    "claim_class": "class-a",
                    "verification_mode": "mode-a",
                    "supporting_surface": ["docs"],
                }
            ],
        },
    )
    errors = validate_claim_register(tmp_path)
    assert any(error.startswith("claim register document cannot be read:") for error in errors)


def test_validate_claim_register_reports_structural_and_binding_errors(tmp_path: Path):
    _write_json(
        tmp_path / "data" / "claim_register.json",
        {
            "schema_version": "1.0",
            "claim_classes": ["class-a"],
            "verification_modes": ["mode-a"],
            "claims": [
                "bad",
                {
                    "claim_id": None,
                    "claim": "",
                    "status": "",
                    "stopping_point": "",
                    "claim_class": "other-class",
                    "verification_mode": "other-mode",
                    "supporting_surface": [],
                },
                {
                    "claim_id": "CLM-001",
                    "claim": "Claim one",
                    "status": "live",
                    "stopping_point": "stop",
                    "claim_class": "class-a",
                    "verification_mode": "mode-a",
                    "supporting_surface": ["docs"],
                },
                {
                    "claim_id": "CLM-001",
                    "claim": "Claim duplicate",
                    "status": "live",
                    "stopping_point": "stop",
                    "claim_class": "class-a",
                    "verification_mode": "mode-a",
                    "supporting_surface": ["docs"],
                },
                {
                    "claim_id": "CLM-002",
                    "claim": "Claim two",
                    "status": "live",
                    "stopping_point": "stop",
                    "claim_class": "class-a",
                    "verification_mode": "mode-a",
                    "supporting_surface": ["docs"],
                },
            ],
        },
    )
    _write(
        tmp_path / "docs" / "claim-register.md",
        "| `CLM-001` | class-a | mode-a | Claim one |\n"
        "| `CLM-001` | class-a | mode-a | Claim duplicate |\n"
        "| `CLM-002` | wrong-class | wrong-mode | wrong text |\n"
        "| `CLM-999` | class-a | mode-a | stray |\n",
    )
    errors = validate_claim_register(tmp_path)
    assert "claims[0] must be an object" in errors
    assert "claims[1].claim_id must match CLM-NNN" in errors
    assert "claims[1].claim must be non-empty" in errors
    assert "claims[1].status must be non-empty" in errors
    assert "claims[1].stopping_point must be non-empty" in errors
    assert "claims[1].claim_class is not declared: 'other-class'" in errors
    assert "claims[1].verification_mode is not declared: 'other-mode'" in errors
    assert "claims[1].supporting_surface must be a non-empty string list" in errors
    assert "duplicate claim_id: CLM-001" in errors
    assert "CLM-001: expected exactly one documentation row" in errors
    assert "CLM-002: claim class is not bound in documentation" in errors
    assert "CLM-002: verification mode is not bound in documentation" in errors
    assert "CLM-002: claim text is not bound in documentation" in errors
    assert "documentation contains unknown claim IDs: ['CLM-999']" in errors


def test_validate_proposed_red_lines_load_error_has_context(tmp_path: Path):
    errors = validate_proposed_red_lines(tmp_path)
    assert len(errors) == 1
    assert errors[0].startswith("candidate ledger cannot be loaded:")


def test_validate_proposed_red_lines_rejects_non_list_candidates(tmp_path: Path):
    _write_json(
        tmp_path / "data" / "proposed_red_lines.json",
        {"schema_version": "0.9", "registry_effect": "some", "candidates": {}},
    )
    _write(tmp_path / "docs" / "PROPOSED_RED_LINES.md", "")
    errors = validate_proposed_red_lines(tmp_path)
    assert "candidate ledger schema_version must be 1.0" in errors
    assert "candidate ledger must declare registry_effect=none" in errors
    assert "candidate ledger candidates must be a list" in errors


def test_validate_proposed_red_lines_reports_structural_and_binding_errors(tmp_path: Path):
    _write_json(
        tmp_path / "data" / "proposed_red_lines.json",
        {
            "schema_version": "1.0",
            "registry_effect": "none",
            "candidates": [
                "bad",
                {"id": "   "},
                {
                    "id": "agent-autonomy-limit",
                    "title": "Candidate Alpha",
                    "author_decision": "granted",
                    "scope_boundary": "scope alpha",
                    "typed_exemption_design": {
                        "status": "active",
                        "match_modes": ["any"],
                        "required_evidence_policy": "",
                    },
                    "required_evidence_on_reconsideration": [],
                    "false_positive_controls": "",
                    "positive_cases": [],
                    "negative_cases": [],
                },
                {
                    "id": "agent-autonomy-limit",
                    "title": "Candidate Duplicate",
                    "author_decision": "no_assent_recorded",
                    "scope_boundary": "scope duplicate",
                    "typed_exemption_design": {
                        "status": "not_defined_until_assent",
                        "match_modes": ["any", "all"],
                        "required_evidence_policy": "document policy",
                    },
                    "required_evidence_on_reconsideration": ["one"],
                    "false_positive_controls": ["two"],
                    "positive_cases": ["three"],
                    "negative_cases": ["four"],
                },
                {
                    "id": "authorship-attribution",
                    "title": "Candidate Beta",
                    "author_decision": "no_assent_recorded",
                    "scope_boundary": "scope beta",
                    "typed_exemption_design": "not-a-dict",
                    "required_evidence_on_reconsideration": ["one"],
                    "false_positive_controls": ["two"],
                    "positive_cases": ["three"],
                    "negative_cases": ["four"],
                },
            ],
        },
    )
    _write(
        tmp_path / "docs" / "PROPOSED_RED_LINES.md",
        "| `agent-autonomy-limit` | Different title | Discussion continues | wrong scope |\n",
    )
    errors = validate_proposed_red_lines(tmp_path)
    assert "candidate ledger entry is not an object" in errors
    assert "candidate ledger entry has no id" in errors
    assert "duplicate candidate id: agent-autonomy-limit" in errors
    assert "agent-autonomy-limit: missing or malformed required_evidence_on_reconsideration" in errors
    assert "agent-autonomy-limit: missing or malformed false_positive_controls" in errors
    assert "agent-autonomy-limit: missing or malformed positive_cases" in errors
    assert "agent-autonomy-limit: missing or malformed negative_cases" in errors
    assert "agent-autonomy-limit: author_decision must remain no_assent_recorded" in errors
    assert "agent-autonomy-limit: typed exemptions cannot be active before assent" in errors
    assert "agent-autonomy-limit: match modes must declare any and all" in errors
    assert "agent-autonomy-limit: typed exemptions need a required evidence policy" in errors
    assert "agent-autonomy-limit: title is not bound in docs/PROPOSED_RED_LINES.md" in errors
    assert "agent-autonomy-limit: decision row does not record no assent" in errors
    assert "agent-autonomy-limit: scope boundary is not bound in its decision row" in errors
    assert "authorship-attribution: absent from a current-release decision row" in errors
    assert "authorship-attribution: title is not bound in docs/PROPOSED_RED_LINES.md" in errors
    assert (
        "candidate ids differ from expected six: ['agent-autonomy-limit', 'authorship-attribution']" in errors
    )


def test_validate_release_bindings_detects_metadata_and_beacon_drift(tmp_path: Path):
    _copy_release_tree(tmp_path)
    version = release_bindings_module.__version__
    line = next(item for item in PERSONAL_RED_LINES if item.exemptions)
    exemption = line.exemptions[0]
    evidence = next(iter(exemption.required_evidence))
    readme_path = tmp_path / "README.md"
    readme_path.write_text(
        readme_path.read_text(encoding="utf-8")
        .replace(f"`{version}`", "`0.0.0`", 1)
        .replace("72835fd8…f5aad7", "00000000…000000", 1),
        encoding="utf-8",
    )
    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text(
        pyproject_path.read_text(encoding="utf-8").replace(
            'version = {attr = "red_line.version.PROJECT_VERSION"}',
            'version = {attr = "red_line.version.BROKEN"}',
            1,
        ),
        encoding="utf-8",
    )
    citation_path = tmp_path / "CITATION.cff"
    citation_path.write_text(
        citation_path.read_text(encoding="utf-8").replace(f'version: "{version}"\n', "", 1), encoding="utf-8"
    )
    skill_path = tmp_path / ".agents" / "skills" / "personal-red-lines" / "SKILL.md"
    skill_path.write_text(
        skill_path.read_text(encoding="utf-8").replace(f"version: {version}", "version: 0.0.0", 1),
        encoding="utf-8",
    )
    fixture_path = tmp_path / "tests" / "fixtures" / "canary_committed.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    fixture["registry_digest"] = "0" * 64
    fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
    beacon_path = tmp_path / "manuscript" / "09_red_lines.md"
    beacon_text = beacon_path.read_text(encoding="utf-8")
    evidence = next(kind for kind in exemption.required_evidence if kind.value == "end_use")
    beacon_text = beacon_text.replace(line.standard, "I will do the opposite of this standard.", 1)
    beacon_text = beacon_text.replace(f"`{next(iter(line.scope))}`", "`missing-token`", 1)
    beacon_text = beacon_text.replace(exemption.id, "drifted-exemption-id", 1)
    beacon_text = beacon_text.replace(
        exemption.description, "A completely different exemption description.", 1
    )
    beacon_text = beacon_text.replace(f"`{evidence.value}`", "`missing-evidence`", 1)
    beacon_path.write_text(beacon_text, encoding="utf-8")
    errors = validate_release_bindings(tmp_path)
    assert f"README: version {version} is not bound" in errors
    assert "pyproject: version must resolve through red_line.version.PROJECT_VERSION" in errors
    assert "CITATION: version field is not bound" in errors
    assert "SKILL.md: frontmatter version is not bound to the package version" in errors
    assert "registry digest is not bound consistently to beacon and fixture" in errors
    assert "README truncated registry digest is stale" in errors
    assert f"{line.id}: beacon standard drifted" in errors
    assert f"{line.id}: missing scope token {next(iter(line.scope))}" in errors
    assert f"{line.id}: exemption {exemption.id} drifted" in errors
    assert f"{line.id}: exemption {exemption.id} missing evidence {evidence.value}" in errors


def test_validate_release_bindings_detects_missing_rendered_surfaces(tmp_path: Path):
    _copy_release_tree(tmp_path)
    (tmp_path / "output" / "web" / "index.html").unlink()
    errors = validate_release_bindings(tmp_path, require_rendered=True)
    assert "required rendered surfaces are missing: ['output/web/index.html']" in errors


def test_validate_release_bindings_detects_stale_rendered_metadata(tmp_path: Path):
    _copy_release_tree(tmp_path)
    index_path = tmp_path / "output" / "web" / "index.html"
    index_path.write_text(
        index_path.read_text(encoding="utf-8").replace(release_bindings_module.__version__, "0.0.0", 1),
        encoding="utf-8",
    )
    errors = validate_release_bindings(tmp_path, require_rendered=True)
    assert "rendered metadata does not carry the package version" in errors


def test_validate_release_bindings_detects_installed_version_mismatch(tmp_path: Path):
    _copy_release_tree(tmp_path)
    with _override_attr(release_bindings_module, "installed_version", lambda _: "0.0.0"):
        errors = validate_release_bindings(tmp_path)
    assert "installed package metadata version differs from package version" in errors


def test_validate_release_bindings_handles_missing_package_metadata(tmp_path: Path):
    _copy_release_tree(tmp_path)

    def _raise_package_not_found(_: str) -> str:
        raise PackageNotFoundError("red-line")

    with _override_attr(release_bindings_module, "installed_version", _raise_package_not_found):
        errors = validate_release_bindings(tmp_path)
    assert "installed package metadata for red-line is unavailable" in errors


def test_validate_visual_bindings_detects_source_generator_mismatch(tmp_path: Path):
    _copy_visual_tree(tmp_path)
    mutated_generators = dict(visual_bindings_module.GENERATORS)
    mutated_generators.pop(next(iter(mutated_generators)))
    with _override_attr(visual_bindings_module, "GENERATORS", mutated_generators):
        errors = validate_visual_bindings(tmp_path)
    assert any(error.startswith("figure source/generator mismatch:") for error in errors)


def test_validate_visual_bindings_reports_source_ledger_read_error(tmp_path: Path):
    _copy_visual_tree(tmp_path)
    (tmp_path / "docs" / "visualization-briefs.md").unlink()
    _write(tmp_path / "data" / "source_claims.json", "{not-json")
    errors = validate_visual_bindings(tmp_path)
    assert "visualization brief is missing or empty" in errors
    assert any(error.startswith("source ledger cannot be read for figure bindings:") for error in errors)


def test_validate_visual_bindings_reports_registry_read_error(tmp_path: Path):
    _copy_visual_tree(tmp_path)
    _write(tmp_path / "output" / "figures" / "figure_registry.json", "{not-json")
    errors = validate_visual_bindings(tmp_path)
    assert any(error.startswith("figure registry cannot be read:") for error in errors)


def test_validate_visual_bindings_detects_label_and_output_drift(tmp_path: Path):
    _copy_visual_tree(tmp_path)
    label = next(iter(visual_bindings_module.FIGURE_TEXT))
    spec = visual_bindings_module.FIGURE_TEXT[label]
    brief_path = tmp_path / "docs" / "visualization-briefs.md"
    brief_path.write_text(
        brief_path.read_text(encoding="utf-8").replace(label, "missing-label", 1), encoding="utf-8"
    )
    for manuscript_path in sorted((tmp_path / "manuscript").glob("*.md")):
        manuscript_text = manuscript_path.read_text(encoding="utf-8")
        if label in manuscript_text:
            manuscript_path.write_text(
                manuscript_text.replace(f"{{#{label}", "{#missing-anchor", 1), encoding="utf-8"
            )
            break
    (tmp_path / "output" / "figures" / spec["filename"]).unlink()
    registry_path = tmp_path / "output" / "figures" / "figure_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    registry["figures"][0]["label"] = "fig:unexpected"
    registry_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    errors = validate_visual_bindings(tmp_path)
    assert any(error.startswith("figure registry labels differ from source:") for error in errors)
    assert f"{label}: missing from visualization brief" in errors
    assert f"{label}: missing manuscript anchor" in errors
    assert f"{label}: missing or empty output/figures/{spec['filename']}" in errors


def test_validate_visual_bindings_detects_binding_and_registry_drift(tmp_path: Path):
    _copy_visual_tree(tmp_path)
    label = "fig:scholarship-reading-map"
    spec = visual_bindings_module.FIGURE_TEXT[label]
    ledger_path = tmp_path / "data" / "source_claims.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    ledger["figure_bindings"] = []
    ledger_path.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    registry_path = tmp_path / "output" / "figures" / "figure_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    record = next(item for item in registry["figures"] if item["label"] == label)
    record["caption"] = "drifted caption"
    record["alt"] = "drifted alt"
    record["source_ids"] = ["registry-only-source"]
    registry_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    with _override_figure_spec(label, source_ids=("unknown-source",)):
        errors = validate_visual_bindings(tmp_path)
    assert "source ledger figure_bindings must be an object" in errors
    assert f"{label}: registry caption drifted from figure source" in errors
    assert f"{label}: registry alt text drifted from figure source" in errors
    assert f"{label}: registry source_ids drifted from figure source" in errors
    assert f"{label}: source ledger binding differs from figure source_ids" in errors
    assert f"{label}: unknown source ids: ['unknown-source']" in errors
    assert spec["caption"] != "drifted caption"
    assert spec["alt"] != "drifted alt"


def test_validate_visual_bindings_detects_blank_caption_alt_and_source_less_binding(tmp_path: Path):
    _copy_visual_tree(tmp_path)
    label = "fig:governance-architecture"
    ledger_path = tmp_path / "data" / "source_claims.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    ledger.setdefault("figure_bindings", {})[label] = ["stray-source"]
    ledger_path.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    with _override_figure_spec(label, caption="   ", alt="   ", source_ids=()):
        errors = validate_visual_bindings(tmp_path)
    assert f"{label}: figure source has no non-empty caption" in errors
    assert f"{label}: figure source has no non-empty alt text" in errors
    assert f"{label}: registry caption drifted from figure source" in errors
    assert f"{label}: registry alt text drifted from figure source" in errors
    assert f"{label}: source ledger has bindings but figure source_ids are absent" in errors


def test_proposed_scope_errors_reports_every_checkable_defect_at_once():
    """The four scope checks the validator actually performs must all fire.

    These are the checks that replaced the withdrawn "verified non-laundering"
    claim, so an unexercised branch here would leave the weaker claim as
    unbound as the stronger one was. Each defect is planted separately and the
    corresponding message is required.
    """

    live = sorted(LIVE_SCOPE_TOKENS)[0]
    proposals = "| `c1` | title | zeta, alpha | CONNECTED | STRONG | high |\n"

    unsorted_errors = _proposed_scope_errors("c1", ["zeta", "alpha"], proposals)
    assert any("must be sorted" in error for error in unsorted_errors)

    non_canonical = _proposed_scope_errors("c1", ["Alpha Beta"], proposals)
    assert any("is not canonical" in error for error in non_canonical)

    non_string = _proposed_scope_errors("c1", [7], proposals)
    assert any("is not canonical" in error for error in non_string)

    already_live = _proposed_scope_errors("c1", [live], f"| `c1` | title | {live} | X | Y | Z |\n")
    assert any("already live in PERSONAL_RED_LINES" in error for error in already_live)

    absent_from_row = _proposed_scope_errors("c1", ["alpha"], "| `c1` | title | zeta | X | Y | Z |\n")
    assert any("absent from its published row" in error for error in absent_from_row)


def test_proposed_scope_errors_accepts_the_shape_it_is_meant_to_accept():
    """Negative control: a clean candidate row must produce no errors.

    Without this the assertions above could pass on a function that rejected
    everything.
    """

    proposals = "| `c1` | title | alpha, zeta | CONNECTED | STRONG | high |\n"

    assert _proposed_scope_errors("c1", ["alpha", "zeta"], proposals) == []
