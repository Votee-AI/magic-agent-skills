# Skill Evaluation Report: magic-linguistic-transfer (iteration 1)

> **Date**: 2026-04-23
> **Evaluator**: simulated skill-judge against softaworks/agent-toolkit @ 2026-04-23 rubric
> **SKILL.md**: 165 lines | **References**: 5 files, 472 lines | **Scripts**: 2 files | **Evals**: 5 (high-risk tier)

## Summary
- **Total Score**: **106/120 (88%)**
- **Grade**: **A−** (target: ≥ 96 / B+) — exceeds target by 10 points
- **Pattern**: Process (~200 line target; 165 actual + 472 references = 637 total)
- **Knowledge Ratio**: E:A:R ≈ 75 : 22 : 3
- **Verdict**: Strong A−. The integration knowledge is unusually concrete here (LoRA rank vs URIEL distance is rarely codified this directly).

## Dimension Scores

| Dim | Score | Max | Notes |
|---|---|---|---|
| D1 Knowledge Delta | **18** | 20 | 7 specific items: LoRA rank scales with typology not data, CP needs ≥ 1B target tokens, Unsloth 2× faster than LLaMA-Factory single-GPU, source-mix 10-20% mandatory, MAD-X stacking is for multilingual+multi-task only, vocab-extension method must align with transfer choice, attention-only LoRA loses 2-5 BLEU on hard pairs. The attention-only-vs-all-linear advice for distant pairs is non-obvious and not in standard PEFT docs. |
| D2 Mindset + Procedures | **14** | 15 | 7-step workflow + decision matrices (approach by class+data, LoRA config by URIEL, tool by setup). Cross-skill cooperation explicit. |
| D3 Anti-Pattern Quality | **14** | 15 | 8 NEVERs with WHY. Catches the most expensive mistakes (e.g., "NEVER use LoRA r=4 for typologically-distant pairs — model can't represent the adaptation"). |
| D4 Spec / Description | **14** | 15 | Description WHAT/WHEN/KEYWORDS comprehensive. Pushy trigger ("**Use BEFORE running training jobs**"). |
| D5 Progressive Disclosure | **14** | 15 | MANDATORY READ in Steps 2, 3, 4, 5. Heavy references (adapter_patterns 100L, finetuning_recipes 120L, source_selection 78L, forgetting_mitigation 90L). |
| D6 Freedom Calibration | **13** | 15 | Process pattern. Strong decision support; appropriate mid-low freedom. |
| D7 Pattern Recognition | **8** | 10 | Process pattern. |
| D8 Practical Usability | **11** | 15 | Output Format template. 6 edge cases. lora_config_advisor produces concrete JSON. Some users may want even more worked recipes — minor gap. |

## Per-dimension floor check
| D1 ≥ 15: 18 ✅ | D3 ≥ 10: 14 ✅ | D4 ≥ 13: 14 ✅ | D5 ≥ 12: 14 ✅ |

## Critical issues
None.

## Why transfer scored highest of Phase 2

Transfer-learning knowledge ("rank scales with distance not data", "Unsloth vs LLaMA-Factory tradeoff") is documented across many papers/tools but rarely synthesized into actionable recommendations with concrete thresholds. The skill carries genuine integration-knowledge delta — Claude has seen LoRA paper and PEFT docs but rarely sees them combined with URIEL distance and Joshi class to produce a single-sentence recommendation. The 18/20 D1 reflects this synthesis value.
