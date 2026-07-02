"""Smoke test for skills/magic-linguistic-scope/scripts/uriel_distance.py.

Universal --help smoke: catches argparse / env-import / shebang regressions.
Targeted happy-path cases for this script can be added later as a follow-up.
"""

from .conftest import smoke_help


def test_uriel_distance_help_smoke():
    smoke_help("skills/magic-linguistic-scope/scripts/uriel_distance.py")
