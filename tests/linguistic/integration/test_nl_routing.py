"""Validate that NL triggers in the orchestrator and slash commands are coherent.

This is a structural test, not an LLM eval. It checks:
- Every slash command file has at least one nl_trigger.
- Every slash command's routes_to references a real skill (or 'no skill' meta).
- The orchestrator's routing_logic.md references skills that exist.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILLS_DIR = REPO_ROOT / "skills"
COMMANDS_DIR = REPO_ROOT / "commands" / "linguistic"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def _command_files() -> list[Path]:
    return sorted(p for p in COMMANDS_DIR.glob("*.md") if p.is_file())


def _skill_names() -> set[str]:
    return {p.name for p in SKILLS_DIR.iterdir() if p.is_dir() and not p.name.startswith("_")}


def _parse_frontmatter(text: str) -> dict | None:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    return yaml.safe_load(m.group(1))


def test_ten_commands_present() -> None:
    files = _command_files()
    assert len(files) == 10, f"Expected 10 commands under commands/linguistic/, found {len(files)}"


@pytest.mark.parametrize("cmd", _command_files(), ids=lambda p: p.stem)
def test_command_has_nl_trigger(cmd: Path) -> None:
    fm = _parse_frontmatter(cmd.read_text(encoding="utf-8"))
    assert fm is not None, f"{cmd} missing frontmatter"
    triggers = fm.get("nl_triggers", [])
    assert isinstance(triggers, list) and len(triggers) >= 1, f"{cmd} must declare at least 1 nl_trigger"


@pytest.mark.parametrize("cmd", _command_files(), ids=lambda p: p.stem)
def test_command_routes_to_real_skill(cmd: Path) -> None:
    fm = _parse_frontmatter(cmd.read_text(encoding="utf-8"))
    assert fm is not None
    routes_to = fm.get("routes_to", "")
    if "no skill" in routes_to.lower():
        return  # meta command (e.g. /linguistic:help)
    skill_names = _skill_names()
    # Extract `linguistic-foo` tokens and verify each exists as a skill dir.
    referenced = set(re.findall(r"\blinguistic-[a-z]+\b", routes_to))
    assert referenced, f"{cmd} routes_to has no recognizable linguistic-* skill"
    missing = referenced - skill_names
    assert not missing, f"{cmd} routes_to references missing skills: {missing}"


def test_routing_logic_skills_exist() -> None:
    """The orchestrator's routing_logic.md references skill names that must exist as dirs."""
    routing_md = SKILLS_DIR / "linguistic-orchestrator" / "references" / "routing_logic.md"
    if not routing_md.exists():
        pytest.skip("routing_logic.md not yet authored")
    text = routing_md.read_text(encoding="utf-8")
    referenced = set(re.findall(r"\blinguistic-[a-z]+\b", text))
    skills = _skill_names() | {"linguistic-orchestrator"}
    # Phase 0 may reference optional modules even before they're authored.
    optional = {"linguistic-codeswitch", "linguistic-historical", "linguistic-lexicon"}
    missing = (referenced - skills) - optional
    assert not missing, f"routing_logic.md references unknown skills: {missing}"
