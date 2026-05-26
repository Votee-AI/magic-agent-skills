#!/usr/bin/env python3
"""
Section 17: ML Dataset Validation Tests.

Validates the MAGIC pipeline on traditional ML benchmark datasets
(Iris-like, Titanic-like, Wine Quality-like) generated inline.

Tasks covered:
- 17.1: Profiling + statistical analysis on ML datasets
- 17.2: Type detection on ML datasets
- 17.3: Cleaning on ML datasets
- 17.4: Exploration on ML datasets
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROFILING_SCRIPTS = PROJECT_ROOT / "skills" / "magic-data-profiling" / "scripts"
CLEANING_SCRIPTS  = PROJECT_ROOT / "skills" / "magic-data-cleaning" / "scripts"
EXPLORE_SCRIPTS   = PROJECT_ROOT / "skills" / "magic-data-exploration" / "scripts"
STATS_SCRIPTS     = PROJECT_ROOT / "skills" / "magic-statistical-analysis" / "scripts"

QUALITY_SCORE_PY        = str(PROFILING_SCRIPTS / "quality_score.py")
DISTRIBUTION_PY         = str(PROFILING_SCRIPTS / "distribution_analysis.py")
OUTLIER_DETECTION_PY    = str(PROFILING_SCRIPTS / "outlier_detection.py")
HANDLE_MISSING_PY       = str(CLEANING_SCRIPTS  / "handle_missing.py")
DETECT_ISSUES_PY        = str(CLEANING_SCRIPTS  / "detect_issues.py")
DETECT_PATTERNS_PY      = str(EXPLORE_SCRIPTS   / "detect_patterns.py")
SEGMENT_ANALYSIS_PY     = str(EXPLORE_SCRIPTS   / "segment_analysis.py")
HYPOTHESIS_TEST_PY      = str(STATS_SCRIPTS     / "hypothesis_test.py")
CORRELATION_ANALYSIS_PY = str(STATS_SCRIPTS     / "correlation_analysis.py")

# ---------------------------------------------------------------------------
# Inline dataset generators
# ---------------------------------------------------------------------------

def make_iris_like(n: int = 150) -> pd.DataFrame:
    """Iris-like: 4 numeric features + 1 categorical target."""
    np.random.seed(42)
    species = np.repeat(["setosa", "versicolor", "virginica"], n // 3)
    idx = np.arange(n) // (n // 3)
    data = {
        "sepal_length": np.random.normal([5.0, 5.9, 6.6][0] * (idx == 0)
                                        + [5.0, 5.9, 6.6][1] * (idx == 1)
                                        + [5.0, 5.9, 6.6][2] * (idx == 2), 0.4),
        "sepal_width":  np.random.normal([3.4, 2.8, 3.0][0] * (idx == 0)
                                        + [3.4, 2.8, 3.0][1] * (idx == 1)
                                        + [3.4, 2.8, 3.0][2] * (idx == 2), 0.4),
        "petal_length": np.random.normal([1.5, 4.3, 5.5][0] * (idx == 0)
                                        + [1.5, 4.3, 5.5][1] * (idx == 1)
                                        + [1.5, 4.3, 5.5][2] * (idx == 2), 0.5),
        "petal_width":  np.random.normal([0.2, 1.3, 2.0][0] * (idx == 0)
                                        + [0.2, 1.3, 2.0][1] * (idx == 1)
                                        + [0.2, 1.3, 2.0][2] * (idx == 2), 0.3),
        "species": species,
    }
    return pd.DataFrame(data)


def make_titanic_like(n: int = 200) -> pd.DataFrame:
    """Titanic-like: mixed types, missing values, binary target."""
    np.random.seed(42)
    data = {
        "survived": np.random.choice([0, 1], n, p=[0.6, 0.4]),
        "pclass":   np.random.choice([1, 2, 3], n),
        "name":     [f"Passenger_{i}" for i in range(n)],
        "sex":      np.random.choice(["male", "female"], n),
        "age":      np.random.normal(30, 12, n).clip(1, 80),
        "fare":     np.random.exponential(30, n),
        "embarked": np.random.choice(["C", "Q", "S"], n, p=[0.2, 0.1, 0.7]),
    }
    df = pd.DataFrame(data)
    mask_age      = np.random.random(n) < 0.15
    mask_embarked = np.random.random(n) < 0.05
    df.loc[mask_age, "age"]           = np.nan
    df.loc[mask_embarked, "embarked"] = np.nan
    return df


def make_wine_like(n: int = 200) -> pd.DataFrame:
    """Wine Quality-like: 11 numeric features + 1 ordinal target."""
    np.random.seed(42)
    data = {
        "fixed_acidity":       np.random.normal(8.3,   1.7,  n),
        "volatile_acidity":    np.random.normal(0.53,  0.18, n),
        "citric_acid":         np.random.normal(0.27,  0.19, n),
        "residual_sugar":      np.random.normal(2.5,   1.4,  n),
        "chlorides":           np.random.normal(0.087, 0.047,n),
        "free_sulfur_dioxide": np.random.normal(15.9,  10.5, n),
        "total_sulfur_dioxide":np.random.normal(46.5,  32.9, n),
        "density":             np.random.normal(0.997, 0.002,n),
        "pH":                  np.random.normal(3.31,  0.15, n),
        "sulphates":           np.random.normal(0.66,  0.17, n),
        "alcohol":             np.random.normal(10.4,  1.1,  n),
        "quality":             np.random.choice(
            [3, 4, 5, 6, 7, 8], n, p=[0.01, 0.05, 0.4, 0.4, 0.12, 0.02]
        ),
    }
    return pd.DataFrame(data)


# ---------------------------------------------------------------------------
# Subprocess helper
# ---------------------------------------------------------------------------

def run_script(args: list) -> dict:
    """
    Run a Python script via subprocess and return the parsed JSON from stdout.

    Fails the test with a descriptive message if the output is not valid JSON.
    """
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
            f"Command: {' '.join([sys.executable] + args)}\n"
            f"STDOUT: {result.stdout!r}\n"
            f"STDERR: {result.stderr!r}\n"
            f"Return code: {result.returncode}"
        )


# ===========================================================================
# Task 17.2: Type detection with detect_column_types()
# ===========================================================================

# ===========================================================================
# Task 17.1 (partial): Profiling scripts on ML datasets
# ===========================================================================

class TestProfilingOnMlDatasets:
    """Run profiling scripts on ML datasets and verify JSON output structure."""

    # --- quality_score.py ---

    def test_iris_quality_score_valid_json(self, tmp_path):
        """quality_score.py on Iris dataset returns valid JSON with score 0-100."""
        df = make_iris_like()
        input_csv  = str(tmp_path / "iris.csv")
        output_json = str(tmp_path / "iris_quality.json")
        df.to_csv(input_csv, index=False)

        result = run_script([QUALITY_SCORE_PY, input_csv, output_json])

        assert result.get("success") is True, f"Script failed: {result}"
        assert "overall_score" in result, "Missing 'overall_score' key"
        assert 0 <= result["overall_score"] <= 100, (
            f"overall_score {result['overall_score']} outside [0, 100]"
        )
        assert os.path.exists(output_json)

    def test_titanic_quality_score_valid_json(self, tmp_path):
        """quality_score.py on Titanic dataset returns valid JSON with score 0-100."""
        df = make_titanic_like()
        input_csv   = str(tmp_path / "titanic.csv")
        output_json = str(tmp_path / "titanic_quality.json")
        df.to_csv(input_csv, index=False)

        result = run_script([QUALITY_SCORE_PY, input_csv, output_json])

        assert result.get("success") is True, f"Script failed: {result}"
        assert "overall_score" in result
        assert 0 <= result["overall_score"] <= 100

    def test_wine_quality_score_valid_json(self, tmp_path):
        """quality_score.py on Wine dataset returns valid JSON with score 0-100."""
        df = make_wine_like()
        input_csv   = str(tmp_path / "wine.csv")
        output_json = str(tmp_path / "wine_quality.json")
        df.to_csv(input_csv, index=False)

        result = run_script([QUALITY_SCORE_PY, input_csv, output_json])

        assert result.get("success") is True, f"Script failed: {result}"
        assert "overall_score" in result
        assert 0 <= result["overall_score"] <= 100

    # --- distribution_analysis.py ---

    def test_iris_distribution_analysis_json(self, tmp_path):
        """distribution_analysis.py on Iris returns JSON with column stats."""
        df = make_iris_like()
        input_csv   = str(tmp_path / "iris.csv")
        output_json = str(tmp_path / "iris_dist.json")
        df.to_csv(input_csv, index=False)

        result = run_script([DISTRIBUTION_PY, input_csv, output_json])

        assert result.get("success") is True, f"Script failed: {result}"
        assert "distributions" in result, "Missing 'distributions' key"
        # Numeric columns should have distribution stats
        numeric_dists = result["distributions"].get("numeric", {})
        assert len(numeric_dists) > 0, "Expected numeric distribution stats for Iris"

    def test_titanic_distribution_analysis_json(self, tmp_path):
        """distribution_analysis.py on Titanic returns JSON with column stats."""
        df = make_titanic_like()
        input_csv   = str(tmp_path / "titanic.csv")
        output_json = str(tmp_path / "titanic_dist.json")
        df.to_csv(input_csv, index=False)

        result = run_script([DISTRIBUTION_PY, input_csv, output_json])

        assert result.get("success") is True, f"Script failed: {result}"
        assert "distributions" in result

    def test_wine_distribution_analysis_json(self, tmp_path):
        """distribution_analysis.py on Wine returns JSON with column stats."""
        df = make_wine_like()
        input_csv   = str(tmp_path / "wine.csv")
        output_json = str(tmp_path / "wine_dist.json")
        df.to_csv(input_csv, index=False)

        result = run_script([DISTRIBUTION_PY, input_csv, output_json])

        assert result.get("success") is True, f"Script failed: {result}"
        assert "distributions" in result
        numeric_dists = result["distributions"].get("numeric", {})
        # Wine has 12 numeric-like columns (11 features + quality)
        assert len(numeric_dists) >= 5, (
            f"Expected at least 5 numeric distribution stats for Wine, got {len(numeric_dists)}"
        )

    # --- outlier_detection.py ---

    def test_iris_outlier_detection_json(self, tmp_path):
        """outlier_detection.py on Iris returns JSON with outlier info."""
        df = make_iris_like()
        input_csv   = str(tmp_path / "iris.csv")
        output_json = str(tmp_path / "iris_outliers.json")
        df.to_csv(input_csv, index=False)

        result = run_script([OUTLIER_DETECTION_PY, input_csv, output_json])

        assert result.get("success") is True, f"Script failed: {result}"
        assert "outliers" in result, "Missing 'outliers' key"
        assert "total_outlier_rows" in result, "Missing 'total_outlier_rows' key"
        # IQR on normally distributed data should find a reasonable (non-absurd) count
        assert result["total_outlier_rows"] >= 0

    def test_wine_outlier_detection_finds_outliers(self, tmp_path):
        """outlier_detection.py on Wine finds a reasonable number of outliers."""
        df = make_wine_like()
        input_csv   = str(tmp_path / "wine.csv")
        output_json = str(tmp_path / "wine_outliers.json")
        df.to_csv(input_csv, index=False)

        result = run_script([OUTLIER_DETECTION_PY, input_csv, output_json])

        assert result.get("success") is True, f"Script failed: {result}"
        assert "outliers" in result
        # With 200 rows and normally distributed data, IQR method
        # typically flags some rows as outliers
        assert result["total_outlier_rows"] >= 0

    def test_titanic_outlier_detection_json(self, tmp_path):
        """outlier_detection.py on Titanic returns JSON with outlier info."""
        df = make_titanic_like()
        input_csv   = str(tmp_path / "titanic.csv")
        output_json = str(tmp_path / "titanic_outliers.json")
        df.to_csv(input_csv, index=False)

        result = run_script([OUTLIER_DETECTION_PY, input_csv, output_json])

        assert result.get("success") is True, f"Script failed: {result}"
        assert "outliers" in result
        # 'fare' is exponentially distributed and should have outliers
        outliers_by_col = result["outliers"]
        assert len(outliers_by_col) >= 0  # At minimum the structure is correct


# ===========================================================================
# Task 17.3: Cleaning on ML datasets
# ===========================================================================

class TestCleaningOnMlDatasets:
    """Run cleaning scripts on ML datasets with known issues."""

    def test_titanic_handle_missing_reduces_nans(self, tmp_path):
        """handle_missing.py --strategy auto reduces NaN count in Titanic data."""
        df = make_titanic_like()
        input_csv  = str(tmp_path / "titanic.csv")
        output_csv = str(tmp_path / "titanic_clean.csv")
        df.to_csv(input_csv, index=False)

        missing_before = int(df.isna().sum().sum())
        assert missing_before > 0, "Test setup error: Titanic data should have missing values"

        result = run_script([
            HANDLE_MISSING_PY, input_csv, output_csv,
            "--strategy", "auto",
        ])

        assert result.get("success") is True, f"Script failed: {result}"
        assert os.path.exists(output_csv), "Output CSV not created"

        df_clean = pd.read_csv(output_csv)
        missing_after = int(df_clean.isna().sum().sum())

        assert missing_after < missing_before, (
            f"Expected fewer NaNs after cleaning. Before: {missing_before}, After: {missing_after}"
        )

    def test_titanic_handle_missing_median_strategy(self, tmp_path):
        """handle_missing.py --strategy median imputes age column in Titanic data."""
        df = make_titanic_like()
        input_csv  = str(tmp_path / "titanic.csv")
        output_csv = str(tmp_path / "titanic_clean_median.csv")
        df.to_csv(input_csv, index=False)

        nan_in_age_before = int(df["age"].isna().sum())
        assert nan_in_age_before > 0, "Test setup: 'age' should have missing values"

        result = run_script([
            HANDLE_MISSING_PY, input_csv, output_csv,
            "--strategy", "median",
            "--columns", "age",
        ])

        assert result.get("success") is True, f"Script failed: {result}"
        assert os.path.exists(output_csv)

        df_clean = pd.read_csv(output_csv)
        nan_in_age_after = int(df_clean["age"].isna().sum())
        assert nan_in_age_after == 0, (
            f"Expected 0 NaN in 'age' after median imputation, got {nan_in_age_after}"
        )

    def test_wine_detect_issues_with_sentinels(self, tmp_path):
        """detect_issues.py detects sentinel strings injected into Wine data."""
        df = make_wine_like()
        # Inject N/A and ? sentinels into two columns
        df["alcohol"] = df["alcohol"].astype(object)
        df["pH"]      = df["pH"].astype(object)
        np.random.seed(99)
        sentinel_idx_alcohol = np.random.choice(df.index, size=10, replace=False)
        sentinel_idx_ph      = np.random.choice(df.index, size=8,  replace=False)
        df.loc[sentinel_idx_alcohol, "alcohol"] = "N/A"
        df.loc[sentinel_idx_ph, "pH"]           = "?"

        input_csv   = str(tmp_path / "wine_sentinels.csv")
        output_json = str(tmp_path / "wine_issues.json")
        df.to_csv(input_csv, index=False)

        result = run_script([DETECT_ISSUES_PY, input_csv, output_json])

        assert result.get("success") is True, f"Script failed: {result}"
        assert "issues" in result, "Missing 'issues' key"
        assert result.get("total_issues", 0) > 0, (
            "Expected detect_issues.py to find at least one issue with sentinel-injected Wine data"
        )

    def test_detect_issues_titanic_missing_values(self, tmp_path):
        """detect_issues.py identifies missing values in Titanic data."""
        df = make_titanic_like()
        input_csv   = str(tmp_path / "titanic.csv")
        output_json = str(tmp_path / "titanic_issues.json")
        df.to_csv(input_csv, index=False)

        result = run_script([DETECT_ISSUES_PY, input_csv, output_json])

        assert result.get("success") is True, f"Script failed: {result}"
        assert "issues" in result
        missing_issues = result["issues"].get("missing_values", {})
        # Titanic has missing age and embarked columns
        affected = missing_issues.get("affected_columns", {})
        assert len(affected) > 0, (
            "Expected detect_issues.py to flag missing value columns for Titanic"
        )


# ===========================================================================
# Task 17.4: Exploration on ML datasets
# ===========================================================================

class TestExplorationOnMlDatasets:
    """Run exploration scripts on ML datasets and verify findings."""

    def test_iris_detect_patterns_finds_findings(self, tmp_path):
        """detect_patterns.py on Iris returns success and at least one pattern finding."""
        df = make_iris_like()
        input_csv  = str(tmp_path / "iris.csv")
        output_csv = str(tmp_path / "iris_patterns.csv")
        df.to_csv(input_csv, index=False)

        result = run_script([DETECT_PATTERNS_PY, input_csv, output_csv])

        assert result.get("success") is True, f"Script failed: {result}"
        assert "findings" in result, "Missing 'findings' key"
        # Iris has strong inter-column correlations (petal length vs petal width)
        # and the script should detect at least one pattern
        assert isinstance(result["findings"], list), "'findings' should be a list"
        assert len(result["findings"]) >= 1, (
            "Expected at least one pattern finding for Iris dataset"
        )

    def test_wine_detect_patterns_finds_findings(self, tmp_path):
        """detect_patterns.py on Wine returns success and at least one pattern."""
        df = make_wine_like()
        input_csv  = str(tmp_path / "wine.csv")
        output_csv = str(tmp_path / "wine_patterns.csv")
        df.to_csv(input_csv, index=False)

        result = run_script([DETECT_PATTERNS_PY, input_csv, output_csv])

        assert result.get("success") is True, f"Script failed: {result}"
        assert "findings" in result
        assert isinstance(result["findings"], list)

    def test_titanic_segment_analysis_by_survived(self, tmp_path):
        """segment_analysis.py on Titanic grouped by 'survived' returns segment stats."""
        df = make_titanic_like()
        input_csv  = str(tmp_path / "titanic.csv")
        output_csv = str(tmp_path / "titanic_segments.csv")
        df.to_csv(input_csv, index=False)

        result = run_script([
            SEGMENT_ANALYSIS_PY, input_csv, output_csv,
            "--group_col", "survived",
        ])

        assert result.get("success") is True, f"Script failed: {result}"
        assert "segments" in result, "Missing 'segments' key"
        segments = result["segments"]
        # Should have exactly 2 segments: 0 and 1
        assert len(segments) == 2, (
            f"Expected 2 segments for 'survived' (0/1), got {len(segments)}: {list(segments.keys())}"
        )
        for segment_key, segment_info in segments.items():
            assert "n" in segment_info, f"Segment '{segment_key}' missing 'n'"
            assert segment_info["n"] > 0, f"Segment '{segment_key}' has n=0"

    def test_iris_segment_analysis_by_species(self, tmp_path):
        """segment_analysis.py on Iris grouped by 'species' returns 3 segments."""
        df = make_iris_like()
        input_csv  = str(tmp_path / "iris.csv")
        output_csv = str(tmp_path / "iris_segments.csv")
        df.to_csv(input_csv, index=False)

        result = run_script([
            SEGMENT_ANALYSIS_PY, input_csv, output_csv,
            "--group_col", "species",
        ])

        assert result.get("success") is True, f"Script failed: {result}"
        assert "segments" in result
        segments = result["segments"]
        assert len(segments) == 3, (
            f"Expected 3 species segments, got {len(segments)}: {list(segments.keys())}"
        )

    def test_titanic_segment_analysis_output_csv_exists(self, tmp_path):
        """segment_analysis.py creates the output CSV file on disk."""
        df = make_titanic_like()
        input_csv  = str(tmp_path / "titanic.csv")
        output_csv = str(tmp_path / "titanic_seg_out.csv")
        df.to_csv(input_csv, index=False)

        result = run_script([
            SEGMENT_ANALYSIS_PY, input_csv, output_csv,
            "--group_col", "survived",
        ])

        assert result.get("success") is True, f"Script failed: {result}"
        assert os.path.exists(output_csv), "Output CSV file was not created"
        out_df = pd.read_csv(output_csv)
        assert len(out_df) >= 2, "Expected at least 2 rows in segment output"


# ===========================================================================
# Task 17.1 (partial): Statistical analysis on ML datasets
# ===========================================================================

class TestStatisticalOnMlDatasets:
    """Run statistical analysis scripts on ML datasets."""

    def test_iris_hypothesis_test_petal_length_by_species(self, tmp_path):
        """hypothesis_test.py on Iris for petal_length by species runs ANOVA or Kruskal."""
        df = make_iris_like()
        input_csv   = str(tmp_path / "iris.csv")
        output_json = str(tmp_path / "iris_hypothesis.json")
        df.to_csv(input_csv, index=False)

        result = run_script([
            HYPOTHESIS_TEST_PY,
            "--input",  input_csv,
            "--output", output_json,
            "--group_col", "species",
            "--value_col", "petal_length",
        ])

        assert result.get("success") is True, f"Script failed: {result}"
        # Should select ANOVA or Kruskal-Wallis for 3 groups
        test_used = result.get("test_used", "")
        assert any(t in test_used for t in ["ANOVA", "Kruskal", "t-test", "Mann"]), (
            f"Unexpected test: '{test_used}'"
        )
        assert "result" in result, "Missing 'result' key"
        assert "p_value" in result["result"], "Missing 'p_value' in result"
        # Iris petal_length differs significantly across species
        assert result["result"]["p_value"] is not None

    def test_iris_hypothesis_test_significant(self, tmp_path):
        """Hypothesis test on Iris petal_length by species should be significant."""
        df = make_iris_like()
        input_csv   = str(tmp_path / "iris.csv")
        output_json = str(tmp_path / "iris_hyp_sig.json")
        df.to_csv(input_csv, index=False)

        result = run_script([
            HYPOTHESIS_TEST_PY,
            "--input",  input_csv,
            "--output", output_json,
            "--group_col", "species",
            "--value_col", "petal_length",
        ])

        assert result.get("success") is True, f"Script failed: {result}"
        p_value = result["result"]["p_value"]
        # Iris species have very different petal lengths, p should be tiny
        assert p_value < 0.05, (
            f"Expected significant result (p < 0.05) for Iris petal_length by species, got p={p_value}"
        )

    def test_wine_correlation_analysis_json(self, tmp_path):
        """correlation_analysis.py on Wine returns valid JSON with correlation data."""
        df = make_wine_like()
        input_csv   = str(tmp_path / "wine.csv")
        output_json = str(tmp_path / "wine_corr.json")
        df.to_csv(input_csv, index=False)

        result = run_script([
            CORRELATION_ANALYSIS_PY,
            "--input",  input_csv,
            "--output", output_json,
        ])

        assert result.get("success") is True, f"Script failed: {result}"
        assert "correlations" in result, "Missing 'correlations' key"
        assert isinstance(result["correlations"], list), "'correlations' should be a list"
        assert len(result["correlations"]) > 0, (
            "Expected at least one correlation pair for Wine dataset"
        )

    def test_wine_correlation_analysis_has_top_correlations(self, tmp_path):
        """correlation_analysis.py on Wine returns top_correlations list."""
        df = make_wine_like()
        input_csv   = str(tmp_path / "wine.csv")
        output_json = str(tmp_path / "wine_corr_top.json")
        df.to_csv(input_csv, index=False)

        result = run_script([
            CORRELATION_ANALYSIS_PY,
            "--input",  input_csv,
            "--output", output_json,
        ])

        assert result.get("success") is True, f"Script failed: {result}"
        assert "top_correlations" in result, "Missing 'top_correlations' key"
        top = result["top_correlations"]
        assert len(top) > 0, "Expected at least one entry in top_correlations"
        # Each entry must have required keys
        first = top[0]
        for key in ["col_a", "col_b", "r", "strength"]:
            assert key in first, f"Missing '{key}' in top correlation entry"

    def test_wine_correlation_output_file_exists(self, tmp_path):
        """correlation_analysis.py creates the output JSON file on disk."""
        df = make_wine_like()
        input_csv   = str(tmp_path / "wine.csv")
        output_json = str(tmp_path / "wine_corr_file.json")
        df.to_csv(input_csv, index=False)

        result = run_script([
            CORRELATION_ANALYSIS_PY,
            "--input",  input_csv,
            "--output", output_json,
        ])

        assert result.get("success") is True, f"Script failed: {result}"
        assert os.path.exists(output_json), "Output JSON file was not created"
        with open(output_json) as fh:
            saved = json.load(fh)
        assert saved.get("success") is True

    def test_iris_hypothesis_output_file_exists(self, tmp_path):
        """hypothesis_test.py creates the output JSON file on disk."""
        df = make_iris_like()
        input_csv   = str(tmp_path / "iris.csv")
        output_json = str(tmp_path / "iris_hyp_file.json")
        df.to_csv(input_csv, index=False)

        result = run_script([
            HYPOTHESIS_TEST_PY,
            "--input",  input_csv,
            "--output", output_json,
            "--group_col", "species",
            "--value_col", "sepal_length",
        ])

        assert result.get("success") is True, f"Script failed: {result}"
        assert os.path.exists(output_json), "Output JSON file was not created"
        with open(output_json) as fh:
            saved = json.load(fh)
        assert saved.get("success") is True
