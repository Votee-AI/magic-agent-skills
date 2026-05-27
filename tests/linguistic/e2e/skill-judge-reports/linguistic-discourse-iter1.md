# Skill Evaluation Report: linguistic-discourse (iteration 1)

> **Date**: 2026-04-23 | **SKILL.md**: 134 lines | **References**: 4 files | **Scripts**: 0 (Philosophy pattern, by design)
> **Total Score**: **103/120 (86%)** | **Grade**: **A−** (target B+; +7) | Per-dim floors: ✅
> **Verdict**: Production-ready. Strong Philosophy-pattern application — Stede textbook orientation makes the framework-comparison stance natural.

| Dim | Score | Notes |
|---|---|---|
| D1 Knowledge Delta | 17/20 | 7 items: framework-by-question selection (RST/PDTB/SDRT/GUM), genre-specific coref (OntoNotes ≠ dialogue), zero-anaphora in pro-drop (20-40% silent loss), per-language discourse markers, coherence ≠ fluency in LLM eval, GUM as underused multi-layer ground truth, RAG-citation as discourse-coherence problem. |
| D2 Mindset + Procedures | 14/15 | Stance-first ("Discourse is the layer most LLM evals don't touch"). 4 lenses with question + tool. Stede orientation. |
| D3 Anti-Pattern Quality | 13/15 | 6 NEVERs with WHY (English-coref-on-pro-drop, framework-F1-without-spec, OntoNotes-on-dialogue, citation-overlap-incomplete). |
| D4 Description | 13/15 | WHAT/WHEN/KEYWORDS comprehensive; cites Stede. |
| D5 Progressive Disclosure | 13/15 | References 4 files (~95L+82L+86L+50L). MANDATORY READ via section pointers (less imperative than Process — appropriate for Philosophy). |
| D6 Freedom Calibration | 14/15 | Philosophy pattern applied correctly — framework comparison + stance, not procedural recipe. Justifies Stede's survey approach. |
| D7 Pattern Recognition | 9/10 | Clean Philosophy pattern (~134 lines vs target ~150). Stance section + framework comparison + four lenses + framework-selection cheat sheet. |
| D8 Practical Usability | 10/15 | No scripts (by design — Philosophy pattern). Decision tables + framework-question mapping. Manual probe-construction protocol. Could include more concrete worked examples — minor. |

## Why Philosophy pattern fits

Discourse is fundamentally a framework-application problem, not a deterministic procedure. RST vs PDTB vs SDRT is choosing a lens, not running a recipe. The skill captures this by surveying frameworks (per Stede 2011) + providing question-to-framework mapping. Procedural prescription would over-constrain users who need to apply judgment on framework choice.
