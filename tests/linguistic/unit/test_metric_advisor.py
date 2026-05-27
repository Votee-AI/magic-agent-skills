"""Smoke test for skills/linguistic-eval/scripts/metric_advisor.py.

Universal --help smoke: catches argparse / env-import / shebang regressions.
Targeted happy-path cases for this script can be added later as a follow-up.
"""

from .conftest import smoke_help


def test_metric_advisor_help_smoke():
    smoke_help("skills/linguistic-eval/scripts/metric_advisor.py")
