# Scenario: Text Data Analysis

## Input
- File: `datasets/text_corpus.jsonl`
- Description: 200 text documents with id, text (paragraphs), and label (4 categories). JSONL format.

## User Prompt
"Load the JSONL text corpus at datasets/text_corpus.jsonl. Profile the text columns, analyze vocabulary and text length distributions, compare text statistics across the label groups, create visualizations of word frequencies and text length, and generate a report summarizing your findings."

## Expected Behavior
1. Agent activates `data-loading` skill, runs `detect_format.py` (detects JSONL) then `load_file.py` → `ckpt_01_loaded.csv`
2. Agent activates `magic-data-profiling` skill, runs `distribution_analysis.py` → detects text columns, reports word count and vocabulary distributions
3. Agent activates `data-exploration` skill, runs `segment_analysis.py` with `--group_col label` → compares text stats across label groups
4. Agent activates `data-visualization` skill, generates word frequency bar chart and text length histogram
5. Agent activates `report-generation` skill, generates report with text-specific findings

## Success Criteria
- [ ] JSONL format detected and loaded correctly
- [ ] Text columns identified (not treated as numeric)
- [ ] Word count statistics reported (mean, median, min, max)
- [ ] Vocabulary size reported per text column
- [ ] Top 20 terms identified
- [ ] Segment analysis compares groups by text metrics
- [ ] Visualizations include text-appropriate charts (word frequency bars, text length histogram)
- [ ] Report includes text-specific findings with uncertainty language
- [ ] No numeric statistics (mean, std) applied to text content

## Verification Script
```bash
python tests/e2e/verify_scenario.py \
  --scenario text_analysis \
  --workspace /path/to/workspace \
  --checks tests/e2e/expected/text_analysis_checks.json
```
