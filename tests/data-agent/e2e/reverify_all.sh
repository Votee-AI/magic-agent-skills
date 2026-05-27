#!/usr/bin/env bash
# Re-verification script: runs all 32 data agent scripts against synthetic data.
# Usage: bash tests/e2e/reverify_all.sh
set -uo pipefail

PROJ_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SKILLS="$PROJ_ROOT/skills"
DATA="$PROJ_ROOT/tests/e2e/datasets"
INPUT="$DATA/full_pipeline_messy.csv"
WORK="/tmp/e2e_reverify_all"
PASS=0
FAIL=0
WARN=0
RESULTS=()

rm -rf "$WORK"
mkdir -p "$WORK"/{magic-data-loading,magic-data-profiling,magic-data-cleaning,magic-data-validation,magic-data-exploration,magic-data-transformation,magic-statistical-analysis,magic-data-visualization,magic-report-generation}

# Generate cleaned version for scripts that need clean numeric data
echo "=== Preparing cleaned dataset ==="
python3 "$SKILLS/magic-data-cleaning/scripts/handle_missing.py" "$INPUT" "$WORK/cleaned.csv" 2>"$WORK/handle_missing_prep.stderr" || true

run_script() {
    local name="$1"
    local skill="$2"
    shift 2
    local cmd=("$@")
    local stderr_file="$WORK/${skill}/${name}.stderr"

    if "${cmd[@]}" 2>"$stderr_file" >/dev/null; then
        # Check for FutureWarning in stderr
        if grep -q "FutureWarning" "$stderr_file" 2>/dev/null; then
            RESULTS+=("WARN|$skill|$name|FutureWarning in stderr")
            ((WARN++))
        else
            RESULTS+=("PASS|$skill|$name|")
            ((PASS++))
        fi
    else
        local err
        err=$(tail -1 "$stderr_file" 2>/dev/null || echo "unknown error")
        RESULTS+=("FAIL|$skill|$name|$err")
        ((FAIL++))
    fi
}

echo "=== Running all 32 scripts ==="

# --- magic-data-loading (4 scripts) ---
run_script "detect_format" "magic-data-loading" \
    python3 "$SKILLS/magic-data-loading/scripts/detect_format.py" "$INPUT" "$WORK/magic-data-loading/format.json"

run_script "sample_rows" "magic-data-loading" \
    python3 "$SKILLS/magic-data-loading/scripts/sample_rows.py" "$INPUT" "$WORK/magic-data-loading/sample.csv" --method head --n 50

run_script "load_file" "magic-data-loading" \
    python3 "$SKILLS/magic-data-loading/scripts/load_file.py" "$INPUT" "$WORK/magic-data-loading/loaded.csv"

run_script "validate_load" "magic-data-loading" \
    python3 "$SKILLS/magic-data-loading/scripts/validate_load.py" --output_path "$WORK/magic-data-loading/validate_load.json" --original_path "$INPUT" "$WORK/magic-data-loading/loaded.csv"

# --- magic-data-profiling (4 scripts) ---
run_script "distribution_analysis" "magic-data-profiling" \
    python3 "$SKILLS/magic-data-profiling/scripts/distribution_analysis.py" "$WORK/cleaned.csv" "$WORK/magic-data-profiling/dist.json"

run_script "correlation_matrix" "magic-data-profiling" \
    python3 "$SKILLS/magic-data-profiling/scripts/correlation_matrix.py" "$WORK/cleaned.csv" "$WORK/magic-data-profiling/corr.json" --method spearman

run_script "outlier_detection" "magic-data-profiling" \
    python3 "$SKILLS/magic-data-profiling/scripts/outlier_detection.py" "$WORK/cleaned.csv" "$WORK/magic-data-profiling/outliers.json" --method iqr --columns purchase_amount

run_script "quality_score" "magic-data-profiling" \
    python3 "$SKILLS/magic-data-profiling/scripts/quality_score.py" "$INPUT" "$WORK/magic-data-profiling/quality.json"

# --- magic-data-cleaning (5 scripts) ---
run_script "detect_issues" "magic-data-cleaning" \
    python3 "$SKILLS/magic-data-cleaning/scripts/detect_issues.py" "$INPUT" "$WORK/magic-data-cleaning/issues.json"

run_script "handle_missing" "magic-data-cleaning" \
    python3 "$SKILLS/magic-data-cleaning/scripts/handle_missing.py" "$INPUT" "$WORK/magic-data-cleaning/cleaned.csv"

run_script "normalize_strings" "magic-data-cleaning" \
    python3 "$SKILLS/magic-data-cleaning/scripts/normalize_strings.py" "$INPUT" "$WORK/magic-data-cleaning/normalized.csv"

# Create a minimal cleaning plan for execute_cleaning_plan
cat > "$WORK/magic-data-cleaning/plan.json" <<'PLAN'
{
  "version": "1.0",
  "columns": {
    "age": {"strategy": "fill_median", "params": {}},
    "income": {"strategy": "fill_median", "params": {}}
  }
}
PLAN
run_script "execute_cleaning_plan" "magic-data-cleaning" \
    python3 "$SKILLS/magic-data-cleaning/scripts/execute_cleaning_plan.py" "$INPUT" "$WORK/magic-data-cleaning/plan_cleaned.csv" "$WORK/magic-data-cleaning/plan.json"

run_script "validate_clean" "magic-data-cleaning" \
    python3 "$SKILLS/magic-data-cleaning/scripts/validate_clean.py" "$INPUT" "$WORK/magic-data-cleaning/cleaned.csv" "$WORK/magic-data-cleaning/validate.json"

# --- magic-data-validation (4 scripts) ---
run_script "infer_schema" "magic-data-validation" \
    python3 "$SKILLS/magic-data-validation/scripts/infer_schema.py" --input "$INPUT" --output "$WORK/magic-data-validation/schema.json"

run_script "validate_schema" "magic-data-validation" \
    python3 "$SKILLS/magic-data-validation/scripts/validate_schema.py" --input "$WORK/cleaned.csv" --schema "$WORK/magic-data-validation/schema.json" --output "$WORK/magic-data-validation/validation.json"

# Create constraints file
cat > "$WORK/magic-data-validation/constraints.json" <<'CONS'
{
  "constraints": [
    {"type": "vocabulary", "columns": ["product_category"], "params": {"allowed": ["Electronics", "Books", "Food", "Sports", "Clothing"]}}
  ]
}
CONS
run_script "check_constraints" "magic-data-validation" \
    python3 "$SKILLS/magic-data-validation/scripts/check_constraints.py" --input "$WORK/cleaned.csv" --constraints "$WORK/magic-data-validation/constraints.json" --output "$WORK/magic-data-validation/constraint_results.json"

run_script "sanity_check" "magic-data-validation" \
    python3 "$SKILLS/magic-data-validation/scripts/sanity_check.py" --input "$INPUT" --output "$WORK/magic-data-validation/sanity.json"

# --- magic-data-exploration (3 scripts) ---
run_script "relationship_explorer" "magic-data-exploration" \
    python3 "$SKILLS/magic-data-exploration/scripts/relationship_explorer.py" "$WORK/cleaned.csv" "$WORK/magic-data-exploration/relationships.csv" --max-pairs 5

run_script "detect_patterns" "magic-data-exploration" \
    python3 "$SKILLS/magic-data-exploration/scripts/detect_patterns.py" "$WORK/cleaned.csv" "$WORK/magic-data-exploration/patterns.json"

run_script "segment_analysis" "magic-data-exploration" \
    python3 "$SKILLS/magic-data-exploration/scripts/segment_analysis.py" "$WORK/cleaned.csv" "$WORK/magic-data-exploration/segments.json" --group_col product_category

# --- magic-data-transformation (5 scripts) ---
run_script "aggregate" "magic-data-transformation" \
    python3 "$SKILLS/magic-data-transformation/scripts/aggregate.py" "$WORK/cleaned.csv" "$WORK/magic-data-transformation/agg.csv" --group_cols product_category --functions mean,count

run_script "derive_columns" "magic-data-transformation" \
    python3 "$SKILLS/magic-data-transformation/scripts/derive_columns.py" "$WORK/cleaned.csv" "$WORK/magic-data-transformation/derived.csv" --expressions "total=purchase_amount*quantity"

run_script "merge_datasets" "magic-data-transformation" \
    python3 "$SKILLS/magic-data-transformation/scripts/merge_datasets.py" "$WORK/cleaned.csv" "$WORK/cleaned.csv" "$WORK/magic-data-transformation/merged.csv" --on id --how inner

run_script "reshape" "magic-data-transformation" \
    python3 "$SKILLS/magic-data-transformation/scripts/reshape.py" "$WORK/magic-data-transformation/agg.csv" "$WORK/magic-data-transformation/melted.csv" --operation melt --id_vars product_category --value_vars purchase_amount_mean,purchase_amount_count

run_script "validate_transform" "magic-data-transformation" \
    python3 "$SKILLS/magic-data-transformation/scripts/validate_transform.py" "$WORK/cleaned.csv" "$WORK/magic-data-transformation/agg.csv" "$WORK/magic-data-transformation/validate_transform.json" --key-columns product_category

# --- magic-statistical-analysis (3 scripts) ---
run_script "descriptive_stats" "magic-statistical-analysis" \
    python3 "$SKILLS/magic-statistical-analysis/scripts/descriptive_stats.py" --input "$WORK/cleaned.csv" --output "$WORK/magic-statistical-analysis/desc.json"

run_script "correlation_analysis" "magic-statistical-analysis" \
    python3 "$SKILLS/magic-statistical-analysis/scripts/correlation_analysis.py" --input "$WORK/cleaned.csv" --output "$WORK/magic-statistical-analysis/corr.json" --method auto

run_script "hypothesis_test" "magic-statistical-analysis" \
    python3 "$SKILLS/magic-statistical-analysis/scripts/hypothesis_test.py" --input "$WORK/cleaned.csv" --output "$WORK/magic-statistical-analysis/hyp.json" --group_col product_category --value_col purchase_amount --test auto

# --- magic-data-visualization (2 scripts) ---
run_script "chart_selector" "magic-data-visualization" \
    python3 "$SKILLS/magic-data-visualization/scripts/chart_selector.py" "$WORK/cleaned.csv" "$WORK/magic-data-visualization/charts.json" --relationship auto

run_script "generate_chart" "magic-data-visualization" \
    python3 "$SKILLS/magic-data-visualization/scripts/generate_chart.py" "$WORK/cleaned.csv" "$WORK/magic-data-visualization/chart.png" --chart_type bar --x_col product_category --y_col purchase_amount

# --- magic-report-generation (2 scripts) ---
run_script "format_table" "magic-report-generation" \
    python3 "$SKILLS/magic-report-generation/scripts/format_table.py" "$WORK/cleaned.csv" "$WORK/magic-report-generation/table.md" --format markdown --max_rows 10

# Create a findings JSON for generate_report
cat > "$WORK/magic-report-generation/findings.json" <<'FINDINGS'
{
  "title": "Test Report",
  "sections": [
    {"heading": "Summary", "content": "This is a test report for re-verification."},
    {"heading": "Data Quality", "content": "10045 rows, 15 columns, 5% missing values."}
  ]
}
FINDINGS
run_script "generate_report" "magic-report-generation" \
    python3 "$SKILLS/magic-report-generation/scripts/generate_report.py" "$WORK/magic-report-generation/findings.json" "$WORK/magic-report-generation/report.md"

# === Summary ===
echo ""
echo "=============================================="
echo "  RE-VERIFICATION SUMMARY"
echo "=============================================="
printf "%-6s | %-25s | %-25s | %s\n" "Status" "Skill" "Script" "Notes"
echo "-------|---------------------------|---------------------------|------"
for r in "${RESULTS[@]}"; do
    IFS='|' read -r status skill script notes <<< "$r"
    printf "%-6s | %-25s | %-25s | %s\n" "$status" "$skill" "$script" "$notes"
done
echo "=============================================="
echo "PASS: $PASS  |  WARN: $WARN  |  FAIL: $FAIL  |  TOTAL: $((PASS + WARN + FAIL))/32"
echo "=============================================="

if [ "$FAIL" -gt 0 ]; then
    echo "RESULT: FAILED — $FAIL script(s) failed"
    exit 1
else
    echo "RESULT: ALL SCRIPTS PASSED"
    exit 0
fi
