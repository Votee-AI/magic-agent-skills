---
description: Review state + findings + recent decisions + skill-routing history.
nl_triggers:
  - "review status"
  - "where are we"
  - "summarize what we've done"
routes_to: magic-linguistic-orchestrator (review mode)
---

# /linguistic:review

Comprehensive review combining `/linguistic:status` (one-line) with `/linguistic:findings` (full list) plus recent skill-routing log entries. Useful for:

- Cross-session resume after a break.
- Stakeholder briefing.
- Pre-merge checklist before advancing a phase.

Output structure:
1. Phase indicator + language/resource summary.
2. Findings (grouped by severity).
3. Decisions Recorded (last 10).
4. Skill Routing History (last 20).
5. Open Questions.
6. Recommended next action.
