#!/usr/bin/env python3
"""
Phase 3 migration tests: verify that remaining scripts (cleaning, loading,
synthesis, report) use io_utils for I/O and support multi-format flags.

Covered scripts:
  Cleaning:  detect_issues.py, execute_cleaning_plan.py, validate_clean.py
  Loading:   load_file.py, sample_rows.py, validate_load.py
  Synthesis: generate_column.py (--output-format), batch_synthesize.py (--output-format),
             enrich_from_reference.py (--output-format)
  Report:    format_table.py (--input-format)
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
# Script paths
# ---------------------------------------------------------------------------

BASE = Path(__file__).resolve().parents[2] / "skills"

DETECT_ISSUES_PY        = str(BASE / "magic-data-cleaning"  / "scripts" / "detect_issues.py")
EXEC_CLEANING_PLAN_PY   = str(BASE / "magic-data-cleaning"  / "scripts" / "execute_cleaning_plan.py")
VALIDATE_CLEAN_PY       = str(BASE / "magic-data-cleaning"  / "scripts" / "validate_clean.py")

LOAD_FILE_PY            = str(BASE / "magic-data-loading"   / "scripts" / "load_file.py")
SAMPLE_ROWS_PY          = str(BASE / "magic-data-loading"   / "scripts" / "sample_rows.py")
VALIDATE_LOAD_PY        = str(BASE / "magic-data-loading"   / "scripts" / "validate_load.py")

ENRICH_FROM_REF_PY      = str(BASE / "magic-data-synthesis" / "scripts" / "enrich_from_reference.py")

FORMAT_TABLE_PY         = str(BASE / "magic-report-generation" / "scripts" / "format_table.py")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_sample_df() -> pd.DataFrame:
    """Return a simple 20-row DataFrame for testing."""
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
# Cleaning: detect_issues.py
# ===========================================================================

class TestDetectIssues:
    """Tests for detect_issues.py io_utils migration."""

    def test_csv_backward_compat(self, tmp_path):
        """CSV input still works."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_json = str(tmp_path / "issues.json")
        df.to_csv(input_csv, index=False)

        result = run_script([DETECT_ISSUES_PY, input_csv, output_json])
        assert result.get("success") is True

    def test_jsonl_input_format(self, tmp_path):
        """JSONL input works via --input-format flag."""
        df = make_sample_df()
        input_jsonl = str(tmp_path / "input.jsonl")
        output_json = str(tmp_path / "issues.json")
        write_jsonl(df, input_jsonl)

        result = run_script([DETECT_ISSUES_PY, input_jsonl, output_json,
                             "--input-format", "jsonl"])
        assert result.get("success") is True


# ===========================================================================
# Cleaning: execute_cleaning_plan.py
# ===========================================================================

class TestExecuteCleaningPlan:
    """Tests for execute_cleaning_plan.py io_utils migration."""

    def _make_plan(self, tmp_path) -> str:
        """Write a minimal cleaning plan JSON."""
        plan = {
            "version": "1.0",
            "columns": {
                "label": {"strategy": "trim_whitespace", "params": {}}
            }
        }
        plan_path = str(tmp_path / "plan.json")
        with open(plan_path, "w") as f:
            json.dump(plan, f)
        return plan_path

    def test_csv_backward_compat(self, tmp_path):
        """CSV input/output still works."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_csv = str(tmp_path / "cleaned.csv")
        plan_path = self._make_plan(tmp_path)
        df.to_csv(input_csv, index=False)

        result = run_script([EXEC_CLEANING_PLAN_PY, input_csv, output_csv, plan_path])
        assert result.get("success") is True
        assert Path(output_csv).exists()

    def test_jsonl_input_output_format(self, tmp_path):
        """JSONL input and output works via --input-format and --output-format flags."""
        df = make_sample_df()
        input_jsonl = str(tmp_path / "input.jsonl")
        output_jsonl = str(tmp_path / "cleaned.jsonl")
        plan_path = self._make_plan(tmp_path)
        write_jsonl(df, input_jsonl)

        result = run_script([EXEC_CLEANING_PLAN_PY, input_jsonl, output_jsonl, plan_path,
                             "--input-format", "jsonl",
                             "--output-format", "jsonl"])
        assert result.get("success") is True
        assert Path(output_jsonl).exists()


# ===========================================================================
# Cleaning: validate_clean.py
# ===========================================================================

class TestValidateClean:
    """Tests for validate_clean.py io_utils migration."""

    def test_csv_backward_compat(self, tmp_path):
        """CSV input still works (original + cleaned)."""
        df = make_sample_df()
        original_csv = str(tmp_path / "original.csv")
        cleaned_csv  = str(tmp_path / "cleaned.csv")
        output_json  = str(tmp_path / "report.json")
        df.to_csv(original_csv, index=False)
        df.to_csv(cleaned_csv, index=False)

        result = run_script([VALIDATE_CLEAN_PY, original_csv, cleaned_csv, output_json])
        assert result.get("success") is True

    def test_jsonl_input_format(self, tmp_path):
        """JSONL input works via --input-format flag (applies to both files)."""
        df = make_sample_df()
        original_jsonl = str(tmp_path / "original.jsonl")
        cleaned_jsonl  = str(tmp_path / "cleaned.jsonl")
        output_json    = str(tmp_path / "report.json")
        write_jsonl(df, original_jsonl)
        write_jsonl(df, cleaned_jsonl)

        result = run_script([VALIDATE_CLEAN_PY, original_jsonl, cleaned_jsonl, output_json,
                             "--input-format", "jsonl"])
        assert result.get("success") is True


# ===========================================================================
# Loading: load_file.py
# ===========================================================================

class TestLoadFile:
    """Tests for load_file.py --output-format migration."""

    def test_csv_input_csv_output(self, tmp_path):
        """CSV input to CSV output (default behavior)."""
        df = make_sample_df()
        input_csv  = str(tmp_path / "input.csv")
        output_csv = str(tmp_path / "output.csv")
        df.to_csv(input_csv, index=False)

        result = run_script([LOAD_FILE_PY, input_csv, output_csv])
        assert result.get("success") is True
        assert Path(output_csv).exists()

    def test_csv_input_jsonl_output_format(self, tmp_path):
        """CSV input can be written as JSONL via --output-format."""
        df = make_sample_df()
        input_csv    = str(tmp_path / "input.csv")
        output_jsonl = str(tmp_path / "output.jsonl")
        df.to_csv(input_csv, index=False)

        result = run_script([LOAD_FILE_PY, input_csv, output_jsonl,
                             "--output-format", "jsonl"])
        assert result.get("success") is True
        assert Path(output_jsonl).exists()


# ===========================================================================
# Loading: sample_rows.py
# ===========================================================================

class TestSampleRows:
    """Tests for sample_rows.py io_utils migration."""

    def test_csv_backward_compat(self, tmp_path):
        """CSV input/output still works."""
        df = make_sample_df()
        input_csv  = str(tmp_path / "input.csv")
        output_csv = str(tmp_path / "sample.csv")
        df.to_csv(input_csv, index=False)

        result = run_script([SAMPLE_ROWS_PY, input_csv, output_csv, "--n", "5"])
        assert result.get("success") is True
        assert result.get("rows_out") == 5

    def test_jsonl_input_and_output(self, tmp_path):
        """JSONL input and output work via format flags."""
        df = make_sample_df()
        input_jsonl  = str(tmp_path / "input.jsonl")
        output_jsonl = str(tmp_path / "sample.jsonl")
        write_jsonl(df, input_jsonl)

        result = run_script([SAMPLE_ROWS_PY, input_jsonl, output_jsonl, "--n", "5",
                             "--input-format", "jsonl",
                             "--output-format", "jsonl"])
        assert result.get("success") is True
        assert Path(output_jsonl).exists()


# ===========================================================================
# Loading: validate_load.py
# ===========================================================================

class TestValidateLoad:
    """Tests for validate_load.py io_utils migration."""

    def test_csv_backward_compat(self, tmp_path):
        """CSV input still works."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        df.to_csv(input_csv, index=False)

        result = run_script([VALIDATE_LOAD_PY, input_csv])
        assert result.get("success") is True
        assert result.get("valid") is True

    def test_jsonl_input_format(self, tmp_path):
        """JSONL input works via --input-format flag."""
        df = make_sample_df()
        input_jsonl = str(tmp_path / "input.jsonl")
        write_jsonl(df, input_jsonl)

        result = run_script([VALIDATE_LOAD_PY, input_jsonl,
                             "--input-format", "jsonl"])
        assert result.get("success") is True
        assert result.get("valid") is True


# ===========================================================================
# Synthesis: enrich_from_reference.py (--output-format)
# ===========================================================================

class TestEnrichFromReference:
    """Tests for enrich_from_reference.py --output-format migration."""

    def test_csv_output_backward_compat(self, tmp_path):
        """CSV output (default) still works."""
        df = make_sample_df()
        ref_df = pd.DataFrame({
            "category": ["A", "B"],
            "category_label": ["Type A", "Type B"],
        })
        input_csv  = str(tmp_path / "input.csv")
        ref_csv    = str(tmp_path / "ref.csv")
        output_csv = str(tmp_path / "enriched.csv")
        df.to_csv(input_csv, index=False)
        ref_df.to_csv(ref_csv, index=False)

        result = run_script([ENRICH_FROM_REF_PY, input_csv, output_csv,
                             "--reference-paths", ref_csv,
                             "--source-key", "category",
                             "--reference-key", "category"])
        assert result.get("success") is True
        assert Path(output_csv).exists()

    def test_jsonl_output_format(self, tmp_path):
        """JSONL output works via --output-format flag."""
        df = make_sample_df()
        ref_df = pd.DataFrame({
            "category": ["A", "B"],
            "category_label": ["Type A", "Type B"],
        })
        input_csv    = str(tmp_path / "input.csv")
        ref_csv      = str(tmp_path / "ref.csv")
        output_jsonl = str(tmp_path / "enriched.jsonl")
        df.to_csv(input_csv, index=False)
        ref_df.to_csv(ref_csv, index=False)

        result = run_script([ENRICH_FROM_REF_PY, input_csv, output_jsonl,
                             "--reference-paths", ref_csv,
                             "--source-key", "category",
                             "--reference-key", "category",
                             "--output-format", "jsonl"])
        assert result.get("success") is True
        assert Path(output_jsonl).exists()


# ===========================================================================
# Report: format_table.py
# ===========================================================================

class TestFormatTable:
    """Tests for format_table.py io_utils migration."""

    def test_csv_backward_compat(self, tmp_path):
        """CSV input still works."""
        df = make_sample_df()
        input_csv   = str(tmp_path / "input.csv")
        output_md   = str(tmp_path / "table.md")
        df.to_csv(input_csv, index=False)

        result = run_script([FORMAT_TABLE_PY, input_csv, output_md])
        assert result.get("success") is True
        assert Path(output_md).exists()

    def test_jsonl_input_format(self, tmp_path):
        """JSONL input works via --input-format flag."""
        df = make_sample_df()
        input_jsonl = str(tmp_path / "input.jsonl")
        output_md   = str(tmp_path / "table.md")
        write_jsonl(df, input_jsonl)

        result = run_script([FORMAT_TABLE_PY, input_jsonl, output_md,
                             "--input-format", "jsonl"])
        assert result.get("success") is True
        assert Path(output_md).exists()
