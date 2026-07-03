"""Smoke test for skills/magic-linguistic-annotate/scripts/iaa_calculator.py.

Universal --help smoke: catches argparse / env-import / shebang regressions.
Targeted happy-path cases for this script can be added later as a follow-up.
"""

from .conftest import smoke_help


def test_iaa_calculator_help_smoke():
    smoke_help("skills/magic-linguistic-annotate/scripts/iaa_calculator.py")
