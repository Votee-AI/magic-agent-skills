"""
Integration Test: Data Cleaning Workflow
==========================================
Tests the full cleaning pipeline: load → detect_issues → handle_missing → normalize_strings → validate_clean
Verifies checkpoint files are created at each step.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

SKILLS_DIR = Path(__file__).parent.parent.parent.parent / "skills"
TEST_DATA_DIR = Path(__file__).parent.parent.parent / "test_data"


def run_script(script_path, *args):
    """Run a skill script and parse JSON output."""
    full_path = SKILLS_DIR / script_path
    result = subprocess.run(
        [sys.executable, str(full_path), *[str(a) for a in args]],
        capture_output=True, text=True, timeout=120
    )
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError:
        output = {"success": False, "error": f"Non-JSON output: {result.stdout[:500]}", "stderr": result.stderr[:500]}
    return output, result.returncode


class TestCleaningWorkflow:
    """Test the full data cleaning pipeline with checkpoint verification."""

    def test_full_cleaning_pipeline(self, tmp_path):
        """Load → detect_issues → handle_missing → normalize_strings → validate_clean"""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        input_file = TEST_DATA_DIR / "sample_missing.csv"

        if not input_file.exists():
            pytest.skip("Test data not generated yet. Run: python tests/generate_test_data.py")

        # Step 1: Detect issues
        ckpt_01 = workspace / "ckpt_01_issues.json"
        result, code = run_script(
            "magic-data-cleaning/scripts/detect_issues.py",
            str(input_file), str(ckpt_01)
        )
        assert result["success"], f"detect_issues failed: {result.get('error')}"
        assert result["total_issues"] > 0, "Should detect issues in sample_missing.csv"
        assert ckpt_01.exists(), "Checkpoint 01 not created"

        # Step 2: Handle missing values
        ckpt_02 = workspace / "ckpt_02_cleaned.csv"
        result, code = run_script(
            "magic-data-cleaning/scripts/handle_missing.py",
            str(input_file), str(ckpt_02),
            "--strategy", "auto"
        )
        assert result["success"], f"handle_missing failed: {result.get('error')}"
        assert result["rows_in"] > 0
        assert ckpt_02.exists(), "Checkpoint 02 not created"

        # Step 3: Normalize strings
        ckpt_03 = workspace / "ckpt_03_normalized.csv"
        result, code = run_script(
            "magic-data-cleaning/scripts/normalize_strings.py",
            str(ckpt_02), str(ckpt_03)
        )
        assert result["success"], f"normalize_strings failed: {result.get('error')}"
        assert ckpt_03.exists(), "Checkpoint 03 not created"

        # Step 4: Validate cleaning
        ckpt_04 = workspace / "ckpt_04_validation.json"
        result, code = run_script(
            "magic-data-cleaning/scripts/validate_clean.py",
            str(input_file), str(ckpt_03), str(ckpt_04)
        )
        assert result["success"], f"validate_clean failed: {result.get('error')}"
        assert ckpt_04.exists(), "Checkpoint 04 not created"

        # Verify all checkpoints exist
        checkpoints = list(workspace.glob("ckpt_*"))
        assert len(checkpoints) >= 4, f"Expected 4+ checkpoints, got {len(checkpoints)}"

    def test_cleaning_preserves_row_count_with_imputation(self, tmp_path):
        """Imputation should preserve row count (no dropping)."""
        input_file = TEST_DATA_DIR / "sample_missing.csv"
        if not input_file.exists():
            pytest.skip("Test data not generated yet")

        output_file = tmp_path / "cleaned.csv"
        result, _ = run_script(
            "magic-data-cleaning/scripts/handle_missing.py",
            str(input_file), str(output_file),
            "--strategy", "median"
        )
        assert result["success"]
        assert result["rows_in"] == result["rows_out"], \
            "Median imputation should preserve all rows"

    def test_issue_detection_then_targeted_cleaning(self, tmp_path):
        """detect_issues output should inform cleaning strategy choice."""
        input_file = TEST_DATA_DIR / "sample_missing.csv"
        if not input_file.exists():
            pytest.skip("Test data not generated yet")

        issues_output = tmp_path / "issues.json"
        result, _ = run_script(
            "magic-data-cleaning/scripts/detect_issues.py",
            str(input_file), str(issues_output)
        )
        assert result["success"]
        assert "missing_values" in result.get("issues", {}), \
            "Should detect missing values in sample_missing.csv"
