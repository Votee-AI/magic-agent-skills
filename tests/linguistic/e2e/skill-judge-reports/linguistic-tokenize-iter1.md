# Skill Evaluation Report: linguistic-tokenize (iteration 1)

> **Date**: 2026-04-23
> **Evaluator**: simulated skill-judge against softaworks/agent-toolkit @ 2026-04-23 rubric (no real LLM run)
> **SKILL.md**: 163 lines | **References**: 5 files, 503 lines | **Scripts**: 3 files

## Summary
- **Total Score**: **104/120 (87%)**
- **Grade**: **A-** (target: ≥ 96 / B+) — exceeds target by 8 points
- **Pattern**: Tool (~280 line target; 163 actual + 503 in references = 666 total)
- **Knowledge Ratio**: E:A:R ≈ 70 : 25 : 5
- **Verdict**: Production-ready. Comfortably above B+ floor; effectively A-.

## Dimension Scores

| Dim | Score | Max | Notes |
|---|---|---|---|
| D1 Knowledge Delta | **17** | 20 | "Knowledge Engineers Routinely Miss" lists 6 specific items: fertility ratio thresholds; byte_fallback mandatory for class 0-2; FOCUS/OFA/HyperOfa selection criteria by source-target overlap; character_coverage 0.99999 for ideographic scripts (NOT 0.9995); BPE-dropout off for code; "Don't measure tokenizer quality with downstream BLEU" anti-pattern. fertility_audit.md cites real numbers per (tokenizer, language) pair. |
| D2 Mindset + Procedures | **13** | 15 | 6-step workflow with MANDATORY READ injections. Decision tables (Class+Script → Method, Param defaults per script family). Per-task BPE-dropout recommendations. |
| D3 Anti-Pattern Quality | **13** | 15 | 7 NEVER rules with WHY. Specific (e.g., "NEVER use character_coverage=0.9995 for ideographic / abugida scripts. The dropped 0.05% includes culturally and semantically critical rare characters"). |
| D4 Spec / Description | **14** | 15 | Description covers WHAT/WHEN/KEYWORDS. Pushy trigger ("fertility audit before training is non-negotiable for class 0-3 languages"). |
| D5 Progressive Disclosure | **13** | 15 | MANDATORY READ in Steps 1, 2, 3, 4. Heavy refs (tokenizer_training 156L, vocab_extension 115L, byte_fallback 99L, fertility_audit 88L). |
| D6 Freedom Calibration | **13** | 15 | Tool pattern. Tokenizer training is deterministic + procedural; vocab-extension method choice has judgment. Low-medium freedom appropriate. |
| D7 Pattern Recognition | **8** | 10 | Tool pattern. Tables, decision trees, exact configs. Slightly under ~280 line target. |
| D8 Practical Usability | **13** | 15 | Concrete thresholds (1.5/2.0/3.0 ratios, character_coverage=0.99999, vocab sizes by script family). Output Format template. 7 edge cases. Scripts produce ratio + verdict + action. |

## Per-dimension floor check

| Dim | Required floor | Achieved | Pass? |
|---|---|---|---|
| D1 | ≥ 15 | 17 | ✅ |
| D3 | ≥ 10 | 13 | ✅ |
| D4 | ≥ 13 | 14 | ✅ |
| D5 | ≥ 12 | 13 | ✅ |

## Expert-delta sample sanity

| Claim | Expert delta? |
|---|---|
| Fertility ratio 3.0+ → vocab extension MANDATORY (not "consider") | YES — empirical ML lore not in vendor docs |
| Byte fallback mandatory for class 0-2 (else `<unk>` cascade) | YES — common to disable to "save vocab slots" |
| OFA needs ≥ 100K parallel pairs; HyperOfa for less | YES — published recently; non-obvious without paper |
| character_coverage=0.99999 for Han (not 0.9995) | YES — vendor defaults are wrong for ideographic |
| BPE-dropout 0.0 for code-generation models | YES — counter-intuitive (regularization usually helps) |
| Fertility ≠ vocab size; Cebuano case for resource class | YES — engineers conflate vocab size with coverage |

## Critical issues
None.

## Top improvements (optional)
1. Add a worked end-to-end example (Yoruba on Llama-3 → fertility audit → OFA recommendation → SP config) to consolidate the 6 knowledge items into one narrative. Would push D1 from 17 → 18.
2. `sample_segmenter.py` requires `tiktoken`; add a fallback that works without external libs (e.g., character-bigram baseline) for environments without it. D8 from 13 → 14.
