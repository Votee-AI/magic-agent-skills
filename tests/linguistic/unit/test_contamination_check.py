"""Smoke test for skills/linguistic-eval/scripts/contamination_check.py.

Universal --help smoke: catches argparse / env-import / shebang regressions.
Targeted happy-path cases for this script can be added later as a follow-up.
"""

from .conftest import smoke_help


def test_contamination_check_help_smoke():
    smoke_help("skills/linguistic-eval/scripts/contamination_check.py")
