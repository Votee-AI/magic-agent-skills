#!/usr/bin/env python3
"""
Workflow Reinforcement — Trigger Accuracy Evaluation.

Comprehensive NL trigger accuracy test — simulates skill routing decisions
using keyword-based scoring across 80+ test queries.

Target: >= 80% accuracy for all 4 P1 skills.

This replaces the skill-creator's run_eval.py for our evaluation needs.
"""

import re
import json
from pathlib import Path
from collections import defaultdict

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = PROJECT_ROOT / "skills"

# --------------------------------------------------------------------------
# Skill metadata loading
# --------------------------------------------------------------------------

def _load_skill_info() -> dict:
    """Load description and NL triggers from all SKILL.md files."""
    skills = {}
    for d in sorted(SKILLS_DIR.iterdir()):
        if d.is_dir() and not d.name.startswith("_") and (d / "SKILL.md").exists():
            content = (d / "SKILL.md").read_text(encoding="utf-8")

            # Extract description
            desc = ""
            fm_match = re.search(r"^---\n(.+?)\n---", content, re.DOTALL)
            if fm_match:
                desc_match = re.search(r'description:\s*"(.+?)"', fm_match.group(1), re.DOTALL)
                if desc_match:
                    desc = desc_match.group(1).replace("\n", " ")

            # Extract NL triggers section
            nl_text = ""
            nl_match = re.search(
                r"## Natural Language Triggers\n(.+?)(?=\n## |\Z)",
                content, re.DOTALL
            )
            if nl_match:
                nl_text = nl_match.group(1)

            # Extract When to Use section
            wtu_text = ""
            wtu_match = re.search(
                r"## When to Use\n(.+?)(?=\n## |\Z)",
                content, re.DOTALL
            )
            if wtu_match:
                wtu_text = wtu_match.group(1)

            skills[d.name] = {
                "description": desc.lower(),
                "nl_triggers": nl_text.lower(),
                "when_to_use": wtu_text.lower(),
                "full_content": content.lower(),
            }
    return skills


SKILLS = _load_skill_info()


def _score_query(skill_name: str, query: str) -> float:
    """Score how well a query matches a skill. Higher = better match."""
    info = SKILLS.get(skill_name, {})
    query_lower = query.lower()
    query_words = set(query_lower.split())
    score = 0.0

    # 1. Exact substring match in NL triggers (strongest signal)
    nl = info.get("nl_triggers", "")
    if query_lower in nl:
        score += 20
    # Partial phrase matching in NL triggers
    for word in query_words:
        if len(word) > 3 and word in nl:
            score += 3

    # 2. Description keyword match
    desc = info.get("description", "")
    desc_words = set(desc.split())
    overlap = query_words & desc_words
    # Filter out stop words
    stop = {"the", "this", "that", "with", "for", "and", "are", "was", "can", "how",
            "what", "when", "use", "data", "file", "help", "want", "need", "get",
            "run", "check", "about", "into", "from", "them", "some", "have", "has",
            "does", "did", "been", "will", "just", "like", "make", "than", "more",
            "its", "any", "all", "new", "our"}
    meaningful_overlap = overlap - stop
    score += len(meaningful_overlap) * 4

    # 3. When to Use match
    wtu = info.get("when_to_use", "")
    for word in query_words - stop:
        if len(word) > 3 and word in wtu:
            score += 2

    return score


def _route_query(query: str) -> tuple[str, dict]:
    """Route a query to the best-matching skill. Returns (skill_name, scores_dict)."""
    scores = {name: _score_query(name, query) for name in SKILLS}
    best = max(scores, key=scores.get)
    return best, scores


# --------------------------------------------------------------------------
# Evaluation dataset: 20 queries per P1 skill (10 should-trigger, 10 should-not)
# --------------------------------------------------------------------------

EVAL_QUERIES = {
    "magic-data-lifecycle": {
        "should_trigger": [
            "which skill handles data cleaning",
            "what order should I process this data",
            "how to approach this data pipeline",
            "I need to load, clean, and validate this dataset",
            "coordinate multiple data processing steps",
            "what skill should I use for profiling",
            "help me plan a multi-step data pipeline",
            "which skill handles what operation",
            "I need to decide the processing order",
            "this task spans multiple data operations",
        ],
        "should_not_trigger": [
            "plot a histogram of column age",
            "run a t-test on groups A and B",
            "generate a report of our findings",
            "fill missing values with the mean",
            "reshape this data from wide to long format",
            "create a scatter plot matrix",
            "validate the schema constraints",
            "synthesize translations for empty fields",
            "detect outliers using IQR method",
            "just load this CSV file",
        ],
    },
    "magic-data-profiling": {
        "should_trigger": [
            "profile this data",
            "what's the quality?",
            "run a quality check",
            "assess data quality",
            "how clean is this data?",
            "detect issues in this dataset",
            "find problems in this data",
            "what's the quality score?",
            "check for outliers and distribution",
            "run distribution analysis on this dataset",
        ],
        "should_not_trigger": [
            "let me explore this data interactively",
            "load this file into the workspace",
            "clean up the missing values",
            "transform data from wide to long",
            "generate a summary report",
            "fill empty fields using LLM",
            "run hypothesis testing on groups",
            "create a visualization of the results",
            "merge datasets A and B",
            "initialize a new workspace",
        ],
    },
    "magic-data-loading": {
        "should_trigger": [
            "load this file",
            "read this CSV",
            "import this data",
            "open this dataset",
            "ingest this file",
            "load this parquet file",
            "read this JSON file into the workspace",
            "import the Excel spreadsheet",
            "load data from this path",
            "read this TSV file",
        ],
        "should_not_trigger": [
            "profile this data for quality",
            "explore what patterns exist",
            "clean up missing values",
            "transform columns to new format",
            "validate the loaded data against schema",
            "generate a report of findings",
            "run statistical hypothesis tests",
            "create a chart of distributions",
            "synthesize missing translations",
            "detect and fix data quality issues",
        ],
    },
}


# --------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------

class TestTriggerAccuracy:
    """Evaluate trigger accuracy for each P1 skill."""

    @pytest.mark.parametrize("skill_name", [
        "magic-data-lifecycle",
        "magic-data-profiling",
        "magic-data-loading",
    ])
    def test_should_trigger_accuracy(self, skill_name):
        """Queries that SHOULD trigger this skill should route to it >= 80%."""
        queries = EVAL_QUERIES[skill_name]["should_trigger"]
        correct = 0
        failures = []
        for query in queries:
            routed, scores = _route_query(query)
            if routed == skill_name:
                correct += 1
            else:
                failures.append(
                    f"  '{query}' -> {routed} "
                    f"(expected={scores.get(skill_name, 0):.0f}, "
                    f"got={scores.get(routed, 0):.0f})"
                )

        accuracy = correct / len(queries) * 100
        assert accuracy >= 80, (
            f"{skill_name}: should-trigger accuracy {accuracy:.0f}% < 80%\n"
            f"Failures:\n" + "\n".join(failures)
        )

    @pytest.mark.parametrize("skill_name", [
        "magic-data-lifecycle",
        "magic-data-profiling",
        "magic-data-loading",
    ])
    def test_should_not_trigger_accuracy(self, skill_name):
        """Queries that SHOULD NOT trigger this skill should NOT route to it >= 70%."""
        queries = EVAL_QUERIES[skill_name]["should_not_trigger"]
        correct = 0
        failures = []
        for query in queries:
            routed, scores = _route_query(query)
            if routed != skill_name:
                correct += 1
            else:
                failures.append(
                    f"  '{query}' -> {routed} (score={scores.get(routed, 0):.0f})"
                )

        accuracy = correct / len(queries) * 100
        assert accuracy >= 70, (
            f"{skill_name}: should-NOT-trigger accuracy {accuracy:.0f}% < 70%\n"
            f"False triggers:\n" + "\n".join(failures)
        )


class TestOverallAccuracy:
    """Aggregate accuracy across all P1 skills."""

    def test_aggregate_accuracy_above_80(self):
        """Overall trigger accuracy across all 80 queries should be >= 80%."""
        total = 0
        correct = 0
        per_skill = {}

        for skill_name, queries in EVAL_QUERIES.items():
            skill_correct = 0
            skill_total = 0

            for query in queries["should_trigger"]:
                total += 1
                skill_total += 1
                routed, _ = _route_query(query)
                if routed == skill_name:
                    correct += 1
                    skill_correct += 1

            for query in queries["should_not_trigger"]:
                total += 1
                skill_total += 1
                routed, _ = _route_query(query)
                if routed != skill_name:
                    correct += 1
                    skill_correct += 1

            per_skill[skill_name] = (skill_correct / skill_total * 100) if skill_total > 0 else 0

        overall = correct / total * 100
        report = "\n".join(f"  {k}: {v:.0f}%" for k, v in per_skill.items())

        assert overall >= 80, (
            f"Overall accuracy {overall:.0f}% < 80%\n"
            f"Per-skill:\n{report}"
        )

    def test_no_skill_below_70(self):
        """No individual skill should drop below 70% accuracy."""
        for skill_name, queries in EVAL_QUERIES.items():
            skill_correct = 0
            skill_total = 0

            for query in queries["should_trigger"]:
                skill_total += 1
                routed, _ = _route_query(query)
                if routed == skill_name:
                    skill_correct += 1

            for query in queries["should_not_trigger"]:
                skill_total += 1
                routed, _ = _route_query(query)
                if routed != skill_name:
                    skill_correct += 1

            accuracy = skill_correct / skill_total * 100
            assert accuracy >= 70, (
                f"{skill_name}: accuracy {accuracy:.0f}% < 70% minimum"
            )


class TestAccuracyReport:
    """Generate and display accuracy report (always passes — informational)."""

    def test_print_accuracy_report(self, capsys):
        """Print detailed accuracy report."""
        results = {}
        for skill_name, queries in EVAL_QUERIES.items():
            should_correct = 0
            should_total = len(queries["should_trigger"])
            shouldnt_correct = 0
            shouldnt_total = len(queries["should_not_trigger"])

            for query in queries["should_trigger"]:
                routed, _ = _route_query(query)
                if routed == skill_name:
                    should_correct += 1

            for query in queries["should_not_trigger"]:
                routed, _ = _route_query(query)
                if routed != skill_name:
                    shouldnt_correct += 1

            results[skill_name] = {
                "trigger": f"{should_correct}/{should_total}",
                "trigger_pct": should_correct / should_total * 100,
                "reject": f"{shouldnt_correct}/{shouldnt_total}",
                "reject_pct": shouldnt_correct / shouldnt_total * 100,
                "overall_pct": (should_correct + shouldnt_correct) / (should_total + shouldnt_total) * 100,
            }

        print("\n=== Trigger Accuracy Report ===")
        print(f"{'Skill':<30} {'Trigger':>10} {'Reject':>10} {'Overall':>10}")
        print("-" * 62)
        for name, r in results.items():
            print(
                f"{name:<30} "
                f"{r['trigger']:>6} ({r['trigger_pct']:>3.0f}%) "
                f"{r['reject']:>6} ({r['reject_pct']:>3.0f}%) "
                f"{r['overall_pct']:>6.0f}%"
            )

        total_correct = sum(
            int(r["trigger"].split("/")[0]) + int(r["reject"].split("/")[0])
            for r in results.values()
        )
        total_queries = sum(
            int(r["trigger"].split("/")[1]) + int(r["reject"].split("/")[1])
            for r in results.values()
        )
        print(f"\n{'TOTAL':<30} {total_correct}/{total_queries} = {total_correct/total_queries*100:.0f}%")
        print(f"Target: >= 80%")
