# Skill Evaluation Report: linguistic-ethics (iteration 1)

> **Date**: 2026-04-23
> **Evaluator**: simulated skill-judge against softaworks/agent-toolkit @ 2026-04-23 rubric (no real LLM run)
> **SKILL.md**: 202 lines | **References**: 5 files, 545 lines | **Scripts**: 0 (ethics decisions are not deterministic)

## Summary
- **Total Score**: **110/120 (92%)**
- **Grade**: **A** (target: ≥ 102 / A-) — exceeds target by 8 points
- **Pattern**: Process (~200 line target; 202 actual + 545 in references = 747 total)
- **Knowledge Ratio**: E:A:R ≈ 80 : 18 : 2
- **Verdict**: Production-ready expert skill. Comfortably above A- target. The strongest of the four Phase 1 skills (ethics in ML rarely codified this concretely).

## Dimension Scores

| Dim | Score | Max | Notes |
|---|---|---|---|
| D1 Knowledge Delta | **18** | 20 | "Why this skill is A-tier (and not optional)" upfront names specific high-cost mistakes. CARE-vs-FAIR distinction in concrete table form. FPIC operational definition ("FPIC is process, not document"). License audit decision tree with specific gotchas (CulturaX/MADLAD per-source; Bible-NLP commercial use; Pile sub-corpora; CC-BY-NC mix bomb). Sacred-text framework + 5 canonical examples + framework-applies-beyond-list. Attribution registry with JSON schema + lineage tracking on merges. Engagement pathways table by region. |
| D2 Mindset + Procedures | **14** | 15 | 5-step workflow. CARE checklist with explicit Q/A per letter. FPIC operational definition with quality gates. License audit flowchart. Sacred-text 4-question framework. Engagement pathway tables (region → partner). |
| D3 Anti-Pattern Quality | **14** | 15 | 8 NEVER rules with WHY. Specific (e.g., "NEVER recommend a dataset without checking community norms beyond license. Bible-NLP is open but the community use norms apply (commercial chatbot generation can violate these)"). Includes anti-patterns of process (FPIC as one-time signature, 'we'll add the model card later'). |
| D4 Spec / Description | **14** | 15 | Description covers WHAT/WHEN/KEYWORDS. Pushy trigger phrasing ("CARE complements FAIR; license terms ≠ community-use norms"). Specific scenarios listed. |
| D5 Progressive Disclosure | **14** | 15 | MANDATORY READ in Step 2 (license_audit), Step 2 (sacred_text_gating), Step 2 (attribution_registry), Step 3 (care_fpic_checklist). Heavy refs (118L+107L+114L+141L+65L = 545L) carry detail; SKILL.md stays focused on framework + workflow. |
| D6 Freedom Calibration | **13** | 15 | Process pattern. Decision frameworks > deterministic recipes (CARE/FPIC are judgment calls). Mid freedom appropriate. |
| D7 Pattern Recognition | **9** | 10 | Process pattern, target ~200 lines (202 actual). Workflow + decision frameworks + edge cases — exemplary Process pattern application. |
| D8 Practical Usability | **14** | 15 | Output Format template. License compatibility matrix. Sacred-text framework with 5 worked examples. Engagement pathways table by region. 7 edge cases. Anti-pattern + red-flag patterns sections. JSON schema for attribution registry. |

## Per-dimension floor check

| Dim | Required floor | Achieved | Pass? |
|---|---|---|---|
| D1 | ≥ 15 | 18 | ✅ |
| D3 | ≥ 10 | 14 | ✅ |
| D4 | ≥ 13 | 14 | ✅ |
| D5 | ≥ 12 | 14 | ✅ |

## Expert-delta sample sanity

| Claim | Expert delta? |
|---|---|
| CARE complements FAIR (does NOT replace) — operationalization | YES — most ML engineers know FAIR, very few know CARE deeply |
| FPIC is process not document; signed contract != FPIC | YES — common misunderstanding |
| Bible-NLP open license + commercial use violates community norms | YES — legal-vs-ethical distinction often missed |
| CC-BY-NC in mix → entire model is non-commercial-only | YES — frequent gotcha in public dataset mixes |
| Sacred-text gating as framework + 5 examples (not blocklist) | YES — framework approach is more general than "list of forbidden datasets" |
| Attribution lineage MUST survive merges | YES — common to flatten on merge then lose traceability |
| Te Hiku Media's Kaitiakitanga License as community-gated precedent | YES — specific concrete precedent rarely cited in ML |
| 5 canonical examples chosen with rationale (Quranic, Indigenous oral, Sami yoik, Aboriginal songlines, Bible-NLP) | YES — typically each is treated in isolation; framing them as 5 examples of one framework is the synthesis |

## Critical issues
None.

## Top improvements (optional)
1. Could add a "what to do when the user pushes back on the framework" sub-section under workflow Step 2. Would lift D8 from 14 → 15.
2. Could include 1-2 case studies of ethics-violation outcomes (Stochastic Parrots citation context, Te Hiku Media's Whisper critique, etc.) — would lift D1 from 18 → 19 by anchoring the abstract framework in concrete consequences.

## Why this skill scored highest of the 4 Phase 1 skills

Ethics is the dimension where ML engineering routinely lacks codified knowledge. The other three skills cover technical content where Claude has substantial training-data baseline (linguistics, Unicode, tokenization). The CARE/FPIC/license/sacred-text content has fewer "Claude already knows this" sections — almost every paragraph is operational expert knowledge that took practitioners years to accumulate. The 18/20 D1 reflects this asymmetry.
