"""Smoke test for skills/linguistic-scripts/scripts/detect_confusables.py.

Universal --help smoke: catches argparse / env-import / shebang regressions.
Targeted happy-path cases for this script can be added later as a follow-up.
"""

from .conftest import smoke_help


def test_detect_confusables_help_smoke():
    smoke_help("skills/linguistic-scripts/scripts/detect_confusables.py")
