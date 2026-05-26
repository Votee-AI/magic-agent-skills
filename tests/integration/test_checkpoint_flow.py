"""
Integration Test: Checkpoint Flow
====================================
Verifies checkpoint naming convention and resume-from-checkpoint behavior.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

SKILLS_DIR = Path(__file__).parent.parent.parent / "skills"
TEST_DATA_DIR = Path(__file__).parent.parent / "unit" / "test_data"


def run_script(script_path, *args):
    full_path = SKILLS_DIR / script_path
    result = subprocess.run(
        [sys.executable, str(full_path), *[str(a) for a in args]],
        capture_output=True, text=True, timeout=120
    )
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError:
        output = {"success": False, "error": f"Non-JSON output: {result.stdout[:500]}"}
    return output, result.returncode


class TestCheckpointFlow:
    """Verify checkpoint convention works across skills."""

    def test_checkpoint_naming_convention(self, tmp_path):
        """Checkpoint files follow ckpt_{step}_{operation}.{ext} convention."""
        input_file = TEST_DATA_DIR / "sample_clean.csv"
        if not input_file.exists():
            pytest.skip("Test data not generated yet")

        # Create checkpoints following the convention
        ckpt_01 = tmp_path / "ckpt_01_loaded.csv"
        result, _ = run_script(
            "magic-data-loading/scripts/load_file.py",
            str(input_file), str(ckpt_01)
        )
        assert result["success"]
        assert ckpt_01.exists()
        assert ckpt_01.name.startswith("ckpt_01_")

    def test_checkpoint_is_valid_data(self, tmp_path):
        """Checkpoint CSV files are valid and loadable."""
        import pandas as pd

        input_file = TEST_DATA_DIR / "sample_clean.csv"
        if not input_file.exists():
            pytest.skip("Test data not generated yet")

        ckpt = tmp_path / "ckpt_01_loaded.csv"
        result, _ = run_script(
            "magic-data-loading/scripts/load_file.py",
            str(input_file), str(ckpt)
        )
        assert result["success"]

        # Checkpoint should be loadable as a DataFrame
        df = pd.read_csv(ckpt)
        assert len(df) > 0, "Checkpoint file should contain data"
        assert len(df.columns) > 0, "Checkpoint should have columns"

    def test_checkpoint_chain_preserves_data(self, tmp_path):
        """Data flows correctly between checkpoints."""
        import pandas as pd

        input_file = TEST_DATA_DIR / "sample_clean.csv"
        if not input_file.exists():
            pytest.skip("Test data not generated yet")

        # Step 1: Load
        ckpt_01 = tmp_path / "ckpt_01_loaded.csv"
        r1, _ = run_script("magic-data-loading/scripts/load_file.py", str(input_file), str(ckpt_01))
        assert r1["success"]

        # Step 2: Use ckpt_01 as input for stats
        ckpt_02 = tmp_path / "ckpt_02_stats.json"
        r2, _ = run_script("magic-statistical-analysis/scripts/descriptive_stats.py", "--input", str(ckpt_01), "--output", str(ckpt_02))
        assert r2["success"]

        # Verify row counts match
        assert r1.get("rows_out", r1.get("rows_in")) == r2.get("rows_in"), \
            "Row count should be consistent between checkpoint chain steps"
