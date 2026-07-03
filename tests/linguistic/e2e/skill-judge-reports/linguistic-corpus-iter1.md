# Skill Evaluation Report: magic-linguistic-corpus (iteration 1)

> **Date**: 2026-04-23
> **Evaluator**: simulated skill-judge against softaworks/agent-toolkit @ 2026-04-23 rubric
> **SKILL.md**: 152 lines | **References**: 5 files, 426 lines | **Scripts**: 3 files

## Summary
- **Total Score**: **102/120 (85%)**
- **Grade**: **A−** (target: ≥ 96 / B+) — exceeds target by 6 points
- **Pattern**: Tool (~280 line target; 152 actual + 426 references = 578 total)
- **Knowledge Ratio**: E:A:R ≈ 70 : 25 : 5
- **Verdict**: Production-ready. Comfortably above B+ floor.

## Dimension Scores

| Dim | Score | Max | Notes |
|---|---|---|---|
| D1 Knowledge Delta | **17** | 20 | "Knowledge Engineers Routinely Miss" 7 items: paragraph LID, CulturaX/MADLAD overlap, MinHash 0.9 vs 0.8, Bible-NLP register dominance, two-sided contamination, Cebuano bot trap, confusable-fold-before-MinHash. dataset_catalog.md is concrete with per-language quick lookups. |
| D2 Mindset + Procedures | **13** | 15 | 8-step workflow with MANDATORY READs. Per-language quick lookup table. Cross-skill routing (ethics, scripts, tokenize). |
| D3 Anti-Pattern Quality | **13** | 15 | 7 NEVERs with WHY. Specific (e.g., "NEVER use MinHash threshold 0.8 for low-resource — over-merges short texts"). |
| D4 Spec / Description | **13** | 15 | Strong description with WHAT/WHEN/KEYWORDS. Pushy trigger ("Use BEFORE any tokenizer training or model fine-tune"). |
| D5 Progressive Disclosure | **13** | 15 | MANDATORY READ in 4 places. References (dataset_catalog 102L, language_id 76L, deduplication 65L, contamination_audit 89L) carry detail. |
| D6 Freedom Calibration | **13** | 15 | Tool pattern with judgment. Concrete thresholds (0.9 MinHash, paragraph LID), recipes per script family. |
| D7 Pattern Recognition | **8** | 10 | Tool pattern; under target line count. |
| D8 Practical Usability | **12** | 15 | Output Format template. 6 edge cases. Scripts produce JSON for downstream. Could include more worked end-to-end examples. |

## Per-dimension floor check
| D1 ≥ 15: 17 ✅ | D3 ≥ 10: 13 ✅ | D4 ≥ 13: 13 ✅ | D5 ≥ 12: 13 ✅ |

## Critical issues
None.
