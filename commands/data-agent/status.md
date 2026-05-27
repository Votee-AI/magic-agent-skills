<!-- Natural Language Triggers: "where are we?", "what's the status?", "show progress", "what have we done?", "current state" -->

Show current workspace state with interaction context.

**Steps:**
1. Read `workspace_state.md` — objective, plan, progress, interaction mode, lifecycle phase
2. Read `logs/analysis_journal.md` — recent decisions and findings
3. Check `data/checkpoints/` for latest checkpoint and its metadata
4. Check `logs/` for recent analysis reports
5. Present a concise status summary:

```
## Workspace Status

**Objective:** [from workspace_state.md]
**Interaction mode:** [Autonomous/Collaborative/Guided]
**Lifecycle phase:** [Discover/Plan/Execute/Validate/Deliver]
**Complexity tier:** [Tier 1/2/3]
**Latest checkpoint:** [name] ([timestamp])
**Quality score:** [if available]

### Recent Decisions
- [last 3-5 decisions from analysis journal]

### Pending Actions
- [next steps based on current phase]
```

$ARGUMENTS
