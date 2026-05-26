#!/usr/bin/env python3
"""
Workflow Reinforcement — NL -> Skill Routing Simulation Tests.

Simulates the routing decision an agent would make when given natural language input.
Tests that SKILL.md descriptions and NL triggers contain sufficient keywords
for an agent to route to the correct skill.

This is a keyword-matching simulation, not a full LLM routing test.
For full LLM-based routing, use the skill-creator evaluation pipeline.
"""

import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = PROJECT_ROOT / "skills"

# All skills with their SKILL.md descriptions
SKILLS = {}
for d in sorted(SKILLS_DIR.iterdir()):
    if d.is_dir() and not d.name.startswith("_") and (d / "SKILL.md").exists():
        content = (d / "SKILL.md").read_text(encoding="utf-8")
        # Extract description from frontmatter
        fm_match = re.search(r"^---\n(.+?)\n---", content, re.DOTALL)
        desc = ""
        if fm_match:
            desc_match = re.search(r'description:\s*"(.+?)"', fm_match.group(1))
            if desc_match:
                desc = desc_match.group(1)
        SKILLS[d.name] = {
            "description": desc,
            "content": content,
        }


def _skill_keyword_score(skill_name: str, query: str) -> int:
    """Score how well a query matches a skill based on keyword overlap.

    Checks description, NL triggers, and When to Use sections.
    """
    info = SKILLS.get(skill_name, {})
    desc = info.get("description", "").lower()
    content = info.get("content", "").lower()
    query_lower = query.lower()
    query_words = set(query_lower.split())

    score = 0
    # Check description keyword overlap
    desc_words = set(desc.split())
    score += len(query_words & desc_words) * 3

    # Check if query appears as a substring in NL triggers
    nl_section_match = re.search(
        r"## natural language triggers\n(.+?)(?=\n## |\Z)",
        content,
        re.DOTALL,
    )
    if nl_section_match:
        nl_text = nl_section_match.group(1)
        # Boost if exact query phrase appears
        if query_lower in nl_text:
            score += 10
        # Boost for word overlap in NL section
        nl_words = set(nl_text.split())
        score += len(query_words & nl_words) * 2

    return score


def _route_query(query: str) -> str:
    """Route a query to the best-matching skill using keyword scoring."""
    scores = {
        name: _skill_keyword_score(name, query)
        for name in SKILLS
    }
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else None


# Test data: (query, expected_skill)
ROUTING_TEST_CASES = [
    # Lifecycle / entry-point queries
    ("start processing this dataset", "magic-data-lifecycle"),
    ("help me clean this data", "magic-data-lifecycle"),

    # Explore queries — magic-data-exploration is the canonical skill.
    ("let me explore this data", "magic-data-exploration"),
    ("what's in this dataset?", "magic-data-exploration"),
    ("I want to investigate this", "magic-data-exploration"),

    # Profiling queries
    ("profile this data", "magic-data-profiling"),
    ("what's the quality score?", "magic-data-profiling"),
    ("assess data quality", "magic-data-profiling"),

    # Loading queries
    ("load this CSV file", "magic-data-loading"),
    ("import this data", "magic-data-loading"),
]


class TestNLRouting:
    """Simulate NL -> skill routing and verify correctness."""

    @pytest.mark.parametrize("query,expected_skill", ROUTING_TEST_CASES)
    def test_query_routes_to_correct_skill(self, query, expected_skill):
        """Query should route to the expected skill."""
        routed = _route_query(query)
        assert routed == expected_skill, (
            f"Query '{query}' routed to '{routed}', expected '{expected_skill}'. "
            f"Scores: {expected_skill}={_skill_keyword_score(expected_skill, query)}, "
            f"{routed}={_skill_keyword_score(routed, query)}"
        )


class TestNLDisambiguation:
    """Verify that similar skills are disambiguated by NL triggers."""

    def test_lifecycle_vs_loading(self):
        """'process this full dataset' should prefer lifecycle over loading."""
        lifecycle_score = _skill_keyword_score("magic-data-lifecycle", "process this full dataset")
        loading_score = _skill_keyword_score("magic-data-loading", "process this full dataset")
        assert lifecycle_score >= loading_score, (
            f"'process this full dataset' should prefer lifecycle "
            f"(score {lifecycle_score}) over loading (score {loading_score})"
        )
