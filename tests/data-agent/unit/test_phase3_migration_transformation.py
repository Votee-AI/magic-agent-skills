#!/usr/bin/env python3
"""
Phase 3 migration tests: verify that all 5 transformation scripts
use io_utils for loading/saving data and are backward-compatible with CSV
while also supporting non-CSV formats.
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
SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "skills" / "magic-data-transformation" / "scripts"

AGGREGATE_PY       = str(SCRIPTS_DIR / "aggregate.py")
VALIDATE_PY        = str(SCRIPTS_DIR / "validate_transform.py")
RESHAPE_PY         = str(SCRIPTS_DIR / "reshape.py")
DERIVE_COLUMNS_PY  = str(SCRIPTS_DIR / "derive_columns.py")
MERGE_DATASETS_PY  = str(SCRIPTS_DIR / "merge_datasets.py")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_sample_df() -> pd.DataFrame:
    """Return a simple 10-row, 3-column DataFrame for testing."""
    return pd.DataFrame({
        "id":     list(range(1, 11)),
        "category": ["A", "B", "A", "B", "A", "B", "A", "B", "A", "B"],
        "value":  [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0],
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
# 1. aggregate.py
# ===========================================================================

class TestAggregate:
    """Tests for aggregate.py io_utils migration."""

    def test_csv_backward_compat(self, tmp_path):
        """CSV input/output still works exactly as before."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_csv = str(tmp_path / "output.csv")
        df.to_csv(input_csv, index=False)

        result = run_script([
            AGGREGATE_PY, input_csv, output_csv,
            "--group-cols", "category",
            "--agg-cols", "value",
            "--functions", "mean,sum",
        ])

        assert result["success"] is True, f"Expected success but got: {result}"
        assert os.path.exists(output_csv), "Output CSV was not created"
        out_df = pd.read_csv(output_csv)
        assert len(out_df) == 2  # two categories: A and B
        assert "category" in out_df.columns

    def test_jsonl_input_output(self, tmp_path):
        """JSONL input and output work via io_utils."""
        df = make_sample_df()
        input_jsonl = str(tmp_path / "input.jsonl")
        output_jsonl = str(tmp_path / "output.jsonl")
        df.to_json(input_jsonl, orient="records", lines=True)

        result = run_script([
            AGGREGATE_PY, input_jsonl, output_jsonl,
            "--group-cols", "category",
            "--agg-cols", "value",
            "--functions", "mean",
        ])

        assert result["success"] is True, f"Expected success but got: {result}"
        assert os.path.exists(output_jsonl), "Output JSONL was not created"
        out_df = pd.read_json(output_jsonl, lines=True)
        assert len(out_df) == 2

    def test_explicit_input_format_flag(self, tmp_path):
        """--input-format csv flag is accepted without error."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_csv = str(tmp_path / "output.csv")
        df.to_csv(input_csv, index=False)

        result = run_script([
            AGGREGATE_PY, input_csv, output_csv,
            "--group-cols", "category",
            "--input-format", "csv",
            "--output-format", "csv",
        ])

        assert result["success"] is True, f"Expected success but got: {result}"

    def test_parquet_input_output(self, tmp_path):
        """Parquet input and output work via io_utils."""
        df = make_sample_df()
        input_pq = str(tmp_path / "input.parquet")
        output_pq = str(tmp_path / "output.parquet")
        df.to_parquet(input_pq, index=False)

        result = run_script([
            AGGREGATE_PY, input_pq, output_pq,
            "--group-cols", "category",
            "--agg-cols", "value",
            "--functions", "sum",
        ])

        assert result["success"] is True, f"Expected success but got: {result}"
        assert os.path.exists(output_pq), "Output Parquet was not created"
        out_df = pd.read_parquet(output_pq)
        assert len(out_df) == 2


# ===========================================================================
# 2. validate_transform.py
# ===========================================================================

class TestValidateTransform:
    """Tests for validate_transform.py io_utils migration."""

    def test_csv_backward_compat(self, tmp_path):
        """CSV input still works; output is a JSON report."""
        df = make_sample_df()
        input_csv = str(tmp_path / "original.csv")
        transformed_csv = str(tmp_path / "transformed.csv")
        report_path = str(tmp_path / "report.csv")
        df.to_csv(input_csv, index=False)
        df.to_csv(transformed_csv, index=False)

        result = run_script([
            VALIDATE_PY, input_csv, transformed_csv, report_path,
        ])

        assert result["success"] is True, f"Expected success but got: {result}"
        assert result["valid"] is True
        assert os.path.exists(report_path), "Validation report was not created"

    def test_jsonl_input(self, tmp_path):
        """JSONL input files are loaded via io_utils."""
        df = make_sample_df()
        input_jsonl = str(tmp_path / "original.jsonl")
        transformed_jsonl = str(tmp_path / "transformed.jsonl")
        report_path = str(tmp_path / "report.csv")
        df.to_json(input_jsonl, orient="records", lines=True)
        df.to_json(transformed_jsonl, orient="records", lines=True)

        result = run_script([
            VALIDATE_PY, input_jsonl, transformed_jsonl, report_path,
            "--input-format", "jsonl",
        ])

        assert result["success"] is True, f"Expected success but got: {result}"
        assert result["valid"] is True

    def test_parquet_input(self, tmp_path):
        """Parquet input files are loaded via io_utils."""
        df = make_sample_df()
        input_pq = str(tmp_path / "original.parquet")
        transformed_pq = str(tmp_path / "transformed.parquet")
        report_path = str(tmp_path / "report.csv")
        df.to_parquet(input_pq, index=False)
        df.to_parquet(transformed_pq, index=False)

        result = run_script([
            VALIDATE_PY, input_pq, transformed_pq, report_path,
            "--input-format", "parquet",
        ])

        assert result["success"] is True, f"Expected success but got: {result}"
        assert result["valid"] is True

    def test_input_format_flag_accepted(self, tmp_path):
        """--input-format flag is accepted by the argument parser."""
        df = make_sample_df()
        input_csv = str(tmp_path / "original.csv")
        transformed_csv = str(tmp_path / "transformed.csv")
        report_path = str(tmp_path / "report.csv")
        df.to_csv(input_csv, index=False)
        df.to_csv(transformed_csv, index=False)

        result = run_script([
            VALIDATE_PY, input_csv, transformed_csv, report_path,
            "--input-format", "csv",
        ])

        assert result["success"] is True, f"Expected success but got: {result}"


# ===========================================================================
# 3. reshape.py
# ===========================================================================

class TestReshape:
    """Tests for reshape.py io_utils migration."""

    def _make_melt_df(self) -> pd.DataFrame:
        """Return a DataFrame suitable for melt (id + multiple value columns)."""
        return pd.DataFrame({
            "id":  list(range(1, 11)),
            "val_a": list(range(10, 110, 10)),
            "val_b": list(range(5, 55, 5)),
        })

    def test_csv_backward_compat_melt(self, tmp_path):
        """CSV input/output still works for melt operation."""
        df = self._make_melt_df()
        input_csv = str(tmp_path / "input.csv")
        output_csv = str(tmp_path / "output.csv")
        df.to_csv(input_csv, index=False)

        result = run_script([
            RESHAPE_PY, input_csv, output_csv,
            "--operation", "melt",
            "--id-vars", "id",
        ])

        assert result["success"] is True, f"Expected success but got: {result}"
        assert os.path.exists(output_csv)
        out_df = pd.read_csv(output_csv)
        # melt of 10 rows x 2 value cols = 20 rows
        assert len(out_df) == 20

    def test_jsonl_input_output_melt(self, tmp_path):
        """JSONL input/output via io_utils for melt."""
        df = self._make_melt_df()
        input_jsonl = str(tmp_path / "input.jsonl")
        output_jsonl = str(tmp_path / "output.jsonl")
        df.to_json(input_jsonl, orient="records", lines=True)

        result = run_script([
            RESHAPE_PY, input_jsonl, output_jsonl,
            "--operation", "melt",
            "--id-vars", "id",
        ])

        assert result["success"] is True, f"Expected success but got: {result}"
        assert os.path.exists(output_jsonl)
        out_df = pd.read_json(output_jsonl, lines=True)
        assert len(out_df) == 20

    def test_explicit_output_format_flag(self, tmp_path):
        """--output-format flag is accepted."""
        df = self._make_melt_df()
        input_csv = str(tmp_path / "input.csv")
        output_csv = str(tmp_path / "output.csv")
        df.to_csv(input_csv, index=False)

        result = run_script([
            RESHAPE_PY, input_csv, output_csv,
            "--operation", "melt",
            "--id-vars", "id",
            "--output-format", "csv",
        ])

        assert result["success"] is True, f"Expected success but got: {result}"

    def test_parquet_input_melt(self, tmp_path):
        """Parquet input via io_utils for melt."""
        df = self._make_melt_df()
        input_pq = str(tmp_path / "input.parquet")
        output_csv = str(tmp_path / "output.csv")
        df.to_parquet(input_pq, index=False)

        result = run_script([
            RESHAPE_PY, input_pq, output_csv,
            "--operation", "melt",
            "--id-vars", "id",
        ])

        assert result["success"] is True, f"Expected success but got: {result}"
        out_df = pd.read_csv(output_csv)
        assert len(out_df) == 20


# ===========================================================================
# 4. derive_columns.py
# ===========================================================================

class TestDeriveColumns:
    """Tests for derive_columns.py io_utils migration."""

    def test_csv_backward_compat(self, tmp_path):
        """CSV input/output still works."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_csv = str(tmp_path / "output.csv")
        df.to_csv(input_csv, index=False)

        result = run_script([
            DERIVE_COLUMNS_PY, input_csv, output_csv,
            "--expressions", '{"double_value": "value * 2"}',
        ])

        assert result["success"] is True, f"Expected success but got: {result}"
        assert os.path.exists(output_csv)
        out_df = pd.read_csv(output_csv)
        assert "double_value" in out_df.columns
        assert len(out_df) == 10

    def test_jsonl_input_output(self, tmp_path):
        """JSONL input/output via io_utils."""
        df = make_sample_df()
        input_jsonl = str(tmp_path / "input.jsonl")
        output_jsonl = str(tmp_path / "output.jsonl")
        df.to_json(input_jsonl, orient="records", lines=True)

        result = run_script([
            DERIVE_COLUMNS_PY, input_jsonl, output_jsonl,
            "--expressions", '{"double_value": "value * 2"}',
        ])

        assert result["success"] is True, f"Expected success but got: {result}"
        assert os.path.exists(output_jsonl)
        out_df = pd.read_json(output_jsonl, lines=True)
        assert "double_value" in out_df.columns
        assert len(out_df) == 10

    def test_output_format_flag_accepted(self, tmp_path):
        """--output-format flag is accepted without error."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_csv = str(tmp_path / "output.csv")
        df.to_csv(input_csv, index=False)

        result = run_script([
            DERIVE_COLUMNS_PY, input_csv, output_csv,
            "--expressions", '{"triple_value": "value * 3"}',
            "--input-format", "csv",
            "--output-format", "csv",
        ])

        assert result["success"] is True, f"Expected success but got: {result}"

    def test_parquet_input_csv_output(self, tmp_path):
        """Parquet input with CSV output via io_utils."""
        df = make_sample_df()
        input_pq = str(tmp_path / "input.parquet")
        output_csv = str(tmp_path / "output.csv")
        df.to_parquet(input_pq, index=False)

        result = run_script([
            DERIVE_COLUMNS_PY, input_pq, output_csv,
            "--expressions", '{"id_plus_1": "id + 1"}',
        ])

        assert result["success"] is True, f"Expected success but got: {result}"
        out_df = pd.read_csv(output_csv)
        assert "id_plus_1" in out_df.columns
        assert list(out_df["id_plus_1"]) == list(range(2, 12))


# ===========================================================================
# 5. merge_datasets.py
# ===========================================================================

class TestMergeDatasets:
    """Tests for merge_datasets.py io_utils migration."""

    def _make_left_df(self) -> pd.DataFrame:
        return pd.DataFrame({
            "id":    list(range(1, 11)),
            "value": list(range(10, 110, 10)),
        })

    def _make_right_df(self) -> pd.DataFrame:
        return pd.DataFrame({
            "id":   list(range(1, 11)),
            "label": [f"label_{i}" for i in range(1, 11)],
        })

    def test_csv_backward_compat(self, tmp_path):
        """CSV left/right input and CSV output still work."""
        left_csv  = str(tmp_path / "left.csv")
        right_csv = str(tmp_path / "right.csv")
        out_csv   = str(tmp_path / "output.csv")
        self._make_left_df().to_csv(left_csv, index=False)
        self._make_right_df().to_csv(right_csv, index=False)

        result = run_script([
            MERGE_DATASETS_PY, left_csv, right_csv, out_csv,
            "--on", "id",
        ])

        assert result["success"] is True, f"Expected success but got: {result}"
        assert os.path.exists(out_csv)
        out_df = pd.read_csv(out_csv)
        assert len(out_df) == 10
        assert "label" in out_df.columns

    def test_jsonl_input_output(self, tmp_path):
        """JSONL left/right input and JSONL output via io_utils."""
        left_jsonl  = str(tmp_path / "left.jsonl")
        right_jsonl = str(tmp_path / "right.jsonl")
        out_jsonl   = str(tmp_path / "output.jsonl")
        self._make_left_df().to_json(left_jsonl, orient="records", lines=True)
        self._make_right_df().to_json(right_jsonl, orient="records", lines=True)

        result = run_script([
            MERGE_DATASETS_PY, left_jsonl, right_jsonl, out_jsonl,
            "--on", "id",
        ])

        assert result["success"] is True, f"Expected success but got: {result}"
        assert os.path.exists(out_jsonl)
        out_df = pd.read_json(out_jsonl, lines=True)
        assert len(out_df) == 10
        assert "label" in out_df.columns

    def test_output_format_flag_accepted(self, tmp_path):
        """--output-format flag is accepted without error."""
        left_csv  = str(tmp_path / "left.csv")
        right_csv = str(tmp_path / "right.csv")
        out_csv   = str(tmp_path / "output.csv")
        self._make_left_df().to_csv(left_csv, index=False)
        self._make_right_df().to_csv(right_csv, index=False)

        result = run_script([
            MERGE_DATASETS_PY, left_csv, right_csv, out_csv,
            "--on", "id",
            "--output-format", "csv",
        ])

        assert result["success"] is True, f"Expected success but got: {result}"

    def test_parquet_left_csv_right(self, tmp_path):
        """Parquet left input with CSV right input via io_utils."""
        left_pq   = str(tmp_path / "left.parquet")
        right_csv = str(tmp_path / "right.csv")
        out_csv   = str(tmp_path / "output.csv")
        self._make_left_df().to_parquet(left_pq, index=False)
        self._make_right_df().to_csv(right_csv, index=False)

        result = run_script([
            MERGE_DATASETS_PY, left_pq, right_csv, out_csv,
            "--on", "id",
        ])

        assert result["success"] is True, f"Expected success but got: {result}"
        out_df = pd.read_csv(out_csv)
        assert len(out_df) == 10
        assert "label" in out_df.columns

    def test_explicit_format_flags(self, tmp_path):
        """Explicit --input-format and --right-format flags are accepted."""
        left_csv  = str(tmp_path / "left.csv")
        right_csv = str(tmp_path / "right.csv")
        out_csv   = str(tmp_path / "output.csv")
        self._make_left_df().to_csv(left_csv, index=False)
        self._make_right_df().to_csv(right_csv, index=False)

        result = run_script([
            MERGE_DATASETS_PY, left_csv, right_csv, out_csv,
            "--on", "id",
            "--input-format", "csv",
            "--right-format", "csv",
            "--output-format", "csv",
        ])

        assert result["success"] is True, f"Expected success but got: {result}"
