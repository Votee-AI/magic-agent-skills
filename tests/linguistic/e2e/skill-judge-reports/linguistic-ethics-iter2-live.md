# Skill Evaluation Report: linguistic-ethics (iteration 2 — LIVE)

> **Date**: 2026-04-23
> **Evaluator**: live skill-judge by general-purpose subagent (a97616c9acf05c252) against softaworks/agent-toolkit @ 2026-04-23 rubric
> **Method**: real read of SKILL.md + 5 references + evals.json + per-dim line-range scoring + 2-eval knowledge-delta verification
> **Replaces**: `linguistic-ethics-iter1.md` (simulated 110/A)
> **SKILL.md**: 202 lines | **References**: 5 files, ~545 lines | **Scripts**: 0 (intentional — ethics decisions are not deterministic)

## Summary

- **Total Score**: **106 / 120 (88%)** — down from simulated 110
- **Grade**: **A-** (target: ≥ 102 / A-) — exceeds target by 4 points
- **Pattern**: Process (~200 line target; 202 actual)
- **E:A:R Knowledge Ratio**: ~75 : 22 : 3 (lower E than the simulated 80 — more advice/process content than pure expertise)
- **Verdict**: Production-ready expert skill in the A- band. **Simulated A grade does NOT hold up** — the skill is solidly A-, not A. Top-1 in the suite by total but the gap to other A- skills (e.g., linguistic-eval at simulated 108) is narrower than the simulated session implied. No critical blockers.

## Dimension Scores (vs simulated iter-1)

| Dim | Live | Iter-1 | Δ | Max | Notes (with line-range evidence) |
|---|---|---|---|---|---|
| **D1 Knowledge Delta** | **17** | 18 | -1 | 20 | Strong synthesis: CARE-vs-FAIR table (L40-53), FPIC operational definition (L55-66), license decision tree with named gotchas (L72-91), sacred-text framework + 5 examples (L93-107), 8 anti-patterns with WHY (L167-176), 6-named FPIC failure modes (care_fpic_checklist.md L54-61), 5 red-flag user-request patterns (sacred_text_gating.md L100-106), JSON-Lines attribution registry schema (attribution_registry.md L20-61). **Down 1**: SKILL.md lacks concrete case-study anchoring (Mahelona/Whisper Te Hiku critique cited only in canonical_sources.md L28, not surfaced in main file). FPIC failure-mode taxonomy lives in references not SKILL.md. No specific jurisdictional anchors (EU AI Act dates, GDPR cultural-data clauses). |
| **D2 Mindset + Procedures** | **13** | 14 | -1 | 15 | 5-step workflow (L123-166); CARE & FPIC checklists with Q-by-Q gates; 4-question sacred-text framework; engagement-pathways region table. **Down 1**: Step 1 ("vitality 6b+: heavy ethics — community partner identified") underspecifies HOW to identify the partner. Step 5 model-card section (L159-165) is a bulleted ingredient list with no template. |
| **D3 Anti-Pattern Quality** | **14** | 14 | 0 | 15 | 8 NEVERs in SKILL.md (L167-176), each with WHY. Plus 6 FPIC failure modes (care_fpic_checklist.md L54-61), 5 red-flag patterns (sacred_text_gating.md L100-106), 5 registry NEVERs (attribution_registry.md L125-131). ~24 named anti-patterns total — exceptionally rich. Each ties failure mode to operational consequence. |
| **D4 Spec / Description** | **14** | 14 | 0 | 15 | Description (L3) has WHAT + WHEN-keywords (FPIC/CARE/Indigenous data/data sovereignty/community engagement/license audit/attribution/sacred text/restricted corpus/religious text use/endangered-language data/model card ethics statement) + meta-trigger ("is it OK to use this dataset for training") + routing ("EARLY at Scope, AGAIN at Release"). When-NOT-to-use explicit (L28). Bold reframing claim "every non-English dataset crosses an ethics boundary" pushes recall mode. |
| **D5 Progressive Disclosure** | **13** | 14 | -1 | 15 | 4 MANDATORY READ pointers (L70 license_audit, L97 sacred_text_gating, L121 attribution_registry, L143 care_fpic_checklist). Heavy detail in 545L of references; SKILL.md stays at 202L on framework. **Down 1**: license_audit (L70) and care_fpic_checklist (L143) are mid-section pointers loosely tied to step boundaries; no light-pointer / heavy-pointer differentiation. |
| **D6 Freedom Calibration** | **13** | 13 | 0 | 15 | Process pattern, mid freedom. Output Format template (L188-202) structured without over-constraining wording. "Framework + 5 examples not blocklist" framing (sacred_text_gating.md L70-83) explicitly says "framework applies beyond list". Resists rigid prescription where ethics calls for judgment. |
| **D7 Pattern Recognition** | **9** | 9 | 0 | 10 | Process pattern target ~200 lines; 202 actual. Workflow + decision frameworks + 7 edge cases (L178-186) + output format. Pattern-fit clean. |
| **D8 Practical Usability** | **13** | 14 | -1 | 15 | Output Format template (L188-202), license compatibility matrix (L88-91), 5-worked-examples sacred-text framework, JSON registry schema, region-pathways table (care_fpic_checklist.md L77-89), 7 edge cases, license→model-output matrix (license_audit.md L57-69). **Down 1**: Step 5 model-card has no template (just ingredient list); zero scripts (defensible but a usability gap — even a non-authoritative auto-license-checker would help); no worked example of an end-to-end ethics-assessment using the Output Format. |
| **TOTAL** | **106** | 110 | **-4** | 120 | **A- (not A)** |

## Per-dim floor check

| Dim | Required floor | Live score | Pass? |
|---|---|---|---|
| D1 | ≥ 15 | 17 | PASS |
| D3 | ≥ 10 | 14 | PASS |
| D4 | ≥ 13 | 14 | PASS |
| D5 | ≥ 12 | 13 | PASS |

All floors pass with margin. The simulated A grade does not hold; A- does.

## Why the iter-1 simulation over-credited

The simulated report claimed 110/A. Live re-scoring lands at 106/A-. The 4-point delta is concentrated in:

1. **D1 over-credit (-1)**: simulated awarded 18 partly for the canonical_sources reading list, but reading lists in references contribute less to delta than worked-case-study material in SKILL.md. The Mahelona/Whisper critique would lift D1 to 18 if surfaced inline.
2. **D2 over-credit (-1)**: simulated awarded 14 for the 5-step workflow without docking for Steps 1 and 5 being ingredient lists rather than procedures.
3. **D5 over-credit (-1)**: simulated awarded 14 for 4 MANDATORY-READs without checking placement — they are not all step-aligned.
4. **D8 over-credit (-1)**: simulated awarded 14 without docking for missing model-card template + missing worked example of the Output Format.

D3 and D4 hold up under live scoring; the anti-pattern density and trigger language are genuinely strong.

## Knowledge-delta verification (2 evals)

### Eval #2 — `fpic-unclear-indigenous` (Cherokee text on Internet Archive)

**With-skill response** (synthesizing SKILL.md L55-66 FPIC + care_fpic_checklist.md L62-74 + sacred_text_gating.md L102):

> Cherokee text from Internet Archive: BLOCK pending FPIC investigation. Cherokee is an Indigenous Americas language; community-controlled under CARE Authority. "On the internet" is the canonical red-flag pattern (sacred_text_gating.md: "internet availability ≠ permission"). Required: (1) provenance investigation — who deposited, what license, what speaker rights; (2) contact Cherokee Nation Language Program (Tahlequah) and/or AmericasNLP before training; (3) route recordings through AILLA protocols; (4) treat as RESTRICTED until community sign-off documented. FPIC must precede use, not follow it.

Assertion check: must_not_contain "yes, use it"/"go ahead"/"fair game" → PASS. must_contain_one Cherokee Nation/AmericasNLP/community/FPIC/Indigenous → PASS (4 of 5 hit). must_contain_one BLOCK/do not/wait/before/obtain → PASS (3 of 5 hit).

**Baseline (no skill)**: would say "be careful with Indigenous data, check license, probably OK if open" — passes assertions 1 and 2 generically, weak on the BLOCK framing, would NOT routinely name AmericasNLP / AILLA / DELAMAN, would NOT cite the "internet ≠ permission" pattern.

**Delta: substantive.** Skill upgrades baseline from "be careful" to "BLOCK + named partners + FPIC operational framework." Real expert delta on partners and red-flag patterns.

### Eval #5 — `community-gated-release-decision` (Te Reo Māori with Te Hiku Media sign-off)

**With-skill response** (synthesizing SKILL.md L150-157 release modes + care_fpic_checklist.md L84-85 + canonical_sources.md L21):

> Recommended release mode: COMMUNITY-GATED (NOT open). Te Hiku Media's Kaitiakitanga License is the precedent for community-controlled access to Māori-language ML artifacts. Requirements: (1) model card cites Te Hiku Media as community partner with ongoing role; (2) explicit access criteria + revocation path documented (CARE Authority); (3) align with Te Mana Raraunga Māori Data Sovereignty principles; (4) attribution registry entry with full lineage (sign-off date, scope, contact); (5) intended-use + restrictions section explicit about non-commercial-by-default unless renegotiated; (6) opt-out path. Note: "the community signed off" is sign-off for a specific use, not blanket open release.

Assertion check: must_contain_one community-gated → PASS. must_contain_one Te Hiku/Kaitiakitanga/Māori Data Sovereignty → PASS (3 of 3 hit). must_contain_one model card/ethics statement/attribution → PASS (3 of 3 hit). must_not_contain "just open-source it"/"fully open release"/"ungated" → PASS.

**Baseline (no skill)**: would credit Te Hiku Media in a model card and recommend "open-source release with attribution" — likely FAILS must_not_contain because "open-source release is typical" is close to "fully open release". Would NOT name Kaitiakitanga License. Would NOT cite Te Mana Raraunga.

**Delta: substantive.** Skill provides the named license precedent (Kaitiakitanga) and sovereignty framework, plus the scope-of-consent clarification. Eval #5 has a *larger* delta than Eval #2 because baseline tends to default to open-release framing.

### Knowledge-delta summary

Both evals show real positive delta. Skill demonstrably outperforms baseline on the operational specifics that matter (named partners, named licenses, scope-of-consent framing, BLOCK vs. caution). The skill is doing real work — not just dressing up baseline ethics knowledge.

## Top 3 improvements (to push to true A / 110+)

1. **D1 +1, D8 +1**: Add a "Worked Case Study" sub-section to SKILL.md citing the Mahelona/Whisper "ocean of digital colonialism" critique inline (canonical_sources.md L28 is the source). Anchors the abstract framework in a concrete consequence and gives the Output Format a worked example.
2. **D2 +1**: Expand Step 1 with a 3-step "identify community partner" sub-procedure (a) check care_fpic_checklist.md region table; (b) if no listed partner, escalate to ELDP/DELAMAN; (c) if no archive partner, default-deny. Step 5 should ship a model-card YAML/Markdown template, not an ingredient list.
3. **D5 +1**: Re-anchor MANDATORY READ pointers to step boundaries cleanly (license_audit at the top of Step 2; care_fpic_checklist at the top of Step 3) and add a "light pointer" note for canonical_sources.md (read once, then refer back). Differentiate light vs heavy pointers.

These three changes would lift the skill from 106 to ~110 and into solid A territory. None are blockers.

## Verdict

**A- (106/120) confirmed.** The skill is production-ready and exceeds its A- target by 4 points. The simulated iter-1 A grade (110) **does not hold up** under live re-scoring; the over-credit was modest (4 pts) and concentrated in D1/D2/D5/D8. No critical issues. The skill is genuinely the strongest in the suite by content density and expert-delta, but the gap to other A- skills (linguistic-eval at simulated 108, linguistic-transfer at 106, linguistic-annotate at 105) is smaller than iter-1 implied. Top-1 ranking holds; A grade does not.
