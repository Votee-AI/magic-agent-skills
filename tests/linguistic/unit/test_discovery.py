"""Discovery test: every script under skills/*/scripts/*.py must have a smoke test."""

from __future__ import annotations

from pathlib import Path

UNIT_DIR = Path(__file__).resolve().parent


def test_every_script_has_a_smoke_test(script_paths):
    missing = []
    for script in script_paths:
        expected = UNIT_DIR / f"test_{script.stem}.py"
        if not expected.exists():
            missing.append(str(script.relative_to(UNIT_DIR.parents[1])))
    assert not missing, "Scripts without a corresponding tests/unit/test_<basename>.py:\n  - " + "\n  - ".join(missing)
