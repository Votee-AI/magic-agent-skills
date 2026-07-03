"""
E2E Test Fixtures
=================
Generates E2E datasets on first run if they don't exist.
"""
import subprocess
import sys
from pathlib import Path

import pytest

DATASETS_DIR = Path(__file__).parent / "datasets"
GENERATE_SCRIPT = Path(__file__).parent / "generate_e2e_data.py"


@pytest.fixture(scope="session", autouse=True)
def ensure_e2e_datasets():
    """Generate E2E datasets if they don't exist."""
    if not DATASETS_DIR.exists() or not any(DATASETS_DIR.iterdir()):
        result = subprocess.run(
            [sys.executable, str(GENERATE_SCRIPT)],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode != 0:
            pytest.skip(f"Could not generate E2E datasets: {result.stderr[:300]}")
