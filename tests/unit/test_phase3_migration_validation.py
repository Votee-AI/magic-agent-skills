#!/usr/bin/env python3
"""
Phase 3 migration tests: verify that all 6 validation scripts
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
SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "skills" / "magic-data-validation" / "scripts"

INFER_SCHEMA_PY       = str(SCRIPTS_DIR / "infer_schema.py")
VALIDATE_SCHEMA_PY    = str(SCRIPTS_DIR / "validate_schema.py")
CHECK_CONSTRAINTS_PY  = str(SCRIPTS_DIR / "check_constraints.py")
SANITY_CHECK_PY       = str(SCRIPTS_DIR / "sanity_check.py")
VALIDATE_STATS_PY     = str(SCRIPTS_DIR / "validate_statistics.py")
CONTENT_VALIDATOR_PY  = str(SCRIPTS_DIR / "content_validator.py")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_sample_df() -> pd.DataFrame:
    """Return a simple 20-row DataFrame with numeric + text + category columns."""
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
# 1. infer_schema.py
# ===========================================================================

class TestInferSchema:
    """Tests for infer_schema.py io_utils migration."""

    def test_csv_backward_compat(self, tmp_path):
        """CSV input still works exactly as before."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_json = str(tmp_path / "schema.json")
        df.to_csv(input_csv, index=False)

        result = run_script([INFER_SCHEMA_PY, "--input", input_csv,
                             "--output", output_json])
        assert result.get("success") is True
        assert "columns" in result or Path(output_json).exists()

    def test_jsonl_input_format(self, tmp_path):
        """JSONL input works via --input-format flag."""
        df = make_sample_df()
        input_jsonl = str(tmp_path / "input.jsonl")
        output_json = str(tmp_path / "schema.json")
        write_jsonl(df, input_jsonl)

        result = run_script([INFER_SCHEMA_PY, "--input", input_jsonl,
                             "--output", output_json,
                             "--input-format", "jsonl"])
        assert result.get("success") is True


# ===========================================================================
# 2. validate_schema.py
# ===========================================================================

class TestValidateSchema:
    """Tests for validate_schema.py io_utils migration."""

    def _make_schema(self, tmp_path) -> str:
        """Write a minimal schema JSON for testing."""
        schema = {
            "columns": {
                "id": {"type": "integer"},
                "value": {"type": "float"},
                "label": {"type": "string"},
            }
        }
        schema_path = str(tmp_path / "schema.json")
        with open(schema_path, "w") as f:
            json.dump(schema, f)
        return schema_path

    def test_csv_backward_compat(self, tmp_path):
        """CSV input still works."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_json = str(tmp_path / "result.json")
        schema_path = self._make_schema(tmp_path)
        df.to_csv(input_csv, index=False)

        result = run_script([VALIDATE_SCHEMA_PY, "--input", input_csv,
                             "--schema", schema_path, "--output", output_json])
        assert result.get("success") is True

    def test_jsonl_input_format(self, tmp_path):
        """JSONL input works via --input-format flag."""
        df = make_sample_df()
        input_jsonl = str(tmp_path / "input.jsonl")
        output_json = str(tmp_path / "result.json")
        schema_path = self._make_schema(tmp_path)
        write_jsonl(df, input_jsonl)

        result = run_script([VALIDATE_SCHEMA_PY, "--input", input_jsonl,
                             "--schema", schema_path, "--output", output_json,
                             "--input-format", "jsonl"])
        assert result.get("success") is True


# ===========================================================================
# 3. check_constraints.py
# ===========================================================================

class TestCheckConstraints:
    """Tests for check_constraints.py io_utils migration."""

    def _make_constraints(self, tmp_path) -> str:
        """Write a minimal constraints JSON for testing."""
        constraints = {
            "columns": {
                "value": {"min": 0, "max": 200},
                "score": {"min": 0, "max": 100},
            }
        }
        constraints_path = str(tmp_path / "constraints.json")
        with open(constraints_path, "w") as f:
            json.dump(constraints, f)
        return constraints_path

    def test_csv_backward_compat(self, tmp_path):
        """CSV input still works."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_json = str(tmp_path / "result.json")
        constraints_path = self._make_constraints(tmp_path)
        df.to_csv(input_csv, index=False)

        result = run_script([CHECK_CONSTRAINTS_PY, "--input", input_csv,
                             "--constraints", constraints_path, "--output", output_json])
        assert result.get("success") is True

    def test_jsonl_input_format(self, tmp_path):
        """JSONL input works via --input-format flag."""
        df = make_sample_df()
        input_jsonl = str(tmp_path / "input.jsonl")
        output_json = str(tmp_path / "result.json")
        constraints_path = self._make_constraints(tmp_path)
        write_jsonl(df, input_jsonl)

        result = run_script([CHECK_CONSTRAINTS_PY, "--input", input_jsonl,
                             "--constraints", constraints_path, "--output", output_json,
                             "--input-format", "jsonl"])
        assert result.get("success") is True


# ===========================================================================
# 4. sanity_check.py
# ===========================================================================

class TestSanityCheck:
    """Tests for sanity_check.py io_utils migration."""

    def test_csv_backward_compat(self, tmp_path):
        """CSV input still works."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_json = str(tmp_path / "result.json")
        df.to_csv(input_csv, index=False)

        result = run_script([SANITY_CHECK_PY, "--input", input_csv,
                             "--output", output_json])
        assert result.get("success") is True

    def test_jsonl_input_format(self, tmp_path):
        """JSONL input works via --input-format flag."""
        df = make_sample_df()
        input_jsonl = str(tmp_path / "input.jsonl")
        output_json = str(tmp_path / "result.json")
        write_jsonl(df, input_jsonl)

        result = run_script([SANITY_CHECK_PY, "--input", input_jsonl,
                             "--output", output_json,
                             "--input-format", "jsonl"])
        assert result.get("success") is True


# ===========================================================================
# 5. validate_statistics.py
# ===========================================================================

class TestValidateStatistics:
    """Tests for validate_statistics.py io_utils migration."""

    def _make_stats(self, df: pd.DataFrame, tmp_path) -> str:
        """Write a minimal statistics JSON that matches the sample DataFrame."""
        stats_data = {
            "columns": {
                col: {
                    "count": int(df[col].count()),
                    "mean": float(df[col].mean()) if pd.api.types.is_numeric_dtype(df[col]) else None,
                }
                for col in ["value", "score"]
            }
        }
        stats_path = str(tmp_path / "stats.json")
        with open(stats_path, "w") as f:
            json.dump(stats_data, f)
        return stats_path

    def test_csv_backward_compat(self, tmp_path):
        """CSV input still works (positional args: source, stats, output)."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        stats_path = self._make_stats(df, tmp_path)
        output_json = str(tmp_path / "result.json")
        df.to_csv(input_csv, index=False)

        result = run_script([VALIDATE_STATS_PY, input_csv, stats_path, output_json])
        assert result.get("success") is True

    def test_jsonl_input_format(self, tmp_path):
        """JSONL input works via --input-format flag."""
        df = make_sample_df()
        input_jsonl = str(tmp_path / "input.jsonl")
        stats_path = self._make_stats(df, tmp_path)
        output_json = str(tmp_path / "result.json")
        write_jsonl(df, input_jsonl)

        result = run_script([VALIDATE_STATS_PY, input_jsonl, stats_path, output_json,
                             "--input-format", "jsonl"])
        assert result.get("success") is True


# ===========================================================================
# 6. content_validator.py
# ===========================================================================

class TestContentValidator:
    """Tests for content_validator.py io_utils migration."""

    def test_csv_backward_compat(self, tmp_path):
        """CSV input still works (positional: input_path output_path)."""
        df = make_sample_df()
        input_csv = str(tmp_path / "input.csv")
        output_json = str(tmp_path / "result.json")
        df.to_csv(input_csv, index=False)

        result = run_script([CONTENT_VALIDATOR_PY, input_csv, output_json])
        assert result.get("success") is True

    def test_jsonl_input_format(self, tmp_path):
        """JSONL input works via --input-format flag."""
        df = make_sample_df()
        input_jsonl = str(tmp_path / "input.jsonl")
        output_json = str(tmp_path / "result.json")
        write_jsonl(df, input_jsonl)

        result = run_script([CONTENT_VALIDATOR_PY, input_jsonl, output_json,
                             "--input-format", "jsonl"])
        assert result.get("success") is True
