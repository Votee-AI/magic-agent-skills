"""
Integration Test: Cross-Skill Workflow
=========================================
Tests: data-loading → data_profiling → data-cleaning → data-validation → statistical-analysis
Full cross-skill chain verification.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

SKILLS_DIR = Path(__file__).parent.parent.parent.parent / "skills"
TEST_DATA_DIR = Path(__file__).parent.parent.parent / "test_data"


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


class TestCrossSkillWorkflow:
    """Test full cross-skill data processing pipeline."""

    def test_full_pipeline_missing_data(self, tmp_path):
        """Load messy data → profile → clean → validate → analyze."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        input_file = TEST_DATA_DIR / "sample_missing.csv"

        if not input_file.exists():
            pytest.skip("Test data not generated yet")

        # 1. Load (data-loading skill)
        ckpt_01 = workspace / "ckpt_01_loaded.csv"
        r1, _ = run_script("magic-data-loading/scripts/load_file.py", str(input_file), str(ckpt_01))
        assert r1["success"], f"Load failed: {r1.get('error')}"

        # 2. Profile (data_profiling skill)
        ckpt_02 = workspace / "ckpt_02_quality.json"
        r2, _ = run_script("magic-data-profiling/scripts/quality_score.py", str(ckpt_01), str(ckpt_02))
        assert r2["success"], f"Quality score failed: {r2.get('error')}"
        # Missing data should lower quality score
        assert r2.get("overall_score", 100) < 96, "Score should reflect missing data"

        # 3. Clean (data-cleaning skill)
        ckpt_03 = workspace / "ckpt_03_cleaned.csv"
        r3, _ = run_script(
            "magic-data-cleaning/scripts/handle_missing.py",
            str(ckpt_01), str(ckpt_03), "--strategy", "auto"
        )
        assert r3["success"], f"Cleaning failed: {r3.get('error')}"

        # 4. Validate (data-validation skill)
        ckpt_04 = workspace / "ckpt_04_schema.json"
        r4, _ = run_script("magic-data-validation/scripts/infer_schema.py", "--input", str(ckpt_03), "--output", str(ckpt_04))
        assert r4["success"], f"Schema inference failed: {r4.get('error')}"

        # 5. Analyze (statistical-analysis skill)
        ckpt_05 = workspace / "ckpt_05_stats.json"
        r5, _ = run_script("magic-statistical-analysis/scripts/descriptive_stats.py", "--input", str(ckpt_03), "--output", str(ckpt_05))
        assert r5["success"], f"Stats failed: {r5.get('error')}"

        # Verify all checkpoints exist
        checkpoints = sorted(workspace.glob("ckpt_*"))
        assert len(checkpoints) >= 5, f"Expected 5+ checkpoints, got {len(checkpoints)}"

    def test_data_flows_correctly_between_skills(self, tmp_path):
        """Output of one skill should be valid input to the next."""
        input_file = TEST_DATA_DIR / "sample_clean.csv"
        if not input_file.exists():
            pytest.skip("Test data not generated yet")

        # Load → Profile → Stats should all work on same data
        loaded = tmp_path / "loaded.csv"
        r1, _ = run_script("magic-data-loading/scripts/load_file.py", str(input_file), str(loaded))
        assert r1["success"]

        stats_out = tmp_path / "stats.json"
        r2, _ = run_script("magic-statistical-analysis/scripts/descriptive_stats.py", "--input", str(loaded), "--output", str(stats_out))
        assert r2["success"]

        # Row counts should be consistent
        assert r1.get("rows_out", r1.get("rows_in")) == r2.get("rows_in"), \
            "Row count mismatch between load output and stats input"
