---
description: Force a strategic decision (resource class, transfer source, eval suite, ethics gate).
nl_triggers:
  - "decide on [topic]"
  - "make a call on [topic]"
  - "what should we use for [topic]?"
routes_to: magic-linguistic-orchestrator (decision mode)
---

# /linguistic:decide

Crystallize a pending decision recorded in `workspace_state.md` under "Open Questions". The orchestrator presents the options with bounded pros/cons and routes to the relevant specialist for the recommendation.

Common decisions:
- Transfer source language (via `magic-linguistic-scope` URIEL distance).
- Vocabulary extension method (via `magic-linguistic-tokenize`).
- Eval benchmark suite (via `magic-linguistic-eval`).
- Sacred-text gating threshold (via `magic-linguistic-ethics`).
- Adapter vs full fine-tune vs LoRA (via `magic-linguistic-transfer`).

Decisions are recorded with rationale in `workspace_state.md` under "Decisions Recorded".
