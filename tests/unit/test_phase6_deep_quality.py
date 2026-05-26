#!/usr/bin/env python3
"""Unit tests for Phase 6: deep_quality_analysis.py 3-level orchestrator."""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pytest

SCRIPTS_DIR = Path(__file__).parent.parent.parent / "skills" / "magic-data-profiling" / "scripts"


@pytest.fixture
def sample_csv(tmp_path):
    """Create a sample CSV with various data quality issues."""
    df = pd.DataFrame({
        "word": ["打鼻鼾", "價錢", "文雅", "匡", "X", "", None, "需要", "齊集", "熔"],
        "pronunciation": ["daa2 bei6 hon4", "gaa3 cin4", "man4 ngaa5", "hong1", "N/A", "TBD", None, "seoi1 jiu3", "cai4 zaap6", "jung4"],
        "definitions": ["瞓覺時因為呼吸受阻", "一件貨品", "温文優雅", None, "???", "", None, "為咗達成某啲目的", "所有人同一時段", "固體物質受熱"],
    })
    path = tmp_path / "sample.csv"
    df.to_csv(path, index=False)
    return str(path)


def run_script(args, timeout=60):
    """Run deep_quality_analysis.py with given args."""
    cmd = [sys.executable, str(SCRIPTS_DIR / "deep_quality_analysis.py")] + args
    env = os.environ.copy()
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
    return result


class TestSurfaceLevel:
    def test_surface_produces_output(self, sample_csv, tmp_path):
        output = str(tmp_path / "result.json")
        result = run_script([sample_csv, output, "--depth", "surface"])
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert os.path.exists(output)

        with open(output) as f:
            data = json.load(f)
        assert "levels" in data or "analysis" in data

    def test_surface_detects_missing_values(self, sample_csv, tmp_path):
        output = str(tmp_path / "result.json")
        result = run_script([sample_csv, output, "--depth", "surface"])
        assert result.returncode == 0, f"stderr: {result.stderr}"

        with open(output) as f:
            data = json.load(f)

        # Navigate to surface level
        analysis = data.get("analysis", data)
        levels = analysis.get("levels", analysis)
        surface = levels.get("surface", levels)
        missing = surface.get("missing", {})

        # At least one column should have missing values
        has_missing = any(
            v.get("null_count", 0) > 0
            for v in missing.values()
        ) if missing else False
        assert has_missing, f"Expected missing values in: {missing}"

    def test_surface_detects_sentinels(self, sample_csv, tmp_path):
        output = str(tmp_path / "result.json")
        result = run_script([sample_csv, output, "--depth", "surface"])
        assert result.returncode == 0, f"stderr: {result.stderr}"

        with open(output) as f:
            data = json.load(f)

        analysis = data.get("analysis", data)
        levels = analysis.get("levels", analysis)
        surface = levels.get("surface", levels)
        sentinels = surface.get("sentinels", {})

        # At least one column should have sentinel values (X, N/A, TBD, ???, "")
        total_sentinels = sum(
            v.get("sentinel_count", 0) for v in sentinels.values()
        )
        assert total_sentinels > 0, f"Expected sentinel values in: {sentinels}"


class TestPatternLevel:
    def test_pattern_includes_surface(self, sample_csv, tmp_path):
        output = str(tmp_path / "result.json")
        result = run_script([sample_csv, output, "--depth", "pattern"])
        assert result.returncode == 0, f"stderr: {result.stderr}"

        with open(output) as f:
            data = json.load(f)

        analysis = data.get("analysis", data)
        levels = analysis.get("levels", analysis)
        assert "surface" in levels
        assert "pattern" in levels

    def test_pattern_detects_cjk_columns(self, sample_csv, tmp_path):
        output = str(tmp_path / "result.json")
        result = run_script([sample_csv, output, "--depth", "pattern", "--cjk-aware"])
        assert result.returncode == 0, f"stderr: {result.stderr}"

        with open(output) as f:
            data = json.load(f)

        analysis = data.get("analysis", data)
        levels = analysis.get("levels", analysis)
        pattern = levels.get("pattern", {})
        cjk_cols = pattern.get("cjk_columns", [])

        # "word" and "definitions" should be CJK-dominant
        assert "word" in cjk_cols, f"Expected 'word' in CJK columns: {cjk_cols}"


class TestDeepLevel:
    def test_deep_includes_all_levels(self, sample_csv, tmp_path):
        output = str(tmp_path / "result.json")
        result = run_script([sample_csv, output, "--depth", "deep"])
        assert result.returncode == 0, f"stderr: {result.stderr}"

        with open(output) as f:
            data = json.load(f)

        analysis = data.get("analysis", data)
        levels = analysis.get("levels", analysis)
        assert "surface" in levels
        assert "pattern" in levels
        assert "deep" in levels

    def test_deep_has_sampled_values(self, sample_csv, tmp_path):
        output = str(tmp_path / "result.json")
        result = run_script([sample_csv, output, "--depth", "deep"])
        assert result.returncode == 0, f"stderr: {result.stderr}"

        with open(output) as f:
            data = json.load(f)

        analysis = data.get("analysis", data)
        levels = analysis.get("levels", analysis)
        deep = levels.get("deep", {})
        sampled = deep.get("sampled_values", {})

        # Should have sampled values for at least one column
        assert len(sampled) > 0

    def test_deep_has_summary(self, sample_csv, tmp_path):
        output = str(tmp_path / "result.json")
        result = run_script([sample_csv, output, "--depth", "deep"])
        assert result.returncode == 0, f"stderr: {result.stderr}"

        with open(output) as f:
            data = json.load(f)

        analysis = data.get("analysis", data)
        summary = analysis.get("summary", data.get("summary", {}))
        assert "total_issues" in summary or "by_severity" in summary


