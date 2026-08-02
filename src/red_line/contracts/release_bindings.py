"""Validate code, beacon prose, metadata, and canary surfaces as one contract."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version as installed_version
import json
from pathlib import Path
import re

from red_line import PERSONAL_RED_LINES, __version__
from red_line.canary import registry_hash


def _normal(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    return " ".join(text.replace("\u2011", "-").replace("*", " ").split())


def validate_release_bindings(root: Path, *, require_rendered: bool = False) -> list[str]:
    """Validate source bindings, optionally requiring rendered surfaces.

    Source and unit-test gates run before the sibling template renderer, so
    they must remain valid from a clean checkout with no ignored ``output/``
    tree. Strict release-manifest validation passes ``require_rendered=True``
    after the canonical PDF/HTML render has completed.
    """

    beacon = (root / "manuscript" / "09_red_lines.md").read_text(encoding="utf-8")
    readme = (root / "README.md").read_text(encoding="utf-8")
    config = (root / "manuscript" / "config.yaml").read_text(encoding="utf-8")
    citation = (root / "CITATION.cff").read_text(encoding="utf-8")
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    skill = (root / ".agents" / "skills" / "personal-red-lines" / "SKILL.md").read_text(encoding="utf-8")
    fixture = json.loads((root / "tests" / "fixtures" / "canary_committed.json").read_text(encoding="utf-8"))
    digest = registry_hash(PERSONAL_RED_LINES)
    errors: list[str] = []
    for label, text in (("README", readme), ("manuscript config", config), ("CITATION", citation)):
        if f'"{__version__}"' not in text and f"`{__version__}`" not in text:
            errors.append(f"{label}: version {__version__} is not bound")
    if (
        'dynamic = ["version"]' not in pyproject
        or 'version = {attr = "red_line.version.PROJECT_VERSION"}' not in pyproject
    ):
        errors.append("pyproject: version must resolve through red_line.version.PROJECT_VERSION")
    try:
        if installed_version("red-line") != __version__:
            errors.append("installed package metadata version differs from package version")
    except PackageNotFoundError:
        errors.append("installed package metadata for red-line is unavailable")
    if f'version: "{__version__}"' not in citation:
        errors.append("CITATION: version field is not bound")
    if f"version: {__version__}" not in skill:
        errors.append("SKILL.md: frontmatter version is not bound to the package version")
    if digest not in beacon or digest != fixture.get("registry_digest"):
        errors.append("registry digest is not bound consistently to beacon and fixture")
    match = re.search(r"`([0-9a-f]{8})…([0-9a-f]{6})`", readme)
    if not match or (match.group(1), match.group(2)) != (digest[:8], digest[-6:]):
        errors.append("README truncated registry digest is stale")
    if require_rendered:
        rendered_candidates = (
            root / "output" / "web" / "index.html",
            root / "output" / "pdf" / "_combined_manuscript.md",
        )
        missing_rendered = [str(path.relative_to(root)) for path in rendered_candidates if not path.exists()]
        if missing_rendered:
            errors.append(f"required rendered surfaces are missing: {missing_rendered}")
        rendered = [path for path in rendered_candidates if path.exists()]
        if rendered and not all(
            __version__ in path.read_text(encoding="utf-8", errors="replace") for path in rendered
        ):
            errors.append("rendered metadata does not carry the package version")
    normalized = _normal(beacon)
    for line in PERSONAL_RED_LINES:
        marker = f"## {line.id} —"
        start = normalized.find(marker)
        end = normalized.find(" ## ", start + len(marker)) if start >= 0 else -1
        section = normalized[start:] if start >= 0 else ""
        if end >= 0:
            section = section[:end]
        for expected, label in (
            (line.title, "title"),
            (line.standard, "standard"),
            (line.rationale, "rationale"),
            (f"Stated by: {line.stated_by}", "stated_by"),
            (f"Stated on: {line.stated_on}", "stated_on"),
            (f"Severity: {line.severity.value.upper()}", "severity"),
            (
                f"Max tier: {'air-gapped' if line.max_tier.value == 'air_gapped' else line.max_tier.value}",
                "max_tier",
            ),
        ):
            if _normal(expected) not in section:
                errors.append(f"{line.id}: beacon {label} drifted")
        for token in line.scope:
            if f"`{token}`" not in section:
                errors.append(f"{line.id}: missing scope token {token}")
        for exemption in line.exemptions:
            if exemption.id not in section or _normal(exemption.description) not in section:
                errors.append(f"{line.id}: exemption {exemption.id} drifted")
            for kind in exemption.required_evidence:
                if f"`{kind.value}`" not in section:
                    errors.append(f"{line.id}: exemption {exemption.id} missing evidence {kind.value}")
    return errors
