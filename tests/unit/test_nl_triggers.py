#!/usr/bin/env python3
"""
Workflow Reinforcement — NL Trigger Pattern Coverage Tests.

Validates:
- All 4 P1 skills have Natural Language Triggers sections
- Each NL trigger section has >= 3 trigger patterns
- All slash commands have corresponding NL trigger comments
- NL triggers mention equivalent slash commands
"""

import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = PROJECT_ROOT / "skills"
COMMANDS_DIR = PROJECT_ROOT / "commands" / "magic"

# P1 skills that MUST have NL trigger sections
P1_SKILLS = [
    "magic-data-lifecycle",
    "magic-data-profiling",
    "magic-data-loading",
]

# All slash command files that should have NL trigger comments
SLASH_COMMANDS = [
    "explore.md",
    "findings.md",
    "propose.md",
    "decide.md",
    "status.md",
    "lifecycle.md",
    "review.md",
    "spec.md",
    "init-workspace.md",
]

# Mapping of slash commands to expected NL trigger keywords
COMMAND_TRIGGER_KEYWORDS = {
    "explore.md": ["explore", "investigate"],
    "findings.md": ["find", "issue"],
    "propose.md": ["propose", "suggest", "should"],
    "decide.md": ["go with", "decision"],
    "status.md": ["status", "where"],
    "lifecycle.md": ["phase", "lifecycle"],
    "review.md": ["review"],
    "spec.md": ["spec", "plan"],
    "init-workspace.md": ["workspace", "initialize"],
}


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_nl_trigger_lines(text: str) -> list[str]:
    """Extract lines from the Natural Language Triggers section."""
    lines = []
    in_section = False
    for line in text.splitlines():
        if re.match(r"^##\s+Natural Language Triggers", line):
            in_section = True
            continue
        if in_section and re.match(r"^##\s+", line):
            break  # Next section
        if in_section and line.strip().startswith("-"):
            lines.append(line.strip())
    return lines


class TestP1SkillNLTriggers:
    """Verify P1 skills have Natural Language Triggers sections."""

    @pytest.mark.parametrize("skill_name", P1_SKILLS)
    def test_has_nl_triggers_section(self, skill_name):
        """Each P1 skill must have a ## Natural Language Triggers section."""
        path = SKILLS_DIR / skill_name / "SKILL.md"
        assert path.exists(), f"SKILL.md not found for {skill_name}"
        content = _read_text(path)
        assert "## Natural Language Triggers" in content, (
            f"{skill_name}/SKILL.md missing '## Natural Language Triggers' section"
        )

    @pytest.mark.parametrize("skill_name", P1_SKILLS)
    def test_has_at_least_3_trigger_patterns(self, skill_name):
        """Each NL trigger section must have >= 3 trigger phrases."""
        path = SKILLS_DIR / skill_name / "SKILL.md"
        content = _read_text(path)
        trigger_lines = _extract_nl_trigger_lines(content)
        assert len(trigger_lines) >= 3, (
            f"{skill_name}/SKILL.md has only {len(trigger_lines)} NL trigger "
            f"patterns (need >= 3): {trigger_lines}"
        )

    @pytest.mark.parametrize("skill_name", P1_SKILLS)
    def test_nl_triggers_before_workflow(self, skill_name):
        """NL triggers section should appear before Workflow section."""
        path = SKILLS_DIR / skill_name / "SKILL.md"
        content = _read_text(path)
        nl_pos = content.find("## Natural Language Triggers")
        workflow_pos = content.find("## Workflow")
        if workflow_pos == -1:
            # Some skills use different section names
            workflow_pos = content.find("## The Stance")
        if workflow_pos == -1:
            workflow_pos = content.find("## Overview")
        if nl_pos != -1 and workflow_pos != -1:
            assert nl_pos < workflow_pos, (
                f"{skill_name}: NL Triggers appears after Workflow/Stance/Overview"
            )

    def test_lifecycle_triggers_mention_slash_commands(self):
        """Lifecycle NL triggers should mention equivalent slash commands."""
        path = SKILLS_DIR / "magic-data-lifecycle" / "SKILL.md"
        content = _read_text(path)
        # Check the trigger section mentions the equivalence
        assert "/magic:lifecycle" in content or "/magic:status" in content, (
            "Lifecycle NL triggers should reference equivalent slash commands"
        )

    def test_exploration_skill_has_triggers(self):
        """magic-data-exploration should have NL trigger section."""
        path = SKILLS_DIR / "magic-data-exploration" / "SKILL.md"
        content = _read_text(path)
        assert "## Natural Language Triggers" in content, (
            "magic-data-exploration should have NL triggers section"
        )

    def test_triggers_use_natural_phrases(self):
        """NL triggers should use conversational language, not technical jargon."""
        for skill_name in P1_SKILLS:
            path = SKILLS_DIR / skill_name / "SKILL.md"
            content = _read_text(path)
            trigger_lines = _extract_nl_trigger_lines(content)
            # At least some lines should contain quoted natural language phrases
            quoted_lines = [
                line for line in trigger_lines
                if '"' in line or "'" in line
            ]
            assert len(quoted_lines) >= 2, (
                f"{skill_name}: NL triggers should have >= 2 quoted phrase lines, "
                f"got {len(quoted_lines)} out of {len(trigger_lines)}"
            )


class TestSlashCommandNLTriggers:
    """Verify all slash command files have NL trigger comments."""

    @pytest.mark.parametrize("cmd_file", SLASH_COMMANDS)
    def test_has_nl_trigger_comment(self, cmd_file):
        """Each slash command file should have an HTML comment with NL triggers."""
        path = COMMANDS_DIR / cmd_file
        assert path.exists(), f"Command file not found: {cmd_file}"
        content = _read_text(path)
        assert "<!-- Natural Language Triggers:" in content, (
            f"{cmd_file} missing NL trigger HTML comment"
        )

    @pytest.mark.parametrize("cmd_file", SLASH_COMMANDS)
    def test_trigger_comment_has_keywords(self, cmd_file):
        """NL trigger comment should contain relevant keywords."""
        path = COMMANDS_DIR / cmd_file
        content = _read_text(path)
        expected_keywords = COMMAND_TRIGGER_KEYWORDS.get(cmd_file, [])
        comment_match = re.search(
            r"<!-- Natural Language Triggers:(.+?)-->", content, re.DOTALL
        )
        if comment_match and expected_keywords:
            comment_text = comment_match.group(1).lower()
            found = [kw for kw in expected_keywords if kw in comment_text]
            assert len(found) >= 1, (
                f"{cmd_file}: NL trigger comment missing expected keywords "
                f"{expected_keywords}. Found: {comment_text.strip()}"
            )


class TestNLTriggerConsistency:
    """Cross-check NL triggers between SKILL.md files and slash commands."""

    def test_exploration_skill_and_command_aligned(self):
        """magic-data-exploration NL triggers should overlap with explore.md triggers."""
        skill_content = _read_text(
            SKILLS_DIR / "magic-data-exploration" / "SKILL.md"
        )
        cmd_content = _read_text(COMMANDS_DIR / "explore.md")
        assert "explore" in skill_content.lower()
        assert "explore" in cmd_content.lower()

    def test_lifecycle_skill_and_command_aligned(self):
        """magic-data-lifecycle NL triggers should overlap with lifecycle.md triggers."""
        skill_content = _read_text(
            SKILLS_DIR / "magic-data-lifecycle" / "SKILL.md"
        )
        cmd_content = _read_text(COMMANDS_DIR / "lifecycle.md")
        assert "phase" in skill_content.lower() or "lifecycle" in skill_content.lower()
        assert "phase" in cmd_content.lower() or "lifecycle" in cmd_content.lower()
