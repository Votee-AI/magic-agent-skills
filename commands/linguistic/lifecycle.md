---
description: Enter the full linguistic pipeline orchestrator (Scope → Acquire → Analyze → Evaluate → Release).
nl_triggers:
  - "help me build an LLM for [language]"
  - "start the linguistic pipeline"
  - "let's work on [language]"
routes_to: linguistic-orchestrator
---

# /linguistic:lifecycle

Activate the `linguistic-orchestrator` skill and enter the 5-phase pipeline. The orchestrator will:

1. Read or create `workspace_state.md` for the current cwd.
2. Identify the target language(s) and resource class via `linguistic-scope`.
3. Triage the user's request to the right phase (Scope / Acquire / Analyze / Evaluate / Release).
4. Route to the appropriate specialist skill(s).

This is the same behavior as natural-language entry. Use the slash command when you want to be explicit, or to start a fresh pipeline session.
