#!/usr/bin/env python3
"""
Phase 3 migration tests: verify that all 4 exploration scripts
use io_utils for loading data and are backward-compatible with CSV
while also supporting non-CSV formats (JSONL).
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
SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "skills" / "magic-data-exploration" / "scripts"

DETECT_PATTERNS_PY       = str(SCRIPTS_DIR / "detect_patterns.py")
SEGMENT_ANALYSIS_PY      = str(SCRIPTS_DIR / "segment_analysis.py")
RELATIONSHIP_EXPLORER_PY = str(SCRIPTS_DIR / "relationship_explorer.py")
PREPARE_EXPLORATION_PY   = str(SCRIPTS_DIR / "prepare_for_exploration.py")


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
# 1. detect_patterns.py
# ===========================================================================

class TestDetectPatterns:
    """Tests for detect_patterns.py io_utils migration."""

    def test_csv_backward_compat(self, tmp_path):
        """CSV input still works exactly as before."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_csv = str(tmp_path / "output.csv")
        df.to_csv(input_csv, index=False)

        result = run_script([
            DETECT_PATTERNS_PY, input_csv, output_csv,
        ])

        assert result["success"] is True, f"Expected success, got: {result}"
        assert result["rows_in"] == 20

    def test_jsonl_input(self, tmp_path):
        """JSONL input is accepted via --input-format."""
        df = make_sample_df()
        input_jsonl = str(tmp_path / "input.jsonl")
        output_csv = str(tmp_path / "output.csv")
        write_jsonl(df, input_jsonl)

        result = run_script([
            DETECT_PATTERNS_PY, input_jsonl, output_csv,
            "--input-format", "jsonl",
        ])

        assert result["success"] is True, f"Expected success, got: {result}"
        assert result["rows_in"] == 20


# ===========================================================================
# 2. segment_analysis.py
# ===========================================================================

class TestSegmentAnalysis:
    """Tests for segment_analysis.py io_utils migration."""

    def test_csv_backward_compat(self, tmp_path):
        """CSV input still works and segments are produced."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_csv = str(tmp_path / "output.csv")
        df.to_csv(input_csv, index=False)

        result = run_script([
            SEGMENT_ANALYSIS_PY, input_csv, output_csv,
            "--group_col", "category",
        ])

        assert result["success"] is True, f"Expected success, got: {result}"
        assert result["rows_in"] == 20
        assert "segments" in result

    def test_jsonl_input(self, tmp_path):
        """JSONL input is accepted via --input-format."""
        df = make_sample_df()
        input_jsonl = str(tmp_path / "input.jsonl")
        output_csv = str(tmp_path / "output.csv")
        write_jsonl(df, input_jsonl)

        result = run_script([
            SEGMENT_ANALYSIS_PY, input_jsonl, output_csv,
            "--group_col", "category",
            "--input-format", "jsonl",
        ])

        assert result["success"] is True, f"Expected success, got: {result}"
        assert result["rows_in"] == 20


# ===========================================================================
# 3. relationship_explorer.py
# ===========================================================================

class TestRelationshipExplorer:
    """Tests for relationship_explorer.py io_utils migration."""

    def test_csv_backward_compat(self, tmp_path):
        """CSV input still works and relationships are produced."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_csv = str(tmp_path / "output.csv")
        df.to_csv(input_csv, index=False)

        result = run_script([
            RELATIONSHIP_EXPLORER_PY, input_csv, output_csv,
            "--columns", "value,score",
        ])

        assert result["success"] is True, f"Expected success, got: {result}"
        assert result["rows_in"] == 20

    def test_jsonl_input(self, tmp_path):
        """JSONL input is accepted via --input-format."""
        df = make_sample_df()
        input_jsonl = str(tmp_path / "input.jsonl")
        output_csv = str(tmp_path / "output.csv")
        write_jsonl(df, input_jsonl)

        result = run_script([
            RELATIONSHIP_EXPLORER_PY, input_jsonl, output_csv,
            "--columns", "value,score",
            "--input-format", "jsonl",
        ])

        assert result["success"] is True, f"Expected success, got: {result}"
        assert result["rows_in"] == 20


# ===========================================================================
# 4. prepare_for_exploration.py
# ===========================================================================

class TestPrepareForExploration:
    """Tests for prepare_for_exploration.py io_utils migration."""

    def test_csv_backward_compat(self, tmp_path):
        """CSV input/output still works; text features are derived."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_csv = str(tmp_path / "output.csv")
        df.to_csv(input_csv, index=False)

        result = run_script([
            PREPARE_EXPLORATION_PY, input_csv, output_csv,
            "--columns", "label",
        ])

        assert result["success"] is True, f"Expected success, got: {result}"
        assert result["rows_in"] == 20
        # Derived features should include label_length, label_word_count, label_is_present
        assert result["columns_derived"] >= 1
        # Output file should exist
        assert Path(output_csv).exists()

    def test_jsonl_input_csv_output(self, tmp_path):
        """JSONL input with CSV output via --input-format."""
        df = make_sample_df()
        input_jsonl = str(tmp_path / "input.jsonl")
        output_csv = str(tmp_path / "output.csv")
        write_jsonl(df, input_jsonl)

        result = run_script([
            PREPARE_EXPLORATION_PY, input_jsonl, output_csv,
            "--columns", "label",
            "--input-format", "jsonl",
        ])

        assert result["success"] is True, f"Expected success, got: {result}"
        assert result["rows_in"] == 20
        assert Path(output_csv).exists()

    def test_csv_input_jsonl_output(self, tmp_path):
        """CSV input with JSONL output via --output-format."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_jsonl = str(tmp_path / "output.jsonl")
        df.to_csv(input_csv, index=False)

        result = run_script([
            PREPARE_EXPLORATION_PY, input_csv, output_jsonl,
            "--columns", "label",
            "--output-format", "jsonl",
        ])

        assert result["success"] is True, f"Expected success, got: {result}"
        # Verify JSONL output can be read back
        df_out = pd.read_json(output_jsonl, lines=True)
        assert len(df_out) == 20
        assert "label_length" in df_out.columns
