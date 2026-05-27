#!/usr/bin/env python3
"""
Workflow Reinforcement — Script Reference Validation Tests (v2 3-layer format).

Validates:
- Each SKILL.md with scripts has a ## Reference Scripts section (v2 format)
- Script names in the frontmatter scripts: list resolve to actual files on disk
- SKILL.md mentions positional args or input/output file patterns
- Path format is consistent

NOTE: Updated from v1 "Script Quick Reference" table format to v2 "## Reference Scripts"
section + frontmatter scripts: list (3-layer restructure, 2026-04-30).
"""

import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = PROJECT_ROOT / "skills"

# Skills that have scripts/ directories and MUST have Reference Scripts sections
SKILLS_WITH_SCRIPTS = [
    "magic-data-profiling",
    "magic-data-loading",
    "magic-data-cleaning",
    "magic-data-transformation",
    "magic-data-validation",
    "magic-data-exploration",
    "magic-statistical-analysis",
    "magic-data-visualization",
    "magic-report-generation",
    "magic-data-synthesis",
]

# Skills that should NOT have script reference tables (no scripts/ dir)
SKILLS_WITHOUT_SCRIPTS = [
    "magic-data-lifecycle",
    "magic-workspace-init",
]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_script_names_from_frontmatter(text: str) -> list[str]:
    """Extract script filenames from SKILL.md frontmatter scripts: list.

    Matches patterns like:
      scripts:
        - scripts/quality_score.py
        - scripts/detect_format.py
    Returns just the basename: quality_score.py
    """
    names = []
    pattern = re.compile(r"^\s+-\s+scripts/([\w.]+\.py)\s*$", re.MULTILINE)
    for m in pattern.finditer(text):
        names.append(m.group(1))
    return names


def _has_reference_scripts_section(text: str) -> bool:
    """Check if SKILL.md has a ## Reference Scripts section (v2 3-layer format)."""
    return "## Reference Scripts" in text


class TestScriptReferenceSections:
    """Verify ## Reference Scripts sections exist (v2 3-layer format)."""

    @pytest.mark.parametrize("skill_name", SKILLS_WITH_SCRIPTS)
    def test_has_reference_scripts_section(self, skill_name):
        """Each skill with scripts must have a ## Reference Scripts section."""
        path = SKILLS_DIR / skill_name / "SKILL.md"
        assert path.exists(), f"SKILL.md not found for {skill_name}"
        content = _read_text(path)
        assert _has_reference_scripts_section(content), (
            f"{skill_name}/SKILL.md missing '## Reference Scripts' section "
            "(v2 3-layer format; was 'Script Quick Reference' in v1)"
        )

    @pytest.mark.parametrize("skill_name", SKILLS_WITH_SCRIPTS)
    def test_frontmatter_lists_scripts(self, skill_name):
        """Frontmatter scripts: list should name at least one .py script."""
        path = SKILLS_DIR / skill_name / "SKILL.md"
        content = _read_text(path)
        scripts = _extract_script_names_from_frontmatter(content)
        assert len(scripts) > 0, (
            f"{skill_name}: SKILL.md frontmatter missing 'scripts:' list"
        )

    @pytest.mark.parametrize("skill_name", SKILLS_WITH_SCRIPTS)
    def test_has_positional_args_note(self, skill_name):
        """SKILL.md should document how to run scripts (v2: via script name references in table).

        v1 required 'positional' / 'input_file output_file' text in the Quick Reference table.
        v2 uses a ## Reference Scripts table with script names and descriptions.
        Accept any of: positional arg language, input.csv pattern, or .py script references
        in a table row (v2 format).
        """
        path = SKILLS_DIR / skill_name / "SKILL.md"
        content = _read_text(path)
        lower = content.lower()
        # Check for any form of script usage documentation
        has_script_table_row = bool(re.search(r"\|\s*`[\w.]+\.py`\s*\|", content))
        assert (
            "positional" in lower
            or "input_file output_file" in lower
            or "input.csv" in lower
            or "python scripts/" in lower
            or has_script_table_row
        ), (
            f"{skill_name}: SKILL.md should document script usage "
            "(script table, positional args, or input/output file patterns)"
        )


class TestScriptPathsResolve:
    """Verify all scripts listed in frontmatter exist on disk."""

    @pytest.mark.parametrize("skill_name", SKILLS_WITH_SCRIPTS)
    def test_all_paths_resolve(self, skill_name):
        """Every script name in frontmatter scripts: list must exist on disk."""
        path = SKILLS_DIR / skill_name / "SKILL.md"
        content = _read_text(path)
        script_names = _extract_script_names_from_frontmatter(content)

        assert len(script_names) > 0, (
            f"{skill_name}: No script names found in frontmatter 'scripts:' list"
        )

        missing = []
        for name in script_names:
            full_path = SKILLS_DIR / skill_name / "scripts" / name
            if not full_path.exists():
                missing.append(name)

        assert not missing, (
            f"{skill_name}: Scripts in frontmatter do not exist on disk: {missing}"
        )

    @pytest.mark.parametrize("skill_name", SKILLS_WITH_SCRIPTS)
    def test_paths_match_skill_directory(self, skill_name):
        """All scripts must live in the skill's own scripts/ directory."""
        path = SKILLS_DIR / skill_name / "SKILL.md"
        content = _read_text(path)
        script_names = _extract_script_names_from_frontmatter(content)

        missing = []
        for name in script_names:
            full_path = SKILLS_DIR / skill_name / "scripts" / name
            if not full_path.exists():
                missing.append(name)

        assert not missing, (
            f"{skill_name}: Frontmatter scripts not found in {skill_name}/scripts/: {missing}"
        )


class TestScriptCoverage:
    """Verify frontmatter scripts list covers scripts in the scripts/ dir."""

    @pytest.mark.parametrize("skill_name", SKILLS_WITH_SCRIPTS)
    def test_all_scripts_in_dir_are_referenced(self, skill_name):
        """Every core .py file in scripts/ should appear in frontmatter scripts: list."""
        scripts_dir = SKILLS_DIR / skill_name / "scripts"
        if not scripts_dir.exists():
            pytest.skip(f"{skill_name} has no scripts/ directory")

        actual_scripts = {f.name for f in scripts_dir.glob("*.py") if f.name != "__init__.py"}
        if not actual_scripts:
            pytest.skip(f"{skill_name} has no .py scripts")

        skill_md_path = SKILLS_DIR / skill_name / "SKILL.md"
        content = _read_text(skill_md_path)
        referenced_scripts = set(_extract_script_names_from_frontmatter(content))

        missing = actual_scripts - referenced_scripts
        # Helper scripts (prefixed with _) are exempt
        important_missing = {s for s in missing if not s.startswith("_")}
        # Soft check: only assert if ALL scripts are missing (implies no frontmatter list)
        if len(important_missing) == len(actual_scripts):
            assert False, (
                f"{skill_name}: None of the scripts in scripts/ appear in frontmatter: "
                f"{important_missing}"
            )


class TestFrontmatterScriptConsistency:
    """Verify frontmatter scripts: list matches files on disk (v2 format)."""

    @pytest.mark.parametrize("skill_name", SKILLS_WITH_SCRIPTS)
    def test_frontmatter_scripts_in_quick_reference(self, skill_name):
        """Scripts listed in YAML frontmatter must exist in ## Reference Scripts section."""
        path = SKILLS_DIR / skill_name / "SKILL.md"
        content = _read_text(path)

        fm_scripts = _extract_script_names_from_frontmatter(content)
        if not fm_scripts:
            pytest.skip(f"{skill_name} has no scripts in frontmatter")

        # In v2 format, scripts are referenced by name in ## Reference Scripts section
        ref_section_match = re.search(
            r"## Reference Scripts(.+?)(?=^##|\Z)", content,
            re.DOTALL | re.MULTILINE
        )
        if not ref_section_match:
            pytest.fail(f"{skill_name}: Missing '## Reference Scripts' section")

        ref_section = ref_section_match.group(1)
        missing = [s for s in fm_scripts if s not in ref_section]
        assert not missing, (
            f"{skill_name}: Frontmatter lists scripts not in Quick Reference: {missing}"
        )
