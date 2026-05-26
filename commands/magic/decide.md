<!-- Natural Language Triggers: "let's go with option X", "record that decision", "I choose...", "do option X", "record that" -->

Record a decision in the analysis journal.

**Steps:**
1. Read `logs/analysis_journal.md` to understand current state
2. If arguments provided, record the decision directly
3. If no arguments, ask the user what decision to record:
   - What was the context? (e.g., "Cleaning plan for column X")
   - What options were considered?
   - What was decided and why?
4. Format and append the entry to `## User Decisions` in `logs/analysis_journal.md`:

```markdown
### Decision: [Brief title]
- **Timestamp:** 2026-04-10T15:30:00+08:00
- **Context:** Sentinel values found in 3,270 rows of `definitions_yue`
- **Options considered:** A. Fill via LLM synthesis, B. Drop rows, C. Flag and skip
- **Chosen:** A — Fill via LLM synthesis
- **Rationale:** Definitions are recoverable from context columns
- **Follow-up:** Route to magic-data-synthesis with fill-sentinels mode
```

5. If the decision triggers further processing, route to the appropriate skill:
   - Cleaning decisions → `magic-data-cleaning`
   - Synthesis/fill decisions → `magic-data-synthesis`
   - Transform decisions → `magic-data-transformation`
6. Confirm: "Decision recorded. [Next action if applicable]."

**Prefixes:** `[auto]` for autonomous mode, `[fast-forward]` for fast-forwarded decisions.

**See also:** `/magic:findings` to review options, `/magic:propose` to generate a plan, `/magic:review` to see decision history.

$ARGUMENTS
