#!/usr/bin/env python3
"""
Documentation consistency tests.

Validates:
- Workspace templates exist and are referenced correctly
"""

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = PROJECT_ROOT / "skills"
TEMPLATES_DIR = SKILLS_DIR / "magic-data-lifecycle" / "references"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Tests: Workspace templates
# ---------------------------------------------------------------------------

class TestWorkspaceTemplatesExist:
    """Validate workspace templates exist on disk."""

    def test_workspace_state_template_exists(self):
        path = TEMPLATES_DIR / "workspace_state_template.md"
        assert path.exists(), f"Missing: {path}"

    def test_analysis_journal_template_exists(self):
        path = TEMPLATES_DIR / "analysis_journal_template.md"
        assert path.exists(), f"Missing: {path}"

    def test_workspace_state_template_has_required_sections(self):
        """workspace_state.md template should have key section headers."""
        path = TEMPLATES_DIR / "workspace_state_template.md"
        text = _read_text(path)
        required = ["Objective", "Data Overview", "Current Plan",
                     "Current Task", "Completed Work"]
        for section in required:
            assert section in text, (
                f"workspace_state_template.md missing section: {section}"
            )

    def test_analysis_journal_template_has_required_sections(self):
        """analysis_journal.md template should have key section headers."""
        path = TEMPLATES_DIR / "analysis_journal_template.md"
        text = _read_text(path)
        required = ["Summary", "Decisions", "Open Questions"]
        for section in required:
            assert section in text, (
                f"analysis_journal_template.md missing section: {section}"
            )
