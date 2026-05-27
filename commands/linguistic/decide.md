---
description: Force a strategic decision (resource class, transfer source, eval suite, ethics gate).
nl_triggers:
  - "decide on [topic]"
  - "make a call on [topic]"
  - "what should we use for [topic]?"
routes_to: linguistic-orchestrator (decision mode)
---

# /linguistic:decide

Crystallize a pending decision recorded in `workspace_state.md` under "Open Questions". The orchestrator presents the options with bounded pros/cons and routes to the relevant specialist for the recommendation.

Common decisions:
- Transfer source language (via `linguistic-scope` URIEL distance).
- Vocabulary extension method (via `linguistic-tokenize`).
- Eval benchmark suite (via `linguistic-eval`).
- Sacred-text gating threshold (via `linguistic-ethics`).
- Adapter vs full fine-tune vs LoRA (via `linguistic-transfer`).

Decisions are recorded with rationale in `workspace_state.md` under "Decisions Recorded".
