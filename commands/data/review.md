<!-- Natural Language Triggers: "review what we've done", "show decisions", "review progress", "what did we decide?", "decision history" -->

Review decisions and quality progress for the current workspace.

**Steps:**
1. Read `logs/analysis_journal.md` — all recorded decisions
2. Read quality reports from `logs/` — quality scores over time (if multiple runs)
3. Read `workspace_state.md` — current lifecycle phase and objective
4. Present a review summary:

```
## Decision Review

### Decisions Made ([count] total)
| # | When | Context | Decision | Follow-up |
|---|------|---------|----------|-----------|
| 1 | ... | ... | ... | ... |

### Quality Progress
- Initial quality score: [if available]
- Current quality score: [if available]
- Key improvements: [summary of what changed]

### Open Items
- [decisions still pending or follow-ups not yet completed]

### Recommendations
- [suggestions for next steps based on review]
```

$ARGUMENTS
