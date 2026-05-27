"""Phase 4 (final) structural tests."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILLS_DIR = REPO_ROOT / "skills"
ORCH = SKILLS_DIR / "linguistic-orchestrator"

PHASE4_SKILLS = ["linguistic-eval", "linguistic-codeswitch", "linguistic-historical", "linguistic-lexicon"]
A_TIER = {"linguistic-eval"}
MINDSET = {"linguistic-codeswitch", "linguistic-historical", "linguistic-lexicon"}
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


@pytest.mark.parametrize("skill_name", PHASE4_SKILLS)
def test_skill_present_in_orchestrator_routing(skill_name: str) -> None:
    routing = (ORCH / "references" / "routing_logic.md").read_text(encoding="utf-8")
    pipeline = (ORCH / "references" / "pipeline_phases.md").read_text(encoding="utf-8")
    skill_md = (ORCH / "SKILL.md").read_text(encoding="utf-8")
    combined = routing + pipeline + skill_md
    bare = skill_name.removeprefix("linguistic-")
    # Accept full name, bare suffix in table cell (with or without parenthetical), or backtick
    assert (
        skill_name in combined
        or f"| {bare} |" in combined
        or f"| {bare} (" in combined  # e.g., "| codeswitch (optional, may not exist yet) |"
        or f"`{bare}`" in combined
    ), f"{skill_name} (or bare suffix '{bare}') is not referenced anywhere in the orchestrator"


@pytest.mark.parametrize("skill_name", PHASE4_SKILLS)
def test_skill_has_valid_frontmatter(skill_name: str) -> None:
    p = SKILLS_DIR / skill_name / "SKILL.md"
    assert p.exists()
    m = FRONTMATTER_RE.match(p.read_text())
    assert m, f"no YAML frontmatter in {p}"
    fm = yaml.safe_load(m.group(1))
    assert fm["name"] == skill_name
    assert fm["metadata"]["domain"] == "linguistics"
    assert fm["metadata"]["phase"] == 4
    assert fm["metadata"].get("entry_point") is not True


@pytest.mark.parametrize("skill_name", PHASE4_SKILLS)
def test_skill_has_anti_patterns_section(skill_name: str) -> None:
    p = SKILLS_DIR / skill_name / "SKILL.md"
    text = p.read_text(encoding="utf-8")
    assert re.search(r"##\s+Anti-patterns", text, re.IGNORECASE)
    assert len(re.findall(r"\*\*NEVER\*\*", text)) >= 3


@pytest.mark.parametrize("skill_name", PHASE4_SKILLS)
def test_skill_has_required_references(skill_name: str) -> None:
    assert (SKILLS_DIR / skill_name / "references" / "canonical_sources.md").exists()


@pytest.mark.parametrize("skill_name", PHASE4_SKILLS)
def test_skill_has_evals(skill_name: str) -> None:
    import json

    p = SKILLS_DIR / skill_name / "evals" / "evals.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["skill_name"] == skill_name
    n = len(data["evals"])
    if skill_name in A_TIER:
        assert n >= 5, f"{skill_name} is A-tier; expected ≥ 5 evals, got {n}"
    else:
        assert n >= 3, f"{skill_name} expected ≥ 3 evals, got {n}"


@pytest.mark.parametrize("skill_name", MINDSET)
def test_mindset_skill_short(skill_name: str) -> None:
    """Mindset stubs should be small (≤ 100 lines)."""
    p = SKILLS_DIR / skill_name / "SKILL.md"
    n_lines = sum(1 for _ in p.open(encoding="utf-8"))
    assert n_lines <= 100, f"{skill_name} is Mindset; expected ≤ 100 lines, got {n_lines}"
