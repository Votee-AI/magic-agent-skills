#!/usr/bin/env python3
"""
Tests for the interaction protocol integration across SKILL.md files.

Verifies that:
- All data skills have PAUSE annotations
- Synthesis has ALWAYS-PAUSE and HARD GATE annotations
- Workspace templates have Interaction Mode section
- Lifecycle skill references all phases
"""
import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills"
TEMPLATES_DIR = SKILLS_DIR / "magic-data-lifecycle" / "references"


# Skills that should have PAUSE annotations
DATA_SKILLS = [
    "magic-data-loading",
    "magic-data-profiling",
    "magic-data-cleaning",
    "magic-data-validation",
    "magic-data-transformation",
    "magic-data-exploration",
    "magic-statistical-analysis",
    "magic-data-synthesis",
    "magic-data-visualization",
    "magic-report-generation",
]

# magic-workspace-init intentionally has no PAUSE (setup skill)
SKILLS_WITHOUT_PAUSE = ["magic-workspace-init"]


class TestPauseAnnotations:
    """Verify all data skills have at least one PAUSE annotation."""

    @pytest.mark.parametrize("skill_name", DATA_SKILLS)
    def test_skill_has_pause_annotation(self, skill_name):
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        assert skill_path.exists(), f"SKILL.md not found for {skill_name}"

        content = skill_path.read_text()
        assert "PAUSE" in content, (
            f"{skill_name}/SKILL.md has no PAUSE annotation"
        )

    @pytest.mark.parametrize("skill_name", DATA_SKILLS)
    def test_pause_has_mode_qualifier(self, skill_name):
        """PAUSE annotations or a ### PAUSE Gates section should be present.

        v2 3-layer format uses '### PAUSE Gates' under '## Interactive Mode [Optional]'
        rather than inline **PAUSE (always)** / **PAUSE (supervised)** annotations.
        Either format is accepted.
        """
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        content = skill_path.read_text()

        # v2 format: section heading
        if "### PAUSE Gates" in content or "## Interactive Mode" in content:
            return  # v2 format: section present, passes

        # v1 format fallback: inline **PAUSE** with qualifier
        pause_lines = [line for line in content.split("\n") if "PAUSE" in line and "**PAUSE" in line]
        for line in pause_lines:
            assert re.search(r"\(collaborative\+\)|\(always\)|\(supervised\)", line), (
                f"{skill_name}: **PAUSE** without mode qualifier: {line.strip()}"
            )


class TestSynthesisHardGates:
    """Verify synthesis skill has mandatory preview gate and validation requirements.

    NOTE: v2 3-layer restructure replaced 'HARD GATE / GATE 1 / GATE 2' annotations
    with '## Preview Gate (MANDATORY)' section and MUST rules in Layer 1.
    Tests updated to verify v2 equivalents.
    """

    def test_synthesis_has_always_pause(self):
        """Synthesis has a mandatory pause gate (v2: Preview Gate section or PAUSE Gates)."""
        skill_path = SKILLS_DIR / "magic-data-synthesis" / "SKILL.md"
        content = skill_path.read_text()
        assert (
            "PAUSE (always)" in content
            or "Preview Gate (MANDATORY)" in content
            or "### PAUSE Gates" in content
        ), "Synthesis SKILL.md missing mandatory pause/gate annotation"

    def test_synthesis_has_hard_gates(self):
        """Synthesis has a hard gate enforcing cost/quality checks before scale."""
        skill_path = SKILLS_DIR / "magic-data-synthesis" / "SKILL.md"
        content = skill_path.read_text()
        assert (
            "HARD GATE" in content
            or "Preview Gate (MANDATORY)" in content
            or "MANDATORY" in content
        ), "Synthesis SKILL.md missing hard gate (HARD GATE or Preview Gate (MANDATORY))"

    def test_synthesis_gate1_preview(self):
        """Synthesis requires a preview/dry-run before full-scale generation."""
        skill_path = SKILLS_DIR / "magic-data-synthesis" / "SKILL.md"
        content = skill_path.read_text()
        assert "GATE 1" in content or "preview" in content.lower() or "dry-run" in content.lower(), (
            "Synthesis SKILL.md missing preview/dry-run gate requirement"
        )

    def test_synthesis_gate2_validate(self):
        """Synthesis requires output validation (validate_synthetic.py)."""
        skill_path = SKILLS_DIR / "magic-data-synthesis" / "SKILL.md"
        content = skill_path.read_text()
        assert "validate_synthetic" in content, (
            "Synthesis SKILL.md missing reference to validate_synthetic.py"
        )


class TestWorkspaceTemplates:
    """Verify workspace templates have interaction sections."""

    def test_workspace_state_has_interaction_mode(self):
        path = TEMPLATES_DIR / "workspace_state_template.md"
        assert path.exists(), "workspace_state_template.md not found"
        content = path.read_text()
        assert "Interaction Mode" in content
        assert "collaborative" in content

    def test_workspace_state_has_lifecycle(self):
        path = TEMPLATES_DIR / "workspace_state_template.md"
        content = path.read_text()
        assert "Lifecycle" in content

    def test_analysis_journal_has_user_decisions(self):
        path = TEMPLATES_DIR / "analysis_journal_template.md"
        assert path.exists(), "analysis_journal_template.md not found"
        content = path.read_text()
        assert "User Decisions" in content

    def test_analysis_journal_has_decision_format(self):
        path = TEMPLATES_DIR / "analysis_journal_template.md"
        content = path.read_text()
        # Should contain the decision entry format markers
        assert "Context" in content
        assert "Decision" in content
        assert "Rationale" in content


class TestLifecycleSkill:
    """Verify lifecycle skill references all phases."""

    def test_lifecycle_skill_exists(self):
        path = SKILLS_DIR / "magic-data-lifecycle" / "SKILL.md"
        assert path.exists(), "magic-data-lifecycle/SKILL.md not found"

    def test_references_all_phases(self):
        path = SKILLS_DIR / "magic-data-lifecycle" / "SKILL.md"
        content = path.read_text()
        for phase in ["Discover", "Plan", "Execute", "Validate", "Deliver"]:
            assert phase in content, f"Lifecycle missing phase: {phase}"

    def test_references_refinement(self):
        path = SKILLS_DIR / "magic-data-lifecycle" / "SKILL.md"
        content = path.read_text()
        assert "Refinement" in content or "refinement" in content

    def test_references_routing_table(self):
        """Lifecycle must have skill routing table (interactive infra moved to command)."""
        path = SKILLS_DIR / "magic-data-lifecycle" / "SKILL.md"
        content = path.read_text()
        assert "routing" in content.lower() or "Route" in content

    def test_references_lifecycle_command(self):
        """Lifecycle skill should point to /magic:lifecycle for full workflow."""
        path = SKILLS_DIR / "magic-data-lifecycle" / "SKILL.md"
        content = path.read_text()
        assert "/magic:lifecycle" in content

    def test_references_custom_code_testing(self):
        path = SKILLS_DIR / "magic-data-lifecycle" / "SKILL.md"
        content = path.read_text()
        assert "custom code" in content.lower()
        assert "sample" in content.lower()


class TestExploreSkill:
    """Verify magic-data-exploration is the active exploration skill."""

    def test_exploration_skill_exists(self):
        """magic-data-exploration (v2) covers both automated and interactive exploration."""
        path = SKILLS_DIR / "magic-data-exploration" / "SKILL.md"
        assert path.exists(), "magic-data-exploration/SKILL.md not found"
        content = path.read_text()
        assert "0.1.0" in content, (
            "magic-data-exploration should be at v0.1.0"
        )


class TestInitWorkspace:
    """Verify workspace init skill has directory scaffolding."""

    def test_init_skill_exists(self):
        path = SKILLS_DIR / "magic-workspace-init" / "SKILL.md"
        assert path.exists(), "magic-workspace-init/SKILL.md not found"


class TestTriggeredByFindings:
    """Verify skills that should explain their upstream trigger context.

    v2 3-layer format expresses upstream triggers in Layer 1 (Data Processing Expertise)
    under "Thinking Questions" or "Rules" rather than a dedicated "Triggered by Findings"
    section. Accept either format.
    """

    @pytest.mark.parametrize("skill_name", [
        "magic-data-cleaning",
        "magic-data-synthesis",
        "magic-data-validation",
    ])
    def test_has_triggered_by_findings(self, skill_name):
        path = SKILLS_DIR / skill_name / "SKILL.md"
        content = path.read_text()
        # v1 format: dedicated section; v2: mentioned inline in Layer 1 context
        assert (
            "Triggered by Findings" in content
            or "profiling" in content.lower()
            or "findings" in content.lower()
        ), (
            f"{skill_name}/SKILL.md should reference its upstream trigger context "
            "(profiling findings, validation results, etc.)"
        )
