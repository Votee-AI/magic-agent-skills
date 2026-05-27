#!/usr/bin/env python3
"""
Workflow Reinforcement — SKILL.md Structural Validation Tests.

Validates:
- All SKILL.md files have valid YAML frontmatter
- Entry-point skills have entry_point: true metadata
- NL Triggers section appears before other content sections in P1 skills
- When to Use sections exist in required skills
- Progressive disclosure ordering: metadata -> NL Triggers -> When to Use -> Workflow
"""

import re
import yaml
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = PROJECT_ROOT / "skills"

# All skill directories (excluding internal dirs)
ALL_SKILLS = sorted(
    d.name for d in SKILLS_DIR.iterdir()
    if d.is_dir()
    and not d.name.startswith("_")
    and (d / "SKILL.md").exists()
)

# Skills that should be entry points
ENTRY_POINT_SKILLS = ["magic-data-lifecycle"]

# P1 skills that need full reinforcement
P1_SKILLS = [
    "magic-data-lifecycle",
    "magic-data-profiling",
    "magic-data-loading",
]

# Skills that should have When to Use sections
SKILLS_WITH_WHEN_TO_USE = [
    "magic-data-lifecycle",
    "magic-data-profiling",
    "magic-data-loading",
    "magic-data-exploration",
    "magic-data-cleaning",
    "magic-data-transformation",
    "magic-data-validation",
    "magic-data-synthesis",
    "magic-data-visualization",
    "magic-statistical-analysis",
    "magic-report-generation",
]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _parse_frontmatter(text: str) -> dict:
    """Parse YAML frontmatter from SKILL.md."""
    match = re.match(r"^---\n(.+?)\n---", text, re.DOTALL)
    if not match:
        return {}
    try:
        return yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return {}


def _get_section_positions(text: str) -> dict[str, int]:
    """Get positions of ## sections in the document."""
    sections = {}
    for match in re.finditer(r"^(## .+)$", text, re.MULTILINE):
        section_name = match.group(1).strip()
        sections[section_name] = match.start()
    return sections


class TestFrontmatterValid:
    """Verify all SKILL.md files have valid YAML frontmatter."""

    @pytest.mark.parametrize("skill_name", ALL_SKILLS)
    def test_has_frontmatter(self, skill_name):
        """Each SKILL.md must have YAML frontmatter."""
        path = SKILLS_DIR / skill_name / "SKILL.md"
        content = _read_text(path)
        assert content.startswith("---"), (
            f"{skill_name}/SKILL.md does not start with YAML frontmatter"
        )
        assert content.count("---") >= 2, (
            f"{skill_name}/SKILL.md has incomplete frontmatter (missing closing ---)"
        )

    @pytest.mark.parametrize("skill_name", ALL_SKILLS)
    def test_frontmatter_parses(self, skill_name):
        """Frontmatter YAML must parse without errors."""
        path = SKILLS_DIR / skill_name / "SKILL.md"
        content = _read_text(path)
        fm = _parse_frontmatter(content)
        assert fm, f"{skill_name}/SKILL.md frontmatter failed to parse"

    @pytest.mark.parametrize("skill_name", ALL_SKILLS)
    def test_has_required_fields(self, skill_name):
        """Frontmatter must have name, description, and metadata."""
        path = SKILLS_DIR / skill_name / "SKILL.md"
        content = _read_text(path)
        fm = _parse_frontmatter(content)
        assert "name" in fm, f"{skill_name}: missing 'name' in frontmatter"
        assert "description" in fm, f"{skill_name}: missing 'description' in frontmatter"
        assert "metadata" in fm, f"{skill_name}: missing 'metadata' in frontmatter"

    @pytest.mark.parametrize("skill_name", ALL_SKILLS)
    def test_description_is_meaningful(self, skill_name):
        """Description should be substantive (>= 30 chars) and user-facing."""
        path = SKILLS_DIR / skill_name / "SKILL.md"
        content = _read_text(path)
        fm = _parse_frontmatter(content)
        desc = fm.get("description", "")
        assert len(desc) >= 30, (
            f"{skill_name}: description too short ({len(desc)} chars): '{desc}'"
        )

    @pytest.mark.parametrize("skill_name", ALL_SKILLS)
    def test_metadata_has_domain(self, skill_name):
        """Metadata must include domain."""
        path = SKILLS_DIR / skill_name / "SKILL.md"
        content = _read_text(path)
        fm = _parse_frontmatter(content)
        metadata = fm.get("metadata", {})
        assert "domain" in metadata, f"{skill_name}: metadata missing 'domain'"


class TestEntryPointMetadata:
    """Verify entry-point skills have correct metadata."""

    @pytest.mark.parametrize("skill_name", ENTRY_POINT_SKILLS)
    def test_has_entry_point_true(self, skill_name):
        """Entry-point skills must have entry_point: true in metadata."""
        path = SKILLS_DIR / skill_name / "SKILL.md"
        content = _read_text(path)
        fm = _parse_frontmatter(content)
        metadata = fm.get("metadata", {})
        assert metadata.get("entry_point") is True, (
            f"{skill_name}: metadata should have 'entry_point: true', "
            f"got: {metadata.get('entry_point')}"
        )

    @pytest.mark.parametrize("skill_name", ENTRY_POINT_SKILLS)
    def test_phase_is_zero(self, skill_name):
        """Entry-point skills should be phase 0."""
        path = SKILLS_DIR / skill_name / "SKILL.md"
        content = _read_text(path)
        fm = _parse_frontmatter(content)
        metadata = fm.get("metadata", {})
        assert metadata.get("phase") == 0, (
            f"{skill_name}: entry-point skill should be phase 0, "
            f"got: {metadata.get('phase')}"
        )


class TestWhenToUseSections:
    """Verify When to Use sections exist where required."""

    @pytest.mark.parametrize("skill_name", SKILLS_WITH_WHEN_TO_USE)
    def test_has_when_to_use(self, skill_name):
        """Required skills must have a When to Use section."""
        path = SKILLS_DIR / skill_name / "SKILL.md"
        content = _read_text(path)
        assert "## When to Use" in content or "**When to Use" in content, (
            f"{skill_name}/SKILL.md missing 'When to Use' section"
        )

    @pytest.mark.parametrize("skill_name", SKILLS_WITH_WHEN_TO_USE)
    def test_has_when_not_to_use(self, skill_name):
        """Required skills should also have When NOT to Use guidance."""
        path = SKILLS_DIR / skill_name / "SKILL.md"
        content = _read_text(path)
        assert "When NOT to Use" in content or "NOT to Use" in content, (
            f"{skill_name}/SKILL.md missing 'When NOT to Use' guidance"
        )


class TestProgressiveDisclosureOrdering:
    """Verify section ordering follows progressive disclosure pattern."""

    @pytest.mark.parametrize("skill_name", P1_SKILLS)
    def test_nl_triggers_before_when_to_use(self, skill_name):
        """NL Triggers should appear before When to Use."""
        path = SKILLS_DIR / skill_name / "SKILL.md"
        content = _read_text(path)
        nl_pos = content.find("## Natural Language Triggers")
        wtu_pos = content.find("## When to Use")
        if nl_pos != -1 and wtu_pos != -1:
            assert nl_pos < wtu_pos, (
                f"{skill_name}: NL Triggers should come before When to Use"
            )

    @pytest.mark.parametrize("skill_name", P1_SKILLS)
    def test_when_to_use_before_workflow(self, skill_name):
        """When to Use should appear before Workflow/Stance sections."""
        path = SKILLS_DIR / skill_name / "SKILL.md"
        content = _read_text(path)
        wtu_pos = content.find("## When to Use")
        # Look for the main content sections
        workflow_pos = content.find("## Workflow")
        stance_pos = content.find("## The Stance")
        overview_pos = content.find("## Overview")

        main_pos = min(
            p for p in [workflow_pos, stance_pos, overview_pos] if p != -1
        ) if any(p != -1 for p in [workflow_pos, stance_pos, overview_pos]) else -1

        if wtu_pos != -1 and main_pos != -1:
            assert wtu_pos < main_pos, (
                f"{skill_name}: When to Use should come before main content sections"
            )


class TestLifecycleSpecificStructure:
    """Verify lifecycle skill has routing knowledge (interactive infra moved to /data-agent:lifecycle command)."""

    def setup_method(self):
        self.path = SKILLS_DIR / "magic-data-lifecycle" / "SKILL.md"
        self.content = _read_text(self.path)

    def test_has_routing_table(self):
        """Lifecycle must have skill routing table."""
        assert "Skill" in self.content and "Route" in self.content or "routing" in self.content.lower()

    def test_has_pipeline_ordering(self):
        """Lifecycle must document pipeline ordering."""
        assert "Profile" in self.content
        assert "Clean" in self.content
        assert "Validate" in self.content

    def test_has_thinking_section(self):
        """Lifecycle must have Thinking section for routing decisions."""
        assert "### Thinking" in self.content

    def test_has_checkpointing(self):
        """Lifecycle must have Checkpointing section."""
        assert "## Checkpointing" in self.content

    def test_has_self_healing(self):
        """Lifecycle must have Self-Healing section."""
        assert "## Self-Healing" in self.content

    def test_has_edge_cases(self):
        """Lifecycle must have Edge Cases section."""
        assert "## Edge Cases" in self.content


class TestExplorationStructure:
    """Verify magic-data-exploration has required elements."""

    def setup_method(self):
        self.path = SKILLS_DIR / "magic-data-exploration" / "SKILL.md"
        self.content = _read_text(self.path)

    def test_has_thinking_section(self):
        """Exploration should have Thinking section."""
        assert "### Thinking" in self.content

    def test_has_rules_section(self):
        """Exploration should have Rules section."""
        assert "### Rules" in self.content

    def test_has_transition_guidance(self):
        """Exploration should have guidance for transitioning to action."""
        assert "transition" in self.content.lower() or "action" in self.content.lower()
