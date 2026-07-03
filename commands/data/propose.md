<!-- Natural Language Triggers: "what should we do?", "propose a plan", "suggestions?", "what's the next step?", "create a processing plan" -->

Run a propose-then-act cycle for the current data processing task.

**Steps:**
1. Read workspace_state.md to understand the current objective and progress
2. Inspect the data — run discovery scripts as appropriate: `detect_issues.py` (cleaning skill, Tier A scriptable), `detect_all_issues.py` (profiling skill, Tier A scriptable), `detect_patterns.py` (exploration skill, Tier A scriptable). All three can be called directly via CLI.
3. Present findings as numbered options with:
   - What was found (issue type, affected columns, severity)
   - Proposed approach for each finding (clean, transform, synthesize, skip)
   - Estimated impact (rows affected, data loss risk)
4. Wait for user to choose which options to pursue
5. Record the decision in analysis_journal.md
6. Hand off to the appropriate skill for execution

**Output format:**
```
## Processing Proposal

### 1. [Issue title] — [severity: HIGH/MEDIUM/LOW]
**Affected:** [column(s)], [N rows] ([X%] of data)
**Finding:** [concrete description with sample values]
**Options:**
  A. [approach] — [estimated impact]
  B. [approach] — [estimated impact]
  C. Skip — flag for manual review
**Recommended:** [option] because [rationale]

### 2. ...
```

**Key rules:**
- Always present options before acting
- Use uncertainty language ("suggests", "appears to", "may indicate")
- Include confidence levels (high/medium/low) for each finding
- Never force a single path — always offer alternatives

**See also:** `/data:findings` for raw findings, `/data:decide` to record choices, `/data:spec` to formalize as a data spec.

$ARGUMENTS
