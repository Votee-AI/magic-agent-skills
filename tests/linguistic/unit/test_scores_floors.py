"""0013-skill-judge-regression-ci floor assertion (Wave 2).

Parametrized over the 18 skill entries in tests/e2e/scores.json. Each test asserts:
- target_score field present
- iter-2-live.total >= target_score
- iter-2-live.per_dim_floors_met is True

Test placement: tests/unit/ (JSON-read assertion, not e2e flow).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCORES_PATH = REPO_ROOT / "tests" / "linguistic" / "e2e" / "scores.json"

_SCORES = json.loads(SCORES_PATH.read_text())["scores"]
_SKILLS = sorted(_SCORES.items())


@pytest.mark.parametrize("skill,data", _SKILLS, ids=[s for s, _ in _SKILLS])
def test_skill_score_meets_target(skill: str, data: dict):
    # Each skill has a single iter-N-live block; pick the most recent (lexicographic max key).
    iter_keys = sorted(k for k in data.keys() if k.startswith("iter-"))
    assert iter_keys, f"{skill}: no iter-N-live block found"
    latest = data[iter_keys[-1]]
    target = latest.get("target_score")
    assert target is not None, f"{skill}: latest iter block missing target_score"
    assert latest["total"] >= target, f"{skill}: total={latest['total']} < target_score={target} (iter={iter_keys[-1]})"
    assert latest["per_dim_floors_met"] is True, (
        f"{skill}: per_dim_floors_met is {latest['per_dim_floors_met']!r} "
        f"(iter={iter_keys[-1]}); fix the failing dim or re-score"
    )
