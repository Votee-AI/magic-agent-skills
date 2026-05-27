"""Confirm orchestrator's routing references Phase 2 skills + their structural integrity.

Same pattern as Phase 1 test.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILLS_DIR = REPO_ROOT / "skills"
ORCH = SKILLS_DIR / "linguistic-orchestrator"

PHASE2_SKILLS = [
    "linguistic-corpus",
    "linguistic-bitext",
    "linguistic-transfer",
]

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


@pytest.mark.parametrize("skill_name", PHASE2_SKILLS)
def test_skill_present_in_orchestrator_routing(skill_name: str) -> None:
    routing = (ORCH / "references" / "routing_logic.md").read_text(encoding="utf-8")
    pipeline = (ORCH / "references" / "pipeline_phases.md").read_text(encoding="utf-8")
    skill_md = (ORCH / "SKILL.md").read_text(encoding="utf-8")
    combined = routing + pipeline + skill_md
    bare = skill_name.removeprefix("linguistic-")
    assert (skill_name in combined) or (f"| {bare} |" in combined) or (f"`{bare}`" in combined), (
        f"{skill_name} (or bare suffix '{bare}') is not referenced in the orchestrator"
    )


@pytest.mark.parametrize("skill_name", PHASE2_SKILLS)
def test_skill_has_valid_frontmatter(skill_name: str) -> None:
    p = SKILLS_DIR / skill_name / "SKILL.md"
    assert p.exists(), f"{skill_name}/SKILL.md missing"
    text = p.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    assert m, f"{skill_name}/SKILL.md has no YAML frontmatter"
    fm = yaml.safe_load(m.group(1))
    assert fm["name"] == skill_name
    assert fm["metadata"]["domain"] == "linguistics"
    assert fm["metadata"]["phase"] == 2
    assert fm["metadata"].get("entry_point") is not True


@pytest.mark.parametrize("skill_name", PHASE2_SKILLS)
def test_skill_has_anti_patterns_section(skill_name: str) -> None:
    p = SKILLS_DIR / skill_name / "SKILL.md"
    text = p.read_text(encoding="utf-8")
    assert re.search(r"##\s+Anti-patterns", text, re.IGNORECASE), (
        f"{skill_name}/SKILL.md missing 'Anti-patterns' section"
    )
    nevers = re.findall(r"\*\*NEVER\*\*", text)
    assert len(nevers) >= 3, f"{skill_name}/SKILL.md has only {len(nevers)} NEVER rules; expected ≥ 3"


@pytest.mark.parametrize("skill_name", PHASE2_SKILLS)
def test_skill_has_required_references(skill_name: str) -> None:
    p = SKILLS_DIR / skill_name / "references" / "canonical_sources.md"
    assert p.exists(), f"{skill_name}/references/canonical_sources.md missing"


@pytest.mark.parametrize("skill_name", PHASE2_SKILLS)
def test_skill_has_evals(skill_name: str) -> None:
    import json

    p = SKILLS_DIR / skill_name / "evals" / "evals.json"
    assert p.exists(), f"{skill_name}/evals/evals.json missing"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["skill_name"] == skill_name
    n = len(data["evals"])
    risky = {"linguistic-transfer"}
    if skill_name in risky:
        assert n >= 5, f"{skill_name} is risky tier; expected ≥ 5 evals, got {n}"
    else:
        assert n >= 3, f"{skill_name} expected ≥ 3 evals, got {n}"
