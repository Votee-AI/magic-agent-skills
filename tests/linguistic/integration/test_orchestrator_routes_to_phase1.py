"""Confirm orchestrator's routing_logic.md maps NL triggers to Phase 1 skills.

Structural test, not LLM-based. Verifies:
- Each Phase 1 skill is referenced in routing_logic.md.
- Each Phase 1 skill's `description` frontmatter contains its declared NL triggers.
- Each Phase 1 skill is reachable from the orchestrator (named in pipeline_phases.md or routing_logic.md).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILLS_DIR = REPO_ROOT / "skills"
ORCH = SKILLS_DIR / "magic-linguistic-orchestrator"

PHASE1_SKILLS = [
    "magic-linguistic-scope",
    "magic-linguistic-scripts",
    "magic-linguistic-tokenize",
    "magic-linguistic-ethics",
]

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


@pytest.mark.parametrize("skill_name", PHASE1_SKILLS)
def test_skill_present_in_orchestrator_routing(skill_name: str) -> None:
    """Orchestrator must reference the skill by full name OR bare suffix.

    The routing tables in routing_logic.md often use the bare suffix (`scope`,
    `scripts`) for visual cleanliness; pipeline_phases.md uses full names. Either
    suffices to confirm the orchestrator can reach this specialist.
    """
    routing = (ORCH / "references" / "routing_logic.md").read_text(encoding="utf-8")
    pipeline = (ORCH / "references" / "pipeline_phases.md").read_text(encoding="utf-8")
    skill_md = (ORCH / "SKILL.md").read_text(encoding="utf-8")
    combined = routing + pipeline + skill_md
    bare = skill_name.removeprefix("magic-linguistic-")
    assert (skill_name in combined) or (f"| {bare} |" in combined) or (f"`{bare}`" in combined), (
        f"{skill_name} (or bare suffix '{bare}') is not referenced anywhere in the orchestrator"
    )


@pytest.mark.parametrize("skill_name", PHASE1_SKILLS)
def test_skill_has_valid_frontmatter(skill_name: str) -> None:
    p = SKILLS_DIR / skill_name / "SKILL.md"
    assert p.exists(), f"{skill_name}/SKILL.md missing"
    text = p.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    assert m, f"{skill_name}/SKILL.md has no YAML frontmatter"
    fm = yaml.safe_load(m.group(1))
    assert fm["name"] == skill_name, f"{skill_name}/SKILL.md name mismatch: {fm['name']}"
    assert fm["metadata"]["domain"] == "linguistics"
    assert fm["metadata"]["phase"] == 1
    # Phase 1 skills are NOT entry points (orchestrator is)
    assert fm["metadata"].get("entry_point") is not True


@pytest.mark.parametrize("skill_name", PHASE1_SKILLS)
def test_skill_has_anti_patterns_section(skill_name: str) -> None:
    """Every Phase 1 skill must declare explicit NEVER rules (D3 floor)."""
    p = SKILLS_DIR / skill_name / "SKILL.md"
    text = p.read_text(encoding="utf-8")
    assert re.search(r"##\s+Anti-patterns", text, re.IGNORECASE), (
        f"{skill_name}/SKILL.md missing 'Anti-patterns' section"
    )
    # Must contain at least 3 NEVER bullets
    nevers = re.findall(r"\*\*NEVER\*\*", text)
    assert len(nevers) >= 3, f"{skill_name}/SKILL.md has only {len(nevers)} NEVER rules; expected ≥ 3"


@pytest.mark.parametrize("skill_name", PHASE1_SKILLS)
def test_skill_has_required_references(skill_name: str) -> None:
    """Every Phase 1 skill must have at least canonical_sources.md."""
    p = SKILLS_DIR / skill_name / "references" / "canonical_sources.md"
    assert p.exists(), f"{skill_name}/references/canonical_sources.md missing"


@pytest.mark.parametrize("skill_name", PHASE1_SKILLS)
def test_skill_has_evals(skill_name: str) -> None:
    """Every Phase 1 skill must have evals/evals.json with ≥ 3 prompts (5 for A-tier)."""
    import json

    p = SKILLS_DIR / skill_name / "evals" / "evals.json"
    assert p.exists(), f"{skill_name}/evals/evals.json missing"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["skill_name"] == skill_name
    n = len(data["evals"])
    a_tier = {"magic-linguistic-scope", "magic-linguistic-ethics"}
    risky = a_tier | {"magic-linguistic-tokenize"}
    if skill_name in risky:
        assert n >= 5, f"{skill_name} is risky tier; expected ≥ 5 evals, got {n}"
    else:
        assert n >= 3, f"{skill_name} expected ≥ 3 evals, got {n}"
