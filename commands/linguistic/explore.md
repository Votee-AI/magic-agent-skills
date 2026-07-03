---
description: Investigate a corpus or language interactively, without committing to a pipeline plan.
nl_triggers:
  - "explore this language"
  - "what's in this corpus?"
  - "investigate [dataset/language]"
routes_to: magic-linguistic-orchestrator (explore mode) → corpus / scope (specialist)
---

# /linguistic:explore

Enter exploration mode — read-only, curiosity-driven inspection of a language or corpus before deciding what to do.

The orchestrator will read available data (Wikipedia dumps, FLEx exports, OLDI snapshots, etc.) and surface:
- Language identification confidence (via `magic-linguistic-scope`).
- Script & encoding observations (via `magic-linguistic-scripts`).
- Corpus size, register mix, dedup stats (via `magic-linguistic-corpus`).
- Tokenizer fertility against a baseline (via `magic-linguistic-tokenize`).

You stay in exploration mode until you opt into a plan via `/linguistic:propose` or `/linguistic:lifecycle`.
