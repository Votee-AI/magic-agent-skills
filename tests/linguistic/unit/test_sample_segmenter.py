"""Smoke test for skills/magic-linguistic-tokenize/scripts/sample_segmenter.py.

Universal --help smoke: catches argparse / env-import / shebang regressions.
Targeted happy-path cases for this script can be added later as a follow-up.
"""

from .conftest import smoke_help


def test_sample_segmenter_help_smoke():
    smoke_help("skills/magic-linguistic-tokenize/scripts/sample_segmenter.py")
