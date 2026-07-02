---
description: List structured findings (data gaps, ethics flags, fertility issues, eval contamination).
nl_triggers:
  - "what are the findings"
  - "show me the issues"
  - "what's wrong"
routes_to: magic-linguistic-orchestrator (findings mode)
---

# /linguistic:findings

Surface structured findings accumulated by specialist skills during the session, grouped by severity:

| Severity | Examples |
|---|---|
| **HIGH** | License violation risk; sacred-text in training corpus; eval set contamination > 10%; tokenizer fertility > 5x baseline |
| **MEDIUM** | Significant register imbalance (e.g., Bible-only); URIEL distance to chosen transfer source > 0.6; missing ethics sign-off |
| **LOW** | Minor dedup gain available; stale benchmark version; non-canonical romanization |

Each finding includes: source skill, evidence, recommended action, and optional auto-fix toggle (collaborative mode).
