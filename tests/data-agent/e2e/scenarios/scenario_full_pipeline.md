# Scenario: Full Pipeline

## Mode: Synthetic (Automated)

## Input
- File: `datasets/full_pipeline_messy.csv`
- Generation: `python tests/e2e/generate_e2e_data.py` (seed=42)
- Description: 10,000+ rows (including 45 duplicates), 15 columns. Contains missing values (age 3%, income 8%, city 15%), duplicates, outliers in purchase_amount and quantity, 3 text columns, mixed date formats, whitespace issues.

## User Prompt (for agent testing)
"Load the CSV at tests/e2e/datasets/full_pipeline_messy.csv, profile it, clean any issues you find, validate the cleaned data, run statistical analysis on the numeric columns, create visualizations of the key findings, and generate a report."

## Expected Behavior
1. Agent activates `data-loading` skill, runs `detect_format.py` then `load_file.py` -> `ckpt_01_loaded.csv`
2. Agent activates `magic-data-profiling` skill, runs `quality_score.py` -> `ckpt_02_profiled.json`
3. Agent activates `data-cleaning` skill, runs `detect_issues.py` then `handle_missing.py` -> `ckpt_03_cleaned.csv`
4. Agent activates `data-validation` skill, runs `sanity_check.py` -> `ckpt_04_validated.json`
5. Agent activates `statistical-analysis` skill, runs `descriptive_stats.py` -> `ckpt_05_stats.json`
6. Agent activates `data-visualization` skill, runs `generate_chart.py` -> `ckpt_06_chart.png`
7. Agent activates `report-generation` skill, runs `generate_report.py` -> `ckpt_07_report.md`

## Success Criteria
- [ ] All checkpoint files created (ckpt_01 through ckpt_07)
- [ ] Cleaned data has fewer rows than original (duplicates removed)
- [ ] Report contains all 6 mandatory sections (Summary, Data Provenance, Methodology, Key Findings, Caveats, Next Steps)
- [ ] Charts use colorblind-safe palette
- [ ] Statistical outputs include uncertainty language ("suggests", "appears to")
- [ ] Text columns profiled with word count/vocabulary stats (not mean/median)
- [ ] Quality score reported
- [ ] Row counts tracked across all steps (rows_in/rows_out)

## Verification

### Programmatic (no agent needed):
```bash
python tests/e2e/generate_e2e_data.py
python tests/e2e/scenario_runner.py \
  --scenario full_pipeline \
  --input tests/e2e/datasets/full_pipeline_messy.csv \
  --workspace /tmp/e2e_full_pipeline
python tests/e2e/verify_scenario.py \
  --scenario full_pipeline \
  --workspace /tmp/e2e_full_pipeline
```

### Agent-based:
```bash
# 1. Give agent the user prompt above
# 2. Verify:
python tests/e2e/verify_scenario.py \
  --scenario full_pipeline \
  --workspace /path/to/agent/workspace \
  --checks tests/e2e/expected/full_pipeline_checks.json
```
