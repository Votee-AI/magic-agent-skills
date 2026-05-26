#!/usr/bin/env python3
"""
Workflow Reinforcement — E2E Test Scaffolds.

These tests validate end-to-end workflow behavior:
- NL-only workflow completion (no slash commands)
- Mixed mode (NL + slash commands)
- Regression against existing interactive features

NOTE: Full E2E tests require an agent testing infrastructure (LLM-based).
These scaffolds validate the structural prerequisites that enable correct
agent behavior — they verify that the SKILL.md files contain the right
instructions and routing signals.
"""

import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = PROJECT_ROOT / "skills"
COMMANDS_DIR = PROJECT_ROOT / "commands" / "magic"


class TestNLWorkflowPrerequisites:
    """Verify structural prerequisites for NL-only workflow completion.

    E2E Scenario: User says "help me check this data [path]"
    Expected: workspace init → loading → profiling → guidance shown
    """

    def test_lifecycle_has_skill_routing(self):
        """Lifecycle should describe skill routing for data operations."""
        content = (SKILLS_DIR / "magic-data-lifecycle" / "SKILL.md").read_text()
        assert "routing" in content.lower() or "which skill" in content.lower()

    def test_lifecycle_references_loading_skill(self):
        """Lifecycle auto-detection should reference magic-data-loading."""
        content = (SKILLS_DIR / "magic-data-lifecycle" / "SKILL.md").read_text()
        assert "magic-data-loading" in content

    def test_lifecycle_references_profiling_scripts(self):
        """Lifecycle should reference quality_score.py and detect_all_issues.py."""
        content = (SKILLS_DIR / "magic-data-lifecycle" / "SKILL.md").read_text()
        assert "quality_score.py" in content
        assert "detect_all_issues.py" in content

    def test_lifecycle_has_pipeline_phases(self):
        """Lifecycle should describe the pipeline phase sequence."""
        content = (SKILLS_DIR / "magic-data-lifecycle" / "SKILL.md").read_text()
        assert "Discover" in content
        assert "Deliver" in content


class TestMixedModePrerequisites:
    """Verify NL and slash commands produce equivalent behavior.

    E2E Scenario: User alternates between NL and /magic commands.
    """

    def test_nl_triggers_match_slash_commands(self):
        """NL trigger sections should reference their equivalent slash commands."""
        pairs = [
            ("magic-data-lifecycle", "/magic:lifecycle"),
            ("magic-data-exploration", "explore"),
        ]
        for skill_name, slash_cmd in pairs:
            content = (SKILLS_DIR / skill_name / "SKILL.md").read_text()
            assert slash_cmd in content, (
                f"{skill_name} NL triggers don't reference {slash_cmd}"
            )

    def test_slash_commands_mention_nl_equivalence(self):
        """Slash command files should note NL equivalence via comments."""
        for cmd_file in COMMANDS_DIR.glob("*.md"):
            content = cmd_file.read_text()
            assert "Natural Language Triggers" in content, (
                f"{cmd_file.name} missing NL trigger comment"
            )

    def test_lifecycle_nl_and_command_same_workflow(self):
        """Both NL and /magic:lifecycle should describe the same workflow."""
        skill_content = (SKILLS_DIR / "magic-data-lifecycle" / "SKILL.md").read_text()
        # Both should reference Discover → Plan → Execute → Validate → Deliver
        assert "Discover" in skill_content
        assert "Plan" in skill_content
        assert "Execute" in skill_content
        assert "Validate" in skill_content
        assert "Deliver" in skill_content


class TestRegressionPrerequisites:
    """Verify existing interactive features are not broken by workflow reinforcement."""

    def test_pause_annotations_preserved(self):
        """All data skills should still have PAUSE annotations."""
        data_skills = [
            "magic-data-loading", "magic-data-profiling", "magic-data-cleaning",
            "magic-data-validation", "magic-data-transformation",
            "magic-data-exploration", "magic-statistical-analysis",
            "magic-data-synthesis", "magic-data-visualization",
            "magic-report-generation",
        ]
        for skill_name in data_skills:
            content = (SKILLS_DIR / skill_name / "SKILL.md").read_text()
            assert "PAUSE" in content, f"{skill_name} lost PAUSE annotation"

    def test_synthesis_hard_gates_preserved(self):
        """Synthesis skill should still have HARD GATE."""
        content = (SKILLS_DIR / "magic-data-synthesis" / "SKILL.md").read_text()
        assert "HARD GATE" in content

    def test_explore_read_only_preserved(self):
        """Explore skill should still enforce read-only stance."""
        content = (SKILLS_DIR / "magic-data-exploration" / "SKILL.md").read_text()
        assert "MUST NOT" in content
        assert "read-only" in content.lower() or "Read-Only" in content

    def test_workspace_templates_preserved(self):
        """Workspace templates should still exist and have required sections."""
        templates = SKILLS_DIR / "magic-data-lifecycle" / "references"
        assert (templates / "workspace_state_template.md").exists()
        assert (templates / "analysis_journal_template.md").exists()

    def test_checkpoint_conventions_preserved(self):
        """Skills should still reference checkpointing conventions."""
        for skill_name in ["magic-data-loading", "magic-data-profiling", "magic-data-cleaning"]:
            content = (SKILLS_DIR / skill_name / "SKILL.md").read_text()
            assert "ckpt_" in content or "Checkpoint" in content, (
                f"{skill_name} lost checkpointing references"
            )


class TestJSONLWorkflowPrerequisites:
    """Verify prerequisites for JSONL real data test (T-WR-01).

    E2E Scenario: Agent receives <your-test-data.jsonl> with "help me check this data"
    Expected: auto-skill activation, quality_score.py runs, findings presented
    """

    def test_loading_handles_jsonl(self):
        """Loading skill should handle JSONL files."""
        content = (SKILLS_DIR / "magic-data-loading" / "SKILL.md").read_text()
        assert "jsonl" in content.lower() or "JSONL" in content

    def test_loading_has_detect_format(self):
        """Loading should reference detect_format.py for auto-detection."""
        content = (SKILLS_DIR / "magic-data-loading" / "SKILL.md").read_text()
        assert "detect_format.py" in content

    def test_profiling_handles_text_data(self):
        """Profiling should mention text column handling."""
        content = (SKILLS_DIR / "magic-data-profiling" / "SKILL.md").read_text()
        assert "text" in content.lower()

    def test_lifecycle_auto_profiles_on_first_load(self):
        """Lifecycle should auto-run profiling after first data load."""
        content = (SKILLS_DIR / "magic-data-lifecycle" / "SKILL.md").read_text()
        assert "auto-profile" in content.lower() or "Auto-profile" in content


class TestLifecycleAdherencePrerequisites:
    """Verify prerequisites for full lifecycle adherence test (T-WR-02).

    E2E Scenario: Full Discover → Plan → Execute → Validate with phase indicators.
    """

    def test_phase_sequence_documented(self):
        """Phase sequence should be documented in lifecycle skill."""
        content = (SKILLS_DIR / "magic-data-lifecycle" / "SKILL.md").read_text()
        assert "Discover" in content and "Deliver" in content

    def test_workspace_state_updates_documented(self):
        """Workspace state updates should be documented."""
        content = (SKILLS_DIR / "magic-data-lifecycle" / "SKILL.md").read_text()
        assert "workspace_state.md" in content

    def test_quality_gating_documented(self):
        """Quality gating guidance should be in lifecycle skill."""
        content = (SKILLS_DIR / "magic-data-lifecycle" / "SKILL.md").read_text()
        assert "quality" in content.lower()
