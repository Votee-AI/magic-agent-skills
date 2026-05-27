# Skill Evaluation Report: linguistic-semantics (iteration 2 — LIVE)

> **Date**: 2026-04-23
> **Evaluator**: live skill-judge rubric pass (real read of SKILL.md + 4 references + 2 scripts; honest line-range scoring; live script execution; with-skill vs baseline simulated against 2 of 3 evals)
> **Replaces**: iter-1 simulated stub (101/120)
> **SKILL.md**: 123 lines (header + body) | **References**: 4 files (wordnet_omw 78 L, framenet_srl 72 L, mwe_parseme 83 L, canonical_sources 39 L = 272 L) | **Scripts**: 2 files (wordnet_coverage.py 106 L, srl_frame_advisor.py 94 L)

## Summary
- **Total Score**: **102/120 (85%)**
- **Grade**: **A-** (target: ≥ 96 / B+) — exceeds B+ target by 6 points
- **Pattern**: Process (~200-line target; 123 actual + 272 references = 395 lines)
- **Knowledge Ratio**: E : A : R ≈ **70 : 22 : 8**
- **Method**: live judge (this session) + live script execution + evals simulated against assertion list
- **Verdict**: SHIP. Live re-score lands +1 vs the iter-1 simulated stub (101 → 102), within calibration noise. All Phase-1 per-dim floors clear. Three minor defects flagged for follow-up (do not affect grade).

## Dimension Scores (with line-range evidence)

| Dim | Score | Max | Evidence |
|---|---|---|---|
| **D1 Knowledge Delta** | **17** | 20 | 7 concrete expert claims with mechanisms in "The Knowledge Engineers Routinely Miss" (SKILL L28-42): (1) "English Princeton WordNet: 117K synsets. Many OMW languages: 5-30K" L30 — quantified parity gap; (2) "PropBank-style SRL frames are NOT 1:1 across languages. English 'GIVE' frame ≠ Spanish 'DAR' frame structure exactly. Per-language frame inventories drift; alignment via Predicate Matrix or MultiFrameNet is required" L32 — named bridging mechanism; (3) "MWE handling is the dominant low-resource MT failure mode" L34 with concrete examples ("kick the bucket", "let the cat out of the bag", "raining cats and dogs") + "treat MWEs as units before tokenization"; (4) "Sense splitting vs lumping is corpus-design, not just lexicographic preference" L36 — calibration of methodology axis; (5) "BLEU/chrF underestimate semantic equivalence on low-resource MT" + COMET / LaBSE / SONAR named alternative L38; (6) "Yoruba has ~5K synsets vs English 117K" L40 — concrete low-resource calibration; (7) "Light verbs ('take a walk', 'give a smile') are MWE-adjacent" L42. Backed by per-language coverage table in wordnet_omw.md L17-44 (21 languages) and per-language FrameNet table in framenet_srl.md L19-30 (8 named projects + Predicate Matrix bridge). MWE estimate "30-50% of MT errors on idiomatic text trace to MWE mishandling" (mwe_parseme.md L20). **Gaps:** no inline worked example threading one language end-to-end through Steps 1-5 (e.g., Yoruba: WordNet 4.3% → no FrameNet → custom MWE catalog → COMET unavailable → bilingual pivot); no quantitative WSD baseline numbers; no concrete chengyu/yojijukugo dictionary names beyond "large dedicated chengyu catalogs exist" (mwe_parseme.md L57). Saturates at 17 — 7 expert items, all with mechanism, but 2 lack named numerical anchor (sense-splitting axis L36; light-verbs L42 are descriptive). |
| **D2 Mindset + Procedures** | **13** | 15 | 5-step workflow (L46-90) with mindset-first framing — Step 1 surfaces resource gap before any tooling decision; Step 2 distinguishes native FrameNet from Predicate Matrix bridge before recommending tools; Step 3 frames MWE as "treat as units before tokenization" (architectural choice, not late-stage filter); Step 4 frames metric choice as cross-lingual problem (COMET / LaBSE) not BLEU patch. Per-language coverage tables (wordnet_omw.md L21-43, framenet_srl.md L21-30, mwe_parseme.md L52-60) act as decision tables. Scripts emit structured JSON config consumable downstream. **Gap:** Step 4 (sense-equivalence eval) and Step 5 (output) are thin (12 lines combined L72-90); no manual spot-check protocol with explicit precision gate (compare bitext's "≥ 90% N=50"); no concrete worked-example walkthrough on a specific pair. |
| **D3 Anti-Pattern Quality** | **13** | 15 | 7 NEVERs (L92-100), each with mechanism: L94 "NEVER assume English WordNet structure transfers to other OMW languages. Coverage varies 10-20×"; L95 "NEVER ignore MWE handling in MT — silent literal translation of idioms is a top failure mode"; L96 "NEVER use English PropBank frames for non-English SRL without per-language alignment audit"; L97 "NEVER report semantic-equivalence with BLEU as primary metric. Use COMET / LaBSE for cross-lingual"; L98 "NEVER assume sense-disambiguation eval scales from English to low-resource — sense inventories differ + coverage is sparse"; L99 "NEVER treat 'kick the bucket' as 3 unrelated content words" (concrete worked-anti-example); L100 "NEVER skip cross-lingual frame alignment when comparing SRL outputs across languages". Mirrored in scripts (`anti_patterns` array in srl_frame_advisor.py L82-86). Reference-level anti-patterns extend the count: framenet_srl.md L60-62 ("Using English PropBank frames directly", "Treating Frame F as universal", "Reporting 'SRL F1' cross-lingually without alignment scheme"); mwe_parseme.md L72-75 (4 MWE NEVERs). **Gap:** wordnet_coverage.py has no `anti_patterns` block (asymmetric vs srl_frame_advisor.py); no NEVER on "training synthetic on the same model's WSD output" (analogous to bitext's model-collapse rule); no NEVER explicitly forbidding chrF as primary semantic metric (only BLEU is named in L97). |
| **D4 Spec / Description** | **13** | 15 | Description (L3) covers WHAT ("Lexical + frame semantics for the target language: WordNet / Open Multilingual WordNet (OMW) coverage, FrameNet / PropBank-style SRL guidance, multi-word expressions (MWE / PARSEME)"), WHEN (very dense keyword list: "WordNet, OMW, synset, sense disambiguation, FrameNet, PropBank, semantic role labeling, SRL, MWE, idioms, multi-word expressions, light verbs, phrasal verbs, semantic equivalence"), worked-example trigger ("asks how to handle 'kick the bucket' style mistranslation"), routing context ("Routed by linguistic-orchestrator in the Analyze phase"). When-NOT-to-use block (L26) routes correctly to `linguistic-eval` (surface metrics), `linguistic-syntax` (POS/dep), `linguistic-annotate` (annotation methodology). **Gap:** no explicit "use even if you don't know if you need it" pushy cue (compare linguistic-scope's "Use BEFORE..." framing); description front-loads jargon — "Predicate Matrix" / "MultiFrameNet" not in trigger list though in body; no "BEFORE training MT / RAG on a target with low OMW coverage" pushy reframe. Solid 13, not 14. |
| **D5 Progressive Disclosure** | **13** | 15 | THREE MANDATORY READ markers — Step 1 wordnet_omw.md (L48), Step 2 framenet_srl.md (L56), Step 3 mwe_parseme.md (L65). References sized appropriately (39-83 L each, total 272 L). Body = 123 L; refs = 272 L; ratio 0.45 main : ref = healthy split. Scripts referenced inline at usage site (wordnet_coverage.py L50, srl_frame_advisor.py L58). **Gap:** canonical_sources.md (the snapshot/dating doc, 39 L, 24 named refs spanning 4 sub-domains) is NOT linked from SKILL.md — agent has no path to discover it; should be linked from a "Refresh / canonical sources" section but no such section exists in the body. Same defect pattern as linguistic-bitext, linguistic-corpus, linguistic-transfer, linguistic-morph, linguistic-syntax, linguistic-annotate. |
| **D6 Freedom Calibration** | **12** | 15 | Process pattern correctly chosen — task is decision-driven (use-WordNet-or-fallback, use-FrameNet-or-Predicate-Matrix, MWE strategy gating). Decision trees enforce specific answers per coverage tier (wordnet_coverage.py L83-88: ≥30%/≥10%/<10% three-tier recommendation). Output template (L81-90) constrains structured handoff. **Gap:** Step 4 (sense-equivalence eval) gives three options (COMET / LaBSE / SONAR) but no decision rule for which to pick under what conditions — open freedom where calibration is possible (compare bitext's per-pair-class margin table). MWE strategy options (Step 3, L67-70) similarly enumerated without per-language steering ("PARSEME-tagged corpora" or "build per-target catalog" — but the per-family treatment table exists in mwe_parseme.md L52-60 and is not surfaced as a decision rule in the body). Mid freedom; two calibration misses. |
| **D7 Pattern Recognition** | **8** | 10 | Clean Process pattern: 123 lines main, 5 numbered steps, output format template (L113-122), 7 NEVERs, 6 edge cases (L102-109: OMW-absent, FrameNet-absent, MWE-catalog-absent, polysemous-cross-lingual, honorific-distinctions, macrolanguage-merged-senses). Scripts are recommendation-only Phase-1 cached snapshots (wordnet_coverage.py L17 "Phase 1 cached snapshot", srl_frame_advisor.py L16 same) — explicit phase-gating is honest pattern hygiene. **Gap:** under target line count (123 vs ~200) for Process pattern; no `--measure` flag or live OMW-API-call path on either script (both are 100% cached); no shared utility module for coverage-tier lookup (logic in wordnet_coverage.py L83-88 could be reused by srl_frame_advisor's "no native" recommendation); only 2 scripts (compare bitext's also-2 but with measurement-stub vs annotate's 2 + chained mode hint). |
| **D8 Practical Usability** | **13** | 15 | Output format template (L113-122) is concrete and complete (six labeled fields). 6 edge cases (L102-109) cover the most likely real-world misroutings. Both scripts produce structured JSON consumable by orchestrator. Live execution: `wordnet_coverage.py Yoruba` returns 5000 synsets / 4.3% coverage / "Coverage minimal — synset-based query expansion / WSD not viable; use cross-lingual embeddings" — directly load-bearing for Eval #1 answer; `wordnet_coverage.py English` returns 117000 / 100.0% / "adequate" baseline; `srl_frame_advisor.py Spanish` returns Spanish FrameNet ~150 frames + AnCora SRL + "Native SRL / FrameNet resources available — use directly" + 3 anti-patterns — directly load-bearing for Eval #3; `srl_frame_advisor.py Yoruba` returns "absent" / "absent" / "absent" / "n/a" / "No SRL infrastructure — fall back to UD parse + manual semantic role inference". All four invocations exit 0 with valid JSON. **Gaps:** (1) no live MWE coverage script (PARSEME availability / chengyu catalog lookup) — Step 3 has no scripted decision support; (2) no `--measure` mode for fresh OMW API call; (3) no inline worked example threading one language through Steps 1-5 in SKILL.md body. |

**Total: 17 + 13 + 13 + 13 + 13 + 12 + 8 + 13 = 102/120**

## Per-dimension floor check (Phase 1 gates)

| Dim | Required floor | Achieved | Pass? |
|---|---|---|---|
| D1 | ≥ 15 | 17 | YES |
| D3 | ≥ 10 | 13 | YES |
| D4 | ≥ 13 | 13 | YES (exactly) |
| D5 | ≥ 12 | 13 | YES |

All Phase-1 floors clear (D4 exactly at floor — same edge as bitext, syntax, morph).

## E : A : R Knowledge Ratio

| Bucket | Approx. share | Source |
|---|---|---|
| **Expert insight** | ~70% | "The Knowledge Engineers Routinely Miss" 7-item block (SKILL L28-42); per-language OMW coverage table (wordnet_omw.md L21-43, 21 languages); per-language FrameNet projects table (framenet_srl.md L21-30); per-family MWE strategy table (mwe_parseme.md L52-60); MWE error rate "30-50% of MT errors on idiomatic text" (mwe_parseme.md L20); per-language SRL tooling matrix (srl_frame_advisor.py L17-43, 25 languages); cached coverage tier thresholds 30%/10% (wordnet_coverage.py L83-88); concrete bilingual MWE example "kick the bucket" → "estirar la pata" (mwe_parseme.md L18); chengyu (Mandarin) + yojijukugo (Japanese) named per-family idiom traditions (mwe_parseme.md L57-58) |
| **Anti-patterns** | ~22% | 7 NEVERs in SKILL L92-100; 4 NEVERs in mwe_parseme.md L72-75; 3 NEVERs in framenet_srl.md L60-62; mirrored anti_patterns array in srl_frame_advisor.py L82-86; concrete worked anti-example "kick the bucket as 3 unrelated content words" L99; "NEVER report semantic-equivalence with BLEU" L97 (cross-references linguistic-eval); "Building MWE catalog without native-speaker review" (mwe_parseme.md L74) |
| **References** | ~8% | canonical_sources.md (39 L, 24 academic citations across WordNet, FrameNet, PropBank/SRL, MWE/PARSEME, foundational semantics, lexicography); wordnet_omw.md "See also" block L73-78 (Fellbaum, Bond & Foster + 2 URLs); framenet_srl.md "See also" L64-72 (Fillmore, Baker, Palmer, Lopez de Lacalle + 2 URLs); mwe_parseme.md "See also" L77-83 (Sag, Constant, Savary + 2 URLs) |

## Eval verification — knowledge delta on 2 evals

### Eval #1 — wordnet-coverage-yoruba (RAG synonym expansion)

**Prompt:** "I'm building a RAG system that uses WordNet synonym expansion for query broadening. Will it work for Yoruba documents?"

**With-skill answer (simulated using SKILL L40, L94, L97; wordnet_omw.md L38, L57-61; live `wordnet_coverage.py Yoruba` JSON):**

> **NO** — and the failure mode is silent, which makes it dangerous. Live coverage check (`wordnet_coverage.py Yoruba`): Yoruba OMW exposes ~5,000 synsets vs Princeton's 117,000 — that's **4.3% coverage** (the script flags it as "Coverage minimal — synset-based query expansion / WSD not viable; use cross-lingual embeddings"). For a RAG synonym-expansion pipeline, that means: when you call `wn.synsets(yoruba_term)`, the lookup will return `None` for the vast majority of content terms, so your query expansion silently degrades to identity (no broadening). The retrieval will still run, but the recall lift you designed for is absent — you will not notice in offline metrics if your test set happens to use high-frequency terms that did get aligned. **Recommended alternative:** swap synset-based expansion for **cross-lingual embedding similarity** — LaBSE or SONAR will give you query-document semantic match without depending on patchy synset alignment. This is in the skill's anti-pattern list explicitly: "NEVER assume English WordNet structure transfers to other OMW languages. Coverage varies 10-20×." The same gap applies to most class 0-2 OMW entries — Swahili (3%), Tamil (3%), Khmer/Twi/Inuktitut/Cherokee (absent), Arabic (8%), Hebrew (7%) all fail the same way. If you must use synset-based expansion, restrict to high-coverage languages only (Japanese 48%, Mandarin 36%, Portuguese 35%, Spanish 32%) and document the silent-failure risk for the rest.

**Assertions:**
- `must_contain_one ["NO", "no", "do not", "won't work", "will fail"]` → "NO" + "won't" + "fails" all present — PASS
- `must_contain_one ["LaBSE", "SONAR", "cross-lingual embedding"]` → "LaBSE" + "SONAR" + "cross-lingual embedding similarity" all present — PASS
- `must_not_contain ["WordNet works for most languages", "OMW is comprehensive"]` → absent — PASS

**3/3 PASS.**

**Baseline answer (no skill, simulated for general Sonnet-class LLM):**

> WordNet has multilingual extensions (Open Multilingual WordNet) that cover many languages including some African languages, so synonym expansion may work for Yoruba to some extent. You can use NLTK's wordnet API and check whether `wn.synsets('term', lang='yor')` returns results. Coverage will be lower than English, so expect partial functionality. As a fallback, consider sentence embeddings (multilingual BERT, LaBSE) for semantic similarity if WordNet coverage is too sparse.

**Baseline assertion check:**
- assertion 1 ("NO"-class): would say "may work to some extent" / "partial functionality" — that is the OPPOSITE of NO; assertion 1 likely **FAIL**
- assertion 2 (LaBSE/SONAR/cross-lingual embedding): would mention "LaBSE" or "multilingual BERT" — likely **PASS** on LaBSE
- assertion 3 (must_not_contain): would not say "WordNet works for most languages" verbatim — likely **PASS**

Expected baseline: **2/3 PASS** (fails the load-bearing first assertion).

**Delta verdict:** **HIGH** — baseline gives a wishy-washy "may work, expect partial functionality" answer that fails to flag the 4% coverage as effectively-broken for query expansion. The skill turns this into a hard NO with a quantified mechanism (4.3% silent return-None rate), names the alternative (LaBSE / SONAR cross-lingual embedding), and generalizes the risk to other class 0-2 OMW languages. The 17K-vs-117K calibration + the silent-failure framing are the load-bearing differentiators that the user's RAG architecture decision actually depends on.

### Eval #2 — mwe-idiom-mt-failure (kick the bucket → patear el cubo)

**Prompt:** "Our En-Es MT model translates 'kick the bucket' literally to 'patear el cubo'. How do I fix this?"

**With-skill answer (simulated using SKILL L34, L67-70, L95, L99; mwe_parseme.md L7-12, L18-20, L36-49, L72-75):**

> Diagnosis: this is an **MWE / idiomatic mistranslation** — "kick the bucket" is a non-compositional multi-word expression (means "die"; not "kick" + "bucket"). Your MT model is treating the three tokens as independent content words and producing a literal calque. The skill flags this explicitly as the **dominant low-resource MT failure mode for idiomatic text** — estimates suggest 30-50% of MT errors on idiomatic input trace to MWE mishandling. Target: the Spanish equivalent is **"estirar la pata"** (literally "stretch the paw"), which is the idiomatic-equivalent expression, not a literal translation. **Fix recipe (three options, in order of investment):** (1) **Pre-tokenize known MWEs as single units** before BPE / SentencePiece — replace "kick the bucket" with `<mwe_kick_the_bucket>` so the model translates it as a unit. Tradeoff: brittle for variant forms ("kicked the bucket", "kicks the bucket") — needs lemma-aware matching. (2) **Inline MWE tags during training** using PARSEME-tagged training data — tag MWE spans during training and let the model learn to handle them. Less brittle but requires PARSEME-tagged parallel data (Spanish has PARSEME coverage). (3) **Post-translation idiom replacement** — translate as-is, then post-process to swap literal-translated idioms for the target-language equivalent. Requires a bilingual idiom dictionary as the supplementary fix. **Quick win:** start with option (3) + a 500-entry bilingual idiom catalog (the skill notes 500 is a useful starting size). Long-term, option (2) with PARSEME-aligned training data is the most robust. **Anti-patterns to avoid:** NEVER treat "kick the bucket" as 3 unrelated content words; NEVER build the MWE catalog without native-speaker review (collocations ≠ idioms); NEVER apply the same treatment to all MWE types (light verbs differ from idioms differ from collocations).

**Assertions:**
- `must_contain_one ["MWE", "idiom", "multi-word"]` → all three present — PASS
- `must_contain_one ["PARSEME", "pre-tokenize", "tag"]` → "PARSEME" + "pre-tokenize" + "tag" all present — PASS
- `must_contain_one ["dominant", "common", "frequent"]` → "dominant low-resource MT failure mode" present — PASS

**3/3 PASS** (also satisfies expected-output bonus: PARSEME named, pre-tokenize + inline-tag both named, "estirar la pata" named, bilingual idiom dictionary named).

**Baseline answer (no skill, simulated):**

> "Kick the bucket" is an English idiom meaning "to die"; the Spanish "patear el cubo" is a literal translation that wouldn't be understood. The Spanish equivalent is something like "estirar la pata" or "irse al otro barrio". To fix this in your MT system, you have a few options: (1) augment training data with examples that show idiomatic translations, (2) post-process common idioms with a dictionary lookup, (3) fine-tune on parallel data that contains the idiomatic phrases. You may also want to consider sub-word tokenization adjustments so the model can learn idioms as units.

**Baseline assertion check:**
- assertion 1 (MWE/idiom/multi-word): would say "idiom" — PASS
- assertion 2 (PARSEME/pre-tokenize/tag): unlikely to name "PARSEME" specifically; would say "tokenize" or "augment training data" but not "tag spans" or "pre-tokenize as single units" specifically — borderline, leaning PASS on "tokenize"
- assertion 3 (dominant/common/frequent): unlikely to provide quantitative framing ("30-50% of MT errors") or "dominant failure mode" calibration; would say "common issue with idioms" — borderline PASS on "common"

Expected baseline: **2-3 / 3 PASS** (likely passes all three on technicality but at lower fidelity).

**Delta verdict:** **MODERATE-to-HIGH** — both pass assertions, but the with-skill answer adds: (a) the named **PARSEME shared task** as the data resource (baseline says vague "augment training data"); (b) the **30-50% / "dominant low-resource MT failure mode"** calibration that justifies the engineering investment; (c) the **3-tier intervention ladder** (pre-tokenize / inline-tag / post-process) with explicit tradeoffs (brittleness for variant forms); (d) the **500-entry catalog** starting size; (e) the **collocations ≠ idioms** native-speaker-review anti-pattern. The skill turns "here are some options" into a defensible engineering plan with named data resources, named tradeoffs, and an explicit quick-win path. Baseline would land the user in a months-long fine-tuning project; skill routes them to a 500-entry catalog + post-process for the quick win and PARSEME tagging for the long-term fix.

## Live script execution evidence

```
$ python3 skills/linguistic-semantics/scripts/wordnet_coverage.py Yoruba
→ synsets_available: 5000
→ coverage_pct_vs_princeton: 4.3
→ project: "Yoruba WordNet (limited)"
→ recommendation: "Coverage minimal — synset-based query expansion / WSD not viable;
                   use cross-lingual embeddings"
→ exit code 0  [load-bearing for Eval #1]

$ python3 skills/linguistic-semantics/scripts/wordnet_coverage.py English
→ synsets_available: 117000  coverage_pct: 100.0
→ recommendation: "Coverage adequate for most lexical-semantics tasks"
→ exit code 0  [baseline anchor]

$ python3 skills/linguistic-semantics/scripts/srl_frame_advisor.py Spanish
→ framenet: "Spanish FrameNet (~150 frames)"
→ propbank: "AnCora SRL"
→ recommended_approach: "Native SRL / FrameNet resources available — use directly"
→ anti_patterns: 3 entries (English-PropBank-direct, F1-cross-lingual, frame-universality)
→ exit code 0  [load-bearing for Eval #3]

$ python3 skills/linguistic-semantics/scripts/srl_frame_advisor.py Yoruba
→ framenet: "absent"  propbank: "absent"  srl_tool: "absent"
→ via_predicate_matrix: "n/a"
→ recommended_approach: "No SRL infrastructure — fall back to UD parse +
                         manual semantic role inference"
→ exit code 0  [contrast case]
```

All four invocations clean; JSON is consumable by orchestrator. Coverage-tier logic in `wordnet_coverage.py` L83-88 (≥30% / ≥10% / <10%) correctly fires the "minimal" tier for Yoruba.

## Defects observed

| ID | Severity | Location | Observation |
|---|---|---|---|
| D1 | P3 (discoverability) | SKILL.md (no link to canonical_sources.md) | The dating/refresh-snapshot reference (39 L, 24 academic citations spanning WordNet, FrameNet, PropBank/SRL, MWE/PARSEME, foundational semantics, lexicography) is not surfaced from SKILL.md. Agents have no path to discover it. Add a `## Refresh / canonical sources` section linking it. Same defect as bitext, corpus, transfer, morph, syntax, annotate. Drives D5 −1 vs theoretical max. |
| D2 | P3 (asymmetric script convention) | wordnet_coverage.py vs srl_frame_advisor.py L82-86 | `srl_frame_advisor.py` emits an `anti_patterns` array in its JSON output; `wordnet_coverage.py` does not. Asymmetry — pick one convention. The wordnet script could surface the parallel "NEVER assume English WordNet structure transfers" + "NEVER use synset-based expansion below 10% coverage" anti-patterns inline. |
| D3 | P3 (no MWE script) | scripts/ (only 2 scripts) | Step 3 (MWE / PARSEME handling) has no scripted decision support — there is no `parseme_coverage.py` or `mwe_strategy_advisor.py` to mirror what wordnet_coverage and srl_frame_advisor do for Steps 1-2. Step 3 is purely doc-driven. Drives D7 −1 / D8 −1 vs theoretical max. |
| D4 | P3 (Step 4 thin) | SKILL.md L72-77 | Step 4 (sense-equivalence eval) lists three options (COMET / LaBSE / SONAR) without a decision rule — for what target-language coverage tier should the agent prefer COMET vs LaBSE? No `comet_coverage.py` script either. Drives D6 −1 vs theoretical max. |
| D5 | P3 (no `--measure` mode) | both scripts | Both scripts are Phase-1 cached snapshots ("Phase 1 cached snapshot 2026-04-23"). No `--measure` flag for fresh OMW-API or PARSEME-shared-task lookup. Honest phase-gating, but no live measurement path today. |

None block shipping. D1 is the consistent suite-level defect and should be batched into a single follow-up commit across all affected skills.

## Verdict

**SHIP** as `iter-2-live`. Honest live measurement (102) sits **+1 vs iter-1 simulated (101)**, within calibration noise — the simulated 101 holds up under live scoring. All Phase-1 per-dim floors clear (D1=17≥15, D3=13≥10, D4=13≥13 exactly, D5=13≥12).

**Knowledge delta** is HIGH on Eval #1 (skill unlocks the load-bearing 4.3% calibration + LaBSE/SONAR routing + silent-failure framing the baseline misses on assertion 1) and MODERATE-to-HIGH on Eval #2 (both pass; skill adds PARSEME naming, 30-50% calibration, 3-tier ladder, 500-entry catalog quick-win — turning a vague answer into a defensible engineering plan).

**E : A : R ratio** ≈ 70 : 22 : 8 — expert-density-dominant with healthy reference and anti-pattern shares; consistent with other live-scored Phase-3 skills (semantics 70:22:8, corpus 72:23:5, annotate 70:22:8, transfer 70:25:5).

**Phase-2 levers projected to lift to 106-108:**
1. canonical_sources.md MANDATORY READ + Refresh section (D5 +1)
2. inline Yoruba worked example threading Steps 1-5 with concrete numbers (D1 +1, D8 +1)
3. parseme_coverage.py third script + per-family MWE-strategy decision rule (D7 +1, D8 +1)
4. wordnet_coverage.py emit anti_patterns array for symmetry with srl_frame_advisor (D3 +1, D2 +1)
5. Step 4 COMET-vs-LaBSE decision rule keyed off OMW coverage tier (D6 +1)

**Comparative framing:** at iter-2-live, linguistic-semantics (102) ties with linguistic-bitext (102), linguistic-morph (102), and linguistic-syntax (102) — a tight A- cluster sitting one or two points behind ethics (106), scope (105), transfer (105), and the simulated-but-not-yet-relived linguistic-eval (108). The simulated 101 is honestly priced; Phase-1 ship target met.
