#!/usr/bin/env python3
"""
Phase 3 migration tests: verify that all 5 profiling scripts
use io_utils for loading data and are backward-compatible with CSV
while also supporting non-CSV formats (JSONL).

Scripts under test (all in skills/magic-data-profiling/scripts/):
  1. quality_score.py
  2. distribution_analysis.py
  3. outlier_detection.py
  4. correlation_matrix.py
  5. detect_all_issues.py
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "skills" / "magic-data-profiling" / "scripts"

QUALITY_SCORE_PY       = str(SCRIPTS_DIR / "quality_score.py")
DISTRIBUTION_PY        = str(SCRIPTS_DIR / "distribution_analysis.py")
OUTLIER_DETECTION_PY   = str(SCRIPTS_DIR / "outlier_detection.py")
CORRELATION_MATRIX_PY  = str(SCRIPTS_DIR / "correlation_matrix.py")
DETECT_ALL_ISSUES_PY   = str(SCRIPTS_DIR / "detect_all_issues.py")


# ---------------------------------------------------------------------------
# Sample data helpers
# ---------------------------------------------------------------------------

def make_sample_df() -> pd.DataFrame:
    """
    Return a 30-row DataFrame with a mix of numeric and text columns.
    Wide enough for correlation analysis (needs >= 2 numeric cols).
    """
    import random
    random.seed(42)
    n = 30
    return pd.DataFrame({
        "id":       list(range(1, n + 1)),
        "score":    [round(50 + random.gauss(0, 10), 2) for _ in range(n)],
        "value":    [round(100 + i * 2.5 + random.gauss(0, 5), 2) for i in range(n)],
        "category": [["alpha", "beta", "gamma"][i % 3] for i in range(n)],
    })


def run_script(args: list) -> dict:
    """Run a script with the given argument list and return parsed JSON output."""
    result = subprocess.run(
        [sys.executable] + args,
        capture_output=True,
        text=True,
    )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        pytest.fail(
            f"Script did not produce valid JSON.\n"
            f"STDOUT: {result.stdout!r}\n"
            f"STDERR: {result.stderr!r}\n"
            f"Return code: {result.returncode}"
        )


# ===========================================================================
# 1. quality_score.py
# ===========================================================================

class TestQualityScore:
    """Tests for quality_score.py io_utils migration."""

    def test_csv_backward_compat(self, tmp_path):
        """CSV input produces a valid JSON quality report."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_json = str(tmp_path / "output.json")
        df.to_csv(input_csv, index=False)

        result = run_script([QUALITY_SCORE_PY, input_csv, output_json])

        assert result["success"] is True, f"Expected success but got: {result}"
        assert "overall_score" in result
        assert 0 <= result["overall_score"] <= 100
        assert os.path.exists(output_json)

    def test_input_format_flag_csv(self, tmp_path):
        """--input-format csv flag is accepted and works correctly."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_json = str(tmp_path / "output.json")
        df.to_csv(input_csv, index=False)

        result = run_script([
            QUALITY_SCORE_PY, input_csv, output_json,
            "--input-format", "csv",
        ])

        assert result["success"] is True, f"Expected success but got: {result}"
        assert "overall_score" in result

    def test_jsonl_input(self, tmp_path):
        """JSONL input is loaded via io_utils and produces a valid JSON report."""
        df = make_sample_df()
        input_jsonl = str(tmp_path / "input.jsonl")
        output_json = str(tmp_path / "output.json")
        df.to_json(input_jsonl, orient="records", lines=True)

        result = run_script([
            QUALITY_SCORE_PY, input_jsonl, output_json,
            "--input-format", "jsonl",
        ])

        assert result["success"] is True, f"Expected success but got: {result}"
        assert "overall_score" in result
        assert 0 <= result["overall_score"] <= 100
        # Output is always JSON regardless of input format
        assert os.path.exists(output_json)
        with open(output_json) as f:
            saved = json.load(f)
        assert saved["success"] is True

    def test_jsonl_auto_detect(self, tmp_path):
        """JSONL input is auto-detected from extension when no --input-format flag given."""
        df = make_sample_df()
        input_jsonl = str(tmp_path / "input.jsonl")
        output_json = str(tmp_path / "output.json")
        df.to_json(input_jsonl, orient="records", lines=True)

        result = run_script([QUALITY_SCORE_PY, input_jsonl, output_json])

        assert result["success"] is True, f"Expected success but got: {result}"
        assert "overall_score" in result

    def test_output_report_structure(self, tmp_path):
        """Output JSON contains expected dimension keys."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_json = str(tmp_path / "output.json")
        df.to_csv(input_csv, index=False)

        result = run_script([QUALITY_SCORE_PY, input_csv, output_json])

        assert result["success"] is True
        assert "dimensions" in result
        dims = result["dimensions"]
        for key in ("completeness", "consistency", "uniqueness", "validity"):
            assert key in dims, f"Missing dimension: {key}"


# ===========================================================================
# 2. distribution_analysis.py
# ===========================================================================

class TestDistributionAnalysis:
    """Tests for distribution_analysis.py io_utils migration."""

    def test_csv_backward_compat(self, tmp_path):
        """CSV input produces a valid JSON distribution report."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_json = str(tmp_path / "output.json")
        df.to_csv(input_csv, index=False)

        result = run_script([DISTRIBUTION_PY, input_csv, output_json])

        assert result["success"] is True, f"Expected success but got: {result}"
        assert "distributions" in result
        assert os.path.exists(output_json)

    def test_input_format_flag_csv(self, tmp_path):
        """--input-format csv flag is accepted."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_json = str(tmp_path / "output.json")
        df.to_csv(input_csv, index=False)

        result = run_script([
            DISTRIBUTION_PY, input_csv, output_json,
            "--input-format", "csv",
        ])

        assert result["success"] is True, f"Expected success but got: {result}"

    def test_jsonl_input(self, tmp_path):
        """JSONL input is loaded via io_utils and produces a valid JSON report."""
        df = make_sample_df()
        input_jsonl = str(tmp_path / "input.jsonl")
        output_json = str(tmp_path / "output.json")
        df.to_json(input_jsonl, orient="records", lines=True)

        result = run_script([
            DISTRIBUTION_PY, input_jsonl, output_json,
            "--input-format", "jsonl",
        ])

        assert result["success"] is True, f"Expected success but got: {result}"
        assert "distributions" in result
        assert os.path.exists(output_json)
        with open(output_json) as f:
            saved = json.load(f)
        assert saved["success"] is True

    def test_jsonl_auto_detect(self, tmp_path):
        """JSONL input is auto-detected from extension."""
        df = make_sample_df()
        input_jsonl = str(tmp_path / "input.jsonl")
        output_json = str(tmp_path / "output.json")
        df.to_json(input_jsonl, orient="records", lines=True)

        result = run_script([DISTRIBUTION_PY, input_jsonl, output_json])

        assert result["success"] is True, f"Expected success but got: {result}"

    def test_output_report_has_numeric_and_text(self, tmp_path):
        """Distribution report separates numeric and text columns."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_json = str(tmp_path / "output.json")
        df.to_csv(input_csv, index=False)

        result = run_script([DISTRIBUTION_PY, input_csv, output_json])

        assert result["success"] is True
        dists = result["distributions"]
        assert "numeric" in dists
        assert "text" in dists
        # score and value are numeric
        assert "score" in dists["numeric"] or "value" in dists["numeric"]
        # category is text
        assert "category" in dists["text"]


# ===========================================================================
# 3. outlier_detection.py
# ===========================================================================

class TestOutlierDetection:
    """Tests for outlier_detection.py io_utils migration."""

    def test_csv_backward_compat(self, tmp_path):
        """CSV input produces a valid JSON outlier report."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_json = str(tmp_path / "output.json")
        df.to_csv(input_csv, index=False)

        result = run_script([OUTLIER_DETECTION_PY, input_csv, output_json])

        assert result["success"] is True, f"Expected success but got: {result}"
        assert "outliers" in result
        assert os.path.exists(output_json)

    def test_input_format_flag_csv(self, tmp_path):
        """--input-format csv flag is accepted."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_json = str(tmp_path / "output.json")
        df.to_csv(input_csv, index=False)

        result = run_script([
            OUTLIER_DETECTION_PY, input_csv, output_json,
            "--input-format", "csv",
        ])

        assert result["success"] is True, f"Expected success but got: {result}"

    def test_jsonl_input(self, tmp_path):
        """JSONL input is loaded via io_utils and produces a valid JSON outlier report."""
        df = make_sample_df()
        input_jsonl = str(tmp_path / "input.jsonl")
        output_json = str(tmp_path / "output.json")
        df.to_json(input_jsonl, orient="records", lines=True)

        result = run_script([
            OUTLIER_DETECTION_PY, input_jsonl, output_json,
            "--input-format", "jsonl",
        ])

        assert result["success"] is True, f"Expected success but got: {result}"
        assert "outliers" in result
        assert os.path.exists(output_json)
        with open(output_json) as f:
            saved = json.load(f)
        assert saved["success"] is True

    def test_jsonl_auto_detect(self, tmp_path):
        """JSONL input is auto-detected from extension."""
        df = make_sample_df()
        input_jsonl = str(tmp_path / "input.jsonl")
        output_json = str(tmp_path / "output.json")
        df.to_json(input_jsonl, orient="records", lines=True)

        result = run_script([OUTLIER_DETECTION_PY, input_jsonl, output_json])

        assert result["success"] is True, f"Expected success but got: {result}"

    def test_outlier_report_structure(self, tmp_path):
        """Outlier report contains expected top-level keys."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_json = str(tmp_path / "output.json")
        df.to_csv(input_csv, index=False)

        result = run_script([OUTLIER_DETECTION_PY, input_csv, output_json])

        assert result["success"] is True
        assert "total_outlier_rows" in result
        assert "total_outlier_pct" in result
        assert "method" in result


# ===========================================================================
# 4. correlation_matrix.py
# ===========================================================================

class TestCorrelationMatrix:
    """Tests for correlation_matrix.py io_utils migration."""

    def test_csv_backward_compat(self, tmp_path):
        """CSV input produces a valid JSON correlation report and matrix CSV."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_json = str(tmp_path / "output.json")
        df.to_csv(input_csv, index=False)

        result = run_script([CORRELATION_MATRIX_PY, input_csv, output_json])

        assert result["success"] is True, f"Expected success but got: {result}"
        assert "significant_pairs" in result
        assert os.path.exists(output_json)
        # Secondary CSV matrix output should also exist
        matrix_csv = str(tmp_path / "output_matrix.csv")
        assert os.path.exists(matrix_csv), "Correlation matrix CSV was not created"

    def test_input_format_flag_csv(self, tmp_path):
        """--input-format csv flag is accepted."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_json = str(tmp_path / "output.json")
        df.to_csv(input_csv, index=False)

        result = run_script([
            CORRELATION_MATRIX_PY, input_csv, output_json,
            "--input-format", "csv",
        ])

        assert result["success"] is True, f"Expected success but got: {result}"

    def test_jsonl_input(self, tmp_path):
        """JSONL input is loaded via io_utils and produces a valid JSON correlation report."""
        df = make_sample_df()
        input_jsonl = str(tmp_path / "input.jsonl")
        output_json = str(tmp_path / "output.json")
        df.to_json(input_jsonl, orient="records", lines=True)

        result = run_script([
            CORRELATION_MATRIX_PY, input_jsonl, output_json,
            "--input-format", "jsonl",
        ])

        assert result["success"] is True, f"Expected success but got: {result}"
        assert "significant_pairs" in result
        assert os.path.exists(output_json)
        with open(output_json) as f:
            saved = json.load(f)
        assert saved["success"] is True

    def test_jsonl_auto_detect(self, tmp_path):
        """JSONL input is auto-detected from extension."""
        df = make_sample_df()
        input_jsonl = str(tmp_path / "input.jsonl")
        output_json = str(tmp_path / "output.json")
        df.to_json(input_jsonl, orient="records", lines=True)

        result = run_script([CORRELATION_MATRIX_PY, input_jsonl, output_json])

        assert result["success"] is True, f"Expected success but got: {result}"

    def test_matrix_csv_saved_via_save_dataframe(self, tmp_path):
        """Secondary matrix CSV is created (via save_dataframe) and is readable."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_json = str(tmp_path / "output.json")
        df.to_csv(input_csv, index=False)

        result = run_script([CORRELATION_MATRIX_PY, input_csv, output_json])

        assert result["success"] is True
        matrix_csv_path = result.get("matrix_csv_path")
        assert matrix_csv_path is not None
        assert os.path.exists(matrix_csv_path)
        # Must be loadable as a DataFrame (index written with index=True via save_dataframe)
        matrix_df = pd.read_csv(matrix_csv_path, index_col=0)
        # Should be a square matrix: rows == columns (both equal number of numeric columns)
        assert matrix_df.shape[0] == matrix_df.shape[1], (
            f"Correlation matrix is not square: shape={matrix_df.shape}"
        )


# ===========================================================================
# 5. detect_all_issues.py
# ===========================================================================

class TestDetectAllIssues:
    """Tests for detect_all_issues.py io_utils migration (special kwargs variant)."""

    def test_csv_backward_compat(self, tmp_path):
        """CSV input produces a valid merged JSON report."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_json = str(tmp_path / "output.json")
        df.to_csv(input_csv, index=False)

        result = run_script([DETECT_ALL_ISSUES_PY, input_csv, output_json])

        assert result["success"] is True, f"Expected success but got: {result}"
        assert "summary" in result
        assert "quality" in result
        assert "outliers" in result
        assert os.path.exists(output_json)

    def test_input_format_flag_csv(self, tmp_path):
        """--input-format csv flag is accepted and works correctly."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_json = str(tmp_path / "output.json")
        df.to_csv(input_csv, index=False)

        result = run_script([
            DETECT_ALL_ISSUES_PY, input_csv, output_json,
            "--input-format", "csv",
        ])

        assert result["success"] is True, f"Expected success but got: {result}"

    def test_jsonl_input(self, tmp_path):
        """JSONL input is loaded via io_utils with dtype=str, keep_default_na=False kwargs."""
        df = make_sample_df()
        input_jsonl = str(tmp_path / "input.jsonl")
        output_json = str(tmp_path / "output.json")
        df.to_json(input_jsonl, orient="records", lines=True)

        result = run_script([
            DETECT_ALL_ISSUES_PY, input_jsonl, output_json,
            "--input-format", "jsonl",
        ])

        assert result["success"] is True, f"Expected success but got: {result}"
        assert "summary" in result
        assert os.path.exists(output_json)
        with open(output_json) as f:
            saved = json.load(f)
        assert saved["success"] is True

    def test_jsonl_auto_detect(self, tmp_path):
        """JSONL input is auto-detected from extension."""
        df = make_sample_df()
        input_jsonl = str(tmp_path / "input.jsonl")
        output_json = str(tmp_path / "output.json")
        df.to_json(input_jsonl, orient="records", lines=True)

        result = run_script([DETECT_ALL_ISSUES_PY, input_jsonl, output_json])

        assert result["success"] is True, f"Expected success but got: {result}"

    def test_sentinels_detected_in_csv(self, tmp_path):
        """Sentinel detection still works after migration (uses io_utils with kwargs)."""
        import pandas as pd
        # Include some sentinel values
        df = make_sample_df().copy()
        df.loc[0, "category"] = "N/A"
        df.loc[1, "category"] = "TBD"
        input_csv = str(tmp_path / "input_sentinels.csv")
        output_json = str(tmp_path / "output.json")
        df.to_csv(input_csv, index=False)

        result = run_script([DETECT_ALL_ISSUES_PY, input_csv, output_json])

        assert result["success"] is True, f"Expected success but got: {result}"
        sentinels = result.get("sentinels", {})
        assert sentinels.get("success") is True
        # At least some sentinels should have been found
        assert sentinels.get("total_sentinel_cells", 0) >= 2

    def test_merged_report_structure(self, tmp_path):
        """Output contains all expected top-level section keys."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_json = str(tmp_path / "output.json")
        df.to_csv(input_csv, index=False)

        result = run_script([DETECT_ALL_ISSUES_PY, input_csv, output_json])

        assert result["success"] is True
        for key in ("summary", "sentinels", "quality", "distributions", "outliers", "correlations"):
            assert key in result, f"Missing top-level key in report: {key}"
        summary = result["summary"]
        assert "quality_score" in summary
        assert "total_outliers" in summary
