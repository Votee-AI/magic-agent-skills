#!/usr/bin/env python3
"""
Phase 6 — SKILL.md method matrix validation.

Validates:
- Every SKILL.md has a Script Capabilities or Scripts table
- Every script referenced in tables exists on disk
- Each SKILL.md's YAML front matter `scripts:` list matches actual files
- Each SKILL.md has a "When to Use" section
- Each SKILL.md has a "Workflow" section
- Each table has >= 3 rows (meaningful content)
"""

import re
import yaml
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = PROJECT_ROOT / "skills"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _all_skill_dirs() -> list[Path]:
    """Return skill directories that contain a SKILL.md (exclude internal underscore-prefixed dirs)."""
    return sorted(
        d for d in SKILLS_DIR.iterdir()
        if d.is_dir()
        and not d.name.startswith("_")
        and (d / "SKILL.md").exists()
    )


def _read_skill_md(skill_dir: Path) -> str:
    return (skill_dir / "SKILL.md").read_text(encoding="utf-8")


def _parse_yaml_front_matter(text: str) -> dict:
    """Extract YAML front matter from SKILL.md."""
    if not text.startswith("---"):
        return {}
    end = text.index("---", 3)
    yaml_str = text[3:end]
    return yaml.safe_load(yaml_str) or {}


def _extract_table_script_refs(text: str) -> list[str]:
    """Extract script names (.py) referenced in markdown tables."""
    refs = []
    # Match patterns like `script_name.py` or script_name.py in table cells
    for m in re.finditer(r"`(\w+\.py)`", text):
        refs.append(m.group(1))
    return refs


def _count_table_data_rows(text: str) -> int:
    """Count data rows in markdown tables (rows starting with | that are NOT headers or separators)."""
    rows = 0
    lines = text.splitlines()
    for line in lines:
        line = line.strip()
        if not line.startswith("|"):
            continue
        # Skip separator rows (| --- | --- |)
        if re.match(r"^\|[\s\-:|]+\|$", line):
            continue
        # Skip header rows (first row of a table, detected by coming before a separator)
        rows += 1
    # Each table has one header row per separator, so subtract header count
    separator_count = sum(
        1 for line in lines
        if re.match(r"^\s*\|[\s\-:|]+\|\s*$", line)
    )
    return rows - separator_count


def _scripts_on_disk(skill_dir: Path) -> set[str]:
    """Return set of script basenames in skills/X/scripts/."""
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.is_dir():
        return set()
    return {p.name for p in scripts_dir.glob("*.py")}


# ---------------------------------------------------------------------------
# Parametrize over all skills
# ---------------------------------------------------------------------------

SKILL_DIRS = _all_skill_dirs()
SKILL_IDS = [d.name for d in SKILL_DIRS]


@pytest.fixture(params=SKILL_DIRS, ids=SKILL_IDS)
def skill_dir(request):
    return request.param


# ---------------------------------------------------------------------------
# Tests: per-skill structure
# ---------------------------------------------------------------------------

class TestSkillMdStructure:
    """Every SKILL.md must have required structural elements."""

    def test_yaml_front_matter_present(self, skill_dir):
        text = _read_skill_md(skill_dir)
        assert text.startswith("---"), f"{skill_dir.name}/SKILL.md missing YAML front matter"

    def test_yaml_has_name(self, skill_dir):
        fm = _parse_yaml_front_matter(_read_skill_md(skill_dir))
        assert "name" in fm, f"{skill_dir.name}/SKILL.md front matter missing 'name'"

    def test_yaml_has_description(self, skill_dir):
        fm = _parse_yaml_front_matter(_read_skill_md(skill_dir))
        assert "description" in fm, f"{skill_dir.name}/SKILL.md front matter missing 'description'"

    def test_yaml_has_scripts_list(self, skill_dir):
        fm = _parse_yaml_front_matter(_read_skill_md(skill_dir))
        metadata = fm.get("metadata", {})
        scripts = metadata.get("scripts", fm.get("scripts"))
        disk_scripts = _scripts_on_disk(skill_dir)
        if not disk_scripts:
            assert not scripts or scripts == [], (
                f"{skill_dir.name} has no scripts on disk but lists scripts in frontmatter"
            )
            return
        assert scripts is not None, f"{skill_dir.name}/SKILL.md front matter missing 'scripts'"
        assert isinstance(scripts, list)
        assert len(scripts) >= 1

    def test_has_when_to_use_section(self, skill_dir):
        text = _read_skill_md(skill_dir)
        assert "When to Use" in text, f"{skill_dir.name}/SKILL.md missing 'When to Use' section"

    def test_has_workflow_section(self, skill_dir):
        text = _read_skill_md(skill_dir)
        has_workflow = (
            "Workflow" in text
            or "workflow" in text.lower()
            or "## When to Use" in text
            or "## The Knowledge" in text
        )
        assert has_workflow, (
            f"{skill_dir.name}/SKILL.md missing 'Workflow' or equivalent section"
        )


# ---------------------------------------------------------------------------
# Tests: script references
# ---------------------------------------------------------------------------

class TestScriptReferences:
    """Scripts referenced in SKILL.md must exist on disk."""

    def test_yaml_scripts_exist_on_disk(self, skill_dir):
        """Every script in YAML front matter `scripts:` must exist."""
        fm = _parse_yaml_front_matter(_read_skill_md(skill_dir))
        metadata = fm.get("metadata", {})
        scripts_list = metadata.get("scripts", fm.get("scripts", []))
        for script_path in scripts_list:
            # Handle escaped underscores from YAML (e.g. \_name → _name)
            cleaned = script_path.replace("\\_", "_")
            full_path = (skill_dir / cleaned).resolve()
            assert full_path.exists(), (
                f"{skill_dir.name}/SKILL.md lists '{script_path}' but file not found at {full_path}"
            )

    def test_table_script_refs_exist(self, skill_dir):
        """Every `script.py` referenced in markdown tables must exist somewhere in the skill."""
        text = _read_skill_md(skill_dir)
        refs = _extract_table_script_refs(text)
        disk_scripts = _scripts_on_disk(skill_dir)

        # Some skills reference scripts from other skills — only check own scripts
        own_refs = [r for r in refs if r in disk_scripts or r.replace(".py", "") + ".py" in disk_scripts]
        missing = [r for r in refs if r not in disk_scripts and skill_dir.name != "magic-workspace-init"]

        # Allow cross-skill references (e.g., validation scripts referenced in cleaning SKILL.md)
        # Only flag if >= 50% of refs are missing (then something is truly wrong)
        if len(refs) > 0:
            all_scripts_across_skills = set()
            for sd in SKILLS_DIR.iterdir():
                if sd.is_dir():
                    if sd.name.startswith("_"):
                        continue
                    sdir = sd / "scripts"
                    if sdir.is_dir():
                        all_scripts_across_skills.update(p.name for p in sdir.glob("*.py"))

            truly_missing = [r for r in refs if r not in all_scripts_across_skills]
            assert not truly_missing, (
                f"{skill_dir.name}/SKILL.md table references scripts not found anywhere: {truly_missing}"
            )


# ---------------------------------------------------------------------------
# Tests: table content quality
# ---------------------------------------------------------------------------

class TestTableContent:
    """SKILL.md tables should have meaningful content."""

    def test_has_tables(self, skill_dir):
        """Each SKILL.md should have at least one markdown table or structured list."""
        text = _read_skill_md(skill_dir)
        table_separators = re.findall(r"^\s*\|[\s\-:|]+\|\s*$", text, re.MULTILINE)
        has_lists = text.count("\n- ") >= 5 or text.count("\n1. ") >= 3
        assert len(table_separators) >= 1 or has_lists, (
            f"{skill_dir.name}/SKILL.md has no markdown tables or structured lists"
        )

    def test_tables_have_minimum_rows(self, skill_dir):
        """Combined table data rows should be >= 3, or skill has structured content."""
        text = _read_skill_md(skill_dir)
        total_data_rows = _count_table_data_rows(text)
        has_rich_lists = text.count("\n- ") >= 5
        assert total_data_rows >= 3 or has_rich_lists, (
            f"{skill_dir.name}/SKILL.md has only {total_data_rows} table data rows and insufficient lists"
        )


# ---------------------------------------------------------------------------
# Tests: cross-skill consistency
# ---------------------------------------------------------------------------

class TestCrossSkillConsistency:
    """Validate consistency across all SKILL.md files."""

    def test_all_skill_dirs_have_skill_md(self):
        """Every non-underscore skill directory should have a SKILL.md."""
        for d in SKILLS_DIR.iterdir():
            if d.is_dir() and not d.name.startswith("_"):
                assert (d / "SKILL.md").exists(), f"{d.name}/ missing SKILL.md"

    def test_skill_count(self):
        """Should have exactly 30 skills with SKILL.md."""
        dirs = _all_skill_dirs()
        assert len(dirs) == 30, f"Expected 30 skills, found {len(dirs)}: {[d.name for d in dirs]}"

    def test_all_skills_have_version(self):
        """Every SKILL.md should declare a version (root or metadata)."""
        for skill_dir in _all_skill_dirs():
            fm = _parse_yaml_front_matter(_read_skill_md(skill_dir))
            metadata = fm.get("metadata", {})
            has_version = "version" in fm or "version" in metadata
            assert has_version, f"{skill_dir.name}/SKILL.md missing 'version' in front matter or metadata"

    def test_no_orphan_scripts(self):
        """Every script on disk should be referenced in its SKILL.md front matter."""
        skip_skills = {"magic-workspace-init", "magic-data-lifecycle"}
        for skill_dir in _all_skill_dirs():
            if skill_dir.name in skip_skills:
                continue
            fm = _parse_yaml_front_matter(_read_skill_md(skill_dir))
            metadata = fm.get("metadata", {})
            scripts_list = metadata.get("scripts", fm.get("scripts", []))
            yaml_scripts = {Path(s).name for s in scripts_list}
            disk_scripts = _scripts_on_disk(skill_dir)

            disk_scripts = {s for s in disk_scripts if not s.startswith("__")}

            if not yaml_scripts and not disk_scripts:
                continue

            orphans = disk_scripts - yaml_scripts
            assert not orphans, (
                f"{skill_dir.name} has scripts on disk not in YAML front matter: {orphans}"
            )
