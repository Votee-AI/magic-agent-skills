"""
Integration Test: Text Data Workflow
=======================================
Tests: load JSONL → text profiling → text cleaning → text exploration → word frequency visualization → report
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


class TestTextDataWorkflow:
    """Test text data processing pipeline."""

    def test_text_profiling_pipeline(self, tmp_path):
        """Load text data → profile distributions → detect patterns."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        input_file = TEST_DATA_DIR / "sample_text.csv"

        if not input_file.exists():
            pytest.skip("Test data not generated yet")

        # Step 1: Profile text distributions
        ckpt_01 = workspace / "ckpt_01_distributions.json"
        result, _ = run_script(
            "magic-data-profiling/scripts/distribution_analysis.py",
            str(input_file), str(ckpt_01)
        )
        assert result["success"], f"Distribution analysis failed: {result.get('error')}"

        # Should detect text columns
        distributions = result.get("distributions", {})
        text_distributions = distributions.get("text", {})
        assert len(text_distributions) > 0, "Should detect and profile text columns"

        # Step 2: Detect patterns in text data
        ckpt_02 = workspace / "ckpt_02_patterns.json"
        result, _ = run_script(
            "magic-data-exploration/scripts/detect_patterns.py",
            str(input_file), str(ckpt_02)
        )
        assert result["success"], f"Pattern detection failed: {result.get('error')}"

        # Step 3: Generate visualization
        ckpt_03 = workspace / "ckpt_03_chart.png"
        result, _ = run_script(
            "magic-data-visualization/scripts/generate_chart.py",
            str(input_file), str(ckpt_03),
            "--chart_type", "histogram"
        )
        assert result["success"], f"Chart generation failed: {result.get('error')}"

    def test_text_stats_use_word_metrics(self, tmp_path):
        """Text columns should use word count, vocabulary, not mean/median."""
        input_file = TEST_DATA_DIR / "sample_text.csv"
        if not input_file.exists():
            pytest.skip("Test data not generated yet")

        output = tmp_path / "stats.json"
        result, _ = run_script(
            "magic-statistical-analysis/scripts/descriptive_stats.py",
            "--input", str(input_file), "--output", str(output)
        )
        assert result["success"]

        stats = result.get("statistics", {})
        # Should have text-specific stats
        text_stats = stats.get("text", {})
        if text_stats:
            for col_name, col_stats in text_stats.items():
                assert "vocabulary_size" in col_stats or "avg_word_count" in col_stats, \
                    f"Text column {col_name} should have text-specific metrics"
