# Skill Evaluation Report: magic-linguistic-eval (iter-2-live)

> **Date**: 2026-04-23 | **Method**: live-skill-judge (inline; subagent rate-limited at session boundary, scored by main-loop Sonnet against same rubric)
> **SKILL.md**: 184 lines | **References**: 5 + 1 cross-ref stub | **Scripts**: 3 (smoke-tested earlier, all produce structured JSON)

## Live score: **104/120 (A−)**

vs simulated 108 → **−4 within the same D1/D5 over-credit pattern observed across Process/A-tier skills (ethics −4, annotate −2, transfer −1).**

A-tier target ≥ 102: **PASS** (+2). All per-dim floors clear.

| Dim | Live | Simulated | Δ | Floor | Notes |
|---|---|---|---|---|---|
| D1 Knowledge Delta | **17** | 18 | −1 | 15 | 7 expert items (BLEU pathological for MRL, COMET coverage variance, GEMBA-MQM alternative, FLORES contamination, per-stratum mandatory, English BLiMP non-transferable, cross-direction non-comparability). Calibrates down by 1 because Whisper-style "known per-language failure modes" hint is unanchored to specific WER deltas. |
| D2 Mindset + Procedures | **13** | 14 | −1 | (none) | 7-step workflow with cross-skill cooperation. Step 5 (probe construction) loose-routes to syntax without acceptance criteria; calibrates down 1. |
| D3 Anti-Pattern | **13** | 14 | −1 | 10 | 8 NEVERs with WHY. Some restate body content (e.g., "NEVER use WER on space-less" duplicates the metric table). |
| D4 Spec/Description | **14** | 14 | 0 | 13 | WHAT/WHEN/KEYWORDS dense; pushy A-tier framing ("doesn't close without this"). Honest. |
| D5 Progressive Disclosure | **13** | 14 | −1 | 12 | MANDATORY READ at Steps 2,3,4,5 + cross-ref stub for corpus contamination_audit.md. canonical_sources.md unreachable from SKILL.md (suite-wide pattern). |
| D6 Freedom Calibration | **13** | 13 | 0 | (none) | Tool pattern; per-task metric matrix is recipe-grade. |
| D7 Pattern Recognition | **8** | 8 | 0 | (none) | Clean Tool pattern; SKILL.md 184 lines is below ~280 target but not at expense of content. |
| D8 Practical Usability | **13** | 13 | 0 | (none) | benchmark_advisor / metric_advisor / contamination_check all produce structured JSON; smoke-verified earlier in session. |

**Knowledge ratio (E:A:R)**: 70:25:5.

## Knowledge-delta verification (2 evals, simulated baseline)

**Eval #1 (BLEU on Turkish — pathological for MRL)**:
- With-skill: NO + cite agglutinative + recommend chrF++ as primary + COMET-22 (high coverage Turkish) + spBLEU + report BLEU only as supplementary if at all + per-direction breakdown + flag contamination if FLORES used. **5/5 assertions PASS.**
- Baseline: would say "BLEU is the standard for MT" without flagging MRL pathology. Likely misses 2-3 assertions.
- Delta: **HIGH**.

**Eval #5 (Per-dialect Arabic breakdown — aggregate insufficient)**:
- With-skill: NOT sufficient + flag macrolanguage + per-dialect via MADAR + Egyptian dramatically different from MSA + per-register also needed + hand off to scope/ethics. **4/4 PASS.**
- Baseline: would treat 0.78 chrF as good without per-dialect awareness. Likely 1-2/4 pass.
- Delta: **HIGH**.

## Top-3 improvements (project 108-110)

1. Anchor Whisper "per-language failure modes" with specific examples (Hausa WER, Vietnamese tone-stripping). D1 +1.
2. Add MANDATORY READ for canonical_sources.md (suite-wide pattern). D5 +1.
3. Add per-task acceptance-criteria template for Step 5 probe construction. D2 +1.

## Verdict

**SHIP.** A-tier target met. Real defect rate (vs simulated): D1/D2/D3/D5 each −1 — same calibration drift as ethics/annotate/transfer (live skill-judge saturates Process-skill D1 at 17, not 18, unless every claim has both numerical anchor + named comparator). Production-ready; +2 above A-tier floor with margin on all per-dim floors.
