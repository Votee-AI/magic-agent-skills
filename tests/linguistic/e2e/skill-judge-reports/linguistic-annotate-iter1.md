# Skill Evaluation Report: linguistic-annotate (iteration 1)

> **Date**: 2026-04-23 | **SKILL.md**: 165 lines | **References**: 5 files | **Scripts**: 2 files (incl. working IAA calculator)
> **Total Score**: **105/120 (88%)** | **Grade**: **A−** (target B+; +9) | Per-dim floors: ✅
> **Verdict**: Production-ready. Strong D1 (annotation methodology rarely codified this concretely for ML).

| Dim | Score | Notes |
|---|---|---|
| D1 Knowledge Delta | 18/20 | 8 specific items: Cohen κ skew failure mode, Krippendorff α for missing/ordinal, γ for spans, threshold + bootstrap CI, adjudication required not optional, calibration cost asymmetry, AL diversity > uncertainty for LR, single-annotator-gold = no gold. |
| D2 Mindset + Procedures | 14/15 | 6-step workflow + per-task IAA decision matrix + per-resource AL strategy. Concrete protocols. |
| D3 Anti-Pattern Quality | 14/15 | 8 NEVERs with WHY. Specific (e.g., "NEVER use Cohen κ on highly skewed classes — use PABAK"). |
| D4 Description | 14/15 | WHAT/WHEN/KEYWORDS comprehensive. Pushy trigger. |
| D5 Progressive Disclosure | 14/15 | MANDATORY READ at Steps 1, 3, 4, 5; references substantial (95L+108L+86L+70L+56L = 415L). |
| D6 Freedom Calibration | 13/15 | Process pattern; appropriate. |
| D7 Pattern Recognition | 8/10 | Process pattern. |
| D8 Practical Usability | 10/15 | Working IAA calculator (Cohen κ + Fleiss + PABAK + bootstrap CI) — concrete tool. Adjudication workflow detailed. Could include more tooling-specific config templates. |

## Why this scored highest of Phase 3a

Annotation methodology + IAA is rarely codified concretely in ML literature. The skill captures empirical practitioner knowledge (κ skew failure modes, calibration cost asymmetry, span vs nominal metric choice) that takes years to learn from doing. The working `iaa_calculator.py` with bootstrap CI is a real artifact, not just advisory.
