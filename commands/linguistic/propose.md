---
description: Generate a phase plan for the current target language (or for a freshly-named one).
nl_triggers:
  - "propose a plan"
  - "what should I do for [language]?"
  - "give me a roadmap"
routes_to: magic-linguistic-orchestrator (planning mode)
---

# /linguistic:propose

Produce a structured plan covering all 5 phases (Scope → Acquire → Analyze → Evaluate → Release) for the target language, including:

- Recommended data sources (with ethics flags).
- Tokenizer + vocabulary strategy.
- Adapter / fine-tune choice.
- Eval suite + metrics.
- Release gating.

Output is a `plan.md` written to the current workspace, suitable for review and editing before execution.
