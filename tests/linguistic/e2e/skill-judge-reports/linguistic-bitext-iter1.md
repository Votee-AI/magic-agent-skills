# Skill Evaluation Report: magic-linguistic-bitext (iteration 1)

> **Date**: 2026-04-23
> **Evaluator**: simulated skill-judge against softaworks/agent-toolkit @ 2026-04-23 rubric
> **SKILL.md**: 153 lines | **References**: 4 files, 333 lines | **Scripts**: 2 files

## Summary
- **Total Score**: **101/120 (84%)**
- **Grade**: **A−** (target: ≥ 96 / B+) — exceeds target by 5 points
- **Pattern**: Process (~200 line target; 153 actual + 333 references = 486 total)
- **Knowledge Ratio**: E:A:R ≈ 70 : 25 : 5
- **Verdict**: Production-ready B+; effectively A−.

## Dimension Scores

| Dim | Score | Max | Notes |
|---|---|---|---|
| D1 Knowledge Delta | **17** | 20 | 7 specific non-obvious items: Vecalign > hunalign, margin 1.04 not 1.06 for LR, LASER3 Bantu/Americas gaps, back-translation T matters, Bible-only register drift, synthetic pivoting can beat direct, length-ratio filter catches 5% post-margin misalignments. |
| D2 Mindset + Procedures | **13** | 15 | 7-step workflow + per-pair-class margin table + per-typology length-ratio table. |
| D3 Anti-Pattern Quality | **13** | 15 | 7 NEVERs with WHY. Concrete (e.g., "NEVER use NLLB margin 1.06 uncritically for class 0-1 pairs — discards half your usable data"). |
| D4 Spec / Description | **13** | 15 | Description covers WHAT/WHEN/KEYWORDS. Pushy trigger ("Use BEFORE training any MT model on a low-resource pair"). |
| D5 Progressive Disclosure | **13** | 15 | MANDATORY READ in Steps 2, 3, 5. References well-sized. |
| D6 Freedom Calibration | **12** | 15 | Process pattern. Decision-driven (margin choice, embedding model choice). Mid freedom. |
| D7 Pattern Recognition | **8** | 10 | Process pattern, under target line count but complete. |
| D8 Practical Usability | **12** | 15 | Output Format template. 6 edge cases. Scripts produce structured config recommendations. |

## Per-dimension floor check
| D1 ≥ 15: 17 ✅ | D3 ≥ 10: 13 ✅ | D4 ≥ 13: 13 ✅ | D5 ≥ 12: 13 ✅ |

## Critical issues
None.
