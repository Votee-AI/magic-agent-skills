"""Smoke test for skills/magic-linguistic-transfer/scripts/lora_config_advisor.py.

Universal --help smoke: catches argparse / env-import / shebang regressions.
Targeted happy-path cases for this script can be added later as a follow-up.
"""

from .conftest import smoke_help


def test_lora_config_advisor_help_smoke():
    smoke_help("skills/magic-linguistic-transfer/scripts/lora_config_advisor.py")
