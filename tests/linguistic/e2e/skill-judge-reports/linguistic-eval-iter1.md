# Skill Evaluation Report: linguistic-eval (iteration 1)

> **Date**: 2026-04-23 | **SKILL.md**: 184 lines | **References**: 6 files (incl. cross-ref stub) | **Scripts**: 3 files | **Evals**: 5 (A-tier)
> **Total Score**: **108/120 (90%)** | **Grade**: **A−** (target ≥ 102 / A-; +6) | Per-dim floors: ✅
> **Verdict**: Production-ready A−. Eval is the orchestrator's terminal specialist; weak content cascades into all release decisions, so this had to land cleanly.

| Dim | Score | Notes |
|---|---|---|
| D1 Knowledge Delta | 18/20 | 7 specific items: BLEU pathological for MRL, COMET coverage variance, GEMBA-MQM as cheap LLM-judge alternative, FLORES-200 in pretrains (lower bound only), per-stratum stratification mandatory, English BLiMP non-transferable, cross-direction non-comparability. Also catches the WER-on-space-less trap. |
| D2 Mindset + Procedures | 14/15 | 7-step workflow + per-task metric matrix + per-class benchmark recommendations + per-stratum reporting protocol. Strong cross-skill cooperation explicit. |
| D3 Anti-Pattern Quality | 14/15 | 8 NEVERs with WHY (BLEU-on-MRL, COMET-without-coverage-check, FLORES-without-contamination, English-BLiMP-verbatim, aggregate-without-stratum, cross-direction-aggregation, parser-F1-as-grammar, WER-on-space-less). |
| D4 Description | 14/15 | WHAT/WHEN/KEYWORDS comprehensive. Pushy trigger ("**The orchestrator's pipeline doesn't close without this**"). |
| D5 Progressive Disclosure | 14/15 | MANDATORY READ at Steps 2, 3, 4, 5; references substantial (~80L+95L+45L+50L+40L). Cross-skill cross-reference handled via stub redirect (avoids duplicating linguistic-corpus contamination methodology). |
| D6 Freedom Calibration | 13/15 | Tool pattern. Concrete recipes per (language, task) pair. |
| D7 Pattern Recognition | 8/10 | Tool pattern. |
| D8 Practical Usability | 13/15 | 3 working scripts (benchmark_advisor produces structured JSON; metric_advisor handles MRL detection + COMET coverage; contamination_check has cached model-cutoff table). Output Format template. 7 edge cases. |

## Why this hits A− cleanly

Evaluation knowledge is operational + non-obvious + high-cost-if-wrong. Engineers routinely report BLEU on Turkish, miss FLORES contamination, aggregate Arabic across MSA + dialects. Each item in the "Knowledge Engineers Routinely Miss" list is a real production trap. The pushy A-tier framing ("doesn't close without this") + 5 evals (high-risk convention) reflect that this is the leverage point.
