# Scenario: Self-Healing

## Mode: Synthetic (Automated)

Three datasets that trigger self-healing behavior:
1. `datasets/latin1_encoded.csv` - Latin-1 encoded file (non-UTF-8)
2. `datasets/mixed_types.csv` - "N/A" and "unknown" in numeric columns
3. `datasets/semicolon_delimited.csv` - Semicolon-delimited CSV

## Self-Healing Test 1: Encoding Error

### User Prompt
"Load and analyze the file at datasets/latin1_encoded.csv"

### Expected Behavior
1. Agent runs `load_file.py` with default encoding (UTF-8)
2. Script fails or produces garbled output
3. Agent runs `detect_format.py` to identify encoding
4. Agent re-runs `load_file.py` with `--encoding latin-1`
5. Load succeeds with correct data

### Verification
- [ ] Agent detected the encoding issue
- [ ] Agent used detect_format.py or read error to diagnose
- [ ] Agent retried with correct encoding parameter
- [ ] Final load succeeded with correct row count (500 rows)

## Self-Healing Test 2: Mixed Type Column

### User Prompt
"Clean the numeric columns in datasets/mixed_types.csv and compute statistics"

### Expected Behavior
1. Agent loads the data (loads successfully but with mixed types)
2. Agent runs detect_issues.py to find type problems
3. Agent cleans mixed types (replaces "N/A"/"unknown"/"null" with NaN)
4. Agent runs statistics on cleaned data

### Verification
- [ ] Agent identified mixed type columns
- [ ] Agent applied cleaning before statistics
- [ ] Final statistics computed successfully

## Self-Healing Test 3: Unusual Delimiter

### User Prompt
"Load and profile datasets/semicolon_delimited.csv"

### Expected Behavior
1. Agent runs `load_file.py` with default comma delimiter
2. Loads as 1 column (wrong structure)
3. Agent notices anomaly or runs `detect_format.py`
4. Agent re-runs `load_file.py` with `--delimiter ";"`
5. Load succeeds with correct 8 columns

### Verification
- [ ] Initial load produced wrong structure
- [ ] Agent detected the delimiter issue
- [ ] Agent retried with correct delimiter
- [ ] Final load has 8 columns, 800 rows

## Programmatic Test
```bash
python tests/e2e/generate_e2e_data.py
python tests/e2e/scenario_runner.py \
  --scenario self_healing \
  --input tests/e2e/datasets \
  --workspace /tmp/e2e_self_healing
python tests/e2e/verify_scenario.py \
  --scenario self_healing \
  --workspace /tmp/e2e_self_healing
```
