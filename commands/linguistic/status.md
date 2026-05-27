---
description: Quick one-line phase + skill-routing summary.
nl_triggers:
  - "what's my status"
  - "where are we?"
  - "current phase?"
routes_to: linguistic-orchestrator (status mode)
---

# /linguistic:status

One-line summary in the form:

```
[Phase: <Scope|Acquire|Analyze|Evaluate|Release> | Language: <name> (<ISO>) | Resource Class: <0-5> | Last skill: <name> | Open findings: <count>]
```

Reads `workspace_state.md` directly. No specialist calls. Fast — used between substantive operations.
