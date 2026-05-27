"""Shared fixtures for tests/unit/.

Smoke-test convention: invoke each script via subprocess (mirroring how end users
run them) using known-good inputs that ship in the suite's cached language data.
No mocks of language data — the suite's value is testing the real inventories.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILLS_ROOT = REPO_ROOT / "skills"


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def script_paths() -> list[Path]:
    """All Python scripts under skills/linguistic-*/scripts/*.py (smoke-test target set)."""
    return sorted(SKILLS_ROOT.glob("linguistic-*/scripts/*.py"))


def run_script(*args: str, timeout: int = 30, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess:
    """Invoke a script with subprocess. NO_NETWORK=1 disables any opt-in --live mode."""
    env = os.environ.copy()
    env.setdefault("NO_NETWORK", "1")
    return subprocess.run(
        [sys.executable, *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(cwd),
        env=env,
    )


def smoke_help(script_relpath: str) -> None:
    """Universal smoke: invoke `python <script> --help` and assert exit 0 + non-empty stdout.

    This is the CLI-fallback smoke pattern from 0008-script-unit-tests/design.md
    for scripts whose primary mode requires inputs infeasible in CI (multi-GB
    corpora, --live mode, etc.). Catches argparse breakage, env-import errors,
    shebang regressions.
    """
    script = REPO_ROOT / script_relpath
    assert script.exists(), f"Script not found: {script_relpath}"
    result = run_script(str(script), "--help")
    assert result.returncode == 0, (
        f"--help failed for {script_relpath}: exit={result.returncode}; stderr={result.stderr}"
    )
    assert result.stdout.strip(), f"--help produced empty stdout for {script_relpath}"
