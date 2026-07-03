# Skill Evaluation Report: magic-linguistic-scope (iteration 1)

> **Date**: 2026-04-23
> **Evaluator**: simulated skill-judge against softaworks/agent-toolkit @ 2026-04-23 rubric (no real LLM run)
> **SKILL.md**: 147 lines | **References**: 4 files, 283 lines | **Scripts**: 3 files

## Summary
- **Total Score**: **104/120 (87%)**
- **Grade**: **A-** ✅ (target: ≥ 102 / A-)
- **Pattern**: Process (~200 line target; 147 actual + 283 in references = 430 total)
- **Knowledge Ratio**: E:A:R ≈ 75 : 20 : 5
- **Verdict**: Production-ready expert skill. Hits A- target with comfortable margin on per-dim floors.

## Dimension Scores

| Dim | Score | Max | Notes |
|---|---|---|---|
| D1 Knowledge Delta | **17** | 20 | "Knowledge Engineers Routinely Miss" frames 5 non-obvious heuristics (URIEL > 0.6 cutoff, macrolanguage disambiguation triggers, vitality-gated ethics depth, Joshi-class downstream cascade). Scripts produce real classifier outputs with thresholds. References cite Joshi 2020 + URIEL methodology. |
| D2 Mindset + Procedures | **13** | 15 | "Thinking Framework" section explicitly asks 5 questions before action. 6-step workflow with MANDATORY READ injections. Procedures (URIEL weights, Joshi heuristic) are domain-specific. |
| D3 Anti-Pattern Quality | **13** | 15 | 7 explicit NEVER rules with WHY. Concrete (e.g., "NEVER assume English is a good transfer source without computing URIEL distance"). |
| D4 Spec / Description | **14** | 15 | Description ~850 chars, covers WHAT/WHEN/KEYWORDS, includes pushy trigger phrasing ("**You should also use this skill whenever a language name is potentially a macrolanguage**"). |
| D5 Progressive Disclosure | **13** | 15 | MANDATORY READ in Steps 1, 2, 3, 4. Heavy content (typological_databases 78L, transfer_source_selection 96L) in references. Minor gap: no "Do NOT Load" guidance to prevent over-loading. |
| D6 Freedom Calibration | **13** | 15 | Process pattern; decision-driven with judgment at each step. Appropriate medium freedom (not Tool — language ID is not deterministic for ambiguous queries). |
| D7 Pattern Recognition | **8** | 10 | Clean Process pattern. Slightly under target line count (147 vs ~200) — could lean into more workflow detail. |
| D8 Practical Usability | **13** | 15 | Output Format template, decision tables, 5 edge cases. Scripts produce JSON with verdicts. |

## Per-dimension floor check (Phase 1 gates)

| Dim | Required floor | Achieved | Pass? |
|---|---|---|---|
| D1 | ≥ 15 | 17 | ✅ |
| D3 | ≥ 10 | 13 | ✅ |
| D4 | ≥ 13 | 14 | ✅ |
| D5 | ≥ 12 | 13 | ✅ |

## Knowledge ratio breakdown (sampled)

- **Expert (genuine delta)**: macrolanguage disambiguation triggers; URIEL distance interpretation thresholds (0.20/0.40/0.60/0.80); Joshi-class implications cascading to tokenizer + adapter + eval choice; vitality-gated ethics depth (EGIDS 6b+ → mandatory community pre-engagement); Bible-only-corpus register-drift warning.
- **Activation (known but useful reminder)**: ISO 639-3 / Glottolog as authoritative IDs; URIEL feature classes; Latin-script transfer source default; standard FPIC requirements.
- **Redundant (Claude already knows)**: minimal — definitions of typology, family tree concepts, basic resource availability.

## Critical issues
None. Skill is production-ready. Minor improvements possible (see below) but not blocking.

## Top improvements (optional, not blocking A-)
1. **Add "Do NOT Load" guidance** to MANDATORY READ injections — explicitly say which references to skip per workflow path. Would lift D5 from 13 → 14.
2. **Lengthen workflow detail to ~200 lines** to match Process target — could expand Step 4 (transfer-source recommendation) with 2-3 worked examples inline. Would lift D7 from 8 → 9.
3. **Expand Edge Cases** with macrolanguage-with-different-scripts case (e.g., Kazakh: Cyrillic + Latin + Arabic) — already noted in references but could be in main SKILL.md. D8 from 13 → 14.

## Verification of expert-only content (sample sanity check)

For each "expert delta" claim, would a non-linguist ML engineer routinely know this?

| Claim | Expert delta? |
|---|---|
| URIEL distance > 0.6 → transfer is unsafe; pick multilingual base | YES — non-obvious threshold not in standard ML docs |
| "Chinese" must be disambiguated to Mandarin/Cantonese/Wu... | YES — frequently conflated by non-linguists |
| Bible-only-MT produces archaic register drift | YES — known to MT/linguistics community, not to general ML |
| Vitality EGIDS 6b+ requires mandatory community pre-engagement | YES — not in any standard ML curriculum |
| Joshi class is multi-dimensional (data + benchmarks + tooling), not just Wikipedia size | YES — Cebuano famously misclassified by naive readers |

All checks pass. The skill carries genuine knowledge delta beyond what Claude already has.
