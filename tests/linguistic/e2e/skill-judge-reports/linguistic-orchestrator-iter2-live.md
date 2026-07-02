# Skill Evaluation Report: magic-linguistic-orchestrator (iteration 2 — LIVE)

> **Date**: 2026-04-23
> **Method**: Live skill-judge (manual rubric application by general-purpose subagent) + simulated knowledge-delta verification on representative ambiguous routing query.
> **Replaces**: `iter-0-bootstrap` PENDING placeholder.
> **SKILL.md**: 221 lines | **References**: 2 files (pipeline_phases.md 95L, routing_logic.md 79L) | **Scripts**: none (orchestrator-appropriate) | **Evals**: none (entry-point skill — structural review only).

## Summary
- **Total Score**: **102/120 (85%)**
- **Grade**: **A-** (target ≥ 102 / A-, at floor; +0)
- **Pattern**: Process (target ~200 lines; 221 actual + 174 references = 395 total)
- **Knowledge Ratio**: E:A:R ≈ 60 : 30 : 10
- **Per-dim floors**: D1 ≥15 ✅, D3 ≥10 ✅, D4 ≥13 ✅, **D5 ≥12 ❌ (11 — one point under)**
- **Verdict**: **ITERATE** — the absolute total clears the A- floor exactly, but the D5 progressive-disclosure floor fails (no MANDATORY READ injections; references exist but are unreferenced from the main file). One focused edit fixes this.

## Dimension Scores

| Dim | Score | Max | Justification (with evidence) |
|---|---|---|---|
| D1 Knowledge Delta | **16** | 20 | Genuine orchestration knowledge: 5-phase mapping rationale (refs L7-15: "linguistic pipeline is data-and-model-shaped, not data-only"); triage tree mapping symptoms→specialist chains (L141-148, e.g. "'garbled output' → scripts→tokenize→eval; script issues silently break downstream"); ELAN→speech→corpus field-data path (L144); Phase Indicators convention (L52-54); NFKC-destroys-Arabic warning (L205). 5-6 expert items vs 7+ in best specialists. Knowledge depth defers (correctly) to specialists. |
| D2 Mindset + Procedures | **13** | 15 | "On First Touch" 4-step procedure (L43-48), "Mid-Pipeline Entry" 4-step recovery (L150-157), per-phase exit criteria (L86, L100, L114, L127), disambiguation procedure ("ONE question, max 4 options, then best-guess", L161-166). Procedures are orchestration-specific. Gap: no labelled "Thinking Framework" header section like specialist skills have. |
| D3 Anti-Pattern Quality | **13** | 15 | 7 NEVERs each with WHY (L201-209): dataset-without-ethics ("community norms"), BLEU-on-MRL ("penalizes morpheme edits"), NFKC-without-policy ("destroys long-s/Arabic"), Joshi-5-assumes-class-0-2-transfer ("vocab+adapter+eval all change"), skip-ethics-in-hurry ("30-sec FPIC saves incidents"), parallel-Analyze-without-confirmation ("expensive over-scope"), overwrite-workspace-without-snapshot. All concrete, all orchestration-specific. |
| D4 Spec / Description | **14** | 15 | Description ~870 chars (L3): WHAT (coordinates 5-phase pipeline + routes specialists), WHEN ("any linguistic/NLP/LLM-for-low-resource-language task"), KEYWORDS (FLORES/Belebele/AfroBench/IndicXTREME/SEACrowd/FLEx/ELAN/Praat/IPA/G2P/BPE/SentencePiece). Pushy trigger expansion: "Use even if the user does not explicitly say 'linguistics' — a target language name (Yoruba, Khmer, Quechua, Cantonese, Twi, ...) is a sufficient trigger." Frontmatter valid; `entry_point: true` metadata signals orchestrator role. |
| D5 Progressive Disclosure | **11** | 15 | **FLOOR FAIL.** References exist and are substantive (pipeline_phases.md 95L, routing_logic.md 79L). However, **the main SKILL.md never injects a MANDATORY READ pointing at them** — Steps 1-4 of "On First Touch" never reference pipeline_phases; Disambiguation section never references routing_logic. Per-phase tables also live entirely in SKILL.md (L75-136) and could be summarized in main with detail in pipeline_phases.md. References are dead-loaded — exist but agent never knows to read them. |
| D6 Freedom Calibration | **13** | 15 | Process pattern, medium-freedom. Constraint where load-bearing (triage tree L141-148 names specific routes), judgment where appropriate ("This is NOT a rigid pipeline — phases overlap and loop back. The orchestrator provides the skeleton; the agent provides the judgment", L73). Mid-pipeline entry (L150-157) explicitly relaxes structure. Calibration matches orchestration role. |
| D7 Pattern Recognition | **9** | 10 | Process pattern hallmarks all present: phase structure, exit criteria per phase, workspace state template (L168-197), mid-pipeline entry, disambiguation procedure. 221 lines slightly above ~200 target but within tolerance. Cleanest Process pattern in the suite. |
| D8 Practical Usability | **13** | 15 | Triage Decision Tree 7 rows symptom→route (L141-148); 5 phase tables with Step/What/Specialist columns; workspace_state.md markdown template (L172-197); 5 edge cases (L213-217: no-workspace, multi-lang, very-high-resource, endangered, user-skips-ethics); Phase Indicator format example (L52-54); "When NOT to Use" carveout (L41). Gap: no end-to-end worked example showing a full routing flow from query→specialist sequence→workspace update. |

## Per-dimension floor check

| Dim | Required floor | Achieved | Pass? |
|---|---|---|---|
| D1 | ≥ 15 | 16 | ✅ |
| D3 | ≥ 10 | 13 | ✅ |
| D4 | ≥ 13 | 14 | ✅ |
| D5 | ≥ 12 | **11** | ❌ |

## Knowledge ratio breakdown (E:A:R ≈ 60:30:10)

- **Expert (genuine delta, ~60%)**: 5-phase rationale (Scope vs Discover/Plan); triage symptom→specialist chains; Phase Indicator convention; NFKC-destroys-Arabic; Bible-register-drift (refs); BLEU-on-MRL primary trap; Joshi cascade; FPIC pre-engagement gate; "script issues silently break downstream" routing principle.
- **Activation (known but useful, ~30%)**: ISO 639-3 / Glottolog as authoritative; 5-phase pipeline names; specialist skill names; standard ethics workflow; per-phase exit criteria; workspace_state.md as memory layer.
- **Redundant (Claude already knows, ~10%)**: definition of pipeline phases; that ELAN/Praat/FLEx are field-data tools; that BLEU exists; basic routing concept.

## Knowledge-delta verification (Step 2)

**Test query**: "My Khmer-trained MT model produces garbled output and weird tokenization. Where do I start?"

**With-skill response** (using triage tree L141 row 1 + routing_logic.md Template 1):
> Phase: Scope→Acquire diagnostic. Khmer is Brahmic abugida (no spaces, complex cluster shaping). Route order: (1) `magic-linguistic-scripts` — verify NFC normalization, ZWNJ/ZWSP audit, Khmer Unicode block (U+1780–U+17FF) confusable check; garbled output is almost always upstream script policy. (2) `magic-linguistic-tokenize` — measure fertility vs English (space-less Brahmic typically 4-6x without preprocessing); audit byte-fallback. (3) `magic-linguistic-eval` — once script+tokenizer fixed, re-measure with chrF++ (NOT BLEU — Khmer is morphologically rich AND space-less; BLEU+WER both degenerate). Phase Indicator: `[Phase: Acquire | Language: Khmer (khm) | Resource Class: 2 | Skills routed: scripts, tokenize, eval]`. Update workspace_state.md.

**Baseline response** (generic ML engineer, no skill):
> Try a different tokenizer, maybe SentencePiece with larger vocab. Check training data quality. Maybe use mBART or NLLB. Garbled output usually means encoding issues — check UTF-8.

**Delta**: With-skill produces correct ordered triage (scripts FIRST per "silently break downstream" rule), names specific specialists, knows Khmer-specific facts (abugida, no spaces, BLEU+WER degeneracy), and enforces workspace hygiene. Baseline misses ordering, routing, MRL metric warning, and Khmer-specific script reasoning.

**Knowledge delta classification**: **HIGH** (≥10 point gap on D1 simulation). The orchestrator's value is the routing chain itself, which a generic engineer doesn't reproduce.

## Critical issues

1. **D5 floor fail (11 vs 12)** — references exist but are never invoked from SKILL.md. This is a structural fix, not a content fix.
2. **Per-phase tables embedded in SKILL.md** (L75-136) bloat the main file when they could live in pipeline_phases.md with summary in main.

## Top 3 improvements (concrete)

1. **Inject MANDATORY READ pointers** (lifts D5 from 11 → 13, clears floor):
   - In "On First Touch" Step 3 ("Identify phase"), add: `> MANDATORY READ: references/pipeline_phases.md before deep phase work`.
   - In "Triage Decision Tree" intro, add: `> MANDATORY READ: references/routing_logic.md for full single-skill trigger table and disambiguation question templates`.
   - In "Mid-Pipeline Entry" Step 1, add: `> MANDATORY READ: references/pipeline_phases.md "Cross-phase: Refinement" section`.

2. **Extract per-phase deep-dive tables to references** (lifts D7 from 9 → 10, brings SKILL.md to ~150 lines):
   - Keep one-liner phase summary + exit criterion in SKILL.md.
   - Move Step/What/Specialist tables into pipeline_phases.md (where they already partially exist).
   - Cross-link with MANDATORY READ.

3. **Add one end-to-end worked example** (lifts D8 from 13 → 14):
   - Walk a query like "build a Yoruba MT model" through scope → ethics → corpus → scripts → tokenize → bitext → transfer → eval, showing the workspace_state.md updates at each hop and at least one disambiguation question.

After these three edits, projected score: 16 + 13 + 13 + 14 + **13** + 13 + **10** + **14** = **106/120 (A-)** with all floors cleared.

## Verdict

**ITERATE** — total score sits at the A- floor (102/120) but the D5 floor fails by 1 point. References are well-written but architecturally orphaned. Three focused edits (MANDATORY READ injection, table relocation, one worked example) lift the skill cleanly into A- territory at 106/120 with all floors satisfied. Skill is functionally usable today (the simulated routing test confirms HIGH knowledge delta on a realistic ambiguous query) but does not meet the suite's structural quality bar without a second pass.
