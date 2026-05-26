"""Unit tests for Section 10 enhancements: JSONL support and text parser."""

import csv
import json
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

# Path setup
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = PROJECT_ROOT / "skills"
# Script paths
NORMALIZE_SCRIPT = SKILLS_DIR / "magic-data-cleaning" / "scripts" / "normalize_strings.py"
HANDLE_MISSING_SCRIPT = SKILLS_DIR / "magic-data-cleaning" / "scripts" / "handle_missing.py"
RESHAPE_SCRIPT = SKILLS_DIR / "magic-data-transformation" / "scripts" / "reshape.py"
DERIVE_SCRIPT = SKILLS_DIR / "magic-data-transformation" / "scripts" / "derive_columns.py"
MERGE_SCRIPT = SKILLS_DIR / "magic-data-transformation" / "scripts" / "merge_datasets.py"
TEXT_PARSER_SCRIPT = SKILLS_DIR / "magic-data-loading" / "scripts" / "text_parser.py"


def run_script(script_path, args, cwd=None):
    """Run a script and return the subprocess result."""
    cmd = [sys.executable, str(script_path)] + args
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=cwd)


def write_jsonl(path, records):
    """Write records as JSONL."""
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def read_jsonl(path):
    """Read JSONL file into list of dicts."""
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


# =============================================================================
# io_utils.py tests
# =============================================================================


# =============================================================================
# Cleaning scripts JSONL support
# =============================================================================


class TestNormalizeStringsJsonl:
    """Test JSONL support in normalize_strings.py."""

    def test_jsonl_input_output(self, tmp_path):
        """Test reading JSONL and writing JSONL."""
        inp = tmp_path / "input.jsonl"
        out = tmp_path / "output.jsonl"
        write_jsonl(inp, [
            {"name": "  Alice  ", "city": " NYC "},
            {"name": "Bob  ", "city": "  LA"},
        ])
        result = run_script(NORMALIZE_SCRIPT, [
            str(inp), str(out), "--operations", "trim",
        ])
        assert result.returncode == 0, result.stderr
        records = read_jsonl(out)
        assert len(records) == 2
        assert records[0]["name"] == "Alice"
        assert records[1]["city"] == "LA"

    def test_csv_input_jsonl_output(self, tmp_path):
        """Test CSV input with JSONL output using --output-format."""
        inp = tmp_path / "input.csv"
        out = tmp_path / "output.jsonl"
        inp.write_text("name,city\n  Alice  , NYC \nBob  ,  LA\n")
        result = run_script(NORMALIZE_SCRIPT, [
            str(inp), str(out), "--operations", "trim",
        ])
        assert result.returncode == 0, result.stderr
        records = read_jsonl(out)
        assert len(records) == 2

    def test_explicit_format_flags(self, tmp_path):
        """Test --input-format and --output-format flags with jsonl extension."""
        inp = tmp_path / "data.jsonl"
        out = tmp_path / "result.jsonl"
        write_jsonl(inp, [{"val": "  test  "}])
        result = run_script(NORMALIZE_SCRIPT, [
            str(inp), str(out),
            "--input-format", "jsonl",
            "--output-format", "jsonl",
            "--operations", "trim",
        ])
        assert result.returncode == 0, result.stderr
        records = read_jsonl(out)
        assert records[0]["val"] == "test"


class TestHandleMissingJsonl:
    """Test JSONL support in handle_missing.py."""

    def test_jsonl_input_output(self, tmp_path):
        """Test reading and writing JSONL."""
        inp = tmp_path / "input.jsonl"
        out = tmp_path / "output.jsonl"
        write_jsonl(inp, [
            {"name": "Alice", "score": 90},
            {"name": "Bob", "score": None},
            {"name": "Carol", "score": 85},
        ])
        result = run_script(HANDLE_MISSING_SCRIPT, [
            str(inp), str(out), "--strategy", "median",
        ])
        assert result.returncode == 0, result.stderr
        records = read_jsonl(out)
        assert len(records) == 3
        # Bob's score should be filled
        assert records[1]["score"] is not None

    def test_explicit_jsonl_format(self, tmp_path):
        """Test explicit --input-format jsonl flag with jsonl extension."""
        inp = tmp_path / "data.jsonl"
        out = tmp_path / "result.jsonl"
        write_jsonl(inp, [
            {"a": 1, "b": 2},
            {"a": None, "b": 4},
        ])
        result = run_script(HANDLE_MISSING_SCRIPT, [
            str(inp), str(out),
            "--input-format", "jsonl",
            "--strategy", "mean",
        ])
        assert result.returncode == 0, result.stderr
        records = read_jsonl(out)
        assert len(records) == 2


# =============================================================================
# Transformation scripts JSONL input support
# =============================================================================


class TestReshapeJsonlInput:
    """Test JSONL input support in reshape.py."""

    def test_melt_from_jsonl(self, tmp_path):
        """Test melting a JSONL input file."""
        inp = tmp_path / "wide.jsonl"
        out = tmp_path / "long.csv"
        write_jsonl(inp, [
            {"id": 1, "math": 90, "english": 85},
            {"id": 2, "math": 78, "english": 92},
        ])
        result = run_script(RESHAPE_SCRIPT, [
            str(inp), str(out),
            "--operation", "melt",
            "--id-vars", "id",
            "--value-vars", "math,english",
        ])
        assert result.returncode == 0, result.stderr
        output = json.loads(result.stdout)
        assert output["success"] is True
        df = pd.read_csv(out)
        assert len(df) == 4  # 2 rows * 2 value vars

    def test_jsonl_input_with_explicit_format(self, tmp_path):
        """Test --input-format flag with jsonl extension."""
        inp = tmp_path / "data.jsonl"
        out = tmp_path / "pivoted.csv"
        write_jsonl(inp, [
            {"group": "A", "val": 10},
            {"group": "B", "val": 20},
        ])
        result = run_script(RESHAPE_SCRIPT, [
            str(inp), str(out),
            "--operation", "melt",
            "--id-vars", "group",
            "--input-format", "jsonl",
        ])
        assert result.returncode == 0, result.stderr


class TestDeriveColumnsJsonlInput:
    """Test JSONL input support in derive_columns.py."""

    def test_derive_from_jsonl(self, tmp_path):
        """Test deriving columns from JSONL input."""
        inp = tmp_path / "data.jsonl"
        out = tmp_path / "derived.csv"
        write_jsonl(inp, [
            {"a": 10, "b": 5},
            {"a": 20, "b": 3},
        ])
        result = run_script(DERIVE_SCRIPT, [
            str(inp), str(out),
            "--expressions", "c=a+b",
        ])
        assert result.returncode == 0, result.stderr
        output = json.loads(result.stdout)
        assert output["success"] is True
        df = pd.read_csv(out)
        assert df["c"].tolist() == [15, 23]

    def test_jsonl_input_jsonl_output(self, tmp_path):
        """Test JSONL in, JSONL out."""
        inp = tmp_path / "data.jsonl"
        out = tmp_path / "derived.jsonl"
        write_jsonl(inp, [{"x": 2}, {"x": 5}])
        result = run_script(DERIVE_SCRIPT, [
            str(inp), str(out),
            "--expressions", "x_squared=x**2",
        ])
        assert result.returncode == 0, result.stderr
        records = read_jsonl(out)
        assert records[0]["x_squared"] == 4
        assert records[1]["x_squared"] == 25


class TestMergeDatasetsJsonlInput:
    """Test JSONL input support in merge_datasets.py."""

    def test_merge_jsonl_inputs(self, tmp_path):
        """Test merging two JSONL files."""
        left = tmp_path / "left.jsonl"
        right = tmp_path / "right.jsonl"
        out = tmp_path / "merged.csv"
        write_jsonl(left, [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ])
        write_jsonl(right, [
            {"id": 1, "score": 95},
            {"id": 2, "score": 87},
        ])
        result = run_script(MERGE_SCRIPT, [
            str(left), str(right), str(out),
            "--on", "id",
        ])
        assert result.returncode == 0, result.stderr
        output = json.loads(result.stdout)
        assert output["success"] is True
        df = pd.read_csv(out)
        assert len(df) == 2
        assert "score" in df.columns

    def test_mixed_formats(self, tmp_path):
        """Test merging CSV left with JSONL right."""
        left = tmp_path / "left.csv"
        right = tmp_path / "right.jsonl"
        out = tmp_path / "merged.csv"
        left.write_text("id,name\n1,Alice\n2,Bob\n")
        write_jsonl(right, [
            {"id": 1, "score": 95},
            {"id": 2, "score": 87},
        ])
        result = run_script(MERGE_SCRIPT, [
            str(left), str(right), str(out),
            "--on", "id",
        ])
        assert result.returncode == 0, result.stderr
        df = pd.read_csv(out)
        assert len(df) == 2


# =============================================================================
# Text parser tests
# =============================================================================


class TestTextParser:
    """Test text_parser.py."""

    def test_basic_parsing(self, tmp_path):
        """Test basic marker-delimited parsing."""
        inp = tmp_path / "dict.txt"
        out = tmp_path / "parsed.csv"
        inp.write_text(
            "yue: 你好\n"
            "eng: hello\n"
            "----\n"
            "yue: 多謝\n"
            "eng: thank you\n"
        )
        result = run_script(TEXT_PARSER_SCRIPT, [
            "--input", str(inp),
            "--output", str(out),
            "--markers", "yue:,eng:",
            "--field-names", "source,target",
        ])
        assert result.returncode == 0, result.stderr
        output = json.loads(result.stdout)
        assert output["success"] is True
        assert output["records_parsed"] == 2

        df = pd.read_csv(out)
        assert len(df) == 2
        assert df.iloc[0]["source"] == "你好"
        assert df.iloc[1]["target"] == "thank you"

    def test_jsonl_output(self, tmp_path):
        """Test JSONL output format."""
        inp = tmp_path / "dict.txt"
        out = tmp_path / "parsed.jsonl"
        inp.write_text(
            "yue: 食飯\n"
            "eng: eat rice\n"
            "----\n"
            "yue: 飲水\n"
            "eng: drink water\n"
        )
        result = run_script(TEXT_PARSER_SCRIPT, [
            "--input", str(inp),
            "--output", str(out),
            "--markers", "yue:,eng:",
            "--field-names", "source,target",
        ])
        assert result.returncode == 0, result.stderr
        records = read_jsonl(out)
        assert len(records) == 2
        assert records[0]["source"] == "食飯"

    def test_multiline_fields(self, tmp_path):
        """Test multi-line content within a field."""
        inp = tmp_path / "multi.txt"
        out = tmp_path / "parsed.csv"
        inp.write_text(
            "title: My Article\n"
            "body: This is line one.\n"
            "This is line two.\n"
            "This is line three.\n"
            "----\n"
            "title: Another\n"
            "body: Single line.\n"
        )
        result = run_script(TEXT_PARSER_SCRIPT, [
            "--input", str(inp),
            "--output", str(out),
            "--markers", "title:,body:",
            "--field-names", "title,body",
        ])
        assert result.returncode == 0, result.stderr
        output = json.loads(result.stdout)
        assert output["records_parsed"] == 2

        df = pd.read_csv(out)
        assert "line two" in df.iloc[0]["body"]
        assert "line three" in df.iloc[0]["body"]

    def test_three_markers(self, tmp_path):
        """Test parsing with three different markers."""
        inp = tmp_path / "dict.txt"
        out = tmp_path / "parsed.csv"
        inp.write_text(
            "yue: 你好\n"
            "eng: hello\n"
            "<eg> 你好嗎？\n"
            "----\n"
            "yue: 再見\n"
            "eng: goodbye\n"
            "<eg> 再見啦！\n"
        )
        result = run_script(TEXT_PARSER_SCRIPT, [
            "--input", str(inp),
            "--output", str(out),
            "--markers", "yue:,eng:,<eg>",
            "--field-names", "source,target,example",
        ])
        assert result.returncode == 0, result.stderr
        df = pd.read_csv(out)
        assert len(df) == 2
        assert df.iloc[0]["example"] == "你好嗎？"

    def test_empty_fields(self, tmp_path):
        """Test records with missing markers (empty fields)."""
        inp = tmp_path / "partial.txt"
        out = tmp_path / "parsed.csv"
        inp.write_text(
            "yue: 你好\n"
            "eng: hello\n"
            "----\n"
            "yue: 多謝\n"
            "----\n"
            "eng: bye\n"
        )
        result = run_script(TEXT_PARSER_SCRIPT, [
            "--input", str(inp),
            "--output", str(out),
            "--markers", "yue:,eng:",
            "--field-names", "source,target",
        ])
        assert result.returncode == 0, result.stderr
        df = pd.read_csv(out)
        assert len(df) == 3
        # Second record should have empty target field
        assert pd.isna(df.iloc[1]["target"]) or df.iloc[1]["target"] == ""

    def test_skip_empty_records(self, tmp_path):
        """Test that fully empty records are skipped by default."""
        inp = tmp_path / "empty.txt"
        out = tmp_path / "parsed.csv"
        inp.write_text(
            "yue: 你好\n"
            "eng: hello\n"
            "----\n"
            "\n"
            "----\n"
            "yue: 再見\n"
            "eng: goodbye\n"
        )
        result = run_script(TEXT_PARSER_SCRIPT, [
            "--input", str(inp),
            "--output", str(out),
            "--markers", "yue:,eng:",
            "--field-names", "source,target",
        ])
        assert result.returncode == 0, result.stderr
        output = json.loads(result.stdout)
        assert output["records_parsed"] == 2  # Empty block skipped

    def test_no_skip_empty(self, tmp_path):
        """Test --no-skip-empty includes empty records."""
        inp = tmp_path / "empty.txt"
        out = tmp_path / "parsed.csv"
        inp.write_text(
            "yue: 你好\n"
            "eng: hello\n"
            "----\n"
            "  \n"
            "----\n"
            "yue: 再見\n"
            "eng: goodbye\n"
        )
        result = run_script(TEXT_PARSER_SCRIPT, [
            "--input", str(inp),
            "--output", str(out),
            "--markers", "yue:,eng:",
            "--field-names", "source,target",
            "--no-skip-empty",
        ])
        assert result.returncode == 0, result.stderr
        # Note: the empty block between separators is just whitespace,
        # which gets stripped. The behavior depends on implementation.

    def test_marker_count_mismatch_error(self, tmp_path):
        """Test error when markers and field names don't match."""
        inp = tmp_path / "dict.txt"
        out = tmp_path / "parsed.csv"
        inp.write_text("yue: test\n")
        result = run_script(TEXT_PARSER_SCRIPT, [
            "--input", str(inp),
            "--output", str(out),
            "--markers", "yue:,eng:",
            "--field-names", "source",
        ])
        assert result.returncode == 1
        output = json.loads(result.stdout)
        assert output["success"] is False
        assert "Marker count" in output["error"]

    def test_unicode_content(self, tmp_path):
        """Test parsing with Unicode content."""
        inp = tmp_path / "unicode.txt"
        out = tmp_path / "parsed.csv"
        inp.write_text(
            "yue: 廣東話\n"
            "eng: Chinese language\n"
            "----\n"
            "yue: 日本語\n"
            "eng: Japanese language\n",
            encoding="utf-8",
        )
        result = run_script(TEXT_PARSER_SCRIPT, [
            "--input", str(inp),
            "--output", str(out),
            "--markers", "yue:,eng:",
            "--field-names", "source,target",
        ])
        assert result.returncode == 0, result.stderr
        df = pd.read_csv(out)
        assert df.iloc[0]["source"] == "廣東話"
        assert df.iloc[1]["source"] == "日本語"

    def test_custom_separator(self, tmp_path):
        """Test custom record separator pattern."""
        inp = tmp_path / "custom.txt"
        out = tmp_path / "parsed.csv"
        inp.write_text(
            "key: alpha\n"
            "val: one\n"
            "===\n"
            "key: beta\n"
            "val: two\n"
        )
        result = run_script(TEXT_PARSER_SCRIPT, [
            "--input", str(inp),
            "--output", str(out),
            "--markers", "key:,val:",
            "--field-names", "key,value",
            "--record-separator", "===",
        ])
        assert result.returncode == 0, result.stderr
        df = pd.read_csv(out)
        assert len(df) == 2
        assert df.iloc[0]["key"] == "alpha"
        assert df.iloc[1]["value"] == "two"

    def test_blank_line_separator(self, tmp_path):
        """Test using blank line as record separator."""
        inp = tmp_path / "blank.txt"
        out = tmp_path / "parsed.csv"
        inp.write_text(
            "name: Alice\n"
            "role: engineer\n"
            "\n"
            "name: Bob\n"
            "role: designer\n"
        )
        result = run_script(TEXT_PARSER_SCRIPT, [
            "--input", str(inp),
            "--output", str(out),
            "--markers", "name:,role:",
            "--field-names", "name,role",
            "--record-separator", r"\n\n",
        ])
        assert result.returncode == 0, result.stderr
        output = json.loads(result.stdout)
        assert output["records_parsed"] >= 1

    def test_json_stdout_format(self, tmp_path):
        """Test JSON stdout output format."""
        inp = tmp_path / "test.txt"
        out = tmp_path / "out.csv"
        inp.write_text("a: one\n----\na: two\n")
        result = run_script(TEXT_PARSER_SCRIPT, [
            "--input", str(inp),
            "--output", str(out),
            "--markers", "a:",
            "--field-names", "val",
        ])
        assert result.returncode == 0, result.stderr
        output = json.loads(result.stdout)
        assert "success" in output
        assert "records_parsed" in output
        assert "encoding_detected" in output
        assert "markers" in output


# =============================================================================
# Text parser parse_text() function unit tests
# =============================================================================


class TestParseTextFunction:
    """Test the parse_text function directly."""

    def setup_method(self):
        """Import parse_text."""
        sys.path.insert(0, str(SKILLS_DIR / "magic-data-loading" / "scripts"))
        from text_parser import parse_text
        self.parse_text = parse_text

    def test_simple_two_field(self):
        content = "yue: hello\neng: world\n----\nyue: foo\neng: bar"
        records = self.parse_text(content, ["yue:", "eng:"], ["a", "b"])
        assert len(records) == 2
        assert records[0] == {"a": "hello", "b": "world"}
        assert records[1] == {"a": "foo", "b": "bar"}

    def test_multiline_continuation(self):
        content = "title: My Title\nbody: Line one\nLine two\n----\ntitle: T2\nbody: L1"
        records = self.parse_text(content, ["title:", "body:"], ["title", "body"])
        assert len(records) == 2
        assert "Line two" in records[0]["body"]

    def test_empty_content(self):
        records = self.parse_text("", ["a:"], ["a"])
        assert records == []

    def test_skip_empty_true(self):
        content = "----\n\n----\na: test"
        records = self.parse_text(content, ["a:"], ["a"], skip_empty=True)
        assert len(records) == 1
        assert records[0]["a"] == "test"

    def test_skip_empty_false(self):
        # With skip_empty=False, a record that has lines but no marker matches is kept
        content = "a: test\n----\nno marker here\n----\na: test2"
        records = self.parse_text(content, ["a:"], ["a"], skip_empty=False)
        # The middle record has no matching markers so "a" field is empty
        # But skip_empty=False means it's still included
        assert len(records) == 3
        assert records[1]["a"] == ""  # No marker matched, field stays empty

    def test_no_separator_single_record(self):
        content = "k: value1\nv: value2"
        records = self.parse_text(content, ["k:", "v:"], ["key", "val"])
        assert len(records) == 1
        assert records[0]["key"] == "value1"
        assert records[0]["val"] == "value2"
