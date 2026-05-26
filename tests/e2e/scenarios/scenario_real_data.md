# Scenario: Real-Data Analysis (User-Guided)

## Overview

Use this mode when testing with your own CSV/data files. You define what the agent should do and what success looks like via a configuration file.

## Setup

### Step 1: Copy the config template

```bash
cp tests/e2e/scenarios/scenario_config_template.json my_config.json
```

### Step 2: Edit the config

Fill in these required fields:

| Field | What to set |
|-------|-------------|
| `scenario_name` | A short name for your test (e.g., `sales_q4_analysis`) |
| `input.file_path` | Absolute path to your CSV file |
| `input.description` | What the data is and what you want to learn |
| `expectations.magic-data-loading.expected_columns` | Column names your data must have |
| `verification.output_files` | File patterns to check for in the workspace |

### Step 3: Define your expectations

This is the critical part. Since real data requires domain knowledge, **you** must tell the system:

- **What issues exist**: Do you expect missing values? Which columns? Duplicates?
- **What cleaning to apply**: Auto? Mean imputation? Drop rows? For which columns?
- **What to analyze**: Which columns are numeric targets? What relationships matter?
- **What charts to produce**: Histogram of revenue? Bar chart by region?
- **What the report should focus on**: Trends? Outliers? Group comparisons?

### Step 4: Generate the agent prompt

Based on your config, craft a prompt like:

> "Load the file at /path/to/my_data.csv. Profile it to assess quality.
> The key columns are [revenue, region, date]. Clean missing values in
> revenue using mean imputation. Run descriptive statistics on revenue
> and compare across regions. Create a histogram of revenue and a bar
> chart by region. Generate a standard report focusing on regional
> performance differences."

Or more simply:

> "Process my data according to the config at /path/to/my_config.json"

## Example: Sales Data Analysis

```json
{
  "scenario_name": "sales_regional_analysis",
  "mode": "real_data",
  "input": {
    "file_path": "/Users/me/data/sales_2024.csv",
    "description": "Q4 2024 sales data. Goal: understand regional revenue patterns."
  },
  "pipeline": [
    "magic-data-loading", "magic-data-profiling", "magic-data-cleaning",
    "magic-statistical-analysis", "magic-data-visualization", "magic-report-generation"
  ],
  "expectations": {
    "magic-data-loading": {
      "min_rows": 500,
      "expected_columns": ["date", "product", "revenue", "units", "region"]
    },
    "magic-data-cleaning": {
      "expected_issues": ["missing_values"],
      "strategy": "mean"
    },
    "magic-statistical-analysis": {
      "target_columns": ["revenue", "units"],
      "tests": ["descriptive", "correlation"]
    },
    "magic-data-visualization": {
      "charts": [
        {"type": "histogram", "column": "revenue"},
        {"type": "bar", "column": "region"}
      ]
    },
    "magic-report-generation": {
      "template": "standard",
      "focus": "Regional revenue differences and top-performing products"
    }
  },
  "verification": {
    "output_files": [
      {"pattern": "ckpt_*.csv", "description": "Cleaned data"},
      {"pattern": "*.png", "description": "Charts"},
      {"pattern": "*report*.md", "description": "Report"}
    ],
    "quality_gates": {
      "min_rows_after_cleaning": 450,
      "max_missing_pct_after_cleaning": 0
    }
  }
}
```

## Verification

After the agent completes, verify outputs:

```bash
python tests/e2e/verify_scenario.py \
  --config my_config.json \
  --workspace /path/to/agent/workspace
```

## Tips

- **Start small**: Test with a subset of your data first (1000 rows)
- **Be specific**: Vague expectations produce vague results
- **Iterate**: Run once, check outputs, refine config, run again
- **Quality gates matter**: Set `min_rows_after_cleaning` to catch aggressive row dropping
- **The agent can't read your mind**: If you need a specific chart type or cleaning strategy, say so explicitly in the prompt or config
