---
description: Investigate a corpus or language interactively, without committing to a pipeline plan.
nl_triggers:
  - "explore this language"
  - "what's in this corpus?"
  - "investigate [dataset/language]"
routes_to: linguistic-orchestrator (explore mode) → corpus / scope (specialist)
---

# /linguistic:explore

Enter exploration mode — read-only, curiosity-driven inspection of a language or corpus before deciding what to do.

The orchestrator will read available data (Wikipedia dumps, FLEx exports, OLDI snapshots, etc.) and surface:
- Language identification confidence (via `linguistic-scope`).
- Script & encoding observations (via `linguistic-scripts`).
- Corpus size, register mix, dedup stats (via `linguistic-corpus`).
- Tokenizer fertility against a baseline (via `linguistic-tokenize`).

You stay in exploration mode until you opt into a plan via `/linguistic:propose` or `/linguistic:lifecycle`.
