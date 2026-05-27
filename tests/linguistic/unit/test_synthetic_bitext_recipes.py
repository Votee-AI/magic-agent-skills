"""Smoke test for skills/linguistic-bitext/scripts/synthetic_bitext_recipes.py.

Universal --help smoke: catches argparse / env-import / shebang regressions.
Targeted happy-path cases for this script can be added later as a follow-up.
"""

from .conftest import smoke_help


def test_synthetic_bitext_recipes_help_smoke():
    smoke_help("skills/linguistic-bitext/scripts/synthetic_bitext_recipes.py")
