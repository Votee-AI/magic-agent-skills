"""Smoke test for skills/magic-linguistic-morph/scripts/paradigm_lookup.py.

Universal --help smoke: catches argparse / env-import / shebang regressions.
Targeted happy-path cases for this script can be added later as a follow-up.
"""

from .conftest import smoke_help


def test_paradigm_lookup_help_smoke():
    smoke_help("skills/magic-linguistic-morph/scripts/paradigm_lookup.py")
