"""Regression test — re-runs structural checks for ALL previously-shipped skills
at every new phase merge.

This is the cross-phase consistency safeguard from ralplan iter-2. Each new
OpenSpec change (Phase 1+) MUST keep this passing for all earlier-phase skills.

The list `SHIPPED_SKILLS` is updated at the end of each phase's merge.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILLS_DIR = REPO_ROOT / "skills"


# Update this list at the end of each phase's merge.
# Phase 0: orchestrator.
# Phase 1: scope, scripts, tokenize, ethics.
# Phase 2: corpus, bitext, transfer.
# Phase 3a: morph, syntax, annotate.
# Phase 3b: semantics, discourse, speech.
# Phase 4 (final): eval + 3 optional Mindset (codeswitch, historical, lexicon).
SHIPPED_SKILLS: list[str] = [
    "linguistic-orchestrator",
    "linguistic-scope",
    "linguistic-scripts",
    "linguistic-tokenize",
    "linguistic-ethics",
    "linguistic-corpus",
    "linguistic-bitext",
    "linguistic-transfer",
    "linguistic-morph",
    "linguistic-syntax",
    "linguistic-annotate",
    "linguistic-semantics",
    "linguistic-discourse",
    "linguistic-speech",
    "linguistic-eval",
    "linguistic-codeswitch",
    "linguistic-historical",
    "linguistic-lexicon",
]


@pytest.mark.parametrize("skill_name", SHIPPED_SKILLS)
def test_shipped_skill_has_skill_md(skill_name: str) -> None:
    p = SKILLS_DIR / skill_name / "SKILL.md"
    assert p.exists(), f"Regression: {skill_name}/SKILL.md was previously shipped but is now missing"


@pytest.mark.parametrize("skill_name", SHIPPED_SKILLS)
def test_shipped_skill_dir_intact(skill_name: str) -> None:
    p = SKILLS_DIR / skill_name
    assert p.is_dir(), f"Regression: {skill_name}/ was previously shipped but the directory is gone"
