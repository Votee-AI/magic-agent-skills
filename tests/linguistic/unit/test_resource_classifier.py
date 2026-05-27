"""Smoke test for skills/linguistic-scope/scripts/resource_classifier.py.

Universal --help smoke: catches argparse / env-import / shebang regressions.
Targeted happy-path cases for this script can be added later as a follow-up.
"""

from .conftest import smoke_help


def test_resource_classifier_help_smoke():
    smoke_help("skills/linguistic-scope/scripts/resource_classifier.py")
