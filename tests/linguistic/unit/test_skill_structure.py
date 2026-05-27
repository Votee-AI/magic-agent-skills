"""Validate SKILL.md frontmatter for every skill that has one.

Skills with no SKILL.md (placeholder dirs for Phase 1+ or optional modules)
are silently skipped. Skills with SKILL.md must have valid YAML frontmatter
with the required fields.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILLS_DIR = REPO_ROOT / "skills"

REQUIRED_FRONTMATTER_FIELDS = ["name", "description"]
ENCOURAGED_FIELDS = ["version", "author", "tags", "metadata"]
ENCOURAGED_METADATA = ["domain", "complexity", "phase", "entry_point"]

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def _skill_md_files() -> list[Path]:
    return sorted(p for p in SKILLS_DIR.glob("linguistic-*/SKILL.md") if p.is_file())


def _parse_frontmatter(text: str) -> dict | None:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    return yaml.safe_load(m.group(1))


@pytest.mark.parametrize("skill_md", _skill_md_files(), ids=lambda p: p.parent.name)
def test_frontmatter_valid(skill_md: Path) -> None:
    text = skill_md.read_text(encoding="utf-8")
    fm = _parse_frontmatter(text)
    assert fm is not None, f"{skill_md} has no YAML frontmatter"
    for field in REQUIRED_FRONTMATTER_FIELDS:
        assert field in fm, f"{skill_md} missing required frontmatter field: {field}"
    assert isinstance(fm["name"], str) and re.match(r"^[a-z0-9][a-z0-9-]*$", fm["name"]), (
        f"{skill_md} name '{fm['name']}' must be lowercase, alphanumeric + hyphens, start with letter/digit"
    )
    assert len(fm["name"]) <= 64, f"{skill_md} name too long ({len(fm['name'])} chars, max 64)"
    assert isinstance(fm["description"], str) and len(fm["description"]) > 30, (
        f"{skill_md} description must be a non-trivial string (>30 chars)"
    )


@pytest.mark.parametrize("skill_md", _skill_md_files(), ids=lambda p: p.parent.name)
def test_skill_md_line_count(skill_md: Path) -> None:
    """No SKILL.md should exceed 500 lines (progressive disclosure)."""
    n_lines = sum(1 for _ in skill_md.open(encoding="utf-8"))
    assert n_lines <= 500, f"{skill_md} has {n_lines} lines (max 500 — move content to references/)"


def test_orchestrator_present() -> None:
    """The orchestrator is the entry-point skill; must exist after Phase 0."""
    p = SKILLS_DIR / "linguistic-orchestrator" / "SKILL.md"
    assert p.exists(), "linguistic-orchestrator/SKILL.md is missing — Phase 0 incomplete"


def test_orchestrator_is_entry_point() -> None:
    p = SKILLS_DIR / "linguistic-orchestrator" / "SKILL.md"
    fm = _parse_frontmatter(p.read_text(encoding="utf-8"))
    assert fm is not None
    md = fm.get("metadata", {})
    assert md.get("entry_point") is True, "linguistic-orchestrator must have metadata.entry_point = true"
    assert md.get("phase") == 0, "linguistic-orchestrator must have metadata.phase = 0"
