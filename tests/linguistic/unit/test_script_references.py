"""Validate that scripts referenced in SKILL.md actually exist on disk.

Catches the "Orphan References" anti-pattern from skill-judge: a skill mentions
scripts/foo.py in its SKILL.md but the file is missing.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILLS_DIR = REPO_ROOT / "skills"

# Match `scripts/whatever.py` or backticked variants.
SCRIPT_REFERENCE_RE = re.compile(r"`?(scripts/[a-zA-Z0-9_]+\.py)`?")


def _skill_md_files() -> list[Path]:
    return sorted(p for p in SKILLS_DIR.glob("linguistic-*/SKILL.md") if p.is_file())


@pytest.mark.parametrize("skill_md", _skill_md_files(), ids=lambda p: p.parent.name)
def test_referenced_scripts_exist(skill_md: Path) -> None:
    text = skill_md.read_text(encoding="utf-8")
    refs = set(SCRIPT_REFERENCE_RE.findall(text))
    missing = []
    for ref in refs:
        path = skill_md.parent / ref
        if not path.exists():
            missing.append(str(path.relative_to(REPO_ROOT)))
    assert not missing, f"{skill_md.relative_to(REPO_ROOT)} references missing scripts: {missing}"


@pytest.mark.parametrize("skill_md", _skill_md_files(), ids=lambda p: p.parent.name)
def test_referenced_references_exist(skill_md: Path) -> None:
    """If SKILL.md says `references/foo.md`, the file must exist."""
    text = skill_md.read_text(encoding="utf-8")
    pattern = re.compile(r"`?(references/[a-zA-Z0-9_]+\.md)`?")
    refs = set(pattern.findall(text))
    missing = [ref for ref in refs if not (skill_md.parent / ref).exists()]
    assert not missing, f"{skill_md.relative_to(REPO_ROOT)} references missing reference files: {missing}"
