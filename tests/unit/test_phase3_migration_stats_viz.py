#!/usr/bin/env python3
"""
Phase 3 migration tests: verify that the 3 visualization scripts and
3 statistical-analysis scripts use io_utils for loading data and are
backward-compatible with CSV while also supporting non-CSV formats (JSONL).
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
VIZ_DIR   = Path(__file__).resolve().parents[2] / "skills" / "magic-data-visualization" / "scripts"
STATS_DIR = Path(__file__).resolve().parents[2] / "skills" / "magic-statistical-analysis" / "scripts"

CHART_SELECTOR_PY     = str(VIZ_DIR  / "chart_selector.py")
GENERATE_CHART_PY     = str(VIZ_DIR  / "generate_chart.py")
VALIDATE_CHART_PY     = str(VIZ_DIR  / "validate_chart.py")

DESCRIPTIVE_STATS_PY  = str(STATS_DIR / "descriptive_stats.py")
HYPOTHESIS_TEST_PY    = str(STATS_DIR / "hypothesis_test.py")
CORRELATION_PY        = str(STATS_DIR / "correlation_analysis.py")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_sample_df() -> pd.DataFrame:
    """Return a simple 20-row DataFrame with numeric + text columns for testing."""
    return pd.DataFrame({
        "id":       list(range(1, 21)),
        "category": (["A", "B"] * 10),
        "value":    [float(i * 5) for i in range(1, 21)],
        "score":    [float(i * 2 + 1) for i in range(1, 21)],
        "label":    [f"item_{i}" for i in range(1, 21)],
    })


def write_jsonl(df: pd.DataFrame, path: str) -> None:
    """Write DataFrame as JSON Lines."""
    df.to_json(path, orient="records", lines=True, force_ascii=False)


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
# Visualization: chart_selector.py
# ===========================================================================

class TestChartSelector:
    """Tests for chart_selector.py io_utils migration."""

    def test_csv_backward_compat(self, tmp_path):
        """CSV input still produces chart recommendations."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_json = str(tmp_path / "output.json")
        df.to_csv(input_csv, index=False)

        result = run_script([
            CHART_SELECTOR_PY, input_csv, output_json,
        ])

        assert result["success"] is True, f"Expected success, got: {result}"
        assert result["rows_in"] == 20
        assert "recommendations" in result

    def test_jsonl_input(self, tmp_path):
        """JSONL input is accepted via --input-format."""
        df = make_sample_df()
        input_jsonl = str(tmp_path / "input.jsonl")
        output_json = str(tmp_path / "output.json")
        write_jsonl(df, input_jsonl)

        result = run_script([
            CHART_SELECTOR_PY, input_jsonl, output_json,
            "--input-format", "jsonl",
        ])

        assert result["success"] is True, f"Expected success, got: {result}"
        assert result["rows_in"] == 20


# ===========================================================================
# Visualization: generate_chart.py
# ===========================================================================

class TestGenerateChart:
    """Tests for generate_chart.py io_utils migration."""

    def test_csv_backward_compat(self, tmp_path):
        """CSV input still generates a chart PNG."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_png = str(tmp_path / "chart.png")
        df.to_csv(input_csv, index=False)

        result = run_script([
            GENERATE_CHART_PY, input_csv, output_png,
            "--chart_type", "histogram",
            "--x_col", "value",
        ])

        assert result["success"] is True, f"Expected success, got: {result}"
        assert result["rows_in"] == 20

    def test_jsonl_input(self, tmp_path):
        """JSONL input is accepted via --input-format."""
        df = make_sample_df()
        input_jsonl = str(tmp_path / "input.jsonl")
        output_png = str(tmp_path / "chart.png")
        write_jsonl(df, input_jsonl)

        result = run_script([
            GENERATE_CHART_PY, input_jsonl, output_png,
            "--chart_type", "histogram",
            "--x_col", "value",
            "--input-format", "jsonl",
        ])

        assert result["success"] is True, f"Expected success, got: {result}"
        assert result["rows_in"] == 20


# ===========================================================================
# Visualization: validate_chart.py
# ===========================================================================

class TestValidateChart:
    """Tests for validate_chart.py io_utils migration."""

    def _make_metadata(self, path: str) -> None:
        """Write a minimal valid chart metadata JSON."""
        metadata = {
            "chart_type": "scatter",
            "x_col": "value",
            "y_col": "score",
        }
        with open(path, "w") as f:
            json.dump(metadata, f)

    def test_csv_backward_compat(self, tmp_path):
        """CSV source data still validates correctly."""
        df = make_sample_df()
        source_csv = str(tmp_path / "source.csv")
        metadata_json = str(tmp_path / "metadata.json")
        output_json = str(tmp_path / "report.json")
        df.to_csv(source_csv, index=False)
        self._make_metadata(metadata_json)

        result = run_script([
            VALIDATE_CHART_PY, source_csv, metadata_json, output_json,
        ])

        assert result["success"] is True, f"Expected success, got: {result}"
        assert result["source_rows"] == 20

    def test_jsonl_input(self, tmp_path):
        """JSONL source data is accepted via --input-format."""
        df = make_sample_df()
        source_jsonl = str(tmp_path / "source.jsonl")
        metadata_json = str(tmp_path / "metadata.json")
        output_json = str(tmp_path / "report.json")
        write_jsonl(df, source_jsonl)
        self._make_metadata(metadata_json)

        result = run_script([
            VALIDATE_CHART_PY, source_jsonl, metadata_json, output_json,
            "--input-format", "jsonl",
        ])

        assert result["success"] is True, f"Expected success, got: {result}"
        assert result["source_rows"] == 20


# ===========================================================================
# Statistical Analysis: descriptive_stats.py
# ===========================================================================

class TestDescriptiveStats:
    """Tests for descriptive_stats.py io_utils migration."""

    def test_csv_backward_compat(self, tmp_path):
        """CSV input still produces statistics."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_json = str(tmp_path / "stats.json")
        df.to_csv(input_csv, index=False)

        result = run_script([
            DESCRIPTIVE_STATS_PY,
            "--input", input_csv,
            "--output", output_json,
        ])

        assert result["success"] is True, f"Expected success, got: {result}"
        assert result["rows_in"] == 20
        assert "statistics" in result

    def test_jsonl_input(self, tmp_path):
        """JSONL input is accepted via --input-format."""
        df = make_sample_df()
        input_jsonl = str(tmp_path / "input.jsonl")
        output_json = str(tmp_path / "stats.json")
        write_jsonl(df, input_jsonl)

        result = run_script([
            DESCRIPTIVE_STATS_PY,
            "--input", input_jsonl,
            "--output", output_json,
            "--input-format", "jsonl",
        ])

        assert result["success"] is True, f"Expected success, got: {result}"
        assert result["rows_in"] == 20


# ===========================================================================
# Statistical Analysis: hypothesis_test.py
# ===========================================================================

class TestHypothesisTest:
    """Tests for hypothesis_test.py io_utils migration."""

    def test_csv_backward_compat(self, tmp_path):
        """CSV input still produces hypothesis test results."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_json = str(tmp_path / "test.json")
        df.to_csv(input_csv, index=False)

        result = run_script([
            HYPOTHESIS_TEST_PY,
            "--input", input_csv,
            "--output", output_json,
            "--group_col", "category",
            "--value_col", "value",
        ])

        assert result["success"] is True, f"Expected success, got: {result}"
        assert result["rows_in"] == 20
        assert "test_used" in result

    def test_jsonl_input(self, tmp_path):
        """JSONL input is accepted via --input-format."""
        df = make_sample_df()
        input_jsonl = str(tmp_path / "input.jsonl")
        output_json = str(tmp_path / "test.json")
        write_jsonl(df, input_jsonl)

        result = run_script([
            HYPOTHESIS_TEST_PY,
            "--input", input_jsonl,
            "--output", output_json,
            "--group_col", "category",
            "--value_col", "value",
            "--input-format", "jsonl",
        ])

        assert result["success"] is True, f"Expected success, got: {result}"
        assert result["rows_in"] == 20


# ===========================================================================
# Statistical Analysis: correlation_analysis.py
# ===========================================================================

class TestCorrelationAnalysis:
    """Tests for correlation_analysis.py io_utils migration."""

    def test_csv_backward_compat(self, tmp_path):
        """CSV input still produces correlation analysis."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_json = str(tmp_path / "corr.json")
        df.to_csv(input_csv, index=False)

        result = run_script([
            CORRELATION_PY,
            "--input", input_csv,
            "--output", output_json,
            "--columns", "value,score",
        ])

        assert result["success"] is True, f"Expected success, got: {result}"
        assert result["rows_in"] == 20
        assert "correlations" in result

    def test_jsonl_input(self, tmp_path):
        """JSONL input is accepted via --input-format."""
        df = make_sample_df()
        input_jsonl = str(tmp_path / "input.jsonl")
        output_json = str(tmp_path / "corr.json")
        write_jsonl(df, input_jsonl)

        result = run_script([
            CORRELATION_PY,
            "--input", input_jsonl,
            "--output", output_json,
            "--columns", "value,score",
            "--input-format", "jsonl",
        ])

        assert result["success"] is True, f"Expected success, got: {result}"
        assert result["rows_in"] == 20
