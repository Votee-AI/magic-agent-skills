"""0013-skill-judge-regression-ci idempotency guard.

If a PR modifies a `target_score` line in `tests/e2e/scores.json`, the same PR
MUST add a matching-date entry in `tests/e2e/scores_changelog.md`. Prevents
silent floor-lowering in the same commit that lowers the actual quality.

The check is opt-out for environments without git (CI runs in a checkout, so
git diff against `main` is available). When git or main is missing, the test
skips.
"""

from __future__ import annotations

import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCORES_REL = "tests/linguistic/e2e/scores.json"
CHANGELOG = REPO_ROOT / "tests" / "linguistic" / "e2e" / "scores_changelog.md"


def _git_diff_against_main() -> str | None:
    """Return the diff text or None if the comparison can't be made."""
    try:
        # Verify we're in a git repo and 'main' exists.
        subprocess.run(
            ["git", "rev-parse", "--verify", "main"],
            capture_output=True,
            check=True,
            cwd=REPO_ROOT,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    result = subprocess.run(
        ["git", "diff", "main", "--", SCORES_REL],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    if result.returncode != 0:
        return None
    return result.stdout


def _check_diff_against_changelog(diff: str, changelog_text: str) -> tuple[bool, str]:
    """Pure-function core of the gating logic, factored out for unit testing.

    Returns (is_ok, reason). is_ok is True when EITHER the diff doesn't touch
    target_score OR the changelog has at least one valid entry.
    """
    if "target_score" not in diff:
        return True, "no target_score modification in diff"
    recent_entry_pattern = re.compile(
        r"^## (\d{4}-\d{2}-\d{2}) — .*(target_score|per_dim_floors_met)",
        re.MULTILINE,
    )
    matches = recent_entry_pattern.findall(changelog_text)
    if not matches:
        return False, (
            "scores.json modifies a target_score line but scores_changelog.md "
            "has no entry mentioning target_score or per_dim_floors_met"
        )
    return True, f"found {len(matches)} matching changelog entries"


def test_target_score_changes_have_changelog_entry():
    diff = _git_diff_against_main()
    if diff is None:
        pytest.skip("git or main branch unavailable; skipping changelog enforcement")
    if not CHANGELOG.exists():
        # If diff touches target_score and changelog doesn't exist → real failure.
        if "target_score" in diff:
            raise AssertionError(
                "tests/e2e/scores_changelog.md is required by 0013 idempotency "
                "guard and is missing, but the diff modifies target_score"
            )
        pytest.skip("changelog absent and no target_score in diff")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    is_ok, reason = _check_diff_against_changelog(diff, CHANGELOG.read_text())
    assert is_ok, (
        f"{reason}. Add a `## {today} — <skill> <field> <old>→<new> — "
        "<rationale>` entry to tests/e2e/scores_changelog.md."
    )


# ----------------------------------------------------------------------------
# 0013 T7: gaming-guard smoke (unit test of the gating logic itself).
# Avoids the need for a real throwaway PR — simulates hostile diffs locally.
# ----------------------------------------------------------------------------


def test_gaming_guard_rejects_lowered_target_without_changelog():
    """Hostile scenario: a contributor lowers target_score in scores.json without
    adding a corresponding changelog entry. The gate MUST fail."""
    hostile_diff = (
        "diff --git a/tests/e2e/scores.json b/tests/e2e/scores.json\n"
        "@@ -10,7 +10,7 @@\n"
        '-      "target_score": 102,\n'
        '+      "target_score": 100,\n'
    )
    empty_changelog = "# scores.json changelog\n\n(no entries)\n"
    is_ok, reason = _check_diff_against_changelog(hostile_diff, empty_changelog)
    assert is_ok is False, "gating logic must reject hostile diff without changelog entry"
    assert "no entry" in reason.lower()


def test_gaming_guard_accepts_lowered_target_with_changelog():
    """Honest scenario: contributor lowers target_score AND adds a rationale entry.
    The gate MUST pass."""
    honest_diff = (
        "diff --git a/tests/e2e/scores.json b/tests/e2e/scores.json\n"
        "@@ -10,7 +10,7 @@\n"
        '-      "target_score": 102,\n'
        '+      "target_score": 100,\n'
    )
    honest_changelog = (
        "# scores.json changelog\n\n"
        "## 2026-04-24 — linguistic-ethics target_score 102→100 — re-baselining after live re-eval surfaced D1 ceiling\n"  # noqa: E501  # long changelog example string
    )
    is_ok, reason = _check_diff_against_changelog(honest_diff, honest_changelog)
    assert is_ok is True, f"gating logic should accept honest diff with changelog: {reason}"


def test_gaming_guard_passes_when_diff_does_not_touch_target_score():
    """Non-target_score scores.json edit (e.g., updating a `note` field) doesn't
    require a changelog entry."""
    benign_diff = (
        "diff --git a/tests/e2e/scores.json b/tests/e2e/scores.json\n"
        "@@ -10,7 +10,7 @@\n"
        '-      "note": "old note",\n'
        '+      "note": "new note",\n'
    )
    empty_changelog = "# scores.json changelog\n\n(no entries)\n"
    is_ok, reason = _check_diff_against_changelog(benign_diff, empty_changelog)
    assert is_ok is True
    assert "no target_score" in reason


def test_gaming_guard_rejects_changelog_entry_missing_required_field_marker():
    """Edge case: changelog entry exists but doesn't mention target_score or
    per_dim_floors_met. Gate must fail (the entry is for some other concern)."""
    hostile_diff = (
        "diff --git a/tests/e2e/scores.json b/tests/e2e/scores.json\n"
        "@@ -10,7 +10,7 @@\n"
        '-      "target_score": 102,\n'
        '+      "target_score": 100,\n'
    )
    weak_changelog = "# scores.json changelog\n\n## 2026-04-24 — linguistic-ethics minor formatting tidy-up\n"
    is_ok, _ = _check_diff_against_changelog(hostile_diff, weak_changelog)
    assert is_ok is False, "gate must require the entry to mention the enforced field by name"
