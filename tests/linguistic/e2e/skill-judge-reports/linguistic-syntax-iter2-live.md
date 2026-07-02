# Skill Evaluation Report: magic-linguistic-syntax (iteration 2 — LIVE)

> **Date**: 2026-04-23
> **Evaluator**: live skill-judge rubric pass (real read of SKILL.md + 4 references + 2 scripts; honest line-range scoring; live script execution; simulated with-skill vs baseline against 2 of 3 evals)
> **Replaces**: iter-1 simulated stub (101/120)
> **SKILL.md**: 136 lines (header + body) | **References**: 4 files (ud_treebanks 73 L, parser_transfer 85 L, agreement_probes 99 L, canonical_sources 37 L = 294 L) | **Scripts**: 2 files (ud_coverage.py 96 L, parser_transfer_advisor.py 99 L)

## Summary
- **Total Score**: **102/120 (85%)**
- **Grade**: **A-** (target: ≥ 96 / B+) — exceeds B+ target by 6 points
- **Pattern**: Process (~150-200-line target; 136 actual + 294 references = 430 lines)
- **Knowledge Ratio**: E : A : R ≈ **68 : 24 : 8**
- **Method**: live judge (this session) + live script execution (4 invocations) + evals simulated against assertion list for #1 (PUD eval-leak trap) and #3 (Yoruba tone-aware agreement probes)
- **Verdict**: SHIP. Live re-score lands +1 vs the iter-1 simulated stub (101 → 102), within calibration noise. All Phase-1 per-dim floors clear. Two minor improvement levers noted (do not affect grade).

## Dimension Scores (with line-range evidence)

| Dim | Score | Max | Evidence |
|---|---|---|---|
| **D1 Knowledge Delta** | **17** | 20 | 6 concrete expert claims with mechanisms in "The Knowledge Engineers Routinely Miss" (SKILL L28-40): (1) "UD treebank coverage is uneven … 100+ treebanks exist but vary 100× in size. Many class 0-2 languages have only PUD-style 1K-sentence test treebanks" L30 — concrete size + use restriction; (2) "Cross-lingual parser transfer source is picked by URIEL distance, NOT treebank size. Closest typological neighbor with adequate data > distant neighbor with massive data" L32 — non-obvious deviation from naive heuristic; (3) "Agreement probes (subject-verb, gender, case) detect grammatical knowledge directly. Better than parsing F1 for evaluating LLMs (which don't expose parses)" L34 — load-bearing rule for LLM eval; (4) "Trankit (2021) is generally better than stanza for low-resource UD parsing. Stanza wins on speed + coverage. UDify (2019) is older but multilingual-shared" L36 — version-aware, names trade-off; (5) "PUD-style 1K test treebanks are TEST sets, not training. Fine-tuning a parser on them = leaked eval. Common rookie mistake; some published 'parser improvements' are this leak" L38 — calibration of severity + how-common; (6) "Switch-reference, ergative-absolutive, polysynthesis break English-trained parsers in non-obvious ways" L40 — concrete typology gotchas. Backed by per-language coverage table (ud_treebanks.md L21-40), per-target transfer-source table (parser_transfer.md L20-30), per-language probe-status table (agreement_probes.md L82-92), per-typology phenomena list (agreement_probes.md L24-56). BLiMP-style accuracy threshold cited concretely ("> 0.85 accuracy = solid" agreement_probes.md L22). **Gaps:** no quantitative numbers per parser tool (Trankit vs stanza UAS delta on low-resource is qualitative, parser_transfer.md L73-78 only says "5-15 points across runs"); no concrete worked example of a real probe pair with log-likelihoods; per-language probe-set status table has 7 rows (could be 15+). |
| **D2 Mindset + Procedures** | **13** | 15 | 6-step workflow (L42-103) with mindset-first framing ("Identify UD treebank availability" L44 before mechanical steps). Per-treebank-availability decision matrix (L56-60) routes the three approaches cleanly. Per-tool decision matrix (L72-77) gives Pick-when criteria for Trankit / stanza / UDify / spaCy. Per-phenomenon probe construction protocol (agreement_probes.md L14-22) with 5 numbered procedural steps. Probe-set sizing rule (target 100-500 minimal pairs, log-likelihood difference > 0 = correct preference) at L89. Hand-off contract specified (L102: "magic-linguistic-eval for benchmark integration; magic-linguistic-annotate if creating UD gold"). **Gaps:** no concrete worked-example walkthrough on a specific language end-to-end (e.g., Yoruba: treebank lookup → transfer source → tool choice → probe set construction); no explicit acceptance gates for each step (e.g., "PASS this step if N pairs ≥ 100 AND diacritics preserved"). |
| **D3 Anti-Pattern Quality** | **13** | 15 | 7 NEVERs (L106-113), each with WHY: L107 "NEVER fine-tune a parser on PUD-style 1K test treebanks. You've leaked your eval"; L108 "NEVER pick parser source treebank by size alone. URIEL typological distance dominates transfer success"; L109 "NEVER report parser F1 as a proxy for LLM grammatical knowledge. Use agreement probes — LLMs don't expose dependency parses"; L110 "NEVER assume English-trained UD parsers handle ergative-absolutive correctly. Subject/object roles are inverted"; L111 "NEVER strip diacritics before tone-language agreement probes. The agreement is in the diacritic"; L112 "NEVER use UDify for new low-resource projects when Trankit is available"; L113 "NEVER treat 'no UD treebank' as 'no syntactic eval possible' — agreement probes work without parses". Mirrored in script (`anti_patterns` array in parser_transfer_advisor.py L87-91 — three rules surfaced). **Gaps:** missing explicit NEVER on UD version drift (mentioned in Edge Cases L118 but not lifted to NEVERs); no NEVER on "parser-on-LLM-output as eval" (this is the inverse of the F1 NEVER and would close the loop); no NEVER on training/test contamination from re-using public PUD splits. |
| **D4 Spec / Description** | **13** | 15 | Description (L3) covers WHAT ("Universal Dependencies (UD) treebank usage, cross-lingual parser transfer (UDify, Trankit, stanza), and agreement-probe construction for grammatical-correctness evaluation"), WHEN ("Use whenever the user mentions UD, Universal Dependencies, treebank, dependency parsing, constituency parsing, parser transfer, agreement probe, subject-verb agreement, gender agreement, case marking, syntactic eval"), KEYWORDS list dense (12+ terms), PUSHY trigger ("or asks how to evaluate whether a low-resource LLM has actually learned grammar (not just lexical surface)"), routing context ("Routed by magic-linguistic-orchestrator in the Analyze phase"). When-NOT-to-use clause (L26) gives a clear stop. **Gaps:** no explicit "use even if you don't know if you need it" cue; description front-loads acronyms (UDify, Trankit, stanza) that newer engineers may not parse on first read; "agreement probe" may not be a phrase a user types — could add "minimal pair" / "BLiMP" / "syntactic eval" as plain-text hooks (BLiMP IS in the description through "agreement probe" mapping but not literally). |
| **D5 Progressive Disclosure** | **13** | 15 | THREE MANDATORY READ markers — Step 1 ud_treebanks.md (L46), Step 3 parser_transfer.md (L63), Step 5 agreement_probes.md (L81). References sized appropriately (73-99 L each, except canonical_sources 37 L). Body = 136 L; refs = 294 L; ratio 0.46 main : ref = healthy split. **Gaps:** canonical_sources.md (the snapshot/dating/citation doc) is NOT linked from SKILL.md at all — agent has no path to discover it; should be linked from a `## Refresh / canonical sources` section in the body but no such section exists; the 37-L canonical doc is therefore "dark" reference unless the orchestrator hands it down. |
| **D6 Freedom Calibration** | **12** | 15 | Process pattern correctly chosen — task is decision-driven (treebank-availability → approach → source → tool → probe-set composition). Decision tables enforce specific answers per scenario. Scripts emit structured JSON config matching the Output Format template. **Gaps:** Step 5 probe-set sizing (L89 "100-500 minimal pairs per phenomenon") is a range, not a per-language calibrated target; no programmatic generation of probes (would need a third script `probe_builder.py`); the per-tool table (L72-77) doesn't tier by target language size class — a user picking Trankit vs stanza for Class 0 Yoruba vs Class 4 English gets the same generic "low-resource → Trankit" without size-thresholded guidance. Mid freedom; one calibration miss. |
| **D7 Pattern Recognition** | **8** | 10 | Clean Process pattern: 136 lines main, 6 numbered steps, decision tables per step (treebank availability L56-60, parser tool L72-77), output format template (L93-103 in Step 6 + duplicate at L126-136 in Output Format section), 7 NEVERs, 6 edge cases (L116-122). Scripts are recommendation-only with no `--measure` mode (honest phase-gating; no stub flags claimed but missing). **Gaps:** under target line count (136 vs ~200) for a Process pattern carrying 3 distinct decision domains (treebank, transfer, probe); two near-duplicate Output Format blocks (L93-103 in Step 6 and L126-136 in Output Format) — minor redundancy; no shared helper / utility for URIEL distance lookup (script does not actually invoke magic-linguistic-scope's URIEL — the rationales are pre-cached strings in `_TRANSFER_SOURCES`, parser_transfer_advisor.py L19-43, so the "URIEL distance" claim in body is only metadata, not computed). |
| **D8 Practical Usability** | **13** | 15 | Output format template (L126-136) is concrete and complete (includes treebank coverage, approach, source rationale, parser tool, probe phenomena, anti-patterns, hand-off). 6 edge cases (L117-122: multiple UD treebanks, version drift, ergative-absolutive, polysynthetic morpheme-level UD, mixed-script code-switched, UD gold errors). Both scripts produce structured JSON consumable by orchestrator. **Live execution:** `ud_coverage.py Yoruba` returns YTB / 100 sentences / training_viable=false / "PUD-style treebank — EVAL ONLY (do NOT fine-tune); cross-lingual zero-shot for parsing" — directly load-bearing for Eval #1. `ud_coverage.py Khmer` returns no-treebank / "cross-lingual zero-shot mandatory; document eval limitation" — load-bearing for Eval #2. `parser_transfer_advisor.py Yoruba` returns Igbo + English candidates with rationales, "Trankit" tool with rationale, agreement_probes_recommended=true, 3-item anti_patterns list. `parser_transfer_advisor.py Khmer` returns Vietnamese + Thai + English source candidates with rationales (Vietnamese first, naming "Geographic + tone-language proximity") — directly answers Eval #2 with the right ranking. All four invocations exit code 0. **Gaps:** (1) no third script for probe construction (probe_builder.py would close the loop on Step 5); (2) the parser_transfer_advisor.py ranks sources but does not emit a numerical URIEL distance (rationales are strings); (3) no example invocation of hand-off to magic-linguistic-eval shown; (4) Yoruba YTB is described as "100 sentences" in ud_coverage.py L36 but ud_treebanks.md L32 also says "100 sentences (?!)" — the (?!) is honest but unprofessional in a reference doc. |

**Total: 17 + 13 + 13 + 13 + 13 + 12 + 8 + 13 = 102/120**

## Per-dimension floor check (Phase 1 gates)

| Dim | Required floor | Achieved | Pass? |
|---|---|---|---|
| D1 | ≥ 15 | 17 | YES |
| D3 | ≥ 10 | 13 | YES |
| D4 | ≥ 13 | 13 | YES (exactly) |
| D5 | ≥ 12 | 13 | YES |

All Phase-1 floors clear (D4 exactly at floor).

## E : A : R Knowledge Ratio

| Bucket | Approx. share | Source |
|---|---|---|
| **Expert insight** | ~68% | "Knowledge Engineers Routinely Miss" 6-item block (SKILL L28-40); per-language treebank size table (ud_treebanks.md L23-40); per-target empirical transfer pairs with UAS estimates (parser_transfer.md L22-29); per-typology probe phenomena (agreement_probes.md L24-56); per-language BLiMP-style availability snapshot (agreement_probes.md L84-92); BLiMP > 0.85 accuracy threshold (L22); URIEL-distance dominance principle |
| **Anti-patterns** | ~24% | 7 NEVERs in SKILL L106-113; mirrored 3-item anti-pattern array in parser_transfer_advisor.py L87-91; eval-leak warning duplicated in ud_treebanks.md L48-50 ("Fine-tuning on PUD = leaked eval = published-paper retraction risk"); diacritic-stripping warning in agreement_probes.md L67-74; UDify-not-for-new-projects rule appears in SKILL + parser_transfer.md L60-65 |
| **References** | ~8% | 4 reference files (294 L total); canonical_sources.md curated reading list (Nivre UD-v2 LREC, de Marneffe UD CL, Zeman CoNLL 2017/2018, Nguyen Trankit EACL, Qi Stanza ACL, Kondratyuk-Straka UDify EMNLP, de Vries 2022 ACL, Lin et al. 2019 ACL, Pires mBERT ACL, Marvin-Linzen 2018 EMNLP, Warstadt BLiMP TACL, Mueller CLAMS ACL, Hu SyntaxGym ACL, Linzen 2016 TACL, Nivre 2008 CL, Carnie 2013, Tallerman 2020) |

## Eval verification — knowledge delta on 2 evals

### Eval #1 — pud-eval-leak-trap (Yoruba YTB ~100 sentences, fine-tune temptation)

**Prompt:** "I have the Yoruba YTB UD treebank (~100 sentences). Can I fine-tune a parser on it and report parsing accuracy?"

**With-skill answer (simulated using SKILL L30, L38, L107; ud_treebanks.md L18 + L32 + L48-50; parser_transfer.md L22-26 Yoruba row; agreement_probes.md L9-12 + L67-74; live `ud_coverage.py Yoruba` and `parser_transfer_advisor.py Yoruba` output):**

> **NO — do not fine-tune on YTB.** YTB is ~100 sentences, far below the 1K floor for even PUD-style test treebanks; UD's tier classification puts it firmly in the "test/eval only" bucket (`ud_coverage.py Yoruba` returns `training_viable: false` with the explicit recommendation "PUD-style treebank — EVAL ONLY (do NOT fine-tune); cross-lingual zero-shot for parsing"). Fine-tuning on a test treebank then reporting parsing accuracy = **leaked eval**, exactly the rookie mistake we flag in the anti-pattern list at SKILL L107 ("NEVER fine-tune a parser on PUD-style 1K test treebanks. You've leaked your eval") and in ud_treebanks.md L48-50 ("Fine-tuning on PUD = leaked eval = published-paper retraction risk"). Some published 'parser improvements' on low-resource languages are exactly this leak pattern (SKILL L38).
>
> **Correct approach: cross-lingual zero-shot transfer.** Per `parser_transfer_advisor.py Yoruba`, the source-treebank ranking is (1) Igbo (same Niger-Congo branch, close URIEL — but Igbo has no UD itself, so blocked), (2) **English** (Latin script overlap; URIEL ~0.62 — distant; expect ~50-60 UAS zero-shot per parser_transfer.md L22). Use **Trankit** (XLM-R-based, best low-resource quality) over stanza or UDify. Reserve YTB as the eval split — report zero-shot UAS on it, never train on it.
>
> **Critically: parsing F1 is NOT the right LLM-grammar metric.** Per SKILL L34 + L109 and agreement_probes.md L7-12: LLMs are autoregressive token models that don't expose dependency parses; running a parser on LLM output measures parsability, not grammatical knowledge. Use **agreement probes / BLiMP-style minimal pairs** instead — construct ≥ 100 minimal pairs per phenomenon, compute log-likelihood difference, target > 0.85 accuracy = solid grammatical knowledge. For Yoruba specifically, **preserve tone diacritics** (NEVER strip — "the agreement is in the diacritic", SKILL L111; agreement_probes.md L67-74 gives the Ọkọ̀/Ọkọ minimal pair).

**Assertions:**
- `must_contain_one ["NO", "no", "do not", "don't", "leaked"]` → "NO — do not fine-tune", "leaked eval" — PASS
- `must_contain_one ["cross-lingual transfer", "Trankit", "zero-shot"]` → "cross-lingual zero-shot transfer", "Trankit", "zero-shot UAS" — PASS
- `must_contain_one ["agreement probe", "BLiMP-style", "minimal pair"]` → all three present — PASS
- `must_not_contain ["fine-tune YTB and report", "100 sentences is enough"]` → absent — PASS

**4/4 PASS.**

**Baseline answer (no skill, simulated for general Sonnet-class LLM):**

> 100 sentences is very small for fine-tuning a parser. You'd risk severe overfitting and the resulting numbers wouldn't be meaningful. Standard practice with such tiny treebanks is to use cross-lingual transfer from a related language with more data. You could fine-tune on a closely related language and evaluate zero-shot on Yoruba. Tools like stanza or UDify support multilingual UD parsing. Be cautious about reporting numbers from tiny treebanks.

**Baseline assertion check:** would likely PASS assertion 1 ("100 sentences is very small", "wouldn't be meaningful" satisfies "do not"); PASS assertion 2 ("cross-lingual transfer", "zero-shot"); FAIL assertion 3 (no agreement probe / BLiMP / minimal pair language); PASS assertion 4 (no forbidden phrases). Expected baseline: **3/4 PASS** (specifically misses the agreement-probe alternative which is the load-bearing LLM-eval insight).

**Delta verdict:** **HIGH on assertion 3, MODERATE overall.** Baseline catches the basic "don't overfit on tiny data" and routes to cross-lingual transfer, but misses the deeper insight: parser-F1-on-LLM-output is the wrong metric class entirely; agreement probes operate without parses and so make the "no UD treebank" objection moot. This is the load-bearing pivot — the skill turns "don't do this, transfer instead" into "don't do this, AND your evaluation framework has an inappropriate dependency on parsing that you should drop in favor of minimal pairs". Baseline also misses (a) the "rookie mistake / published-paper retraction" calibration of severity, (b) the named ranking Igbo→English with URIEL ~0.62 zero-shot ~50-60 UAS, (c) the Trankit > stanza > UDify version-aware preference, (d) the Yoruba-specific diacritic-preservation requirement. Skill turns generic best-practice advice into a defensible, mechanism-grounded recommendation with named tools, named thresholds, and a parallel non-parsing eval channel.

### Eval #3 — agreement-probe-yoruba-tone (LLM grammar eval design)

**Prompt:** "How do I evaluate whether my Yoruba LLM has actually learned grammar (not just lexical patterns)?"

**With-skill answer (simulated using SKILL L34, L83-89, L111; agreement_probes.md L9-22, L43-44, L67-74, L84-92):**

> Use **agreement probes / BLiMP-style minimal pairs**, not parser F1. Per SKILL L34 + agreement_probes.md L9-12: LLMs are autoregressive token models that don't expose dependency parses; running a parser on LLM output only measures parsability of the output, not whether the model has internalized grammar. Agreement probes evaluate grammatical knowledge directly — present a minimal pair (one grammatical, one ungrammatical), measure which the model assigns higher likelihood; if it prefers grammatical, it has learned the agreement.
>
> **Probe construction protocol** (agreement_probes.md L14-22): for each phenomenon, (1) identify the agreement, (2) construct ≥ 100 minimal pairs (target 100-500 per phenomenon, SKILL L89), (3) each pair differs in ONE feature (number / gender / tone / case), (4) compute log-prob assigned by the model to each, (5) score = % of pairs where model prefers grammatical. Per BLiMP convention: > 0.85 accuracy = solid grammatical knowledge; 0.5 = chance.
>
> **Yoruba-specific phenomena** to probe:
> - **Tone-marked semantics** (the load-bearing one for Yoruba). Yoruba is a tone language; tone is lexical and grammatical. Per SKILL L111 anti-pattern: "NEVER strip diacritics before tone-language agreement probes. The agreement is in the diacritic." agreement_probes.md L67-74 gives the canonical pair: grammatical "Ọkọ̀ mi ti dé." (My boat has arrived.) vs ungrammatical "Ọkọ mi ti dé." (stripped tone — different word/meaning entirely). Build pairs for high vs low vs mid tone on the same skeleton.
> - **Subject-verb agreement** (universal phenomenon, agreement_probes.md L28).
> - **Aspect** (perfective vs imperfective markers — Yoruba uses pre-verbal markers ti, ń, máa, etc.).
> - **Pronoun-antecedent agreement** (universal, agreement_probes.md L29).
>
> **Critical caveat: no published BLiMP-Yoruba.** Per agreement_probes.md L84-92 status table, only English (BLiMP, SyntaxGym), French/German (CLAMS), Russian (BLiMP-RU), partial Mandarin/Hebrew exist; "Most others: NO — build your own". You will need to construct the probe set yourself, ideally with a Yoruba native speaker linguist; floor is 100-500 pairs per phenomenon. **Diacritic preservation** must be verified at every pipeline stage (storage, tokenization, model input) — strip-diacritics is a silent killer that turns your tone-agreement probe into a coin flip. Hand off to `magic-linguistic-eval` for benchmark integration.

**Assertions:**
- `must_contain_one ["agreement probe", "BLiMP", "minimal pair"]` → all three present — PASS
- `must_contain_one ["tone", "diacritic"]` → both present multiple times — PASS
- `must_contain_one ["100", "log-likelihood", "log probability"]` → "100 minimal pairs", "log-prob", "log-likelihood" via "log-prob" + accuracy threshold "> 0.85" — PASS (100 + log-prob; log-likelihood implied through "log-prob assigned by the model")
- `must_contain_one ["build your own", "must build", "no published BLiMP"]` → "no published BLiMP-Yoruba", "build your own", "construct the probe set yourself" — PASS

**4/4 PASS.**

**Baseline answer (no skill, simulated):**

> Standard ways to evaluate LLM grammatical knowledge: (1) compute perplexity on held-out Yoruba text; (2) acceptability judgment tasks where the model rates grammatical vs ungrammatical sentences; (3) downstream task performance (NER, POS, sentence classification) — if grammar is learned, these improve. For Yoruba specifically, you'd want a native speaker to construct test items. Be aware that lexical and grammatical signal can be entangled; controlled minimal-pair evaluation is best practice.

**Baseline assertion check:** assertion 1 borderline (would say "minimal-pair evaluation" — PASS); assertion 2 likely FAIL (no explicit tone / diacritic mention without prompting); assertion 3 borderline (no concrete "100" or "log-likelihood" specifically — generic "perplexity"); assertion 4 likely FAIL (no "build your own" framing, no awareness of BLiMP-Yoruba absence). Expected baseline: **1-2 / 4 PASS**.

**Delta verdict:** **HIGH.** Baseline reaches "use minimal pairs, get a native speaker", but misses the load-bearing Yoruba-specific risks: (a) diacritic stripping silently destroys the tone-agreement signal — this is the most common Yoruba NLP pipeline bug and the skill calls it out as a NEVER; (b) no published BLiMP-Yoruba exists, so the user must budget for probe-set construction (the skill quantifies the floor at 100-500 pairs per phenomenon); (c) > 0.85 accuracy is the BLiMP convention for "solid"; (d) parser-F1-on-LLM-output is conceptually wrong for autoregressive LMs (the inverse-of-baseline framing). Skill converts "evaluate grammar with minimal pairs and a native speaker" into a four-step protocol with named phenomena (tone-marked semantics, aspect, S-V agreement, pronoun-antecedent), a diacritic-preservation gate, a per-phenomenon size floor, and a benchmark threshold — all anchored to BLiMP/CLAMS literature.

## Live script execution evidence

```
$ python3 skills/magic-linguistic-syntax/scripts/ud_coverage.py Yoruba
{
  "language": "Yoruba", "iso639_3": "yor",
  "treebanks": ["YTB"], "total_sentences": 100,
  "training_viable": false,
  "notes": "Yoruba: tiny — eval only",
  "recommended_approach": "PUD-style treebank — EVAL ONLY (do NOT fine-tune); cross-lingual zero-shot for parsing",
  "snapshot_date": "2026-04-23"
}
→ exit code 0; load-bearing for Eval #1 (returns the exact NO + cross-lingual recommendation).

$ python3 skills/magic-linguistic-syntax/scripts/ud_coverage.py Khmer
{
  "language": "Khmer (Cambodian)", "iso639_3": "khm",
  "treebanks": [], "total_sentences": 0,
  "training_viable": false,
  "notes": "No UD treebank",
  "recommended_approach": "No UD treebank — cross-lingual zero-shot mandatory; document eval limitation"
}
→ exit code 0; load-bearing for Eval #2 (no UD → must transfer).

$ python3 skills/magic-linguistic-syntax/scripts/parser_transfer_advisor.py Yoruba
{
  ...
  "approach": "cross-lingual zero-shot",
  "transfer_source_candidates": [
    {"iso": "ibo", "rationale": "Same Niger-Congo family branch; close URIEL — but Igbo has no UD itself"},
    {"iso": "eng", "rationale": "English Latin script; URIEL ~0.62 — distant; expect ~50-60 UAS zero-shot"}
  ],
  "parser_tool": {"primary": "Trankit", "rationale": "Cross-lingual transfer; Trankit beats stanza on low-resource quality"},
  "agreement_probes_recommended": true,
  "anti_patterns": [
    "DO NOT fine-tune on PUD-style 1K test treebanks (eval leak)",
    "DO NOT pick source by treebank size alone — URIEL typological distance dominates",
    "DO NOT report parser F1 as proxy for LLM grammatical knowledge"
  ]
}
→ exit code 0; directly produces Eval #1's tool + transfer-source ranking.

$ python3 skills/magic-linguistic-syntax/scripts/parser_transfer_advisor.py Khmer
{
  ...
  "transfer_source_candidates": [
    {"iso": "vie", "rationale": "Geographic + tone-language proximity; Vietnamese has ~12K UD"},
    {"iso": "tha", "rationale": "Tai-Kadai SEA neighbor (no Thai UD however)"},
    {"iso": "eng", "rationale": "fallback distant"}
  ],
  "parser_tool": {"primary": "Trankit", ...}
}
→ exit code 0; directly answers Eval #2 with Vietnamese FIRST (typological preference over English size).
```

All four invocations exit 0; output is structured JSON consumable by orchestrator and directly load-bearing for the simulated eval responses.

## Defects observed

| ID | Severity | Location | Observation |
|---|---|---|---|
| D1 | P3 (discoverability) | SKILL.md (no link to canonical_sources.md) | The 37-L canonical_sources.md (with 17 named refs across UD, parser tools, transfer, BLiMP-style, foundational syntax) is not surfaced from SKILL.md. Agents will not discover it. Add a `## Refresh / canonical sources` section linking it (cf. how magic-linguistic-bitext same-iter has the same defect; same fix pattern). |
| D2 | P3 (calibration metadata) | parser_transfer_advisor.py L19-43 vs SKILL L67 + parser_transfer.md L11-17 | The script ranks sources but does not invoke magic-linguistic-scope's URIEL distance API — `_TRANSFER_SOURCES` is a hand-curated dict with rationales as strings ("URIEL ~0.62"). SKILL body says "Pull URIEL distances from magic-linguistic-scope" (L67) — this is documentation only; the script doesn't actually do it. Either label as "cached" honestly or wire the call. |
| D3 | P3 (redundancy) | SKILL L93-103 vs L126-136 | Output Format template appears twice — once in Step 6 (L93-103) and once in the bottom Output Format section (L126-136). Slightly different wording. Pick one canonical location. |
| D4 | P3 (style) | ud_treebanks.md L32 | "Yoruba YTB | 100 sentences (?!) | NO" — the (?!) is honest but reads as informal in a reference doc. Drop the punctuation; the size speaks for itself. |
| D5 | P2 (no probe-builder) | scripts/ (missing third script) | Step 5 mandates ≥ 100 minimal pairs per phenomenon, but no script exists to scaffold this (compare magic-linguistic-bitext which has both alignment_score.py and synthetic_bitext_recipes.py covering its two main steps). A `probe_builder.py --language yor --phenomenon tone --n 100` would close the loop and lift D8. |

None block shipping. D1-D2 should be reconciled before any external publication.

## Verdict

**SHIP** as `iter-2-live`. Honest live measurement (102) sits +1 vs iter-1 simulated (101), within calibration noise. All Phase-1 per-dim floors clear (D1=17≥15, D3=13≥10, D4=13≥13 exactly, D5=13≥12). Knowledge delta is HIGH on Eval #3 (skill unlocks tone-diacritic-preservation NEVER + no-published-BLiMP-Yoruba calibration + 4-step probe protocol that baseline misses entirely on assertions 2 and 4) and MODERATE on Eval #1 (baseline gets "don't overfit, transfer instead" right but misses the agreement-probe alternative — assertion 3 — which is the load-bearing LLM-eval pivot). Five minor defects flagged for follow-up; none block ship. Optional Phase-2 levers projected to lift to 106-108: (1) link canonical_sources from a Refresh section (D5+1); (2) collapse duplicate Output Format blocks + add worked end-to-end Yoruba example (D2+1, D8+1); (3) add probe_builder.py third script (D7+1, D8+1); (4) wire parser_transfer_advisor.py to actually call magic-linguistic-scope URIEL or label as cached (D2+1).
