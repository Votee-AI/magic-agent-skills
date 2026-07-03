"""Phase 3a structural tests — same pattern as Phase 1/2."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILLS_DIR = REPO_ROOT / "skills"
ORCH = SKILLS_DIR / "magic-linguistic-orchestrator"

PHASE3A_SKILLS = ["magic-linguistic-morph", "magic-linguistic-syntax", "magic-linguistic-annotate"]
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


@pytest.mark.parametrize("skill_name", PHASE3A_SKILLS)
def test_skill_present_in_orchestrator_routing(skill_name: str) -> None:
    routing = (ORCH / "references" / "routing_logic.md").read_text(encoding="utf-8")
    pipeline = (ORCH / "references" / "pipeline_phases.md").read_text(encoding="utf-8")
    skill_md = (ORCH / "SKILL.md").read_text(encoding="utf-8")
    combined = routing + pipeline + skill_md
    bare = skill_name.removeprefix("magic-linguistic-")
    assert (skill_name in combined) or (f"| {bare} |" in combined) or (f"`{bare}`" in combined)


@pytest.mark.parametrize("skill_name", PHASE3A_SKILLS)
def test_skill_has_valid_frontmatter(skill_name: str) -> None:
    p = SKILLS_DIR / skill_name / "SKILL.md"
    assert p.exists()
    m = FRONTMATTER_RE.match(p.read_text())
    assert m, f"no YAML frontmatter in {p}"
    fm = yaml.safe_load(m.group(1))
    assert fm["name"] == skill_name
    assert fm["metadata"]["domain"] == "linguistics"
    assert fm["metadata"]["phase"] == 3
    assert fm["metadata"].get("entry_point") is not True


@pytest.mark.parametrize("skill_name", PHASE3A_SKILLS)
def test_skill_has_anti_patterns_section(skill_name: str) -> None:
    p = SKILLS_DIR / skill_name / "SKILL.md"
    text = p.read_text(encoding="utf-8")
    assert re.search(r"##\s+Anti-patterns", text, re.IGNORECASE)
    assert len(re.findall(r"\*\*NEVER\*\*", text)) >= 3


@pytest.mark.parametrize("skill_name", PHASE3A_SKILLS)
def test_skill_has_required_references(skill_name: str) -> None:
    assert (SKILLS_DIR / skill_name / "references" / "canonical_sources.md").exists()


@pytest.mark.parametrize("skill_name", PHASE3A_SKILLS)
def test_skill_has_evals(skill_name: str) -> None:
    import json

    p = SKILLS_DIR / skill_name / "evals" / "evals.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["skill_name"] == skill_name
    assert len(data["evals"]) >= 3
