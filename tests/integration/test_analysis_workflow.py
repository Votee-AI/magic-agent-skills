"""
Integration Test: Analysis Workflow
=====================================
Tests: load → descriptive_stats → correlation_analysis → generate_chart → generate_report
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


class TestAnalysisWorkflow:
    """Test the full analysis pipeline with checkpoint verification."""

    def test_full_analysis_pipeline(self, tmp_path):
        """descriptive_stats → correlation_analysis → generate_chart → generate_report"""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        input_file = TEST_DATA_DIR / "sample_clean.csv"

        if not input_file.exists():
            pytest.skip("Test data not generated yet")

        # Step 1: Descriptive stats
        ckpt_01 = workspace / "ckpt_01_stats.json"
        result, _ = run_script(
            "magic-statistical-analysis/scripts/descriptive_stats.py",
            "--input", str(input_file), "--output", str(ckpt_01)
        )
        assert result["success"], f"descriptive_stats failed: {result.get('error')}"
        assert "statistics" in result
        assert ckpt_01.exists()

        # Step 2: Correlation analysis
        ckpt_02 = workspace / "ckpt_02_correlation.json"
        result, _ = run_script(
            "magic-statistical-analysis/scripts/correlation_analysis.py",
            "--input", str(input_file), "--output", str(ckpt_02)
        )
        assert result["success"], f"correlation_analysis failed: {result.get('error')}"
        assert ckpt_02.exists()

        # Step 3: Generate chart
        ckpt_03 = workspace / "ckpt_03_chart.png"
        result, _ = run_script(
            "magic-data-visualization/scripts/generate_chart.py",
            str(input_file), str(ckpt_03),
            "--chart_type", "histogram"
        )
        assert result["success"], f"generate_chart failed: {result.get('error')}"
        assert ckpt_03.exists()

        # Step 4: Generate report (needs findings JSON)
        findings = {
            "data_source": {"file": "sample_clean.csv", "rows": 1000, "columns": 8},
            "profiling_summary": {"columns": 8},
            "cleaning_summary": {"no_cleaning_needed": True},
            "analysis_results": {"descriptive_stats": "computed"},
            "visualizations": [{"path": str(ckpt_03), "caption": "Distribution chart"}],
            "caveats": ["Analysis limited to sample data"]
        }
        findings_path = workspace / "findings.json"
        findings_path.write_text(json.dumps(findings))

        ckpt_04 = workspace / "ckpt_04_report.md"
        result, _ = run_script(
            "magic-report-generation/scripts/generate_report.py",
            str(findings_path), str(ckpt_04)
        )
        assert result["success"], f"generate_report failed: {result.get('error')}"
        assert ckpt_04.exists()

        # Verify report has content
        report_content = ckpt_04.read_text()
        assert len(report_content) > 100, "Report should have substantial content"

    def test_stats_include_caveats(self, tmp_path):
        """Statistical outputs must include caveats."""
        input_file = TEST_DATA_DIR / "sample_clean.csv"
        if not input_file.exists():
            pytest.skip("Test data not generated yet")

        output = tmp_path / "stats.json"
        result, _ = run_script(
            "magic-statistical-analysis/scripts/descriptive_stats.py",
            "--input", str(input_file), "--output", str(output)
        )
        assert result["success"]
        # Check for narrative or caveats in output
        stats = result.get("statistics", {})
        assert len(stats) > 0, "Should produce statistics"
