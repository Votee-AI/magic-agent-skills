"""Smoke test for skills/linguistic-transfer/scripts/uriel_transfer_plan.py.

Universal --help smoke: catches argparse / env-import / shebang regressions.
Targeted happy-path cases for this script can be added later as a follow-up.
"""

from .conftest import smoke_help


def test_uriel_transfer_plan_help_smoke():
    smoke_help("skills/linguistic-transfer/scripts/uriel_transfer_plan.py")
