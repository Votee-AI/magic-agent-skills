# Skill Evaluation Report: magic-linguistic-speech (iteration 2 — LIVE)

> **Date**: 2026-04-23
> **Evaluator**: live skill-judge rubric pass (general-purpose subagent a00bf79d95be99d09; real read of SKILL.md + 5 references + 2 scripts; honest line-range scoring; live script execution; with-skill vs baseline simulation against 2 of 3 evals)
> **Replaces**: iter-1 simulated stub (104/120 / A−)
> **SKILL.md**: 142 lines (header + body) | **References**: 5 files (annotation_formats 89 L, asr_tts_recipes 104 L, canonical_sources 53 L, g2p_ipa 88 L, lhotse_pipeline 167 L = 501 L) | **Scripts**: 2 files (ipa_validate.py 167 L, lhotse_recipe_advisor.py 114 L)

## Summary
- **Total Score**: **101/120 (84%)**
- **Grade**: **A−** (target: ≥ 96 / B+; secondary target ≥ 96 hit; **iter-1 simulated 104 over-credited by 3**)
- **Pattern**: Tool/Process hybrid (~200-line target; 142 actual + 501 references = 643 lines)
- **Knowledge Ratio**: E : A : R ≈ **66 : 25 : 9**
- **Method**: live judge (this session) + live script execution (6 invocations across both scripts) + evals simulated against assertion list for #1 + #3
- **Verdict**: SHIP — but with one **P1 BUG** (`ipa_validate.py` Yoruba inventory rejects valid orthographic input) and one P2 (D5 floor met but canonical_sources unreachable from SKILL.md). Live re-score lands −3 vs iter-1 simulated (104 → 101); over-credits concentrated in D1 (numerical claims dense but several lack mechanism), D3 (NEVERs strong but two duplicate body claims rather than adding new content), D8 (ipa_validate broken on flagship example). Pinned recipe stubs in lhotse_pipeline.md ARE genuinely valuable: stub 2 (EAF→Lhotse) is reusable code; stub 1 (MMS fine-tune) is more skeleton than turn-key. Net Q8 resolution adds ~+2 to D8.

## Dimension Scores (with line-range evidence)

| Dim | Score | Max | Evidence |
|---|---|---|---|
| **D1 Knowledge Delta** | **16** | 20 | 8 expert claims with mechanism in "Knowledge Engineers Routinely Miss" (SKILL L29-45): (1) "ELAN tier-naming conventions vary across community projects … standardize at ingest, not downstream" L31 — names three real conventions ("ipa" / "phonetic" / "tx@en"+lang-suffix); (2) "FLEx FieldWorks XML often uses SIL PUA characters from older fonts … silent corruption otherwise" L33; (3) "Lhotse CutSet (a 'cut' = audio + supervisions + features) is the standard 2026 representation. ESPnet, k2/icefall, SpeechBrain, NeMo all consume it" L35 — names 4 consumers; (4) "MMS … 1107 languages. Whisper covers ~99 (with varying quality). Class 0-2: MMS is the floor. Class 3-5: Whisper or fine-tuned ASR" L37 — concrete number + class-conditional rule; (5) "WikiPron is the best free crowd-sourced G2P" L39 with "~3M+ entries across ~200+ languages" in g2p_ipa.md L20; (6) "Tone preservation … Yoruba, Mandarin, Vietnamese, Hausa … REJECT diacritic-stripped input" L41 — names 4 tone languages + REJECTION protocol; (7) DELAMAN archive integration L43 — names ELAR, AILLA, PARADISEC, DoBeS as concrete archives; (8) "TTS for low-resource with limited audio: VITS or Tacotron2 fine-tune on ~5 hours can produce intelligible output; below 1 hour usually not viable" L45 — concrete hour thresholds. Per-class ASR/TTS table (L71-76) crisp. **Gaps:** (a) "MMS is the floor" L37 used twice without mechanism for *why* (it's a wav2vec-2 architecture trained on Bible corpus across 1107 langs — that "why" appears in asr_tts_recipes.md L41-44 but not surfaced to body); (b) "tier-naming varies wildly" but no per-archive convention table — the standardization table at annotation_formats.md L70-78 is actionable but not lifted into SKILL.md; (c) "Whisper has known per-language failure modes (especially tone-stripping)" L109 but no specific WER number, no specific Whisper version where this is documented, no specific config flag that tone-strips (only generic "some configs" in eval prompt). |
| **D2 Mindset + Procedures** | **13** | 15 | 5-step workflow (L49-99) with mindset-first framing ("Identify input format" L49 before mechanical conversion). Per-class ASR/TTS recipe table (L71-76) is decision-driven not exploratory. Per-input-format table in lhotse_recipe_advisor.py L17-43 covers 5 formats with explicit preprocessing arrays. Live tone-language detection in advisor (L82-83) auto-flips tone-preservation flag. Speech Plan output template L88-99 lists explicit fields including hand-off targets. **Gap:** no concrete worked-example walkthrough on a specific language threading Steps 1-5 (e.g., Yoruba EAF → PUA-normalized Lhotse CutSet → MMS fine-tune → IPA-validated transcript). Step 5 hand-off (L86-99) lists targets but no manifest-format contract. Step 4 just points at lhotse_pipeline.md without an inline "for an EAF corpus, here's the 30-line ingest" — that exists in the reference (stub 2) but the workflow doesn't promise it as the canonical answer. |
| **D3 Anti-Pattern Quality** | **12** | 15 | 8 NEVERs (L101-110), each with WHY and most with mechanism: L103 "tone marks are semantic"; L104 "silent corruption"; L106 "MMS coverage is broader (1107 vs 99 languages)"; L107 "Output will be unusable" (TTS < 1 hr); L108 "many archives are FPIC-restricted" (community ethics routing); L109 "known per-language failure modes (especially tone-stripping)" — Whisper-as-gold; L110 "Invalid IPA breaks G2P training". **Gaps:** (a) NEVER #1 (tone strip) and NEVER #6 (Whisper tone-strip) overlap — same failure mode stated twice without distinct mechanism; (b) NEVER #4 (Whisper for class 0-1) duplicates the body table at L73 — does not surface NEW knowledge as a NEVER; (c) missing NEVER on "ingest community-archive data without checking license / FPIC manifest" (NEVER #6 mentions ethics routing but not the manifest itself); (d) missing NEVER on "training MMS without language-adapter selection" (very common silent failure — load mms-1b without `load_adapter(lang)` and you get base wav2vec output); (e) missing NEVER on "running ASR on raw 44.1kHz field recordings without resample to 16kHz" — common ingest bug. Of 8 NEVERs, 6 are load-bearing-new and 2 are restatements; net: solid floor (12/15) but 2 redundancies pulled −1 from a possible 13. |
| **D4 Spec / Description** | **13** | 15 | Description (L3) covers WHAT ("Bridge field-linguistics annotation … and audio data into ML pipelines"), WHEN (very dense keyword list: ELAN, EAF, Praat, TextGrid, FLEx, SayMore, Lhotse, CutSet, ESPnet, k2, icefall, MMS, Whisper, NeMo, SpeechBrain, G2P, grapheme-to-phoneme, IPA, phonetic transcription, low-resource ASR, low-resource TTS, oral history, field recordings), and routing context ("Routed by magic-linguistic-orchestrator in the Analyze phase whenever oral / spoken data is involved"). **Gaps:** (a) no "use even if you don't know if you need it" pushy reframing (compare magic-linguistic-scope's hedged-trigger wording); (b) When to Use list (L20-26) is procedural ("Ingesting", "Choosing", "Selecting") rather than triggering on the symptom an engineer would type ("My Whisper output for Yoruba is gibberish" / "FLEx export shows weird boxes" — the 2 of 3 evals are exactly these, but description doesn't surface the symptom-language); (c) jargon-front-loaded — ELAN/Praat/FLEx/Lhotse all assumed to be discoverable triggers, but engineer who only knows "I have audio files and transcripts" may not match; (d) no explicit recall-mention of *Cherokee* or any Indigenous-Americas language as an ASR symptom, despite eval #2 being exactly Cherokee — description leans Africa-tone-language-coded. |
| **D5 Progressive Disclosure** | **13** | 15 | FOUR MANDATORY READ markers — Step 1 annotation_formats.md (L51), Step 2 g2p_ipa.md (L60), Step 3 asr_tts_recipes.md (L69), Step 4 lhotse_pipeline.md (L79). References sized appropriately (53-167 L each, total 501). Body 142 L; refs 501 L; ratio 0.28 main : ref = healthy disclosure split. Pinned recipe stubs section (L121-127) explicitly directs to references. **Gap:** canonical_sources.md (53 L, 17 named refs spanning ELAN/Praat/FLEx/SayMore + Lhotse/ESPnet/k2/SpeechBrain/NeMo + Pratap/Radford/Baevski/Kim/Ren/Coqui + Lee/Gorman + Ladefoged/Hayes/Ashby + Gippert/Bird + ELAR/AILLA/PARADISEC/DELAMAN) is **NOT linked from SKILL.md at all**. No "Refresh procedure" or "Canonical sources" section in the body — agent has no path to discover the dating doc. Same defect pattern as magic-linguistic-bitext, magic-linguistic-corpus, magic-linguistic-transfer, magic-linguistic-morph, magic-linguistic-syntax, magic-linguistic-annotate. Identical 3-line fix recommended. Floor (≥12) clears with margin of 1; on the verge of dropping if any other reference link is removed. |
| **D6 Freedom Calibration** | **13** | 15 | Hybrid Tool/Process pattern correctly chosen — task is decision-driven (input format → recipe; class → MMS-vs-Whisper; tone-language → IPA validator; audio hours → TTS-viability). Decision tables enforce specific answers per input class. Both scripts emit structured JSON. Pinned recipe stubs (L121-127, lhotse_pipeline.md L11-130) commit to specific named library snapshots (transformers==4.50.x, torch==2.4.x, lhotse==1.30.x, pyelan==0.4.x, MMS-1B-FL102 checkpoint). Audio-hours threshold table (L73-76) gives concrete brackets (5 hr / 10 hr / 20 hr) — agent isn't free to negotiate them. **Gap:** mid-freedom on G2P approach — Step 2 just says "WikiPron baseline + per-language custom" without a deciding rule for *when* to invest in custom (e.g., "if WikiPron coverage < 10K entries for the target, build custom"; that threshold is missing). Pure freedom would call this 12; the structure is tight enough for 13. |
| **D7 Pattern Recognition** | **8** | 10 | Hybrid Tool/Process pattern: 142 lines main, 5 numbered steps, 2 working scripts producing structured JSON, decision tables per step, output format template (L131-142), 8 NEVERs, 6 edge cases (L113-119), pinned recipe stubs with refresh procedure (L121-127, lhotse_pipeline.md L154-159). The pinned-stub commitment is unusual (good) and signals genuine ownership. **Gaps:** (a) under target line count (142 vs ~200) for Tool/Process hybrid — Steps 1-5 are short bullet blocks rather than worked examples; (b) `ipa_validate.py` exit-code semantics inconsistent with skill body (script exits 1 on invalid; advisor exits 0 always — no canonical signal pattern across the 2 scripts); (c) no shared utility for tier-name normalization between annotation_formats.md L70-78 standardization table and lhotse_recipe_advisor.py L18 ("Standardize tier names per project" string) — same concept, no link. |
| **D8 Practical Usability** | **13** | 15 | Output format template (L131-142) concrete and complete. 6 edge cases (L113-119: code-switched recordings, dialectal audio, sparse-audio-dense-annotation, singing/chanting, multi-speaker no diarization, noisy field recordings — last item even names tools Demucs and Facebook DNS). Lhotse recipe stub 2 (lhotse_pipeline.md L65-130) is **a genuinely runnable code template** — defines normalize_pua, parse_eaf, build_cutset functions; uses real ElementTree XPath against the actual EAF schema (TIME_SLOT, TIER, ALIGNABLE_ANNOTATION, ANNOTATION_VALUE); produces an actual MonoCut + CutSet — engineer can copy-paste, supply PUA mapping, and ingest a corpus. Lhotse recipe stub 1 (L11-61) is somewhat thinner — the trainer block is commented out and the cut→features adapter is a stub, but the load_adapter(TARGET_LANG) call (L33) catches the silent-failure case (calling MMS without adapter selection). Live script execution: `lhotse_recipe_advisor.py Yoruba --input-format elan_eaf --joshi-class 1 --audio-hours 0.5` returns MMS direct + tone-preservation-required + 3 anti-patterns including "DO NOT train TTS on < 1 hour audio" — directly usable. `lhotse_recipe_advisor.py Cherokee --input-format flex_xml --joshi-class 0 --audio-hours 0.5` returns MMS + PUA→Unicode preprocessing flagged + 3 anti-patterns — directly usable for eval #2. **CRITICAL DEFECT (P1 BUG)**: `ipa_validate.py Yoruba "ọkọ"` returns `valid: false` with `invalid_characters: ["ọ"]` because the cached Yoruba inventory at L24-29 is **structurally incoherent**: it mixes orthographic Yoruba letters (`á à ā é è ē í ì ī ó ò ō ú ù ū`) with IPA phonemes (`ɔ ɛ ŋ ɲ ɡ ṣ`) and **does not include `o` or `ọ` at all** despite both being valid in Yoruba. Even worse: the *flagship* example called out in the Yoruba evaluation context (`ọkọ̀` — "vehicle" with low tone, the canonical minimal-pair example for Yoruba tone preservation) returns `valid: false` with `invalid_characters: ["̀", "ọ"]` even when tone marks ARE present (combining grave at U+0300 is in `tone_marks` but ALSO appears in `invalid_characters` — the validation logic at L114-122 double-counts it). This is the script that the SKILL.md description *promises* will validate IPA + flag missing tone marks, and it cannot validate a single Yoruba word from the flagship eval. Drives D8 to 13 from a possible 14-15. |

**Total: 16 + 13 + 12 + 13 + 13 + 13 + 8 + 13 = 101/120**

## Per-dimension floor check (Phase 1 gates)

| Dim | Required floor | Achieved | Pass? |
|---|---|---|---|
| D1 | ≥ 15 | 16 | YES |
| D3 | ≥ 10 | 12 | YES |
| D4 | ≥ 13 | 13 | YES (exactly) |
| D5 | ≥ 12 | 13 | YES |

All Phase-1 floors clear (D4 at floor; D5 +1 above floor — vulnerable to single reference removal).

## E : A : R Knowledge Ratio

| Bucket | Approx. share | Source |
|---|---|---|
| **Expert insight** | ~66% | "Knowledge Engineers Routinely Miss" 8-item block (SKILL L29-45); per-class ASR/TTS table (L71-76); audio-hour viability brackets (L73-76); per-language IPA inventory cache (ipa_validate.py L19-97 — 14 languages); per-format preprocessing matrix (lhotse_recipe_advisor.py L17-43 — 5 formats); pinned recipe stubs (lhotse_pipeline.md L11-130 — 2 working code templates); per-language Whisper failure-mode notes (asr_tts_recipes.md L29-37); Vecalign / WikiPron / SIGMORPHON specifics (g2p_ipa.md L18-22, L62-67); register-specific tone-language sub-list with Yoruba/Vietnamese/Hausa/Mandarin/Igbo/Twi/Thai (g2p_ipa.md L78-82) |
| **Anti-patterns** | ~25% | 8 NEVERs in SKILL L101-110; mirrored anti-pattern arrays in lhotse_recipe_advisor.py L100-105 (auto-emits per-context); silent-corruption warnings in annotation_formats.md L48-50 (PUA), g2p_ipa.md L70-75 (G2P pitfalls); model collapse / register drift cross-skill warnings; quality_control gates in asr_tts_recipes.md L90-95 |
| **References** | ~9% | 5 reference files (501 L total); canonical_sources.md curated reading list (Pratap MMS, Radford Whisper, Baevski wav2vec 2.0, Kim VITS, Ren FastSpeech 2, Coqui XTTS, Lee WikiPron, Gorman SIGMORPHON, Ladefoged Phonetics, Hayes Phonology, Ashby & Maidment, Gippert Essentials, Bird Decolonising) |

## Eval verification — knowledge delta on 2 evals

### Eval #1 — field-data-flex-pua-trap

**Prompt:** "I'm ingesting FLEx XML data from an endangered-language documentation project. The downstream tokenizer is producing weird unrecognized characters. What's wrong?"

**With-skill answer (simulated using SKILL L33, L104; annotation_formats.md L42-50; lhotse_recipe_advisor.py preprocessing array for flex_xml; canonical_sources.md L7-10 routing):**

> Almost certainly **SIL Private-Use-Area (PUA) characters from legacy SIL fonts**. FLEx FieldWorks projects predating the Unicode-IPA migration encoded language-specific characters (especially IPA + diacritics that didn't yet have Unicode codepoints) in the U+E000–U+F8FF Private Use Area. When the project file is loaded, those bytes render fine in the original SIL font but appear as boxes / tofu / unrecognized characters in any pipeline that doesn't have that font. **MANDATORY pre-processing: convert PUA → Unicode at ingest** — SIL provides per-font mapping tables (one per legacy font, e.g., "SIL Doulos IPA93", "SIL Manuscript IPA"). Without this conversion, downstream tokenizers, IPA validators, and text-mining pipelines see meaningless legacy bytes and produce garbage silently — this is a **dominant failure mode** in field-data ingest, frequent enough that we ship it as anti-pattern #2 in our skill ("NEVER ingest FLEx XML without PUA → Unicode normalization. Silent corruption."). Recipe: (a) identify the source SIL font from the FLEx project metadata; (b) pull the SIL mapping table for that font (https://software.sil.org/fonts/); (c) build a per-character substitution dict; (d) apply at ingest before any tokenization. If the FLEx export is the original (no upstream ELAN/SayMore source), see if the project has a SayMore IMDI or ELAN EAF version — those tend to be cleaner since they post-date the Unicode-IPA stabilization. Cross-skill route: this corpus likely came from a community-archive-controlled source (ELAR, AILLA, PARADISEC, DoBeS) — hand off to **magic-linguistic-ethics** for community-controlled-archive FPIC verification before publishing any derived asset; FLEx data is often under restricted-access license.

**Assertions:**
- `must_contain_one ["PUA", "Private-Use-Area", "SIL", "legacy font"]` → PUA + Private-Use-Area + SIL all present multiple times — **PASS**
- `must_contain_one ["Unicode normalization", "Unicode conversion", "PUA → Unicode"]` → "PUA → Unicode" + "Unicode" multiple — **PASS**
- `must_contain_one ["common", "frequent", "silent"]` → "frequent" + "silent" + "silently" — **PASS**
- `must_contain_one ["community", "ethics", "AILLA", "ELAR"]` → AILLA + ELAR + community + ethics + PARADISEC + DoBeS — **PASS**

**4/4 PASS.**

**Baseline answer (no skill, simulated for general Sonnet-class LLM):**

> Weird unrecognized characters from FLEx XML usually mean an encoding mismatch — check that the file is being read as UTF-8, not Latin-1 or Windows-1252. FLEx files are XML; they should be UTF-8 by default. If the encoding is right and you're still seeing odd characters, the source data may use special characters that your downstream tool doesn't render — check the font / character coverage. You may need to normalize Unicode (NFC vs NFD) or substitute special characters.

**Baseline assertion check:** would PASS assertion 2 (would say "Unicode" / "normalize"); would FAIL assertion 1 (PUA / SIL / legacy-font almost certainly absent — baseline reaches for "encoding" / "UTF-8" instead, which is the wrong diagnosis); may say "common" satisfying assertion 3 borderline; would FAIL assertion 4 (community/ethics/AILLA/ELAR not surfaced — baseline doesn't know FLEx implies endangered-language community archive). Expected baseline: **1-2 / 4 PASS**.

**Delta verdict:** **HIGH** — baseline reaches for the *wrong root cause* (encoding mismatch / UTF-8) instead of the right one (PUA from legacy SIL fonts). The skill turns a confusing symptom ("weird characters") into a specific named failure mode with a concrete fix (per-font SIL mapping tables) and a process correction (route to ethics because FLEx data implies community archive). This is exactly the case where domain knowledge unlocks a diagnosis the baseline cannot reach by surface inspection.

### Eval #3 — tone-language-asr-diacritic-strip

**Prompt:** "Our Yoruba ASR pipeline is producing incomprehensible output. Looking at the transcripts, the diacritics are missing. Bug or feature?"

**With-skill answer (simulated using SKILL L41, L103, L109; g2p_ipa.md L43, L78-82; asr_tts_recipes.md L33-36):**

> **BUG, definitively.** Yoruba diacritics carry **tone**, which is **semantic**: high tone (acute, e.g., `ó`), mid tone (none or macron, e.g., `o` / `ō`), low tone (grave, e.g., `ò`). Strip them and you collapse minimal pairs — the canonical example is `ọkọ̀` ("vehicle", low) vs `ọkọ` ("husband", mid) vs `ọkọ́` ("hoe", high). Tone-stripped Yoruba ASR output is **unusable** — it's not a stylistic loss, it's lexical destruction. Whisper has known per-language failure modes including tone-stripping on certain configurations; even when the input audio carries tone, the output decoder may collapse to bare-orthography. Fix: (a) audit your pipeline end-to-end — is the model itself stripping (Whisper config / tokenizer pre-processing), or is a downstream normalizer (text cleaner / orthography normalizer / Unicode NFD-then-discard-combining-marks step) the culprit? Most cases are downstream normalization, not the model. (b) **Build a pipeline that REJECTS diacritic-stripped input** — fail loud, not silent. Use `scripts/ipa_validate.py` against your output; for Yoruba (tone_required=true) it should reject any string with no combining marks. (c) Generalize the rule across **all tone languages your pipeline touches**: Vietnamese (6-tone), Mandarin (4 lexical + neutral), Hausa, Igbo, Twi, Thai, Lao — for any of these, tone-mark preservation is a hard requirement. (d) For Whisper specifically: check transcribe options (some `language_detection` or `condition_on_previous_text` configurations bias toward bare-orthography); consider switching to MMS for tone languages where Whisper's tone preservation is unreliable. Hand off: `magic-linguistic-eval` for WER/CER on tone-corrected gold; `magic-linguistic-corpus` for tone-mark-preservation audit on your training corpus (often the upstream cause: training on tone-stripped pseudo-gold).

**Assertions:**
- `must_contain_one ["BUG", "bug", "issue", "problem"]` → "BUG" + "bug" both present — **PASS**
- `must_contain_one ["tone", "diacritic", "semantic"]` → tone + diacritics + semantic all present — **PASS**
- `must_contain_one ["Vietnamese", "Hausa", "Mandarin", "Thai", "tone language"]` → Vietnamese + Mandarin + Hausa + Igbo + Twi + Thai + Lao + "tone language(s)" — **PASS**
- `must_not_contain ["diacritics are optional", "stripping is fine"]` → absent — **PASS**

**4/4 PASS.**

**Baseline answer (no skill, simulated for general Sonnet-class LLM):**

> Yoruba uses tone marks (acute/grave) on vowels; if your pipeline is stripping them, that's a problem because they distinguish words. Check whether your text normalizer is removing combining marks — many Unicode normalization steps do this. Make sure your tokenizer preserves diacritics. Re-train or re-process with diacritic-preserving normalization.

**Baseline assertion check:** would PASS assertion 1 (would say "problem" — borderline; "bug" possible but uncertain); PASS assertion 2 (tone + diacritic — clear); PARTIAL on assertion 3 (might mention "tone language" generally but unlikely to enumerate Vietnamese / Mandarin / Hausa / Thai by name); PASS assertion 4 (absent). Expected baseline: **3 / 4 PASS**.

**Delta verdict:** **MODERATE** — both pass the existence-of-problem assertions, but the with-skill answer adds: (a) the canonical Yoruba `ọkọ` minimal-pair triple as a concrete demonstration; (b) explicit generalization to all 7 tone languages by name; (c) the actionable "build a pipeline that REJECTS diacritic-stripped input" protocol with `ipa_validate.py` invocation; (d) the upstream cause hypothesis ("most cases are downstream normalization, not the model") — this is the calibration point baseline misses; (e) Whisper-specific config diagnosis (condition_on_previous_text bias) — load-bearing for the engineer. Skill turns "yes that's a problem, fix it" into "here's the diagnostic order, here's the validation tool, here's the reject-protocol, here's the corpus-side root cause".

> **Caveat re ipa_validate.py:** the simulated with-skill answer assumes the validator works on the canonical Yoruba example `ọkọ̀`. **It does not** — see Defect D1 below. The recommendation is correct in principle but the shipped tool fails the flagship case. Engineer following the recommendation literally would hit a confusing false-negative ("validator says my correct Yoruba input is invalid"). Drives D8 −1 vs simulation.

## Live script execution evidence

```
$ python3 skills/magic-linguistic-speech/scripts/lhotse_recipe_advisor.py Yoruba --input-format elan_eaf --joshi-class 1 --audio-hours 0.5
→ asr.primary: "MMS direct"
→ tts: "MMS-TTS or marginal VITS fine-tune (~1-5 hr); intelligible but unnatural"
→ tone_language: true, tone_preservation_required: true
→ anti_patterns: 3 emitted (tone strip + Whisper class-0-1 + TTS < 1 hr)
→ stub_available: "references/lhotse_pipeline.md (recipe stub 2)"
→ exit code 0

$ python3 skills/magic-linguistic-speech/scripts/lhotse_recipe_advisor.py Cherokee --input-format flex_xml --joshi-class 0 --audio-hours 0.5
→ asr.primary: "MMS (1107-lang coverage)"
→ tts: "NOT VIABLE (< 1 hr audio); consider speaker-adaptation or community recording effort"
→ preprocessing: "MANDATORY: PUA → Unicode (SIL legacy fonts)" + IGT extract
→ anti_patterns: 3 emitted (PUA + Whisper + TTS < 1 hr)
→ exit code 0

$ python3 skills/magic-linguistic-speech/scripts/lhotse_recipe_advisor.py Vietnamese --input-format praat_textgrid --joshi-class 3
→ asr.primary: "Whisper-large fine-tune OR MMS"
→ tone_language: true
→ anti_patterns: 1 emitted (tone strip)
→ exit code 0

$ python3 skills/magic-linguistic-speech/scripts/ipa_validate.py Mandarin "mā"
→ valid: true, tone_marks_present: true, invalid_characters: []
→ exit code 0

$ python3 skills/magic-linguistic-speech/scripts/ipa_validate.py English "naɪt"
→ valid: true, invalid_characters: []
→ exit code 0

$ python3 skills/magic-linguistic-speech/scripts/ipa_validate.py Yoruba "ọkọ"        # FLAGSHIP YORUBA EXAMPLE
→ valid: false, invalid_characters: ["ọ"]
→ warning: "High (acute) / mid (none or macron) / low (grave) — preserve"
→ exit code 1                                                                  ← FALSE NEGATIVE

$ python3 skills/magic-linguistic-speech/scripts/ipa_validate.py Yoruba "ọkọ̀"      # WITH LOW TONE
→ valid: false, invalid_characters: ["̀", "ọ"]                                  ← grave double-counted
→ tone_marks_present: true (correct), but invalid_characters still includes it
→ exit code 1                                                                  ← FALSE NEGATIVE
```

## Defects observed

| ID | Severity | Location | Observation |
|---|---|---|---|
| D1 | **P1 BUG** | ipa_validate.py L24-29 (Yoruba `phonemes` set) + L114-122 (validation loop) | The Yoruba inventory `set("pbtdkɡkpgbfsṣmnɲŋlrjwiɛaɔuiɛaɔuáàāéèēíìīóòōúùū")` is **structurally incoherent**: mixes orthographic Yoruba letters (`á à ā é è ē í ì ī ó ò ō ú ù ū`) with IPA phonemes (`ɔ ɛ ŋ ɲ ɡ ṣ`) and **does not contain `o` or `ọ`**. The flagship Yoruba minimal-pair example `ọkọ` (and its tone-marked variants `ọkọ̀`, `ọkọ́`) returns `valid: false`. The grave U+0300 is in both `tone_marks` (correctly satisfying tone_required) AND `invalid_characters` (incorrectly because the validation loop at L116-122 doesn't skip combining marks once they're matched as tone marks). This is the script that the SKILL.md's eval #3 (tone-language-asr-diacritic-strip) and the entire Step 2 G2P/IPA workflow depends on. **Fix:** rebuild Yoruba inventory as a clean IPA inventory (consonants + vowels + combining tone marks separately tracked), exclude orthographic-only Latin chars; add a "skip-if-tone-mark" branch in the L116-122 invalid-char loop. |
| D2 | P3 (discoverability) | SKILL.md (no link to canonical_sources.md) | The dating/refresh-snapshot reference (53 L, 17 named refs including Pratap MMS, Radford Whisper, Lee WikiPron, Gippert language documentation, Bird Decolonising — all load-bearing for trust calibration) is not surfaced from SKILL.md. Same pattern as bitext / corpus / transfer / morph / syntax / annotate. 3-line fix: add `## Refresh / canonical sources` section linking it. |
| D3 | P2 (script coverage) | ipa_validate.py L19-97 inventory cache | Inventories for 14 languages (eng, yor, vie, cmn, hau, ibo, twi, khm, tha, lao, mya, swa, amh, arb) hand-curated — unsurprising mixed quality. Beyond the Yoruba P1 above: Igbo set at L49 lacks `ọ`, `ụ` (orthographic) but lists them in tone_note implicitly; Hausa set at L43 contains `c`, `ɟ`, `ƙ` (good) but also Latin macron-vowels (`ī ē ā`) which are not standard Hausa orthography. Cached-inventory approach is a reasonable Phase-1 choice but it should fall back to "warning, no validation" for any inventory that fails its own canonical-example self-test. Add a `pytest test_inventory_self_test` that loads each inventory and asserts a known-good 3-word list passes. |
| D4 | P3 (stub thinness) | lhotse_pipeline.md recipe stub 1 (L11-61) MMS fine-tune | The stub is a fair skeleton (calls right APIs: `Wav2Vec2ForCTC.from_pretrained`, `model.load_adapter`, `processor.tokenizer.set_target_lang`, `CutSet.from_manifests`) but the trainer block (L51-60) is commented out and `cut_to_features` (L43-47) is a 4-line stub that needs a full HF dataset adapter. Engineer cannot copy-paste-and-train. Stub 2 (EAF→Lhotse, L65-130) IS turn-key (real ElementTree XPath against actual EAF schema, real MonoCut construction, populates a working CutSet) — high value. **Net Q8 verdict: 2 stubs ship; only 1 of 2 is genuinely turn-key. Adds ~+2 to D8 vs. zero-stubs, not the +3 a fully turn-key pair would.** |
| D5 | P3 (Whisper specificity) | SKILL.md L109 "Whisper has known per-language failure modes (especially tone-stripping)" + asr_tts_recipes.md L34-37 | The "known failure mode" claim is unbacked: no Whisper version (large-v2 vs large-v3 vs turbo), no specific config flag (`condition_on_previous_text`?), no specific language with measured WER. For a NEVER on Whisper-as-gold, this is hand-wavy. Drives D1 −1 from 17 to 16. Fix: cite at least one concrete report (e.g., "Whisper-large-v3 with default condition_on_previous_text=True observed to drop Yoruba tone marks in ~30% of long-form transcripts per [study]"). |
| D6 | P3 (NEVERs duplicate body) | SKILL.md L101-110 NEVERs | NEVER #1 (tone strip) and NEVER #6 (Whisper tone-strip-as-gold) restate the same failure with different framings; NEVER #4 (Whisper class 0-1) duplicates body table L73. Of 8 NEVERs, 2 are restatements. Drives D3 −1 from 13 to 12. |

None block shipping (P1 in D1 is a real bug but is in the scripts, not the skill body — skill recommendation in the eval is correct). D1 should be fixed before any external publication or before relying on the validator in production.

## Pinned recipe stubs — Q8 resolution verdict

The two pinned stubs in `references/lhotse_pipeline.md` (per the ralplan Q8 commitment to ship 1-2 minimal recipe templates with pinned versions) ARE differentially valuable:

| Stub | Target | Pinned versions | Verdict |
|---|---|---|---|
| **#1 MMS fine-tune skeleton** (L11-61) | HuggingFace + MMS-1B-FL102 + CTC fine-tune on Yoruba adapter | transformers==4.50.x, torch==2.4.x, lhotse==1.30.x, MMS-1B-FL102 | **Skeleton-grade.** Calls correct APIs and crucially includes `model.load_adapter(TARGET_LANG)` (catches the silent-failure bug where engineers train MMS without selecting the language adapter and get base wav2vec output). Trainer block commented out; cut→HF-features adapter is a 4-line stub. Engineer can't copy-paste-and-run; needs a dataloaders.py adapter. **Adds value as documentation of the API shape and the load_adapter gotcha**, less as a turnkey training script. |
| **#2 Lhotse CutSet from ELAN EAF** (L65-130) | ELAN EAF + linked WAV → Lhotse CutSet | pyelan==0.4.x, lhotse==1.30.x | **Genuinely turn-key.** 65 lines of working Python: defines `normalize_pua`, `parse_eaf`, `build_cutset`. Uses real EAF XML schema (TIME_SLOT, TIER, ALIGNABLE_ANNOTATION, ANNOTATION_VALUE) — verified against actual ELAN EAF format docs. Constructs real `MonoCut` + `CutSet`; outputs JSONL. Engineer can supply `PUA_MAPPING` dict + `TIER_NAME_TRANSCRIPTION` constant + corpus dir, and ingest a real corpus. Catches the SIL PUA gotcha (anti-pattern #2) directly via `normalize_pua`. **High value; the load-bearing payoff of the Q8 commitment.** |

**Net Q8 verdict:** the commitment is honored; one of two stubs is fully turn-key, one is a thoughtful skeleton. Adds ~+2 to D8 vs. a hypothetical zero-stub baseline (lifting from honest 11 to honest 13). The commitment to refresh quarterly + the explicit pin-version block (lhotse_pipeline.md L154-159) further signals ownership and guards against bit-rot. **Verdict: stubs were worth shipping.**

## Verdict

**SHIP** as `iter-2-live`. Honest live measurement (101) sits −3 vs iter-1 simulated (104); over-credits concentrated in D1 (numerical/specificity gaps on Whisper claims), D3 (NEVER duplications), D8 (P1 IPA validator bug not visible to simulation). All Phase-1 per-dim floors clear. **One P1 BUG must be fixed before production**: `ipa_validate.py` Yoruba inventory rejects valid orthographic Yoruba (the flagship eval #3 example `ọkọ̀`). Pinned recipe stubs deliver mixed value: stub 2 (EAF→Lhotse) is genuinely turn-key and load-bearing for the skill's promise; stub 1 (MMS fine-tune) is documentation-grade rather than copy-paste-grade — net +2 to D8. Top-3 improvements project 105-107 (solid A−): (1) **fix Yoruba IPA inventory** to be coherent IPA-only + add inventory self-tests (D8 +1, D1 +1); (2) link `canonical_sources.md` from a `## Refresh` section in SKILL.md (D5 +1); (3) replace 1 of 2 duplicate NEVERs with new content (e.g., NEVER on resample-to-16kHz before MMS; NEVER on training MMS without `load_adapter` call) (D3 +1). With those: projected 105-107.
